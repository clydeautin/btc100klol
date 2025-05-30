from app import db
from server.models import Base
from contextlib import contextmanager
from sqlalchemy.orm import Query


class DBAccessor:
    _instance: Base = None
    _db = db

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DBAccessor, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def add(self, instance: Base) -> None:
        self._db.session.add(instance)

    def commit(self) -> None:
        self._db.session.commit()

    def flush(self) -> None:
        self._db.session.flush()

    def rollback(self) -> None:
        self._db.session.rollback()

    def delete(self, instance: Base) -> None:
        self._db.session.delete(instance)

    def refresh(self, instance: Base) -> None:
        self._db.session.refresh(instance)

    def query(self, *args, **kwargs) -> Query:
        return self._db.session.query(*args, **kwargs)

    @contextmanager
    def session_scope(self):
        try:
            yield
            self.commit()
        except Exception:
            self.rollback()
            raise
