from datetime import datetime, timedelta

from server.s3_client import S3ClientFactory
from server.db_accessor import DBAccessor
from server.models import Prompt, DailyImageVersion
from openai_files.openai_client import OpenAIClient
from openai_files.utils import PromptType
from server.models.utils import TaskStatus
from server.models.image_link import ImageLink
from openai_files.helpers import get_prompt

from const import AWS_PRESIGNED_URL_EXPIRATION_SECONDS
import logging

logger = logging.getLogger(__name__)


class DailyImageGenerator:
    def __init__(
        self,
        openai_client: OpenAIClient,
        s3_client: S3ClientFactory,
        db_accessor: DBAccessor,
    ):
        self.openai_client = openai_client
        self.s3_client = s3_client
        self.db_accessor = db_accessor

    def generate_daily_images(
        self,
        prompt_types: list[PromptType],
        target_date: datetime,
        presigned_url_expiry: datetime,
    ) -> list[DailyImageVersion]:
        logger.info(f"Starting daily image generation for target date: {target_date}")
        
        # Get holiday list
        logger.info("Fetching holiday list...")
        holiday_prompt_record = self._create_holiday_prompt_record(target_date)
        holiday_list = self._fetch_holiday_list(holiday_prompt_record, target_date)
        logger.info(f"Holiday list fetched: {len(holiday_list)} chars")

        daily_versions: list[DailyImageVersion] = []

        # Generate image prompts
        for prompt_type in prompt_types:
            logger.info(f"Processing prompt type: {prompt_type.value}")
            image_prompt_record = self._create_image_prompt_record(prompt_type)
            
            logger.info("Generating image prompt...")
            image_prompt_text = self._generate_image_prompt(
                image_prompt_record, holiday_list
            )
            logger.info(f"Image prompt generated: {len(image_prompt_text)} chars")

            # Generate and save image
            image_link = self._create_image_link(image_prompt_record)
            
            logger.info("Generating image via OpenAI...")
            openai_url = self._generate_image(image_link, image_prompt_text)
            
            logger.info("Saving image to S3...")
            s3_url = self._save_to_s3(image_link, openai_url, target_date)
            logger.info(f"Image saved to S3: {s3_url}")

            # Create and finalize daily version
            daily_version = self._create_daily_version(image_link, prompt_type)
            self._finalize_daily_version(daily_version, s3_url, presigned_url_expiry)
            daily_versions.append(daily_version)
            logger.info(f"Daily version finalized for {prompt_type.value}")

        logger.info("Daily image generation completed successfully")
        return daily_versions

    def _create_holiday_prompt_record(
        self,
        target_date: datetime,
    ) -> Prompt:
        prompt = Prompt(
            prompt_text="",
            prompt_date=target_date,
            prompt_type=PromptType.GET_HOLIDAYS,
            status=TaskStatus.PENDING,
        )
        with self.db_accessor.session_scope() as session:
            session.add(prompt)
        return prompt

    def _fetch_holiday_list(self, prompt: Prompt, target_date: datetime) -> str:
        status = TaskStatus.FAILED
        holiday_list = ""
        error: Exception | None = None

        try:
            holiday_list = self.openai_client.fetch_holiday_list(target_date)
            status = TaskStatus.COMPLETED
        except Exception as e:
            holiday_list = str(e)
            error = e

        with self.db_accessor.session_scope() as session:
            attached_prompt = session.merge(prompt)
            attached_prompt.prompt_text = holiday_list
            attached_prompt.status = status

        if error:
            raise error

        return holiday_list

    def _create_image_prompt_record(self, prompt_type: PromptType) -> Prompt:
        prompt = Prompt(
            prompt_text="",
            prompt_date=datetime.now(),
            prompt_type=prompt_type,
            status=TaskStatus.PENDING,
        )
        with self.db_accessor.session_scope() as session:
            session.add(prompt)
        return prompt

    def _generate_image_prompt(self, prompt: Prompt, holiday_list: str) -> str:
        # TODO(john): Extract try/except -> merge -> write to its own helper
        # to DRY this up. Challenge will be to pass db column names.
        # It's probably easier to just pass the entire function to the helper
        # or make it a decorator. Not high priority.
        status = TaskStatus.FAILED
        image_prompt_text = ""
        error: Exception | None = None

        try:
            image_prompt_text = get_prompt(prompt.prompt_type, holiday_list)
            status = TaskStatus.COMPLETED
        except Exception as e:
            image_prompt_text = str(e)
            error = e

        with self.db_accessor.session_scope() as session:
            attached_prompt = session.merge(prompt)
            attached_prompt.status = status
            attached_prompt.prompt_text = image_prompt_text

        if error:
            raise error

        return image_prompt_text

    def _create_image_link(self, prompt: Prompt) -> ImageLink:
        image_link = ImageLink(
            prompt_id=prompt.id,
            openai_image_url="",
            status=TaskStatus.PENDING,
        )
        with self.db_accessor.session_scope() as session:
            session.add(image_link)
        return image_link

    def _generate_image(self, image_link: ImageLink, prompt_text: str) -> str:
        status = TaskStatus.FAILED
        openai_url = ""
        error: Exception | None = None

        try:
            openai_url = self.openai_client.fetch_generated_image_url(prompt_text)
            status = TaskStatus.PROCESSING
        except Exception as e:
            openai_url = str(e)
            error = e

        with self.db_accessor.session_scope() as session:
            attached_image_link = session.merge(image_link)
            attached_image_link.status = status
            attached_image_link.openai_image_url = openai_url

        if error:
            raise error

        return openai_url

    def _save_to_s3(
        self, image_link: ImageLink, openai_url: str, current_date: datetime
    ) -> str:
        status = TaskStatus.FAILED
        s3_image_url = ""
        error: Exception | None = None

        try:
            curr_date_str = current_date.strftime("%d-%b-%Y").upper()
            file_name = f"{image_link.prompt.prompt_type.value}-{curr_date_str}"
            u_file_name = self.openai_client.generate_unique_file_name(file_name)
            s3_image_url = self.s3_client.save_image_to_s3(openai_url, u_file_name)
            status = TaskStatus.COMPLETED
        except Exception as e:
            s3_image_url = str(e)
            error = e

        with self.db_accessor.session_scope() as session:
            attached_image_link = session.merge(image_link)
            attached_image_link.status = status
            attached_image_link.s3_image_url = s3_image_url

        if error:
            raise error

        return u_file_name

    def _create_daily_version(
        self, image_link: ImageLink, prompt_type: PromptType
    ) -> DailyImageVersion:
        daily_version = DailyImageVersion(
            image_link_id=image_link.id,
            image_link=image_link,
            prompt_type=prompt_type,
            prompt_date=datetime.now(),
            status=TaskStatus.PENDING,
        )
        with self.db_accessor.session_scope() as session:
            session.add(daily_version)
        return daily_version

    def _finalize_daily_version(
        self,
        version: DailyImageVersion,
        file_name: str,
        presigned_url_expiry: datetime,
    ) -> None:
        status = TaskStatus.FAILED
        presigned_url = ""
        error: Exception | None = None

        try:
            presigned_url = self.s3_client.fetch_presigned_url(
                file_name,
                AWS_PRESIGNED_URL_EXPIRATION_SECONDS,
            )
            status = TaskStatus.COMPLETED
        except Exception as e:
            presigned_url = str(e)
            error = e

        with self.db_accessor.session_scope() as session:
            is_success = status is TaskStatus.COMPLETED
            attached_version = session.merge(version)

            # Deactivate other versions but only on success
            if is_success:
                session.query(DailyImageVersion).filter(
                    DailyImageVersion.prompt_type == attached_version.prompt_type,
                    DailyImageVersion.is_active,
                    DailyImageVersion.id != attached_version.id,
                ).update({DailyImageVersion.is_active: False})

            # Update current version
            attached_version.presigned_url = presigned_url
            attached_version.status = status
            attached_version.presigned_url_expiry = (
                presigned_url_expiry if is_success else None
            )
            attached_version.is_active = is_success

        if error:
            raise error
