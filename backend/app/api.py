from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .models import Process, ProcessCreate
from .persistence import create_process_db, get_process_db, list_processes_db
from .simulation import run_plaintiff_agent

router = APIRouter(prefix="/api/v1/processes", tags=["processes"])


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
    process = get_process_db(db, str(process_id))
    if process is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return process


@router.post("/{process_id}/agents/plaintiff", tags=["simulation"])
def run_plaintiff_agent_endpoint(process_id: UUID, db: Session = Depends(get_db)):
    process = get_process_db(db, str(process_id))
    if process is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    try:
        return run_plaintiff_agent(process)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
