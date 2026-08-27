from .agent_registry import agent_for
from .ai_provider import AIProvider, get_provider
from .case_memory import get_case_memory
from .models import Process


def run_agent(process: Process, agent: str, name: str, role: str, system: str, instructions: str, provider: AIProvider | None = None):
    active_provider = provider or get_provider()
    memory = get_case_memory(str(process.id)).context()
    recent = memory.get("events", [])[-20:]
    prompt = f"Processo: {process.number}\nÁrea: {process.area.value}\nAutor: {process.plaintiff}\nRéu: {process.defendant}\n\nFATOS:\n{process.facts}\n\nHISTÓRICO RECENTE:\n{recent}\n\n{instructions}"
    response = active_provider.generate(system=system, prompt=prompt)
    return {"agent": agent, "name": name, "role": role, "content": response.text, "provider": response.provider, "model": response.model}


def run_registered_agent(process: Process, role: str, instructions: str, provider: AIProvider | None = None):
    definition = agent_for(role)
    if definition is None:
        raise ValueError(f"Agente não registrado: {role}")
    return run_agent(process, role, definition.display_name, role, definition.system_prompt, instructions, provider)


def run_plaintiff_agent(process, provider=None):
    return run_registered_agent(process, "plaintiff_attorney", "Apresente síntese dos fatos, questões jurídicas, teses, pedidos e provas relevantes.", provider)


def run_defense_agent(process, plaintiff_content, provider=None):
    return run_registered_agent(process, "defense_attorney", f"Analise a manifestação do autor:\n{plaintiff_content}\n\nApresente pontos controvertidos, argumentos defensivos, questões processuais e provas necessárias.", provider)


def run_research_agent(process, plaintiff_content, defense_content, provider=None):
    return run_agent(process, "legal_researcher", "Pesquisador Jurídico", "researcher", "Identifique fontes jurídicas a consultar. Não invente dispositivos, precedentes ou processos.", f"Compare AUTOR:\n{plaintiff_content}\n\nRÉU:\n{defense_content}\n\nIndique fontes brasileiras que precisam ser verificadas.", provider)


def run_judge_agent(process, plaintiff_content, defense_content, research_content, provider=None):
    return run_registered_agent(process, "judge", f"Analise AUTOR:\n{plaintiff_content}\n\nRÉU:\n{defense_content}\n\nPESQUISA:\n{research_content}\n\nProduza análise judicial preliminar, controvérsias, provas e fundamentos pendentes.", provider)


def run_full_simulation(process, provider=None):
    plaintiff=run_plaintiff_agent(process,provider); defense=run_defense_agent(process,plaintiff["content"],provider); research=run_research_agent(process,plaintiff["content"],defense["content"],provider); judge=run_judge_agent(process,plaintiff["content"],defense["content"],research["content"],provider)
    return {"process":process.number,"agents":[plaintiff,defense,research,judge]}
