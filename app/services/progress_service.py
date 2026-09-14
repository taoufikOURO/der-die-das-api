import math

from sqlalchemy.orm import Session as DBSession

from app.models import User, Word, WordProgress, Rush
from app.schemas.word_progress import LevelProgress
from app.config import settings

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
WORDS_TO_REVIEW_LIMIT = 5


def get_level_progress(db: DBSession, user: User) -> LevelProgress:
    """
    Calcule un état complet et détaillé de la progression de l'utilisateur
    sur son niveau actuel (user.level), destiné à alimenter le dashboard.

    Champs calculés et retournés (LevelProgress) :

    - level : le niveau CECRL concerné (celui de l'utilisateur au moment
      de l'appel).
    - total_words : nombre total de mots existant pour ce niveau en base.
    - mastered_words : nombre de mots dont mastered_at est renseigné
      (réussis un nombre suffisant de fois, sur des rushs distincts).
    - in_progress_words : mots déjà tentés au moins une fois, mais pas
      encore maîtrisés (streak insuffisant, ou remis à zéro après un échec).
    - not_started_words : mots du niveau jamais rencontrés par
      l'utilisateur (aucune ligne WordProgress correspondante).
    - completion_ratio : proportion de mots maîtrisés par rapport au
      total du niveau (mastered_words / total_words).
    - level_completed : True si completion_ratio a atteint le seuil
      configuré (settings.level_completion_threshold), signifiant que le
      niveau peut être validé pour passer au suivant.
    - words_needed_to_complete : nombre de mots qu'il reste à maîtriser
      pour atteindre ce seuil, à partir de l'état actuel.
    - estimated_rushes_remaining : estimation du nombre de rushs restants
      pour atteindre words_needed_to_complete, en supposant un rush plein
      (settings.rush_size mots par rush).
    - accuracy : taux de réussite global sur ce niveau, calculé sur
      l'ensemble des tentatives enregistrées (total_correct / total_attempts),
      toutes tentatives confondues, pas seulement les mots maîtrisés.
    - total_rushes_played : nombre de rushs terminés (finished_at renseigné)
      effectués par l'utilisateur sur ce niveau.
    - last_rush_score : score du rush le plus récent terminé sur ce niveau,
      ou None si aucun rush n'a encore été terminé.
    - last_rush_at : date de fin du rush le plus récent, ou None.
    - best_rush_score : meilleur score obtenu parmi tous les rushs
      terminés sur ce niveau, ou None si aucun rush n'a été terminé.
    - words_to_review : liste des mots actuellement les plus fragiles
      (tentés au moins une fois, pas encore maîtrisés), triés par streak
      de réussite croissant, limitée aux WORDS_TO_REVIEW_LIMIT premiers.
    """
    total_words = db.query(Word).filter(Word.level == user.level).count()

    level_word_ids = db.query(Word.id).filter(Word.level == user.level)

    progresses = (
        db.query(WordProgress)
        .filter(
            WordProgress.user_id == user.id, WordProgress.word_id.in_(level_word_ids)
        )
        .all()
    )

    mastered_words = sum(1 for p in progresses if p.mastered_at is not None)
    in_progress_words = sum(
        1 for p in progresses if p.mastered_at is None and p.total_attempts > 0
    )
    not_started_words = total_words - mastered_words - in_progress_words

    completion_ratio = mastered_words / total_words if total_words > 0 else 0.0
    level_completed = completion_ratio >= settings.level_completion_threshold

    required_mastered = math.ceil(total_words * settings.level_completion_threshold)
    words_needed_to_complete = max(0, required_mastered - mastered_words)
    estimated_rushes_remaining = math.ceil(
        words_needed_to_complete / settings.rush_size
    )

    total_attempts = sum(p.total_attempts for p in progresses)
    total_correct = sum(p.total_correct for p in progresses)
    accuracy = total_correct / total_attempts if total_attempts > 0 else 0.0

    finished_rushes = (
        db.query(Rush)
        .filter(
            Rush.user_id == user.id,
            Rush.level == user.level,
            Rush.finished_at.isnot(None),
        )
        .order_by(Rush.finished_at.desc())
        .all()
    )

    total_rushes_played = len(finished_rushes)
    last_rush = finished_rushes[0] if finished_rushes else None
    best_rush_score = max((r.score for r in finished_rushes), default=None)

    # Mots actuellement à revoir : tentés au moins une fois, pas encore maîtrisés,
    # triés par streak croissant (les plus fragiles en premier)
    review_candidates = sorted(
        (p for p in progresses if p.mastered_at is None and p.total_attempts > 0),
        key=lambda p: p.correct_streak,
    )
    review_word_ids = [p.word_id for p in review_candidates[:WORDS_TO_REVIEW_LIMIT]]
    words_to_review = (
        db.query(Word).filter(Word.id.in_(review_word_ids)).all()
        if review_word_ids
        else []
    )

    return LevelProgress(
        level=user.level,
        total_words=total_words,
        mastered_words=mastered_words,
        in_progress_words=in_progress_words,
        not_started_words=not_started_words,
        completion_ratio=completion_ratio,
        level_completed=level_completed,
        words_needed_to_complete=words_needed_to_complete,
        estimated_rushes_remaining=estimated_rushes_remaining,
        accuracy=accuracy,
        total_rushes_played=total_rushes_played,
        last_rush_score=last_rush.score if last_rush else None,
        last_rush_at=last_rush.finished_at if last_rush else None,
        best_rush_score=best_rush_score,
        words_to_review=words_to_review,
    )


def get_next_level(current_level: str) -> str | None:
    """Retourne le niveau suivant, ou None si c'est déjà le dernier (C2)."""

    index = LEVELS.index(current_level)
    if index + 1 < len(LEVELS):
        return LEVELS[index + 1]
    return None


def advance_level(db: DBSession, user: User) -> User:
    """
    Fait passer l'utilisateur au niveau suivant, si le niveau actuel
    est bien terminé. Lève une erreur sinon.
    """

    progress = get_level_progress(db, user)
    if not progress.level_completed:
        raise ValueError("Le niveau actuel n'est pas encore terminé.")

    next_level = get_next_level(user.level)
    if next_level is None:
        raise ValueError("Vous avez déjà atteint le niveau maximum (C2).")

    user.level = next_level
    db.commit()
    db.refresh(user)

    return user
