from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(
        Integer,
        ForeignKey("sessions.id"),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="draft"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )