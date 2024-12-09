# mypy: ignore-errors

from sqlalchemy import (
    Column,
    Date,
    Enum,
    Text,
)
from sqlalchemy.orm import relationship

from .base import Base
from openai_files.utils import PromptType
from .utils import TaskStatus


class Prompt(Base):
    __tablename__ = "prompt"

    image = relationship(
        "ImageLink",
        back_populates="prompt",
        uselist=False,
    )

    prompt_text = Column(
        Text,
        nullable=False,
    )
    prompt_date = Column(Date, nullable=False)
    prompt_type = Column(Enum(PromptType), nullable=False)
    status = Column(
        Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING,
        server_default=TaskStatus.PENDING.name,
    )
