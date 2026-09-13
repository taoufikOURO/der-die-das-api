from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserOut, OTPValidate
from app.services import auth_service
from app.config import settings
from app.core.dependencies import get_current_user, require_guest
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, dependencies=[Depends(require_guest)])
def register(user_data: UserCreate, db: DBSession = Depends(get_db)):
    try:
        user = auth_service.register_user(db, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return user


@router.post("/verify-otp", response_model=UserOut)
def verify_otp(otp_data: OTPValidate, db: DBSession = Depends(get_db)):
    try:
        user = auth_service.verify_otp(db, otp_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return user


@router.post("/resend-otp")
def resend_otp(email: str, db: DBSession = Depends(get_db)):
    try:
        auth_service.resend_otp(db, email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Un nouveau code a été envoyé."}


@router.post("/login", dependencies=[Depends(require_guest)])
def login(login_data: UserLogin, response: Response, db: DBSession = Depends(get_db)):
    try:
        session = auth_service.login_user(db, login_data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    response.set_cookie(
        key="session_token",
        value=session.token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        expires=session.expires_at,
    )

    return {"message": "Connexion réussie."}


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    token = request.cookies.get("session_token")
    auth_service.logout_user(db, token)
    response.delete_cookie("session_token")
    return {"message": "Déconnexion réussie."}
