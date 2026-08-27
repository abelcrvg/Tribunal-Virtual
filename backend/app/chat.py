from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from .case_memory import ProcessEvent, get_case_memory
from .case_store import store
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
    message = ChatMessage(str(uuid4()), process_id, actor, role, content, decision.allowed, decision.assessment.value, now)

    event_type = "chat_message" if decision.allowed else "procedural_intervention"
    get_case_memory(process_id).record(ProcessEvent(type=event_type, actor=actor, content=content, relevance=decision.assessment.value))
    store.add(process_id, event_type, actor, content, decision.assessment.value)
    return message
