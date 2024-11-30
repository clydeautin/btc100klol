import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server.models.base import Base


@pytest.fixture(scope="function")
def engine():
    # init an in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
