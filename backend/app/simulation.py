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
    for marker in ("irrelevant", "pertinent", "decisive", "abusive", "CONCEDER_PALAVRA", "REGISTRAR"):
        text = text.replace(marker, "")
    return text.strip()


def _agent_identity(process: Process, agent: str) -> str:
    seed = sum(ord(c) for c in process.number + agent)
    names = ["Lucas Almeida", "Renata Carvalho", "Bruno Monteiro", "Isabela Freitas", "Daniel Nogueira", "Paula Ribeiro", "Marcelo Teixeira", "Larissa Castro", "Camila Vasconcelos", "Rafael Mendes"]
    oab = 10000 + (seed % 89999)
    state = ["RJ", "SP", "MG", "PR", "RS"][seed % 5]
    if agent == "plaintiff_attorney": return f"Dr(a). {names[seed % len(names)]} — OAB/{state} {oab}"
    if agent == "defense_attorney": return f"Dr(a). {names[(seed + 3) % len(names)]} — OAB/{state} {oab}"
    if agent == "prosecutor": return f"Promotor(a) de Justiça {names[(seed + 5) % len(names)]}"
    if agent == "expert": return f"Perito(a) Judicial {names[(seed + 1) % len(names)]}"
    if agent == "judge": return f"Juiz(a) de Direito {names[(seed + 2) % len(names)]}"
    if agent == "clerk": return f"Servidor(a) da Secretaria {names[(seed + 4) % len(names)]}"
    if agent == "witness": return f"Testemunha {names[(seed + 6) % len(names)]}"
    return "Participante jurídico"


def _format_transcript(session) -> str:
    lines = []
    for message in session.messages[-80:]:
        role = message.role.value if message.role else message.kind.value
        lines.append(f"{message.sender} [{role}]: {message.content}")
    return "\n".join(lines)


def run_agent(process: Process, agent: str, name: str, role: str, system: str, instructions: str, provider: AIProvider | None = None, session=None):
    active_provider = provider or get_provider()
    memory = get_case_memory(str(process.id)).context()
    recent_memory = memory.get("events", [])[-20:]
    identity = _agent_identity(process, agent)
    transcript = _format_transcript(session) if session is not None else ""
    safety = (
        "Esta é uma simulação educacional de audiência. Todos os nomes, números de OAB, datas, locais e fatos não presentes nos autos devem ser fictícios. "
        "NUNCA use placeholders entre colchetes como [Cidade/UF], [Data], [Nome do Perito], [Nome do Advogado], OAB/[UF] ou [Número]. Use a identidade fictícia fornecida. "
        "NUNCA escreva marcadores técnicos como CONCEDER_PALAVRA, REGISTRAR, irrelevant, pertinent, decisive ou abusive. "
        "Respeite estritamente a fase, o papel e o histórico informados. Você é a personagem, não o narrador do sistema. Responda ao que acabou de ser dito, desenvolvendo argumentos, perguntas, respostas ou decisões concretas. "
        "Não repita a abertura da audiência, não diga genericamente que registrou a manifestação e não anuncie que concedeu a palavra quando a personagem deveria efetivamente falar. "
        "Se a instrução pedir fala oral, escreva uma fala oral natural, específica e contextualizada. Só produza uma peça, termo, ata ou sentença quando isso for explicitamente solicitado ou quando a fase for julgamento. "
        "Use o histórico completo da audiência para manter continuidade, nomes, fatos, teses e perguntas coerentes. Não contradiga o que já foi dito sem explicar a mudança. "
        "Não antecipe fatos, provas, testemunhas ou decisões que não estejam nos autos ou no histórico."
    )
    prompt = (
        f"PROCESSO: {process.number}\nÁREA: {process.area.value}\nAUTOR: {process.plaintiff}\nRÉU: {process.defendant}\n"
        f"IDENTIDADE FICTÍCIA DO AGENTE: {identity}\n\nAUTOS E FATOS:\n{process.facts}\n\n"
        f"MEMÓRIA E EVENTOS RELEVANTES:\n{recent_memory}\n\nTRANSCRIÇÃO DA AUDIÊNCIA:\n{transcript}\n\n"
        f"INSTRUÇÃO DO ATO ATUAL:\n{instructions}\n\nREGRAS OBRIGATÓRIAS:\n{safety}"
    )
    response = active_provider.generate(system=system, prompt=prompt)
    return {"agent": agent, "name": identity if agent != "legal_researcher" else name, "role": role, "content": _clean_ai_text(response.text), "provider": response.provider, "model": response.model}


def run_registered_agent(process: Process, role: str, instructions: str, provider: AIProvider | None = None, session=None):
    definition = agent_for(role)
    if definition is None:
        raise ValueError(f"Agente não registrado: {role}")
    return run_agent(process, role, definition.display_name, role, definition.system_prompt, instructions, provider, session=session)


def run_plaintiff_agent(process, provider=None): return run_registered_agent(process, "plaintiff_attorney", "Apresente síntese dos fatos, questões jurídicas, teses, pedidos e provas relevantes.", provider)
def run_defense_agent(process, plaintiff_content, provider=None): return run_registered_agent(process, "defense_attorney", f"Analise a manifestação do autor:\n{plaintiff_content}\n\nApresente pontos controvertidos, argumentos defensivos, questões processuais e provas necessárias.", provider)
def run_research_agent(process, plaintiff_content, defense_content, provider=None): return run_agent(process, "legal_researcher", "Pesquisador Jurídico", "researcher", "Identifique fontes jurídicas a consultar. Não invente dispositivos, precedentes ou processos.", f"Compare AUTOR:\n{plaintiff_content}\n\nRÉU:\n{defense_content}\n\nIndique fontes brasileiras que precisam ser verificadas.", provider)
def run_judge_agent(process, plaintiff_content, defense_content, research_content, provider=None): return run_registered_agent(process, "judge", f"Analise AUTOR:\n{plaintiff_content}\n\nRÉU:\n{defense_content}\n\nPESQUISA:\n{research_content}\n\nProduza análise judicial preliminar, controvérsias, provas e fundamentos pendentes.", provider)
def run_full_simulation(process, provider=None):
    plaintiff=run_plaintiff_agent(process,provider); defense=run_defense_agent(process,plaintiff["content"],provider); research=run_research_agent(process,plaintiff["content"],defense["content"],provider); judge=run_judge_agent(process,plaintiff["content"],defense["content"],research["content"],provider)
    return {"process":process.number,"agents":[plaintiff,defense,research,judge]}
