from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)

from app.database import Base
from app.utils.generators import generate_id, utc_now


class WordProgress(Base):
    """
    État agrégé de la progression d'un utilisateur sur un mot.
    Mis à jour après chaque tentative (jamais recalculé depuis le journal,
    sauf besoin de réconciliation).
    """

    __tablename__ = "word_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "word_id", name="uq_user_word_progress"),
    )

    id = Column(String(32), primary_key=True, default=generate_id)
    user_id = Column(
        String(32),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    word_id = Column(
        String(32),
        ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    correct_streak = Column(Integer, nullable=False, default=0)
    last_counted_rush_id = Column(
        String(32), nullable=True
    )  # évite de compter 2 fois le même rush
    mastered_at = Column(
        DateTime(timezone=True), nullable=True
    )  # null = pas encore maîtrisé

    total_attempts = Column(Integer, nullable=False, default=0)
    total_correct = Column(Integer, nullable=False, default=0)
    last_attempt_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
