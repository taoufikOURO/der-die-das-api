from datetime import datetime
from pydantic import BaseModel

from app.schemas.word import WordOut, WordQuestion


class RushStart(BaseModel):
    """Requête de démarrage d'un rush (le niveau vient normalement du profil utilisateur)."""

    level: str


class RushOut(BaseModel):
    """Représentation d'un rush en cours ou terminé."""

    id: str
    level: str
    started_at: datetime
    finished_at: datetime | None
    score: int | None

    class Config:
        from_attributes = True


class RushWords(BaseModel):
    """Liste des mots proposés pour un rush donné (sans l'article, c'est la question)."""

    rush_id: str
    words: list[WordQuestion]


class RushSummary(BaseModel):
    """Résumé renvoyé à la fin d'un rush (l'article est révélé pour les mots ratés)."""

    rush_id: str
    score: int
    total_words: int
    correct_words: int
    words_to_review: list[WordOut]
