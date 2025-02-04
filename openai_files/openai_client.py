from datetime import datetime, timezone
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

    s3_client = S3ClientFactory()
    client = OpenAIClient()
    holiday_list = client.fetch_holiday_list()
    holiday_image_prompt = get_prompt(PromptType.GENERATE_IMAGE_HAPPY, holiday_list)
    print(holiday_image_prompt)
    holiday_image_url = client.fetch_generated_image_url(holiday_image_prompt)
    print(holiday_image_url)
    curr_date_str = datetime.now().strftime("%d-%b-%Y").upper()
    file_name = f"{PromptType.GENERATE_IMAGE_HAPPY.value}-{curr_date_str}"
    u_file_name = client.generate_unique_file_name(file_name)
    s3_image_url = s3_client.save_image_to_s3(holiday_image_url, u_file_name)
    print(f"{s3_image_url=}")
    pre_signed_url = s3_client.fetch_presigned_url(u_file_name)
    print(f"{pre_signed_url=}")
