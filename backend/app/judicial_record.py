from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

@dataclass(frozen=True)
class JudicialRecord:
    id: str
    process_id: str
    phase: str
    classification: str
    intervention: str
    reasoning: str
    created_at: datetime

def make_record(process_id:str, phase:str, classification:str, intervention:str, reasoning:str)->JudicialRecord:
    return JudicialRecord(str(uuid4()),process_id,phase,classification,intervention,reasoning,datetime.now(timezone.utc))
