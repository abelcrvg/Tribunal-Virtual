from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class ProcessEvent:
    type: str
    actor: str
    content: str
    relevance: str = "normal"
    recorded: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CaseMemory:
    events: list[ProcessEvent] = field(default_factory=list)
    disputed_facts: list[str] = field(default_factory=list)
    relevant_evidence: list[str] = field(default_factory=list)

    def record(self, event: ProcessEvent) -> ProcessEvent:
        self.events.append(event)
        if event.relevance in {"pertinent", "decisive"}:
            self._extract_issue(event.content)
        return event

    def _extract_issue(self, content: str) -> None:
        if content and content not in self.disputed_facts:
            self.disputed_facts.append(content)

    def context(self, limit: int = 20) -> dict:
        return {
            "events": [
                {"type": e.type, "actor": e.actor, "content": e.content, "relevance": e.relevance, "created_at": e.created_at.isoformat()}
                for e in self.events[-limit:]
            ],
            "disputed_facts": self.disputed_facts,
            "relevant_evidence": self.relevant_evidence,
        }


_memory: dict[str, CaseMemory] = {}


def get_case_memory(process_id: str) -> CaseMemory:
    return _memory.setdefault(process_id, CaseMemory())
