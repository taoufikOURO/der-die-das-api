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


@pytest.fixture()
def sample_words(db_session):
    """Insère des mots de test en base, niveau A1, pour les tests de rush/révision."""

    words = [
        Word(
            word="Hund",
            article="der",
            level="A1",
            fr_translation="Chien",
            en_translation="Dog",
        ),
        Word(
            word="Katze",
            article="die",
            level="A1",
            fr_translation="Chat",
            en_translation="Cat",
        ),
        Word(
            word="Buch",
            article="das",
            level="A1",
            fr_translation="Livre",
            en_translation="Book",
        ),
        Word(
            word="Tisch",
            article="der",
            level="A1",
            fr_translation="Table",
            en_translation="Table",
        ),
        Word(
            word="Blume",
            article="die",
            level="A1",
            fr_translation="Fleur",
            en_translation="Flower",
        ),
    ]
    db_session.add_all(words)
    db_session.commit()
    return words


@pytest.fixture()
def authenticated_client(client, mock_send_otp_email, db_session):
    """
    Inscrit, valide l'email et connecte un utilisateur de test.
    Le cookie de session est conservé automatiquement par le TestClient
    pour les requêtes suivantes.
    """

    client.post(
        "/auth/register",
        json={
            "pseudo": "testuser",
            "email": "test@example.com",
            "password": "Test1234",
            "password_confirmation": "Test1234",
            "level": "A1",
        },
    )

    user = db_session.query(User).filter(User.email == "test@example.com").first()
    client.post(
        "/auth/verify-otp",
        json={"email": "test@example.com", "otp_code": user.otp_code},
    )

    client.post("/auth/login", json={"identifier": "testuser", "password": "Test1234"})

    return client
