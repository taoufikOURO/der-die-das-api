from sqlalchemy import Column, String, DateTime, ForeignKey, Integer

from app.database import Base
from app.utils.generators import generate_id, utc_now


class Rush(Base):
    """Représente une session de jeu (un rush) : un ensemble de mots proposés d'affilée."""

    __tablename__ = "rushes"

    id = Column(String(32), primary_key=True, default=generate_id)
    user_id = Column(
        String(32),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    level = Column(String(10), nullable=False)
    started_at = Column(DateTime(timezone=True), default=utc_now)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    score = Column(Integer, nullable=True)
