from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Centralise toutes les variables de configuration de l'application,
    lues automatiquement depuis le fichier .env à la racine du projet.
    """

    database_url: str
    secret_key: str

    mastery_streak_threshold: int = 3
    level_completion_threshold: float = 0.85

    smtp_from: str
    brevo_api_key: str

    otp_expiry_minutes: int = 10
    session_expiry_days: int = 7
    otp_resend_cooldown_seconds: int = 60

    environment: str = "development"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    rush_size: int = 10

    test_database_url: str = ""

    allowed_origins_raw: str = "http://localhost:5173,http://localhost:3000"

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins_raw.split(",")]

    class Config:
        env_file = ".env"
        env_prefix = ""


settings = Settings()
