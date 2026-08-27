import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class ProcessRecord(Base):
    __tablename__ = "processes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    area: Mapped[str] = mapped_column(String(40))
    plaintiff: Mapped[str] = mapped_column(String(200))
    defendant: Mapped[str] = mapped_column(String(200))
    facts: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="created", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    events = relationship("ProcessEventDB", back_populates="process", cascade="all, delete-orphan")
    participants = relationship("ProcessParticipantDB", back_populates="process", cascade="all, delete-orphan")
