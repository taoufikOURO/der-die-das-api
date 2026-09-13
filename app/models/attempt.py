from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, UniqueConstraint

from app.database import Base
from app.utils.generators import generate_id, utc_now


class Attempt(Base):
    """
    Représente l'état courant d'un utilisateur sur un mot donné :
    réussi (maîtrisé) ou raté (à revoir dans les prochains rushs).
    Une seule ligne par couple utilisateur/mot, mise à jour à chaque tentative.
    """

    __tablename__ = "attempts"
    __table_args__ = (UniqueConstraint("user_id", "word_id", name="uq_user_word"),)

    id = Column(String(32), primary_key=True, default=generate_id)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    word_id = Column(String(32), ForeignKey("words.id"), nullable=False, index=True)
    success = Column(Boolean, nullable=False)
    last_attempt_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)