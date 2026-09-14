from typing import Literal

from sqlalchemy.orm import Session as DBSession

from app.models import User, Word, WordProgress
from app.schemas.word import WordWithProgress, WordListOut

Status = Literal["all", "mastered", "in_progress", "not_started"]


def list_words(
    db: DBSession,
    user: User,
    level: str | None,
    status: Status,
    page: int,
    page_size: int,
) -> WordListOut:
    """
    Liste les mots disponibles pour la révision libre, avec la progression
    de l'utilisateur sur chacun. Filtrable par niveau et par statut
    (maîtrisé, en cours, jamais rencontré), avec pagination.
    """

    query = db.query(Word, WordProgress).outerjoin(
        WordProgress,
        (WordProgress.word_id == Word.id) & (WordProgress.user_id == user.id),
    )

    if level:
        query = query.filter(Word.level == level)

    if status == "mastered":
        query = query.filter(WordProgress.mastered_at.isnot(None))
    elif status == "in_progress":
        query = query.filter(
            WordProgress.mastered_at.is_(None), WordProgress.total_attempts > 0
        )
    elif status == "not_started":
        query = query.filter(
            (WordProgress.id.is_(None)) | (WordProgress.total_attempts == 0)
        )

    total = query.count()

    rows = (
        query.order_by(Word.word).offset((page - 1) * page_size).limit(page_size).all()
    )

    words = [
        WordWithProgress(
            id=word.id,
            word=word.word,
            article=word.article,
            level=word.level,
            fr_translation=word.fr_translation,
            en_translation=word.en_translation,
            correct_streak=progress.correct_streak if progress else 0,
            mastered_at=progress.mastered_at if progress else None,
            total_attempts=progress.total_attempts if progress else 0,
        )
        for word, progress in rows
    ]

    return WordListOut(total=total, page=page, page_size=page_size, words=words)
