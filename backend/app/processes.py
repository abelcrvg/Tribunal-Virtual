from uuid import UUID

from .characters import build_characters
from .models import Process, ProcessCreate, ProcessStatus

_processes: dict[UUID, Process] = {}
_counter = 0


def create_process(data: ProcessCreate) -> Process:
    global _counter
    _counter += 1
    process = Process(number=f"{_counter:06d}-2026.TV", characters=[c.__dict__ for c in build_characters(seed=_counter, include_mp=data.include_mp)], **data.model_dump())
    _processes[process.id] = process
    return process


def get_process(process_id: UUID) -> Process | None:
    return _processes.get(process_id)


def list_processes() -> list[Process]:
    return list(_processes.values())


def advance_process(process: Process, status: ProcessStatus) -> Process:
    process.status = status
    return process
