import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.database import Base, get_db
from app.models import User, Word, Attempt, Rush, WordProgress, Session as UserSession
from app.config import settings

engine = create_engine(settings.test_database_url)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    """Crée toutes les tables avant le test, les supprime après."""

    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    """
    Client de test FastAPI, avec la dépendance get_db remplacée par
    la session PostgreSQL de test.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def mock_send_otp_email():
    with patch("app.services.auth_service.send_otp_email") as mock:
        yield mock
