import random

from sqlalchemy.orm import Session as DBSession

from app.models import Rush, Word, Attempt, WordProgress, User
from app.schemas.attempt import AttemptResult
from app.schemas.rush import RushSummary
from app.config import settings
from app.utils.generators import utc_now


def start_rush(db: DBSession, user: User) -> Rush:
    """Crée un nouveau rush pour l'utilisateur, sur son niveau actuel."""

    rush = Rush(user_id=user.id, level=user.level)
    db.add(rush)
    db.commit()
    db.refresh(rush)
    return rush


def get_rush_words(db: DBSession, user: User, rush: Rush) -> list[Word]:
    """
    Sélectionne les mots du rush : uniquement des mots du niveau de
    l'utilisateur qui ne sont pas encore maîtrisés. Les mots ratés
    reviennent donc naturellement, puisqu'ils ne sont jamais marqués
    mastered_at tant qu'ils ne sont pas réussis 3 fois sur 3 rushs.
    """

    mastered_word_ids = db.query(WordProgress.word_id).filter(
        WordProgress.user_id == user.id, WordProgress.mastered_at.isnot(None)
    )

    available_words = (
        db.query(Word)
        .filter(Word.level == user.level)
        .filter(~Word.id.in_(mastered_word_ids))
        .all()
    )

    if not available_words:
        raise ValueError(
            "Aucun mot disponible pour ce niveau, il est peut-être déjà terminé."
        )

    sample_size = min(settings.rush_size, len(available_words))
    return random.sample(available_words, sample_size)


def submit_answer(
    db: DBSession, user: User, rush_id: str, word_id: str, proposed_article: str
) -> AttemptResult:
    """
    Enregistre une tentative dans le journal, puis met à jour l'état
    agrégé de progression sur le mot concerné.
    """

    rush = db.query(Rush).filter(Rush.id == rush_id, Rush.user_id == user.id).first()
    if not rush:
        raise ValueError("Rush introuvable.")

    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise ValueError("Mot introuvable.")

    is_correct = proposed_article == word.article

    attempt = Attempt(
        user_id=user.id, word_id=word.id, rush_id=rush.id, is_correct=is_correct
    )
    db.add(attempt)

    progress = (
        db.query(WordProgress)
        .filter(WordProgress.user_id == user.id, WordProgress.word_id == word.id)
        .first()
    )
    if not progress:
        progress = WordProgress(user_id=user.id, word_id=word.id)
        db.add(progress)
        db.flush()

    progress.total_attempts += 1

    if is_correct:
        progress.total_correct += 1
        # Un seul incrément de streak par rush, même si le mot est retenté plusieurs fois dedans
        if progress.last_counted_rush_id != rush.id:
            progress.correct_streak += 1
            progress.last_counted_rush_id = rush.id
        if progress.correct_streak >= settings.mastery_streak_threshold:
            progress.mastered_at = utc_now()
    else:
        progress.correct_streak = 0
        progress.mastered_at = None
        progress.last_counted_rush_id = None

    progress.last_attempt_at = utc_now()

    db.commit()

    return AttemptResult(
        word_id=word.id, correct_article=word.article, is_correct=is_correct
    )


def finish_rush(db: DBSession, user: User, rush_id: str) -> RushSummary:
    """Calcule et enregistre le résumé de fin de rush."""

    rush = db.query(Rush).filter(Rush.id == rush_id, Rush.user_id == user.id).first()
    if not rush:
        raise ValueError("Rush introuvable.")

    attempts = db.query(Attempt).filter(Attempt.rush_id == rush.id).all()
    total = len(attempts)
    correct = sum(1 for a in attempts if a.is_correct)

    missed_word_ids = [a.word_id for a in attempts if not a.is_correct]
    words_to_review = (
        db.query(Word).filter(Word.id.in_(missed_word_ids)).all()
        if missed_word_ids
        else []
    )

    rush.finished_at = utc_now()
    rush.score = correct
    db.commit()

    return RushSummary(
        rush_id=rush.id,
        score=correct,
        total_words=total,
        correct_words=correct,
        words_to_review=words_to_review,
    )
