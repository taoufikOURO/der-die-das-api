from datetime import timedelta

from sqlalchemy.orm import Session as DBSession

from app.models import User, Session as UserSession
from app.schemas.user import UserCreate, UserLogin, OTPValidate
from app.core.security import (
    hash_password,
    verify_password,
    generate_otp,
    generate_otp_expiry,
    generate_session_token,
    generate_session_expiry,
)
from app.utils.generators import utc_now
from app.utils.mailer import send_otp_email
from app.config import settings


def _check_resend_cooldown(user: User) -> None:
    """Lève une erreur si le délai minimum entre deux envois d'OTP n'est pas respecté."""

    if user.otp_last_sent_at is None:
        return

    cooldown = timedelta(seconds=settings.otp_resend_cooldown_seconds)
    if utc_now() - user.otp_last_sent_at < cooldown:
        raise ValueError("Veuillez attendre avant de demander un nouveau code.")


def register_user(db: DBSession, user_data: UserCreate) -> User:
    """
    Crée un nouvel utilisateur, génère un OTP et l'envoie par email
    pour validation de l'adresse. L'utilisateur ne peut pas se connecter
    tant que l'email n'est pas validé.
    """

    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise ValueError("Cette adresse email est déjà utilisée.")

    existing_pseudo = db.query(User).filter(User.pseudo == user_data.pseudo).first()
    if existing_pseudo:
        raise ValueError("Ce pseudo est déjà utilisé.")

    otp_code = generate_otp()

    user = User(
        pseudo=user_data.pseudo,
        email=user_data.email,
        password=hash_password(user_data.password),
        level=user_data.level,
        otp_code=otp_code,
        otp_expires_at=generate_otp_expiry(),
        otp_purpose="email_verification",
        otp_last_sent_at=utc_now(),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    send_otp_email(user.email, otp_code)

    return user


def verify_otp(db: DBSession, otp_data: OTPValidate) -> User:
    """
    Valide l'adresse email d'un utilisateur à partir du code OTP reçu.
    """

    user = db.query(User).filter(User.email == otp_data.email).first()
    if not user:
        raise ValueError("Utilisateur introuvable.")

    if user.email_validated_at is not None:
        raise ValueError("Cette adresse email est déjà validée.")

    if user.otp_purpose != "email_verification":
        raise ValueError("Code invalide pour cette action.")

    if user.otp_code != otp_data.otp_code:
        raise ValueError("Code de validation incorrect.")

    if user.otp_expires_at is None or user.otp_expires_at < utc_now():
        raise ValueError(
            "Le code de validation a expiré, veuillez en demander un nouveau."
        )

    user.email_validated_at = utc_now()
    user.otp_code = None
    user.otp_expires_at = None
    user.otp_purpose = None

    db.commit()
    db.refresh(user)

    return user


def resend_otp(db: DBSession, email: str) -> None:
    """
    Génère un nouveau code OTP de validation d'email et le renvoie,
    par exemple si le précédent a expiré. Soumis à un délai minimum
    entre deux envois.
    """

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("Utilisateur introuvable.")

    if user.email_validated_at is not None:
        raise ValueError("Cette adresse email est déjà validée.")

    _check_resend_cooldown(user)

    otp_code = generate_otp()
    user.otp_code = otp_code
    user.otp_expires_at = generate_otp_expiry()
    user.otp_purpose = "email_verification"
    user.otp_last_sent_at = utc_now()

    db.commit()

    send_otp_email(user.email, otp_code)


def login_user(db: DBSession, login_data: UserLogin) -> UserSession:
    """
    Vérifie les identifiants et crée une session httpOnly.
    Refuse la connexion si l'email n'a pas encore été validé.
    """

    user = (
        db.query(User)
        .filter(
            (User.pseudo == login_data.identifier)
            | (User.email == login_data.identifier)
        )
        .first()
    )

    if not user or not verify_password(login_data.password, user.password):
        raise ValueError("Identifiants incorrects.")

    if user.email_validated_at is None:
        raise ValueError(
            "Veuillez valider votre adresse email avant de vous connecter."
        )

    session = UserSession(
        user_id=user.id,
        token=generate_session_token(),
        expires_at=generate_session_expiry(),
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def logout_user(db: DBSession, token: str) -> None:
    """Supprime la session correspondant au token, invalidant le cookie httpOnly."""

    session = db.query(UserSession).filter(UserSession.token == token).first()
    if session:
        db.delete(session)
        db.commit()


def forgot_password(db: DBSession, email: str) -> None:
    """
    Génère un OTP pour réinitialiser le mot de passe et l'envoie par email.
    Ne révèle jamais si l'email existe ou non (évite l'énumération de comptes).
    Soumis au même délai minimum entre deux envois que resend_otp.
    """

    user = db.query(User).filter(User.email == email).first()
    if not user:
        return  # silencieux volontairement

    _check_resend_cooldown(user)

    otp_code = generate_otp()
    user.otp_code = otp_code
    user.otp_expires_at = generate_otp_expiry()
    user.otp_purpose = "password_reset"
    user.otp_last_sent_at = utc_now()

    db.commit()

    send_otp_email(user.email, otp_code)


def reset_password(db: DBSession, email: str, otp_code: str, new_password: str) -> None:
    """
    Réinitialise le mot de passe d'un utilisateur après vérification
    de l'OTP envoyé par forgot_password.
    """

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("Code invalide ou expiré.")

    if user.otp_purpose != "password_reset":
        raise ValueError("Code invalide pour cette action.")

    if user.otp_code != otp_code:
        raise ValueError("Code invalide ou expiré.")

    if user.otp_expires_at is None or user.otp_expires_at < utc_now():
        raise ValueError("Code invalide ou expiré.")

    user.password = hash_password(new_password)
    user.otp_code = None
    user.otp_expires_at = None
    user.otp_purpose = None

    db.commit()
