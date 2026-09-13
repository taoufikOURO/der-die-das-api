from sqlalchemy import Column, String

from app.database import Base
from app.utils.generators import generate_id


class Word(Base):
    """
    Représente un mot allemand avec son article grammatical,
    son niveau CECRL (quand connu) et ses traductions.
    """

    __tablename__ = "words"

    id = Column(String(32), primary_key=True, default=generate_id)
    word = Column(String, nullable=False, unique=True, index=True)
    article = Column(String(3), nullable=False)  # der, die, das
    level = Column(
        String(10), nullable=True, index=True
    )  # A1, A2, B1... ou None si inconnu
    fr_translation = Column(String, nullable=True)
    en_translation = Column(String, nullable=True)
