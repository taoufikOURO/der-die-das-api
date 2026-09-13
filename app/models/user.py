from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.generators import generate_id, utc_now


class User(Base):
    __tablename__ = "users"

    id = Column(String(32), primary_key=True, default=generate_id)
    pseudo = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    level = Column(String(10), nullable=False)

    email_validated_at = Column(DateTime(timezone=True), nullable=True)
    otp_code = Column(String(6), nullable=True)
    otp_expires_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    sessions = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )