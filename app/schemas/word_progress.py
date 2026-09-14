from datetime import datetime
from pydantic import BaseModel

from app.schemas.word import WordOut


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
    in_progress_words: int
    not_started_words: int
    completion_ratio: float
    level_completed: bool
    words_needed_to_complete: int
    estimated_rushes_remaining: int
    accuracy: float
    total_rushes_played: int
    last_rush_score: int | None
    last_rush_at: datetime | None
    best_rush_score: int | None
    words_to_review: list[WordOut]
