from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

@dataclass
class DecisionRecord:
    id:str
    process_id:str
    judge:str
    phase:str
    findings:list[str]=field(default_factory=list)
    grounds:list[str]=field(default_factory=list)
    ruling:str=""
    created_at:datetime=field(default_factory=lambda:datetime.now(timezone.utc))
    final:bool=False

def create_decision(process_id:str, judge:str, phase:str, findings:list[str], grounds:list[str], ruling:str, final:bool=False)->DecisionRecord:
    return DecisionRecord(str(uuid4()),process_id,judge,phase,findings,grounds,ruling,datetime.now(timezone.utc),final)
