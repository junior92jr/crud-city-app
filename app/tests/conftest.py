import pytest
from fastapi.testclient import TestClient

from app.database import create_db_and_tables, drop_db_and_tables, get_session
from app.main import create_application


@pytest.fixture(scope="function")
def db_session():
    """Fixture to provide a fresh database session per test with rollback."""
    create_db_and_tables()
    session = next(get_session())

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        drop_db_and_tables()


@pytest.fixture(scope="function")
def client(db_session):
    """Fixture to provide a FastAPI test client with an isolated database session."""

    app = create_application()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_session] = override_get_db

    with TestClient(app) as client:
        yield client
