import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
class ProcessRecord(Base):
    __tablename__="processes"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    number:Mapped[str]=mapped_column(String(40),unique=True,index=True)
    area:Mapped[str]=mapped_column(String(40))
    plaintiff:Mapped[str]=mapped_column(String(200))
    defendant:Mapped[str]=mapped_column(String(200))
    facts:Mapped[str]=mapped_column(Text)
    include_mp:Mapped[bool]=mapped_column(Boolean,default=False)
    jury:Mapped[bool]=mapped_column(Boolean,default=False)
    status:Mapped[str]=mapped_column(String(40),default="created",index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    events:Mapped[list["ProcessEventDB"]]=relationship(back_populates="process",cascade="all, delete-orphan")
    participants:Mapped[list["ProcessParticipantDB"]]=relationship(back_populates="process",cascade="all, delete-orphan")
class ProcessEventDB(Base):
    __tablename__="process_events"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    process_id:Mapped[str]=mapped_column(ForeignKey("processes.id",ondelete="CASCADE"),index=True)
    event_type:Mapped[str]=mapped_column(String(60),index=True)
    actor:Mapped[str]=mapped_column(String(200))
    content:Mapped[str]=mapped_column(Text)
    assessment:Mapped[str]=mapped_column(String(40),default="normal")
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    process:Mapped[ProcessRecord]=relationship(back_populates="events")
class ProcessParticipantDB(Base):
    __tablename__="process_participants"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    process_id:Mapped[str]=mapped_column(ForeignKey("processes.id",ondelete="CASCADE"),index=True)
    name:Mapped[str]=mapped_column(String(200))
    title:Mapped[str]=mapped_column(String(120))
    role:Mapped[str]=mapped_column(String(60),index=True)
    profession:Mapped[str]=mapped_column(String(120))
    fictional:Mapped[bool]=mapped_column(Boolean,default=True)
    process:Mapped[ProcessRecord]=relationship(back_populates="participants")
