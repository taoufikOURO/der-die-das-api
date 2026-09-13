import secrets
from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash un mot de passe en clair avant stockage en base."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie qu'un mot de passe en clair correspond au hash stocké."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_otp() -> str:
    """Génère un code OTP à 6 chiffres, envoyé par email pour valider l'adresse."""
    return f"{secrets.randbelow(1_000_000):06d}"


def generate_otp_expiry() -> datetime:
    """Calcule la date d'expiration de l'OTP, selon la durée configurée dans .env."""
    return datetime.now(timezone.utc) + timedelta(minutes=settings.otp_expiry_minutes)


def generate_session_token() -> str:
    """Génère un token de session opaque, cryptographiquement sûr, pour le cookie httpOnly."""
    return secrets.token_urlsafe(32)


def generate_session_expiry() -> datetime:
    """Calcule la date d'expiration de la session, selon la durée configurée dans .env."""
    return datetime.now(timezone.utc) + timedelta(days=settings.session_expiry_days)
