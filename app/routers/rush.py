from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.rush import RushWords, RushSummary
from app.schemas.attempt import AttemptCreate, AttemptResult
from app.services import rush_service

router = APIRouter(prefix="/rush", tags=["rush"])


@router.post("/start", response_model=RushWords)
def start(
    current_user: User = Depends(get_current_user), db: DBSession = Depends(get_db)
):
    """Démarre un rush pour l'utilisateur actuel et retourne les mots à traiter."""
    try:
        rush = rush_service.start_rush(db, current_user)
        words = rush_service.get_rush_words(db, current_user, rush)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return RushWords(rush_id=rush.id, words=words)


@router.post("/answer", response_model=AttemptResult)
def answer(
    data: AttemptCreate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    """Soumet une réponse pour un mot dans le rush en cours."""
    try:
        result = rush_service.submit_answer(
            db, current_user, data.rush_id, data.word_id, data.proposed_article
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


@router.post("/{rush_id}/finish", response_model=RushSummary)
def finish(
    rush_id: str,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    """Termine le rush en cours et retourne un résumé des résultats."""
    try:
        summary = rush_service.finish_rush(db, current_user, rush_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return summary
