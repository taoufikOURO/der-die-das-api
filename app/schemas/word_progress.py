from datetime import datetime
from pydantic import BaseModel


class WordProgressOut(BaseModel):
    """État de progression d'un utilisateur sur un mot donné."""

    word_id: str
    correct_streak: int
    mastered_at: datetime | None
    total_attempts: int
    total_correct: int

    class Config:
        from_attributes = True


class LevelProgress(BaseModel):
    """Progression agrégée sur un niveau entier, utilisée pour le dashboard."""

    level: str
    total_words: int
    mastered_words: int
    completion_ratio: float
    level_completed: bool
