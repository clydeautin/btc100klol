# mypy: ignore-errors

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Date,
    Enum,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from .base import Base
from .utils import TaskStatus
from openai_files.utils import PromptType


class DailyImageVersion(Base):
    __tablename__ = "daily_image_version"

    image_link_id = Column(
        Integer,
        ForeignKey("image_link.id"),
        nullable=False,
        index=True,
    )
    image_link = relationship("ImageLink")

    presigned_url = Column(
        Text,
        nullable=True,
    )
    presigned_url_expiry = Column(
        DateTime,
        nullable=True,
    )
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    prompt_type = Column(Enum(PromptType), nullable=False)
    prompt_date = Column(Date, nullable=False)

    error = Column(
        Text,
        nullable=True,
    )
    error_message = Column(
        Text,
        nullable=True,
    )

    status = Column(
        Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING,
        server_default=TaskStatus.PENDING.name,
    )

    # TODO(john): create restrictions to ensure that presigned urls also have expiry date.
    # latest_happy_version = daily_image_version.query.filter(
    #     DailyImageVersion.prompt_type == PromptType.HAPPY,
    #     DailyImageVersion.is_active == True,
    # ).order_by(DailyImageVersion.prompt_date.desc()).first()
