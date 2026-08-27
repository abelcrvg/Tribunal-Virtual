from uuid import UUID

from .models import Process, ProcessCreate

_processes: dict[UUID, Process] = {}
_counter = 0


def create_process(data: ProcessCreate) -> Process:
    global _counter
    _counter += 1
    year = 2026
    number = f"{_counter:06d}-{year}.TV"
    process = Process(number=number, **data.model_dump())
    _processes[process.id] = process
    return process


def get_process(process_id: UUID) -> Process | None:
    return _processes.get(process_id)


def list_processes() -> list[Process]:
    return list(_processes.values())
