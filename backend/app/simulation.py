from .ai_provider import AIProvider, get_provider
from .models import Process


SYSTEM_PROMPT = """Você é o agente Advogado do Autor de um tribunal virtual educacional brasileiro.
Analise somente os fatos fornecidos. Não invente fatos, provas, artigos de lei ou jurisprudência.
Quando uma fonte jurídica ainda não estiver disponível no contexto, diga explicitamente que ela precisa ser verificada.
Separe fatos narrados, questões jurídicas, possíveis argumentos e pontos que dependem de prova.
Não apresente a simulação como aconselhamento jurídico real."""


def build_plaintiff_prompt(process: Process) -> str:
    return f"""Processo: {process.number}
Área: {process.area.value}
Autor: {process.plaintiff}
Réu: {process.defendant}

FATOS NARRADOS:
{process.facts}

Produza uma manifestação preliminar do advogado do autor com:
1. síntese objetiva dos fatos;
2. questões jurídicas que precisam ser examinadas;
3. possíveis teses do autor;
4. pedidos que poderiam ser discutidos na simulação;
5. provas ou documentos que seriam relevantes.
"""


def run_plaintiff_agent(process: Process, provider: AIProvider | None = None):
    active_provider = provider or get_provider()
    response = active_provider.generate(
        system=SYSTEM_PROMPT,
        prompt=build_plaintiff_prompt(process),
    )
    return {
        "agent": "plaintiff_attorney",
        "name": "Advogado do Autor",
        "role": "IA de argumentação",
        "content": response.text,
        "provider": response.provider,
        "model": response.model,
    }
