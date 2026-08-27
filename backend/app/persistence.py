from datetime import datetime
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db_models import ProcessRecord
from .models import Process, ProcessCreate, ProcessStatus

def to_domain(record: ProcessRecord) -> Process:
    return Process(
        id=record.id or str(uuid4()), number=record.number, area=record.area,
        plaintiff=record.plaintiff, defendant=record.defendant, facts=record.facts,
        include_mp=record.include_mp if record.include_mp is not None else False,
        jury=record.jury if record.jury is not None else False,
        status=record.status or ProcessStatus.CREATED,
        created_at=record.created_at or datetime.utcnow(),
    )

def create_process_db(db: Session, data: ProcessCreate, number: str) -> Process:
    record=ProcessRecord(number=number,**data.model_dump()); db.add(record); db.commit(); db.refresh(record); return to_domain(record)

def get_process_db(db: Session, process_id: str) -> Process | None:
    record=db.get(ProcessRecord,process_id); return to_domain(record) if record else None

def list_processes_db(db: Session) -> list[Process]:
    records=db.scalars(select(ProcessRecord).order_by(ProcessRecord.created_at.desc())).all(); return [to_domain(r) for r in records]
