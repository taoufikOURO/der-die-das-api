from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.generators import generate_id, utc_now


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(32), primary_key=True, default=generate_id)
    token = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    user = relationship("User", back_populates="sessions")