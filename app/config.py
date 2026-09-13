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

    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_from: str

    otp_expiry_minutes: int = 10
    session_expiry_days: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
