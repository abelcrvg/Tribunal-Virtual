from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from .case_memory import ProcessEvent, get_case_memory
from .courtroom import assess_intervention


@dataclass(frozen=True)
class ChatMessage:
    id: str
    process_id: str
    actor: str
    role: str
    content: str
    accepted: bool
    assessment: str
    created_at: datetime


def submit_message(*, process_id: str, role: str, turn_role: str, actor: str, content: str) -> ChatMessage:
    decision = assess_intervention(role=role, turn_role=turn_role, content=content)
    now = datetime.now(timezone.utc)
    message = ChatMessage(
        id=str(uuid4()),
        process_id=process_id,
        actor=actor,
        role=role,
        content=content,
        accepted=decision.allowed,
        assessment=decision.assessment.value,
        created_at=now,
    )
    memory = get_case_memory(process_id)
    memory.record(ProcessEvent(type="chat_message" if decision.allowed else "procedural_intervention", actor=actor, content=content, relevance=decision.assessment.value))
    return message
