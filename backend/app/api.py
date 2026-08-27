from uuid import UUID

from fastapi import APIRouter, HTTPException

from .models import Process, ProcessCreate
from .processes import create_process, get_process, list_processes

router = APIRouter(prefix="/api/v1/processes", tags=["processes"])


@router.post("", response_model=Process, status_code=201)
def create_new_process(data: ProcessCreate) -> Process:
    return create_process(data)


@router.get("", response_model=list[Process])
def get_processes() -> list[Process]:
    return list_processes()


@router.get("/{process_id}", response_model=Process)
def get_process_by_id(process_id: UUID) -> Process:
    process = get_process(process_id)
    if process is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return process
