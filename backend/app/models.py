from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class CaseArea(str, Enum):
    CONSUMER = "consumer"
    CIVIL = "civil"
    LABOR = "labor"
    CRIMINAL = "criminal"


class ProcessStatus(str, Enum):
    CREATED = "created"
    INITIAL_PETITION = "initial_petition"
    ANSWER = "answer"
    REPLY = "reply"
    JUDICIAL_ANALYSIS = "judicial_analysis"
    SENTENCE = "sentence"
    CLOSED = "closed"


class ProcessCreate(BaseModel):
    area: CaseArea
    plaintiff: str = Field(min_length=2, max_length=200)
    defendant: str = Field(min_length=2, max_length=200)
    facts: str = Field(min_length=20, max_length=10000)
    include_mp: bool = False


class CharacterResponse(BaseModel):
    name: str
    title: str
    profession: str
    role: str
    fictional: bool = True


class Process(ProcessCreate):
    id: UUID = Field(default_factory=uuid4)
    number: str
    status: ProcessStatus = ProcessStatus.CREATED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    characters: list[CharacterResponse] = Field(default_factory=list)
