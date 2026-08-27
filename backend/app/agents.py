from dataclasses import dataclass
from typing import Protocol

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
    status: str = "simulated"


class AIProvider(Protocol):
    def generate(self, *, system: str, prompt: str) -> str: ...


class TemplateProvider:
    """Fallback local provider used until a real AI provider is configured."""

    def generate(self, *, system: str, prompt: str) -> str:
        return (
            "ANÁLISE PRELIMINAR\n\n"
            "Esta manifestação é uma etapa técnica de demonstração do motor do Tribunal Virtual. "
            "O caso recebido deve ser analisado à luz dos fatos apresentados, da legislação aplicável "
            "e das provas que forem posteriormente juntadas ao processo.\n\n"
            "Nenhuma conclusão jurídica definitiva foi produzida enquanto o provedor de IA e a base "
            "jurídica verificável não estiverem configurados."
        )


class PlaintiffAttorneyAgent:
    name = "Advogado do Autor"
    role = "IA de argumentação"

    def __init__(self, provider: AIProvider | None = None):
        self.provider = provider or TemplateProvider()

    def run(self, process: Process) -> AgentResult:
        system = (
            "Você atua como advogado da parte autora em uma simulação educacional. "
            "Não invente fatos, provas, leis ou jurisprudência. Diferencie fatos de argumentos."
        )
        prompt = (
            f"Área: {process.area.value}\n"
            f"Autor: {process.plaintiff}\n"
            f"Réu: {process.defendant}\n"
            f"Fatos: {process.facts}\n\n"
            "Produza uma análise preliminar indicando fatos relevantes, possíveis pedidos "
            "e pontos que precisam de comprovação."
        )
        return AgentResult(self.name, self.role, self.provider.generate(system=system, prompt=prompt))
