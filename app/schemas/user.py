from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    """Données reçues à l'inscription."""

    pseudo: str
    email: EmailStr
    password: str
    password_confirmation: str
    level: str  # A1, A2, B1, B2, C1, C2

    @field_validator("password_confirmation")
    @classmethod
    def passwords_match(cls, value, info):
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Les mots de passe ne correspondent pas.")
        return value


class UserLogin(BaseModel):
    """Données reçues à la connexion (pseudo ou email + mot de passe)."""

    identifier: str  # pseudo ou email
    password: str


class UserOut(BaseModel):
    """Données renvoyées par l'API, jamais le mot de passe ou l'OTP."""

    id: str
    pseudo: str
    email: EmailStr
    level: str
    email_validated_at: datetime | None

    class Config:
        from_attributes = True


class OTPValidate(BaseModel):
    """Données reçues pour valider l'OTP envoyé par email."""

    email: EmailStr
    otp_code: str
