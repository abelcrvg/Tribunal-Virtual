from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from .case_store import store
from .models import ProcessStatus

@dataclass(frozen=True)
class TimelineEntry:
    id: str
    process_id: str
    status: ProcessStatus
    title: str
    description: str
    created_at: datetime

def record_status(process_id: str, status: ProcessStatus, title: str, description: str) -> TimelineEntry:
    entry=TimelineEntry(str(uuid4()),process_id,status,title,description,datetime.now(timezone.utc))
    store.add(process_id,"process_status", "Sistema", f"{title}: {description}", "pertinent")
    return entry
