from datetime import datetime
from pydantic import BaseModel


class AttemptCreate(BaseModel):
    """Réponse envoyée par l'utilisateur pendant un rush."""

    rush_id: str
    word_id: str
    proposed_article: str  # der, die, das


class AttemptResult(BaseModel):
    """Résultat renvoyé après vérification d'une réponse."""

    word_id: str
    correct_article: str
    is_correct: bool


class AttemptOut(BaseModel):
    """Représentation d'une ligne du journal, si consultée directement."""

    id: str
    user_id: str
    word_id: str
    rush_id: str
    is_correct: bool
    created_at: datetime

    class Config:
        from_attributes = True
