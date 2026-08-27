from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .court_session import CourtSession, MessageKind
from .courtroom import Instance, UserRole, build_courtroom
from .processes import get_process

router = APIRouter(prefix="/api/v1/processes/{process_id}/courtroom", tags=["courtroom"])
_sessions: dict[str, CourtSession] = {}


class SessionCreate(BaseModel):
    role: UserRole


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class AppealCreate(BaseModel):
    type: str = Field(min_length=2, max_length=100)
    reason: str = Field(min_length=10, max_length=5000)


@router.post("/session")
def create_session(process_id: UUID, data: SessionCreate):
    process = get_process(process_id)
    if process is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    key = f"{process_id}:{data.role.value}"
    session = CourtSession(id=key, process_id=str(process_id), user_role=data.role)
    session.add_message("Sistema", MessageKind.SYSTEM, "Sessão iniciada. Você escolheu o papel: " + data.role.value)
    _sessions[key] = session
    return {
        "session_id": key,
        "role": data.role,
        "instance": session.instance,
        "phase": session.phase,
        "allowed_roles": list(session.allowed_roles),
        "messages": session.messages,
    }


@router.get("/participants")
def get_participants(process_id: UUID, instance: Instance = Instance.FIRST):
    process = get_process(process_id)
    if process is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    jury = process.area.value == "criminal"
    return {"instance": instance, "participants": [p.__dict__ for p in build_courtroom(include_mp=process.include_mp, jury=jury, instance=instance)]}


@router.get("/session/{role}")
def get_session(process_id: UUID, role: UserRole):
    session = _sessions.get(f"{process_id}:{role.value}")
    if session is None:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    return {
        "session_id": session.id,
        "role": session.user_role,
        "instance": session.instance,
        "phase": session.phase,
        "allowed_roles": list(session.allowed_roles),
        "messages": session.messages,
        "appeals": session.appeals,
    }


@router.post("/session/{role}/messages")
def send_message(process_id: UUID, role: UserRole, data: MessageCreate):
    key = f"{process_id}:{role.value}"
    session = _sessions.get(key)
    if session is None:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    if not session.user_can_speak():
        reprimand = session.reprimand()
        return {
            "accepted": False,
            "message": reprimand,
            "reason": "out_of_turn",
            "allowed_roles": list(session.allowed_roles),
        }
    message = session.add_message(role.value, MessageKind.USER, data.content)
    return {"accepted": True, "message": message, "phase": session.phase, "allowed_roles": list(session.allowed_roles)}


@router.post("/session/{role}/appeals")
def file_appeal(process_id: UUID, role: UserRole, data: AppealCreate):
    key = f"{process_id}:{role.value}"
    session = _sessions.get(key)
    if session is None:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    try:
        appeal = session.file_appeal(data.type, data.reason)
    except (PermissionError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "accepted": True,
        "appeal": appeal,
        "message": "Recurso protocolado para análise de admissibilidade.",
    }
