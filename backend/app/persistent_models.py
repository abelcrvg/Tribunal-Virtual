from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class ProcessEventDB(Base):
    __tablename__ = "process_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    process_id: Mapped[str] = mapped_column(String(36), ForeignKey("processes.id", ondelete="CASCADE"), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    actor: Mapped[str] = mapped_column(String(120))
    content: Mapped[str] = mapped_column(Text)
    relevance: Mapped[str] = mapped_column(String(20), default="normal", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    process = relationship("ProcessDB", back_populates="events")


class ProcessParticipantDB(Base):
    __tablename__ = "process_participants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    process_id: Mapped[str] = mapped_column(String(36), ForeignKey("processes.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    title: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(60), index=True)
    active: Mapped[bool] = mapped_column(default=True)
    fictional: Mapped[bool] = mapped_column(default=True)

    process = relationship("ProcessDB", back_populates="participants")
