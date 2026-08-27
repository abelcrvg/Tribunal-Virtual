from dataclasses import dataclass

from .ai_providers import AIProvider, get_provider
from .models import Process


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


@dataclass(frozen=True)
class AgentResult:
    agent: str
    role: str
    content: str
    status: str = "generated"


class PlaintiffAttorneyAgent:
    name = "Advogado do Autor"
    role = "IA de argumentação"

    def __init__(self, provider: AIProvider | None = None):
        self.provider = provider or get_provider()

    def run(self, process: Process) -> AgentResult:
        system = (
            "Você atua como advogado da parte autora em uma simulação educacional de direito brasileiro. "
            "Não invente fatos, provas, leis, artigos ou jurisprudência. Separe fatos narrados, inferências "
            "e argumentos. Quando não houver fonte verificável disponível, diga explicitamente que a fonte "
            "precisa ser pesquisada. Não apresente a simulação como aconselhamento jurídico real."
        )
        prompt = (
            f"Área jurídica: {process.area.value}\n"
            f"Autor: {process.plaintiff}\n"
            f"Réu: {process.defendant}\n"
            f"Fatos narrados pelo usuário:\n{process.facts}\n\n"
            "Estruture a manifestação em: 1) síntese dos fatos; 2) questões jurídicas a investigar; "
            "3) possíveis teses do autor; 4) pedidos que poderiam ser considerados; 5) provas relevantes. "
            "Não cite números de artigos sem ter a fonte jurídica disponível no contexto."
        )
        return AgentResult(
            self.name,
            self.role,
            self.provider.generate(system=system, prompt=prompt),
        )
