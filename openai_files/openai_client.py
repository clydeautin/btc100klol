from datetime import datetime, timezone
import io
import logging
import requests  # type: ignore
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from const import (
    AWS_REGION,
    AWS_S3_BUCKET,
    DEFAULT_IMAGE_QUALITY,
    DEFAULT_IMAGE_SIZE,
)
from .helpers import get_prompt, get_system_message
from .openai_exceptions import OpenAIClientError
from server.s3_client import get_s3_client
from .utils import PromptType


class OpenAIClient:
    def __init__(self, chat_model: str = "gpt-4o-mini", image_model: str = "dall-e-3"):
        load_dotenv()
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

    def save_image_to_s3(self, image_url: str, unique_file_name: str) -> str:
        """Saves image binary to S3 and returns private URL

        While S3 concerns might be better suited as methods in an S3 object,
        but since S3 is only used to upload and pre-sign images, we can get
        away with overloading the OpenAI client a little bit. We should create
        the S3 object if the scope ever expands beyond this.
        """
        response = requests.get(image_url)
        if response.status_code == 200:
            s3 = get_s3_client()

            image_data = response.content

            s3.upload_fileobj(
                io.BytesIO(image_data),
                AWS_S3_BUCKET,
                unique_file_name,
                ExtraArgs={"ContentType": "image/png"},
            )

            s3_url = (
                f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{u_file_name}"
            )

            return s3_url
        else:
            raise Exception(
                f"Failed to retrieve image. Status code: {response.status_code}"
            )

    def fetch_presigned_url(
        self,
        unique_file_name: str,
        expiration: int = 3600,
    ) -> str:
        """Generates publically accessible S3 image URL

        While S3 concerns might be better suited as methods in an S3 object,
        but since S3 is only used to upload and pre-sign images, we can get
        away with overloading the OpenAI client a little bit. We should create
        the S3 object if the scope ever expands beyond this.
        """
        s3 = get_s3_client()  # Ensure you have your S3 client set up
        try:
            url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": AWS_S3_BUCKET, "Key": unique_file_name},
                ExpiresIn=expiration,
            )
            return url
        except Exception as e:
            print(f"Error generating pre-signed URL: {e}")
            raise

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
    client = OpenAIClient()
    holiday_list = client.fetch_holiday_list()
    holiday_image_prompt = get_prompt(PromptType.GENERATE_IMAGE_HAPPY, holiday_list)
    print(holiday_image_prompt)
    holiday_image_url = client.fetch_generated_image_url(holiday_image_prompt)
    print(holiday_image_url)
    curr_date_str = datetime.now().strftime("%d-%b-%Y").upper()
    file_name = f"{PromptType.GENERATE_IMAGE_HAPPY.value}-{curr_date_str}"
    u_file_name = client.generate_unique_file_name(file_name)
    s3_image_url = client.save_image_to_s3(holiday_image_url, u_file_name)
    pre_signed_url = client.fetch_presigned_url(u_file_name)
    print(f"{pre_signed_url=}")
