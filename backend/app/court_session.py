from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from .courtroom import Instance, UserRole


class MessageKind(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class AppealStatus(str, Enum):
    DRAFT = "draft"
    FILED = "filed"
    ADMITTED = "admitted"
    DENIED = "denied"
    JUDGED = "judged"


@dataclass
class ChatMessage:
    id: str
    sender: str
    kind: MessageKind
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Appeal:
    id: str
    process_id: str
    appellant_role: UserRole
    type: str
    reason: str
    from_instance: Instance
    target_instance: Instance
    status: AppealStatus = AppealStatus.DRAFT


@dataclass
class CourtSession:
    id: str
    process_id: str
    user_role: UserRole
    instance: Instance = Instance.FIRST
    messages: list[ChatMessage] = field(default_factory=list)
    appeals: list[Appeal] = field(default_factory=list)

    def add_message(self, sender: str, kind: MessageKind, content: str) -> ChatMessage:
        message = ChatMessage(str(uuid4()), sender, kind, content)
        self.messages.append(message)
        return message

    def file_appeal(self, appeal_type: str, reason: str) -> Appeal:
        target = Instance.SECOND
        if self.instance == Instance.SECOND:
            target = Instance.STJ
        elif self.instance == Instance.STJ:
            target = Instance.STF
        appeal = Appeal(
            id=str(uuid4()),
            process_id=self.process_id,
            appellant_role=self.user_role,
            type=appeal_type,
            reason=reason,
            from_instance=self.instance,
            target_instance=target,
            status=AppealStatus.FILED,
        )
        self.appeals.append(appeal)
        return appeal
