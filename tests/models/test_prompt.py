from datetime import datetime

import pytest

from server.models.prompt import Prompt
from server.models.utils import TaskStatus
from openai_files.utils import PromptType


@pytest.mark.parametrize(
    "prompt_type",
    [
        PromptType.GENERATE_IMAGE_HAPPY,
        PromptType.GENERATE_IMAGE_SAD,
        PromptType.GET_HOLIDAYS,
    ],
)
def test_prompt_creation(session, prompt_type):
    # Create a new Prompt
    new_prompt = Prompt(
        prompt_text="Generate an image of a crypto investor.",
        prompt_date=datetime.strptime("11-29-2024", "%m-%d-%Y").date(),
        prompt_type=prompt_type,
    )
    session.add(new_prompt)
    session.commit()

    # Query and validate
    saved_prompt = session.query(Prompt).first()
    assert saved_prompt is not None
    assert saved_prompt.prompt_text == "Generate an image of a crypto investor."
    assert saved_prompt.status == TaskStatus.PENDING
