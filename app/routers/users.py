from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.user import UserOut
from app.schemas.word_progress import LevelProgress
from app.services import progress_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    """Retourne les informations de l'utilisateur actuellement connecté."""
    return current_user


@router.get("/me/dashboard", response_model=LevelProgress)
def dashboard(
    current_user: User = Depends(get_current_user), db: DBSession = Depends(get_db)
):
    """ "Retourne les informations de progression de l'utilisateur sur son niveau actuel."""
    return progress_service.get_level_progress(db, current_user)


@router.post("/me/advance-level", response_model=UserOut)
def advance_level(
    current_user: User = Depends(get_current_user), db: DBSession = Depends(get_db)
):
    """Fait passer l'utilisateur au niveau suivant si le niveau actuel est terminé."""
    try:
        user = progress_service.advance_level(db, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return user
