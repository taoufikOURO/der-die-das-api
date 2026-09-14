from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """
    Centralise toutes les variables de configuration de l'application,
    lues automatiquement depuis le fichier .env à la racine du projet.
    """

    database_url: str
    secret_key: str

    mastery_streak_threshold: int = 3
    level_completion_threshold: float = 0.85

    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_from: str

    otp_expiry_minutes: int = 10
    session_expiry_days: int = 7
    otp_resend_cooldown_seconds: int = 60

    environment: str = "development"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    rush_size: int = 10

    test_database_url: str = ""

    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",")]
        return value

    class Config:
        env_file = ".env"


settings = Settings()
