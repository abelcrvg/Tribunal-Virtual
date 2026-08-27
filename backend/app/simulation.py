from .agent_registry import agent_for
from .ai_provider import AIProvider, get_provider
from .case_memory import get_case_memory
from .models import Process


def _clean_ai_text(text: str) -> str:
    text = text.replace("\\####", "####").replace("\\###", "###").replace("\\##", "##").replace("\\#", "#")
    replacements = {
        "[Cidade/UF]": "Comarca indicada nos autos",
        "[Cidade - UF]": "Comarca indicada nos autos",
        "[CIDADE/UF]": "Comarca indicada nos autos",
        "[Data]": "data registrada nos autos",
        "[Nome do Perito]": "perito judicial a ser nomeado",
        "[Nome do Advogado]": "advogado identificado nos autos",
        "[Número]": "número registrado nos autos",
        "OAB/[UF] nº [Número]": "OAB fictícia registrada nos autos",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # These are internal classifier/control markers and must never reach the UI.
    for marker in ("irrelevant", "pertinent", "decisive", "abusive", "CONCEDER_PALAVRA", "REGISTRAR"):
        text = text.replace(marker, "")
    return text.strip()


def _agent_identity(process: Process, agent: str) -> str:
    seed = sum(ord(c) for c in process.number + agent)
    names = ["Lucas Almeida", "Renata Carvalho", "Bruno Monteiro", "Isabela Freitas", "Daniel Nogueira", "Paula Ribeiro", "Marcelo Teixeira", "Larissa Castro"]
    oab = 10000 + (seed % 89999)
    state = ["RJ", "SP", "MG", "PR", "RS"][seed % 5]
    if agent == "plaintiff_attorney": return f"Dr(a). {names[seed % len(names)]} — OAB/{state} {oab}"
    if agent == "defense_attorney": return f"Dr(a). {names[(seed + 3) % len(names)]} — OAB/{state} {oab}"
    if agent == "prosecutor": return f"Promotor(a) de Justiça {names[(seed + 5) % len(names)]}"
    if agent == "expert": return f"Perito(a) Judicial {names[(seed + 1) % len(names)]}"
    if agent == "judge": return f"Juiz(a) de Direito {names[(seed + 2) % len(names)]}"
    return "Participante jurídico"


def run_agent(process: Process, agent: str, name: str, role: str, system: str, instructions: str, provider: AIProvider | None = None):
    active_provider = provider or get_provider()
    memory = get_case_memory(str(process.id)).context()
    recent = memory.get("events", [])[-20:]
    identity = _agent_identity(process, agent)
    safety = (
        "Esta é uma simulação educacional de audiência. Todos os nomes, números de OAB, datas, locais e fatos não presentes nos autos devem ser fictícios. "
        "NUNCA use placeholders entre colchetes como [Cidade/UF], [Data], [Nome do Perito], [Nome do Advogado], OAB/[UF] ou [Número]. Use a identidade fictícia fornecida. "
        "NUNCA escreva marcadores técnicos como CONCEDER_PALAVRA, REGISTRAR, irrelevant, pertinent, decisive ou abusive. "
        "Respeite estritamente a fase e o papel informados na instrução. Se a instrução pedir fala oral, responda como fala de audiência, em primeira pessoa e sem criar petição, ata, termo, relatório ou decisão completa. "
        "Só produza uma peça ou sentença quando a instrução explicitamente pedir uma peça ou a fase for julgamento. Não crie uma nova fase por conta própria. "
        "Não antecipe fatos, provas, testemunhas ou decisões que não estejam nos autos. Quando uma manifestação escrita for explicitamente solicitada, use Markdown ou HTML válido, sem barras invertidas antes de títulos."
    )
    prompt = f"Processo: {process.number}\nÁrea: {process.area.value}\nAutor: {process.plaintiff}\nRéu: {process.defendant}\nIdentidade fictícia do agente: {identity}\n\nFATOS:\n{process.facts}\n\nHISTÓRICO RECENTE:\n{recent}\n\nINSTRUÇÃO PROCESSUAL ATUAL:\n{instructions}\n\nREGRAS OBRIGATÓRIAS:\n{safety}"
    response = active_provider.generate(system=system, prompt=prompt)
    return {"agent": agent, "name": identity if agent != "legal_researcher" else name, "role": role, "content": _clean_ai_text(response.text), "provider": response.provider, "model": response.model}


def run_registered_agent(process: Process, role: str, instructions: str, provider: AIProvider | None = None):
    definition = agent_for(role)
    if definition is None: raise ValueError(f"Agente não registrado: {role}")
    return run_agent(process, role, definition.display_name, role, definition.system_prompt, instructions, provider)


def run_plaintiff_agent(process, provider=None): return run_registered_agent(process, "plaintiff_attorney", "Apresente síntese dos fatos, questões jurídicas, teses, pedidos e provas relevantes.", provider)
def run_defense_agent(process, plaintiff_content, provider=None): return run_registered_agent(process, "defense_attorney", f"Analise a manifestação do autor:\n{plaintiff_content}\n\nApresente pontos controvertidos, argumentos defensivos, questões processuais e provas necessárias.", provider)
def run_research_agent(process, plaintiff_content, defense_content, provider=None): return run_agent(process, "legal_researcher", "Pesquisador Jurídico", "researcher", "Identifique fontes jurídicas a consultar. Não invente dispositivos, precedentes ou processos.", f"Compare AUTOR:\n{plaintiff_content}\n\nRÉU:\n{defense_content}\n\nIndique fontes brasileiras que precisam ser verificadas.", provider)
def run_judge_agent(process, plaintiff_content, defense_content, research_content, provider=None): return run_registered_agent(process, "judge", f"Analise AUTOR:\n{plaintiff_content}\n\nRÉU:\n{defense_content}\n\nPESQUISA:\n{research_content}\n\nProduza análise judicial preliminar, controvérsias, provas e fundamentos pendentes.", provider)
def run_full_simulation(process, provider=None):
    plaintiff=run_plaintiff_agent(process,provider); defense=run_defense_agent(process,plaintiff["content"],provider); research=run_research_agent(process,plaintiff["content"],defense["content"],provider); judge=run_judge_agent(process,plaintiff["content"],defense["content"],research["content"],provider)
    return {"process":process.number,"agents":[plaintiff,defense,research,judge]}
