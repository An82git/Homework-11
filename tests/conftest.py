import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.services.auth import auth_service
from src.database.models import Base
from src.database.db import get_db
from main import app


SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost:5433/postgres"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    
    def get_email(token):
        return token

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[auth_service.get_email_from_token] = get_email

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {"username": "deadpool", "email": "deadpool@example.com", "password": "123456789"}
