from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .agent_orchestrator import build_agent_instruction, register_agent_reply
from .case_store import store
from .case_memory import get_case_memory
from .court_session import CourtPhase, CourtSession, MessageKind
from .courtroom import Instance, UserRole, build_courtroom
from .processes import get_process

router = APIRouter(prefix="/api/v1/processes/{process_id}/courtroom", tags=["courtroom"])
_sessions: dict[str, CourtSession] = {}


class SessionCreate(BaseModel):
    role: UserRole


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class AgentCreate(BaseModel):
    role: UserRole
    sender: str = Field(min_length=2, max_length=120)
    content: str = Field(min_length=1, max_length=10000)


class AppealCreate(BaseModel):
    type: str = Field(min_length=2, max_length=100)
    reason: str = Field(min_length=10, max_length=5000)


def _session(process_id: UUID, role: UserRole) -> CourtSession:
    session = _sessions.get(f"{process_id}:{role.value}")
    if session is None:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    return session


@router.post("/session")
def create_session(process_id: UUID, data: SessionCreate):
    process = get_process(process_id)
    if process is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    key = f"{process_id}:{data.role.value}"
    session = CourtSession(id=key, process_id=str(process_id), user_role=data.role)
    judge = next((p for p in build_courtroom(include_mp=process.include_mp, jury=process.area.value == "criminal", instance=Instance.FIRST) if p.role == UserRole.JUDGE), None)
    judge_name = judge.name if judge else "Magistrado"
    session.add_message(judge_name, MessageKind.RULING, "Declaro aberta a sessão. As partes, testemunhas, peritos e demais participantes deverão observar a ordem de fala e a urbanidade.")
    session.add_message("Sistema", MessageKind.SYSTEM, "O debate é livre. Uma intervenção fora da vez que apresente pertinência relevante poderá ser submetida à apreciação do juízo.")
    _sessions[key] = session
    store.add(str(process_id), "session_opened", judge_name, "Sessão de julgamento aberta", "pertinent")
    return {"session_id": key, "role": data.role, "instance": session.instance, "phase": session.phase, "allowed_roles": list(session.allowed_roles), "messages": session.messages}


@router.get("/participants")
def get_participants(process_id: UUID, instance: Instance = Instance.FIRST):
    process = get_process(process_id)
    if process is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return {"instance": instance, "participants": [p.__dict__ for p in build_courtroom(include_mp=process.include_mp, jury=process.area.value == "criminal", instance=instance)]}


@router.get("/session/{role}")
def get_session(process_id: UUID, role: UserRole):
    session = _session(process_id, role)
    return {"session_id": session.id, "role": session.user_role, "instance": session.instance, "phase": session.phase, "allowed_roles": list(session.allowed_roles), "messages": session.messages, "appeals": session.appeals}


@router.post("/session/{role}/messages")
def send_message(process_id: UUID, role: UserRole, data: MessageCreate):
    session = _session(process_id, role)
    from .courtroom import assess_intervention
    turn_role = next(iter(session.allowed_roles)).value if session.allowed_roles else "none"
    decision = assess_intervention(role=role.value, turn_role=turn_role, content=data.content)
    if role not in session.allowed_roles and decision.assessment.value not in {"pertinent", "decisive"}:
        reprimand = session.reprimand()
        store.add(str(process_id), "reprimand", "Magistrado", reprimand.content, "normal")
        return {"accepted": False, "message": reprimand, "reason": "out_of_turn", "allowed_roles": list(session.allowed_roles), "assessment": decision.assessment.value}
    message = session.add_message(role.value, MessageKind.USER, data.content)
    store.add(str(process_id), "hearing_message", role.value, data.content, decision.assessment.value)
    if role not in session.allowed_roles:
        ruling = session.add_message("Magistrado", MessageKind.RULING, "A intervenção apresenta pertinência com a controvérsia. A palavra é concedida para esclarecimento e a manifestação será considerada no histórico do processo.")
        return {"accepted": True, "message": message, "ruling": ruling, "exception": True, "assessment": decision.assessment.value, "phase": session.phase, "allowed_roles": list(session.allowed_roles)}
    return {"accepted": True, "message": message, "phase": session.phase, "allowed_roles": list(session.allowed_roles), "assessment": decision.assessment.value}


@router.post("/session/{role}/agents")
def agent_message(process_id: UUID, role: UserRole, data: AgentCreate):
    session = _session(process_id, role)
    if data.role not in session.allowed_roles:
        raise HTTPException(status_code=400, detail=f"O papel {data.role.value} não possui a palavra na fase {session.phase.value}.")
    context = get_case_memory(str(process_id)).context()
    instruction = build_agent_instruction(session, data.role, context)
    reply = register_agent_reply(session, data.role, data.sender, data.content)
    return {"message": reply.__dict__, "instruction_context": instruction, "phase": session.phase, "allowed_roles": list(session.allowed_roles)}


@router.post("/session/{role}/advance")
def advance_phase(process_id: UUID, role: UserRole):
    session = _session(process_id, role)
    order = list(CourtPhase)
    index = order.index(session.phase)
    if index >= len(order) - 1:
        raise HTTPException(status_code=400, detail="A audiência já foi encerrada.")
    session.phase = order[index + 1]
    content = f"Passamos à fase: {session.phase.value}."
    store.add(str(process_id), "phase_change", "Magistrado", content, "pertinent")
    message = session.add_message("Magistrado", MessageKind.RULING, content)
    return {"phase": session.phase, "allowed_roles": list(session.allowed_roles), "message": message}


@router.post("/session/{role}/appeals")
def file_appeal(process_id: UUID, role: UserRole, data: AppealCreate):
    session = _session(process_id, role)
    try:
        appeal = session.file_appeal(data.type, data.reason)
    except (PermissionError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    store.add(str(process_id), "appeal_filed", role.value, data.reason, "pertinent")
    return {"accepted": True, "appeal": appeal, "message": "Recurso protocolado para análise de admissibilidade pelo órgão competente."}
