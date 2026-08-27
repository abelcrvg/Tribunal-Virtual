from dataclasses import dataclass


@dataclass(frozen=True)
class AgentRole:
    key: str
    name: str
    description: str


AGENTS = (
    AgentRole("judge", "Magistrado", "Analisa o processo com neutralidade."),
    AgentRole("plaintiff_attorney", "Advogado do autor", "Formula a tese e os pedidos do autor."),
    AgentRole("defense_attorney", "Advogado do réu", "Apresenta a defesa e impugna os argumentos do autor."),
    AgentRole("legal_researcher", "Pesquisador jurídico", "Localiza legislação e fontes jurídicas verificáveis."),
)
