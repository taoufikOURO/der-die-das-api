from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Centralise toutes les variables de configuration de l'application,
    lues automatiquement depuis le fichier .env à la racine du projet.
    """

    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    mastery_streak_threshold: int = 3
    level_completion_threshold: float = 0.85

    class Config:
        env_file = ".env"


# Instance unique, importée partout où la configuration est nécessaire
settings = Settings()
