from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey

from app.database import Base
from app.utils.generators import generate_id, utc_now


class Attempt(Base):
    """Journal immuable de chaque réponse donnée par un utilisateur, pendant un rush donné."""

    __tablename__ = "attempts"

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
    rush_id = Column(
        String(32),
        ForeignKey("rushes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_correct = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
