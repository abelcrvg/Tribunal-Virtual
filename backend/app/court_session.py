from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from .courtroom import Instance, UserRole


class MessageKind(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    RULING = "ruling"


class CourtPhase(str, Enum):
    OPENING = "opening"
    PLAINTIFF = "plaintiff"
    DEFENSE = "defense"
    WITNESS_PLAINTIFF = "witness_plaintiff"
    WITNESS_DEFENSE = "witness_defense"
    EXPERT = "expert"
    MP = "mp"
    CLOSING = "closing"
    DELIBERATION = "deliberation"
    JUDGMENT = "judgment"
    CLOSED = "closed"


class AppealStatus(str, Enum):
    FILED = "filed"
    ADMISSIBILITY = "admissibility"
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
    status: AppealStatus = AppealStatus.ADMISSIBILITY
    review_body: str = ""


APPEAL_ROLES = {
    UserRole.PLAINTIFF_ATTORNEY,
    UserRole.DEFENSE_ATTORNEY,
    UserRole.PROSECUTOR,
}


PHASE_ALLOWED_ROLES: dict[CourtPhase, set[UserRole]] = {
    CourtPhase.OPENING: {UserRole.JUDGE},
    CourtPhase.PLAINTIFF: {UserRole.PLAINTIFF_ATTORNEY},
    CourtPhase.DEFENSE: {UserRole.DEFENSE_ATTORNEY},
    CourtPhase.WITNESS_PLAINTIFF: {UserRole.PLAINTIFF_ATTORNEY, UserRole.DEFENSE_ATTORNEY},
    CourtPhase.WITNESS_DEFENSE: {UserRole.PLAINTIFF_ATTORNEY, UserRole.DEFENSE_ATTORNEY},
    CourtPhase.EXPERT: {UserRole.PLAINTIFF_ATTORNEY, UserRole.DEFENSE_ATTORNEY, UserRole.JUDGE},
    CourtPhase.MP: {UserRole.PROSECUTOR},
    CourtPhase.CLOSING: {UserRole.PLAINTIFF_ATTORNEY, UserRole.DEFENSE_ATTORNEY, UserRole.PROSECUTOR},
    CourtPhase.DELIBERATION: {UserRole.JUDGE, UserRole.JUROR},
    CourtPhase.JUDGMENT: {UserRole.JUDGE},
    CourtPhase.CLOSED: set(),
}


@dataclass
class CourtSession:
    id: str
    process_id: str
    user_role: UserRole
    instance: Instance = Instance.FIRST
    phase: CourtPhase = CourtPhase.OPENING
    messages: list[ChatMessage] = field(default_factory=list)
    appeals: list[Appeal] = field(default_factory=list)

    @property
    def allowed_roles(self) -> set[UserRole]:
        return PHASE_ALLOWED_ROLES[self.phase]

    def add_message(self, sender: str, kind: MessageKind, content: str) -> ChatMessage:
        message = ChatMessage(str(uuid4()), sender, kind, content)
        self.messages.append(message)
        return message

    def user_can_speak(self) -> bool:
        return self.user_role in self.allowed_roles

    def reprimand(self) -> ChatMessage:
        return self.add_message(
            "Magistrado",
            MessageKind.RULING,
            "Peço ordem. Sua intervenção não está autorizada nesta fase da audiência. A palavra será concedida no momento processual adequado.",
        )

    def file_appeal(self, appeal_type: str, reason: str) -> Appeal:
        if self.user_role not in APPEAL_ROLES:
            raise PermissionError("Este papel não possui legitimidade recursal nesta simulação.")
        if self.phase not in {CourtPhase.JUDGMENT, CourtPhase.CLOSED}:
            raise ValueError("O recurso só pode ser apresentado após uma decisão recorrível.")
        if self.instance == Instance.STF:
            raise ValueError("Não há instância recursal superior modelada após o STF.")

        target = {
            Instance.FIRST: Instance.SECOND,
            Instance.SECOND: Instance.STJ,
            Instance.STJ: Instance.STF,
        }[self.instance]
        appeal = Appeal(
            id=str(uuid4()),
            process_id=self.process_id,
            appellant_role=self.user_role,
            type=appeal_type,
            reason=reason,
            from_instance=self.instance,
            target_instance=target,
        )
        self.appeals.append(appeal)
        return appeal
