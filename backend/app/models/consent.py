from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.sql import func

from app.db.database import Base


class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(
        Integer,
        ForeignKey("sessions.id"),
        nullable=False
    )

    capture_consent = Column(
        Boolean,
        nullable=False,
        default=False
    )

    sharing_consent = Column(
        Boolean,
        nullable=False,
        default=False
    )

    language = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )