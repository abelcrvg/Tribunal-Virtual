from dataclasses import dataclass
from .agent_registry import agent_for
from .case_memory import get_case_memory
from .court_session import CourtPhase, CourtSession
from .simulation import run_registered_agent

@dataclass(frozen=True)
class Turn:
    role: str
    instruction: str

PHASE_TURNS={
 CourtPhase.OPENING:[Turn("judge","Abra formalmente a audiência e explique a controvérsia central."),],
 CourtPhase.PLAINTIFF:[Turn("plaintiff_attorney","Faça a manifestação inicial do autor."),],
 CourtPhase.DEFENSE:[Turn("defense_attorney","Apresente a contestação e enfrente os argumentos do autor."),],
 CourtPhase.MP:[Turn("prosecutor","Manifeste-se sobre os pontos relevantes, somente quando cabível."),],
 CourtPhase.CLOSING:[Turn("plaintiff_attorney","Faça alegações finais objetivas."),Turn("defense_attorney","Faça alegações finais da defesa."),],
 CourtPhase.JUDGMENT:[Turn("judge","Produza decisão fundamentada com base no histórico e nas provas registradas."),],
}

def next_agent_turn(session:CourtSession):
    turns=PHASE_TURNS.get(session.phase,[])
    idx=session.turn_index
    if idx>=len(turns): return None
    return turns[idx]

def run_next_agent(process,session,provider=None):
    turn=next_agent_turn(session)
    if turn is None: return None
    definition=agent_for(turn.role)
    if definition is None: return None
    context=get_case_memory(str(process.id)).context()
    result=run_registered_agent(process,turn.role,turn.instruction,provider)
    session.accept_turn()
    return result
