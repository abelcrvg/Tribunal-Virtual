from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .appeals import AppealType, analyze_appeal
from .case_memory import ProcessEvent, get_case_memory
from .case_store import store
from .chat import submit_message
from .courtroom import assess_intervention
from .database import get_db
from .models import Process, ProcessCreate
from .participants import generate_participants
from .persistence import create_process_db, get_process_db, list_processes_db
from .simulation import run_defense_agent, run_full_simulation, run_judge_agent, run_plaintiff_agent, run_research_agent

router = APIRouter(prefix="/api/v1/processes", tags=["processes"])


class InterventionRequest(BaseModel):
    role: str = Field(min_length=2, max_length=80)
    turn_role: str = Field(min_length=2, max_length=80)
    content: str = Field(min_length=1, max_length=10000)


class EventRequest(BaseModel):
    type: str = Field(min_length=2, max_length=80)
    actor: str = Field(min_length=2, max_length=120)
    content: str = Field(min_length=1, max_length=10000)
    relevance: str = Field(default="normal", max_length=20)


class ChatRequest(BaseModel):
    role: str = Field(min_length=2, max_length=80)
    turn_role: str = Field(min_length=2, max_length=80)
    actor: str = Field(min_length=2, max_length=120)
    content: str = Field(min_length=1, max_length=10000)


class AppealRequest(BaseModel):
    case_area: str = Field(min_length=2, max_length=40)
    decision_type: str = Field(min_length=2, max_length=80)
    appellant_role: str = Field(min_length=2, max_length=80)
    appeal_type: AppealType


def _get_process(process_id: UUID, db: Session) -> Process:
    process = get_process_db(db, str(process_id))
    if process is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return process


@router.post("", response_model=Process, status_code=201)
def create_new_process(data: ProcessCreate, db: Session = Depends(get_db)) -> Process:
    count = len(list_processes_db(db)) + 1
    number = f"{count:06d}-2026.TV"
    return create_process_db(db, data, number)


@router.get("", response_model=list[Process])
def get_processes(db: Session = Depends(get_db)) -> list[Process]:
    return list_processes_db(db)


@router.get("/{process_id}", response_model=Process)
def get_process_by_id(process_id: UUID, db: Session = Depends(get_db)) -> Process:
    return _get_process(process_id, db)


@router.get("/{process_id}/participants", tags=["courtroom"])
def participants(process_id: UUID, db: Session = Depends(get_db)):
    process = _get_process(process_id, db)
    jury = process.area.value == "criminal" and process.include_mp
    return [p.__dict__ for p in generate_participants(seed=sum(process.number.encode()), include_mp=process.include_mp, jury=jury, witnesses=3, experts=1)]


@router.get("/{process_id}/memory", tags=["courtroom"])
def process_memory(process_id: UUID, db: Session = Depends(get_db)):
    _get_process(process_id, db)
    return {"legacy": get_case_memory(str(process_id)).context(), "store": store.snapshot(str(process_id))}


@router.post("/{process_id}/memory/events", tags=["courtroom"])
def record_process_event(process_id: UUID, data: EventRequest, db: Session = Depends(get_db)):
    _get_process(process_id, db)
    get_case_memory(str(process_id)).record(ProcessEvent(type=data.type, actor=data.actor, content=data.content, relevance=data.relevance))
    event = store.add(str(process_id), data.type, data.actor, data.content, data.relevance)
    return {"id": event.id, "recorded": True, "relevance": event.relevance}


@router.post("/{process_id}/chat", tags=["courtroom"])
def courtroom_chat(process_id: UUID, data: ChatRequest, db: Session = Depends(get_db)):
    _get_process(process_id, db)
    message = submit_message(process_id=str(process_id), role=data.role, turn_role=data.turn_role, actor=data.actor, content=data.content)
    decision = assess_intervention(role=data.role, turn_role=data.turn_role, content=data.content)
    return {"id": message.id, "accepted": message.accepted, "assessment": message.assessment, "actor": message.actor, "content": message.content, "judge_response": decision.judge_response, "requires_record": decision.requires_record, "reason": decision.reason, "created_at": message.created_at}


@router.post("/{process_id}/courtroom/intervention", tags=["courtroom"])
def courtroom_intervention(process_id: UUID, data: InterventionRequest, db: Session = Depends(get_db)):
    _get_process(process_id, db)
    decision = assess_intervention(role=data.role, turn_role=data.turn_role, content=data.content)
    if decision.requires_record:
        get_case_memory(str(process_id)).record(ProcessEvent(type="intervention", actor=data.role, content=data.content, relevance=decision.assessment.value))
        store.add(str(process_id), "intervention", data.role, data.content, decision.assessment.value)
    return {"assessment": decision.assessment.value, "allowed": decision.allowed, "judge_response": decision.judge_response, "requires_record": decision.requires_record, "reason": decision.reason}


@router.post("/{process_id}/appeals/analyze", tags=["appeals"])
def analyze_process_appeal(process_id: UUID, data: AppealRequest, db: Session = Depends(get_db)):
    _get_process(process_id, db)
    result = analyze_appeal(case_area=data.case_area, decision_type=data.decision_type, appellant_role=data.appellant_role, appeal_type=data.appeal_type)
    if result.admissible:
        store.add(str(process_id), "appeal", data.appellant_role, f"{result.type.value}: {result.reason}", "pertinent")
    return result.__dict__


@router.post("/{process_id}/agents/plaintiff", tags=["simulation"])
def plaintiff(process_id: UUID, db: Session = Depends(get_db)):
    try: return run_plaintiff_agent(_get_process(process_id, db))
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{process_id}/agents/defense", tags=["simulation"])
def defense(process_id: UUID, db: Session = Depends(get_db)):
    try:
        process = _get_process(process_id, db); p = run_plaintiff_agent(process)
        return run_defense_agent(process, p["content"])
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{process_id}/agents/research", tags=["simulation"])
def research(process_id: UUID, db: Session = Depends(get_db)):
    try:
        process = _get_process(process_id, db); p = run_plaintiff_agent(process); d = run_defense_agent(process, p["content"])
        return run_research_agent(process, p["content"], d["content"])
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{process_id}/agents/judge", tags=["simulation"])
def judge(process_id: UUID, db: Session = Depends(get_db)):
    try:
        process = _get_process(process_id); p = run_plaintiff_agent(process); d = run_defense_agent(process, p["content"]); r = run_research_agent(process, p["content"], d["content"])
        return run_judge_agent(process, p["content"], d["content"], r["content"])
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{process_id}/simulation", tags=["simulation"])
def full_simulation(process_id: UUID, db: Session = Depends(get_db)):
    try: return run_full_simulation(_get_process(process_id, db))
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc
