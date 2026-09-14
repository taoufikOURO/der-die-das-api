from datetime import datetime
from pydantic import BaseModel


class WordQuestion(BaseModel):
    id: str
    word: str
    fr_translation: str | None
    en_translation: str | None

    class Config:
        from_attributes = True


class WordOut(BaseModel):
    id: str
    word: str
    article: str
    level: str | None
    fr_translation: str | None
    en_translation: str | None

    class Config:
        from_attributes = True


class WordWithProgress(BaseModel):
    """Mot enrichi de la progression de l'utilisateur, pour l'écran de révision."""

    id: str
    word: str
    article: str
    level: str | None
    fr_translation: str | None
    en_translation: str | None
    correct_streak: int
    mastered_at: datetime | None
    total_attempts: int


class WordListOut(BaseModel):
    """Réponse paginée pour la liste des mots."""

    total: int
    page: int
    page_size: int
    words: list[WordWithProgress]
