from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from .case_store import store
from .participants import Participant, ParticipantRole, generate_participants


@dataclass
class CourtSession:
    id: str
    process_id: str
    user_role: str
    current_phase: str = "abertura"
    current_turn: str = "magistrate"
    opened: bool = True
    messages: list[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_message(self, sender: str, role: str, content: str, kind: str = "ai") -> dict:
        message = {"id": str(uuid4()), "sender": sender, "role": role, "content": content, "kind": kind, "created_at": datetime.now(timezone.utc).isoformat()}
        self.messages.append(message)
        store.add(self.process_id, "hearing_message", sender, content, "normal")
        return message


_sessions: dict[str, CourtSession] = {}


def open_session(process_id: str, user_role: str, seed: int, include_mp: bool, criminal: bool) -> CourtSession:
    session = CourtSession(str(uuid4()), process_id, user_role)
    participants = generate_participants(seed=seed, include_mp=include_mp, jury=criminal, witnesses=3, experts=1)
    judge = next(p for p in participants if p.role == ParticipantRole.MAGISTRATE)
    session.add_message(judge.name, judge.role.value, "Declaro aberta a sessão de julgamento do Tribunal Virtual. As partes e demais participantes deverão observar a ordem de fala e a urbanidade.")
    session.add_message(judge.name, judge.role.value, "A audiência seguirá as fases processuais previstas para esta simulação. Questões relevantes apresentadas fora da vez poderão ser apreciadas pelo juízo.")
    _sessions[session.id] = session
    return session


def get_session(session_id: str) -> CourtSession | None:
    return _sessions.get(session_id)


def user_message(session: CourtSession, content: str, sender: str) -> dict:
    from .courtroom import assess_intervention
    decision = assess_intervention(role=session.user_role, turn_role=session.current_turn, content=content)
    if decision.allowed:
        session.current_turn = "magistrate"
        return session.add_message(sender, session.user_role, content, "user") | {"assessment": decision.assessment.value, "judge_response": decision.judge_response}
    judge_name = "Juízo"
    return session.add_message(judge_name, ParticipantRole.MAGISTRATE.value, decision.judge_response) | {"assessment": decision.assessment.value, "judge_response": decision.judge_response}
