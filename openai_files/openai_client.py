import datetime
import logging
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from .openai_exceptions import OpenAIClientError
from .prompts import get_prompt
from .utils import PromptType


class OpenAIClient:
    def __init__(self, chat_model: str = "gpt-4o-mini"):
        load_dotenv()
        self.client = OpenAI()
        self.chat_model = chat_model

    def fetch_holiday_list(self) -> str:
        date_today = datetime.datetime.now().strftime("%B %d, %Y")
        prompt = get_prompt(PromptType.GET_HOLIDAYS, date_today)
        return self.fetch_chat_completion(prompt)

    def fetch_chat_completion(self, prompt: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.chat_model,
                messages=self.generate_messages(
                    prompt,
                    "You are an expert on international holidays, commemorations, and funny celebrations.",
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
            raise OpenAIClientError(f"OpenAI API call failed: {str(e)}") from e

    def generate_messages(
        self, prompt: str, system_message: Optional[str] = None
    ) -> list:
        system_message = system_message or "You are a helpful assistant."
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ]


if __name__ == "__main__":
    client = OpenAIClient()
    print(client.fetch_holiday_list())
