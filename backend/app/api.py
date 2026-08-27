from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .courtroom import assess_intervention
from .database import get_db
from .models import Process, ProcessCreate
from .persistence import create_process_db, get_process_db, list_processes_db
from .simulation import run_defense_agent, run_full_simulation, run_judge_agent, run_plaintiff_agent, run_research_agent

router = APIRouter(prefix="/api/v1/processes", tags=["processes"])


class InterventionRequest(BaseModel):
    role: str = Field(min_length=2, max_length=80)
    turn_role: str = Field(min_length=2, max_length=80)
    content: str = Field(min_length=1, max_length=10000)


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


@router.post("/{process_id}/courtroom/intervention", tags=["courtroom"])
def courtroom_intervention(process_id: UUID, data: InterventionRequest, db: Session = Depends(get_db)):
    _get_process(process_id, db)
    decision = assess_intervention(role=data.role, turn_role=data.turn_role, content=data.content)
    return {
        "assessment": decision.assessment.value,
        "allowed": decision.allowed,
        "judge_response": decision.judge_response,
        "requires_record": decision.requires_record,
        "reason": decision.reason,
    }


@router.post("/{process_id}/agents/plaintiff", tags=["simulation"])
def plaintiff(process_id: UUID, db: Session = Depends(get_db)):
    try:
        return run_plaintiff_agent(_get_process(process_id, db))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{process_id}/agents/defense", tags=["simulation"])
def defense(process_id: UUID, db: Session = Depends(get_db)):
    try:
        process = _get_process(process_id, db)
        plaintiff_result = run_plaintiff_agent(process)
        return run_defense_agent(process, plaintiff_result["content"])
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{process_id}/agents/research", tags=["simulation"])
def research(process_id: UUID, db: Session = Depends(get_db)):
    try:
        process = _get_process(process_id, db)
        plaintiff_result = run_plaintiff_agent(process)
        defense_result = run_defense_agent(process, plaintiff_result["content"])
        return run_research_agent(process, plaintiff_result["content"], defense_result["content"])
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{process_id}/agents/judge", tags=["simulation"])
def judge(process_id: UUID, db: Session = Depends(get_db)):
    try:
        process = _get_process(process_id, db)
        plaintiff_result = run_plaintiff_agent(process)
        defense_result = run_defense_agent(process, plaintiff_result["content"])
        research_result = run_research_agent(process, plaintiff_result["content"], defense_result["content"])
        return run_judge_agent(process, plaintiff_result["content"], defense_result["content"], research_result["content"])
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{process_id}/simulation", tags=["simulation"])
def full_simulation(process_id: UUID, db: Session = Depends(get_db)):
    try:
        return run_full_simulation(_get_process(process_id, db))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
