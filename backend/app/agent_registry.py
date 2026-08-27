from dataclasses import dataclass
from .courtroom import UserRole

@dataclass(frozen=True)
class AgentDefinition:
    role: UserRole
    display_name: str
    system_prompt: str
    phase_names: tuple[str, ...]

AGENTS = (
    AgentDefinition(UserRole.PLAINTIFF_ATTORNEY, "Advogado do Autor", "Atue pela parte autora. Separe alegações de fatos comprovados e enfrente os pontos relevantes da defesa.", ("plaintiff", "witness_plaintiff", "closing")),
    AgentDefinition(UserRole.DEFENSE_ATTORNEY, "Advogado do Réu", "Atue pela defesa. Identifique lacunas, contradições e argumentos juridicamente relevantes sem inventar fatos.", ("defense", "witness_defense", "closing")),
    AgentDefinition(UserRole.PROSECUTOR, "Promotor de Justiça", "Atue institucionalmente quando cabível, com imparcialidade e respeito ao contraditório.", ("mp", "closing")),
    AgentDefinition(UserRole.JUDGE, "Magistrado", "Conduza a audiência com neutralidade, fundamentação e controle da ordem processual.", ("opening", "witness_plaintiff", "witness_defense", "expert", "mp", "judgment")),
    AgentDefinition(UserRole.EXPERT, "Perito Judicial", "Explique exclusivamente questões técnicas submetidas à perícia e diferencie conclusão técnica de opinião jurídica.", ("expert",)),
    AgentDefinition(UserRole.JUROR, "Conselho de Sentença", "Analise os fatos e provas apresentados na simulação, sem assumir fatos não demonstrados.", ("deliberation",)),
)

def agent_for(role: UserRole) -> AgentDefinition | None:
    return next((agent for agent in AGENTS if agent.role == role), None)
