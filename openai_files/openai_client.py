from datetime import datetime, timezone, timedelta
import logging
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from const import (
    DEFAULT_IMAGE_QUALITY,
    DEFAULT_IMAGE_SIZE,
)
from .helpers import get_prompt, get_system_message
from .openai_exceptions import OpenAIClientError
from .utils import PromptType

load_dotenv()


class OpenAIClient:
    def __init__(self, chat_model: str = "gpt-4o-mini", image_model: str = "dall-e-3"):
        self.client = OpenAI()
        self.chat_model = chat_model
        self.image_model = image_model

    def fetch_holiday_list(self) -> str:
        date_today = datetime.now().strftime("%B %d, %Y")
        prompt = get_prompt(PromptType.GET_HOLIDAYS, date_today)
        system_message = get_system_message(PromptType.GET_HOLIDAYS)

        return self.fetch_chat_completion(
            prompt,
            system_message,
        )

    def fetch_chat_completion(self, prompt: str, system_message: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.chat_model,
                messages=self.generate_messages(
                    prompt,
                    system_message,
                ),
            )

            content = completion.choices[0].message.content
            if not content:
                raise ValueError("OpenAI response message is blank.")

            return content

        except (IndexError, AttributeError, KeyError) as e:
            logging.error(f"Unexpected response structure: {e}")
            raise ValueError(
                "OpenAI chat completion returned an unexpected structure."
            ) from e

        except OpenAIError as e:
            logging.error(f"OpenAI error occurred: {e}")
            raise OpenAIClientError(
                f"OpenAI API chat completion failed: {str(e)}"
            ) from e

    def fetch_generated_image_url(self, prompt) -> str:
        try:
            response = self.client.images.generate(
                model=self.image_model,
                prompt=prompt,
                size=DEFAULT_IMAGE_SIZE,
                quality=DEFAULT_IMAGE_QUALITY,
                n=1,
            )

            url = response.data[0].url
            if not url:
                raise ValueError("OpenAI image URL is blank.")

            return url

        except (IndexError, AttributeError, KeyError) as e:
            logging.error(f"Unexpected response structure: {e}")
            raise ValueError(
                "OpenAI image generation returned an unexpected structure."
            ) from e

        except OpenAIError as e:
            logging.error(f"OpenAI error occurred: {e}")
            raise OpenAIClientError(
                f"OpenAI API image generation failed: {str(e)}"
            ) from e

    def generate_unique_file_name(self, file_name: str, file_type: str = "png") -> str:
        current_utc_epoch_s = int(datetime.now(timezone.utc).timestamp())
        return f"{file_name}-{current_utc_epoch_s}.{file_type}"

    def generate_messages(
        self, prompt: str, system_message: Optional[str] = None
    ) -> list:
        system_message = system_message or "You are a helpful assistant."
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ]


if __name__ == "__main__":
    # Live tests. Remove when launching.
    from server.s3_client import S3ClientFactory
    from server.db_accessor import DBAccessor
    from server.models import Prompt
    from server.models.daily_image_version import DailyImageVersion
    from server.models.image_link import ImageLink
    from openai_files.utils import PromptType
    from server.models.utils import TaskStatus
    from app import create_app

    app = create_app()

    with app.app_context():
        s3_client = S3ClientFactory()
        db_accessor = DBAccessor()

        client = OpenAIClient()

        holiday_prompt = Prompt(
            prompt_text="",
            prompt_date=datetime.now(),
            prompt_type=PromptType.GET_HOLIDAYS,
            status=TaskStatus.PENDING,
        )

        with db_accessor.session_scope():
            db_accessor.add(holiday_prompt)
        try:
            holiday_list = client.fetch_holiday_list()
        except Exception as e:
            with db_accessor.session_scope():
                holiday_prompt.status = TaskStatus.FAILED
                holiday_prompt.prompt_text = str(e)
            raise e

        with db_accessor.session_scope():
            holiday_prompt.prompt_text = holiday_list
            holiday_prompt.status = TaskStatus.COMPLETED

        new_image_prompt = Prompt(
            prompt_text="",
            prompt_date=datetime.now(),
            prompt_type=PromptType.GENERATE_IMAGE_HAPPY,
            status=TaskStatus.PENDING,
        )

        with db_accessor.session_scope():
            db_accessor.add(new_image_prompt)

        try:
            holiday_image_prompt = get_prompt(
                PromptType.GENERATE_IMAGE_HAPPY, holiday_list
            )
        except Exception as e:
            with db_accessor.session_scope():
                new_image_prompt.status = TaskStatus.FAILED
                new_image_prompt.prompt_text = str(e)
            raise e

        with db_accessor.session_scope():
            new_image_prompt.prompt_text = holiday_image_prompt
            new_image_prompt.status = TaskStatus.COMPLETED

        new_image_link = ImageLink(
            prompt_id=new_image_prompt.id,
            openai_image_url="",
            status=TaskStatus.PENDING,
        )

        with db_accessor.session_scope():
            db_accessor.add(new_image_link)

        print(f"{holiday_image_prompt=}")
        try:
            holiday_image_openai_url = client.fetch_generated_image_url(
                holiday_image_prompt
            )
        except Exception as e:
            with db_accessor.session_scope():
                new_image_link.status = TaskStatus.FAILED
                new_image_link.openai_image_url = str(e)
            raise e

        with db_accessor.session_scope():
            new_image_link.openai_image_url = holiday_image_openai_url
            new_image_link.status = TaskStatus.PROCESSING

        # Save image to S3.
        try:
            curr_date_str = datetime.now().strftime("%d-%b-%Y").upper()
            file_name = f"{PromptType.GENERATE_IMAGE_HAPPY.value}-{curr_date_str}"
            u_file_name = client.generate_unique_file_name(file_name)
            s3_image_url = s3_client.save_image_to_s3(
                holiday_image_openai_url, u_file_name
            )
        except Exception as e:
            with db_accessor.session_scope():
                new_image_link.status = TaskStatus.FAILED
                new_image_link.s3_image_url = str(e)
            raise e

        with db_accessor.session_scope():
            new_image_link.s3_image_url = s3_image_url
            new_image_link.status = TaskStatus.COMPLETED

        daily_image_version = DailyImageVersion(
            image_link_id=new_image_link.id,
            image_link=new_image_link,
            prompt_type=PromptType.GENERATE_IMAGE_HAPPY,
            prompt_date=datetime.now(),
            status=TaskStatus.PENDING,
        )

        with db_accessor.session_scope():
            db_accessor.add(daily_image_version)

        try:
            print(f"{s3_image_url=}")
            pre_signed_url = s3_client.fetch_presigned_url(
                u_file_name
            )  # explicit expiration date settings
            print(f"{pre_signed_url=}")
        except Exception as e:
            with db_accessor.session_scope():
                daily_image_version.status = TaskStatus.FAILED
                daily_image_version.error = str(e)
            raise e

        # deactivate all other daily image versions of this prompt type
        # TODO(john): re-activate previous daily image version if this one fails.
        with db_accessor.session_scope():
            db_accessor.query(DailyImageVersion).filter(
                DailyImageVersion.prompt_type == PromptType.GENERATE_IMAGE_HAPPY,
                DailyImageVersion.is_active,
                DailyImageVersion.id != daily_image_version.id,
            ).update({DailyImageVersion.is_active: False})

        with db_accessor.session_scope():
            daily_image_version.presigned_url = pre_signed_url
            daily_image_version.presigned_url_expiry = datetime.now() + timedelta(
                seconds=3600 * 24
            )
            daily_image_version.status = TaskStatus.COMPLETED
            daily_image_version.is_active = True
