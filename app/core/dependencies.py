from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models import User, Session as UserSession
from app.utils.generators import utc_now


def get_current_user(request: Request, db: DBSession = Depends(get_db)) -> User:
    """
    Dépendance FastAPI qui identifie l'utilisateur courant à partir du
    cookie httpOnly de session. Lève une erreur 401 si le cookie est
    absent, invalide, ou si la session a expiré.
    """

    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Non authentifié.")

    session = db.query(UserSession).filter(UserSession.token == token).first()
    if not session:
        raise HTTPException(status_code=401, detail="Session invalide.")

    if session.expires_at < utc_now():
        db.delete(session)
        db.commit()
        raise HTTPException(status_code=401, detail="Session expirée.")

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable.")

    return user


def require_guest(request: Request, db: DBSession = Depends(get_db)) -> None:
    """
    Dépendance FastAPI qui bloque l'accès si l'utilisateur possède déjà
    une session valide. Utilisée sur les routes réservées aux utilisateurs
    déconnectés (register, login).
    """

    token = request.cookies.get("session_token")
    if not token:
        return  # pas de cookie, donc bien déconnecté

    session = db.query(UserSession).filter(UserSession.token == token).first()
    if session and session.expires_at >= utc_now():
        raise HTTPException(status_code=403, detail="Vous êtes déjà connecté.")
