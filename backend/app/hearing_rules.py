from dataclasses import dataclass
from enum import Enum

class InterventionDisposition(str, Enum):
    REPRIMAND="reprimand"
    ADMIT="admit"
    REGISTER="register"

@dataclass(frozen=True)
class InterventionDecision:
    disposition: InterventionDisposition
    reason: str
    requires_ruling: bool

def decide_intervention(allowed: bool, assessment: str) -> InterventionDecision:
    if allowed:
        return InterventionDecision(InterventionDisposition.ADMIT,"A parte possui a palavra nesta etapa.",False)
    if assessment in {"pertinent","decisive"}:
        return InterventionDecision(InterventionDisposition.REGISTER,"A intervenção fora da vez apresenta pertinência material para a controvérsia.",True)
    return InterventionDecision(InterventionDisposition.REPRIMAND,"A intervenção não apresenta pertinência suficiente para interromper a ordem dos trabalhos.",True)
