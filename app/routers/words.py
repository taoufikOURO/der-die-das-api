from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.word import WordListOut
from app.services import word_service

router = APIRouter(prefix="/words", tags=["words"])


@router.get("", response_model=WordListOut)
def list_words(
    level: str | None = Query(default=None),
    status: Literal["all", "mastered", "in_progress", "not_started"] = Query(
        default="all"
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    return word_service.list_words(db, current_user, level, status, page, page_size)
