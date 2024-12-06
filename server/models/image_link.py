# mypy: ignore-errors

from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from .base import Base
from .utils import TaskStatus


class ImageLink(Base):
    __tablename__ = "image_link"

    prompt = relationship("Prompt", back_populates="image")
    prompt_id = Column(
        Integer,
        ForeignKey("prompt.id"),
        nullable=False,
        index=True,
    )

    openai_image_url = Column(
        Text,
        nullable=False,
    )
    s3_image_url = Column(
        Text,
        nullable=True,
    )
    status = Column(
        Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING,
        server_default=TaskStatus.PENDING.name,
    )
