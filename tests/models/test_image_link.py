from datetime import datetime

from server.models.__init__ import ImageLink, Prompt
from server.models.utils import TaskStatus
from openai_files.utils import PromptType


def test_image_link_creation(session):
    new_prompt = Prompt(
        prompt_text="Generate an image of a crypto investor.",
        prompt_date=datetime.strptime("11-29-2024", "%m-%d-%Y").date(),
        prompt_type=PromptType.GENERATE_IMAGE_HAPPY,
        status=TaskStatus.PENDING,
    )
    session.add(new_prompt)
    session.commit()

    new_image_link = ImageLink(
        prompt_id=new_prompt.id,
        openai_image_url="https://openai.com/happy.png",
        s3_image_url=None,
        status=TaskStatus.PENDING,
    )
    session.add(new_image_link)
    session.commit()

    saved_image = session.query(ImageLink).first()
    assert saved_image is not None
    assert saved_image.prompt_id == new_prompt.id
    assert saved_image.openai_image_url == "https://openai.com/happy.png"
    assert saved_image.prompt.prompt_text == "Generate an image of a crypto investor."
