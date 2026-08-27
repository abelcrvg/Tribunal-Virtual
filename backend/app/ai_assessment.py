from dataclasses import dataclass
from .intervention_ai import assess_with_context
@dataclass(frozen=True)
class Assessment:
    label:str
    source:str

def assess(content:str,facts:str,history:list[str],phase:str)->Assessment:
    return Assessment(assess_with_context(content,facts,history,phase),"ai_contextual")
