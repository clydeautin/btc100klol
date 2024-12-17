from typing import Optional, Type, TypeVar

from sqlalchemy.orm import declarative_base, DeclarativeMeta
from sqlalchemy import Column, DateTime, func, Integer

DeclarativeBase: DeclarativeMeta = declarative_base()


class BaseWithoutId(DeclarativeBase):  # type: ignore
    """Expand this for assoc tables."""

    __abstract__ = True

    created = Column(
        DateTime,
        default=func.current_timestamp(),
        nullable=False,
    )
    created_ts = Column(
        Integer,
        default=func.strftime("%s", func.now()),
        nullable=False,
    )
    last_modified = Column(
        DateTime,
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )
    last_modified_ts = Column(
        Integer,
        default=func.strftime("%s", func.now()),
        onupdate=func.strftime("%s", func.now()),
        nullable=False,
    )


# BT = BaseTable
BT = TypeVar("BT", bound="Base")


class Base(BaseWithoutId):
    """Most models should expand on this."""

    __abstract__ = True

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    @classmethod
    def get_by_id(cls: Type[BT], id: int) -> Optional[BT]:
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_by_id_strict(cls: Type[BT], id: int) -> BT:
        return cls.query.filter_by(id=id).one()
