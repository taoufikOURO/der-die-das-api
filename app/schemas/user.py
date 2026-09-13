from datetime import datetime
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, field_validator

Level = Literal["A1", "A2", "B1", "B2", "C1", "C2"]


class UserCreate(BaseModel):
    """Données reçues à l'inscription."""

    pseudo: str = Field(min_length=3, max_length=30)
    email: EmailStr 
    password: str = Field(min_length=8, max_length=72)
    password_confirmation: str = Field(min_length=8, max_length=72)
    level: Level 

    @field_validator("password")
    @classmethod
    def password_length(cls, value: str):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Le mot de passe ne doit pas dépasser 72 octets.")
        if len(value) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères.")
        return value

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
    level: Level
    email_validated_at: datetime | None

    class Config:
        from_attributes = True


class OTPValidate(BaseModel):
    """Données reçues pour valider l'OTP envoyé par email."""

    email: EmailStr
    otp_code: str
