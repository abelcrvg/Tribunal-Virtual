from sqlalchemy import select
from sqlalchemy.orm import Session

from .db_models import ProcessRecord
from .models import Process, ProcessCreate


def to_domain(record: ProcessRecord) -> Process:
    return Process(
        id=record.id,
        number=record.number,
        area=record.area,
        plaintiff=record.plaintiff,
        defendant=record.defendant,
        facts=record.facts,
        include_mp=record.include_mp,
        jury=record.jury,
        status=record.status,
        created_at=record.created_at,
    )


def create_process_db(db: Session, data: ProcessCreate, number: str) -> Process:
    record = ProcessRecord(number=number, **data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return to_domain(record)


def get_process_db(db: Session, process_id: str) -> Process | None:
    record = db.get(ProcessRecord, process_id)
    return to_domain(record) if record else None


def list_processes_db(db: Session) -> list[Process]:
    records = db.scalars(select(ProcessRecord).order_by(ProcessRecord.created_at.desc())).all()
    return [to_domain(record) for record in records]
