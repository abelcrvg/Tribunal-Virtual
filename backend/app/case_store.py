from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class StoredEvent:
    id: str
    process_id: str
    event_type: str
    actor: str
    content: str
    relevance: str
    created_at: datetime


@dataclass
class CaseStore:
    events: dict[str, list[StoredEvent]] = field(default_factory=dict)

    def add(self, process_id: str, event_type: str, actor: str, content: str, relevance: str = "normal") -> StoredEvent:
        event = StoredEvent(str(uuid4()), process_id, event_type, actor, content, relevance, datetime.now(timezone.utc))
        self.events.setdefault(process_id, []).append(event)
        return event

    def list(self, process_id: str) -> list[StoredEvent]:
        return self.events.get(process_id, [])

    def snapshot(self, process_id: str) -> dict:
        events = self.list(process_id)
        return {
            "event_count": len(events),
            "events": [e.__dict__ for e in events[-50:]],
            "high_relevance": [e.__dict__ for e in events if e.relevance in {"pertinent", "decisive"}],
        }


store = CaseStore()
