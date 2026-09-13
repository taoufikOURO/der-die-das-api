from datetime import datetime
from pydantic import BaseModel


class SessionOut(BaseModel):
    """Représentation interne d'une session, non exposée directement à l'utilisateur
    (le cookie httpOnly contient uniquement le token, jamais renvoyé dans le corps JSON).
    """

    id: str
    user_id: str
    expires_at: datetime

    class Config:
        from_attributes = True
