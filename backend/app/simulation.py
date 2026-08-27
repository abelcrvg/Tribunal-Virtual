from .ai_provider import AIProvider, get_provider
from .models import Process


def run_agent(process: Process, agent: str, name: str, role: str, system: str, instructions: str, provider: AIProvider | None = None):
    active_provider = provider or get_provider()
    prompt = f"Processo: {process.number}\nÁrea: {process.area.value}\nAutor: {process.plaintiff}\nRéu: {process.defendant}\n\nFATOS:\n{process.facts}\n\n{instructions}"
    response = active_provider.generate(system=system, prompt=prompt)
    return {"agent": agent, "name": name, "role": role, "content": response.text, "provider": response.provider, "model": response.model}


PLAINTIFF_SYSTEM = """Você é o Advogado do Autor em um tribunal virtual educacional brasileiro.
Não invente fatos, provas, artigos de lei ou jurisprudência. Diferencie fatos alegados de fatos comprovados.
Fontes jurídicas não fornecidas devem ser marcadas como pendentes de verificação."""


def run_plaintiff_agent(process: Process, provider: AIProvider | None = None):
    return run_agent(process, "plaintiff_attorney", "Advogado do Autor", "IA de argumentação", PLAINTIFF_SYSTEM, "Produza: 1) síntese dos fatos; 2) questões jurídicas; 3) possíveis teses; 4) pedidos a discutir; 5) provas relevantes.", provider)


DEFENSE_SYSTEM = """Você é o Advogado do Réu em um tribunal virtual educacional brasileiro.
Atue de forma adversarial e técnica, sem inventar fatos, provas, leis ou jurisprudência.
Identifique lacunas e diferencie alegações de fatos comprovados."""


def run_defense_agent(process: Process, plaintiff_content: str, provider: AIProvider | None = None):
    return run_agent(process, "defense_attorney", "Advogado do Réu", "IA de defesa", DEFENSE_SYSTEM, f"Analise esta manifestação do autor:\n{plaintiff_content}\n\nApresente: pontos controvertidos, argumentos defensivos, fatos que exigem prova, questões processuais e conclusão provisória.", provider)


RESEARCH_SYSTEM = """Você é o Pesquisador Jurídico de uma simulação brasileira.
Identifique fontes jurídicas que precisam ser consultadas. Não invente artigos, súmulas, precedentes ou processos.
Se a base jurídica não estiver disponível, marque a fonte como pendente de consulta."""


def run_research_agent(process: Process, plaintiff_content: str, defense_content: str, provider: AIProvider | None = None):
    return run_agent(process, "legal_researcher", "Pesquisador Jurídico", "Legislação e precedentes", RESEARCH_SYSTEM, f"Compare:\nAUTOR: {plaintiff_content}\n\nRÉU: {defense_content}\n\nListe questões jurídicas e os tipos de fontes brasileiras que devem ser consultados. Não cite dispositivo específico sem segurança.", provider)


JUDGE_SYSTEM = """Você é o Magistrado de uma simulação jurídica educacional brasileira.
Mantenha neutralidade. Não invente fatos, provas, leis ou jurisprudência. Não trate alegações como fatos comprovados.
A decisão é simulada e não possui validade jurídica."""


def run_judge_agent(process: Process, plaintiff_content: str, defense_content: str, research_content: str, provider: AIProvider | None = None):
    return run_agent(process, "judge", "Magistrado", "IA judicial · neutra", JUDGE_SYSTEM, f"Analise:\nAUTOR: {plaintiff_content}\n\nRÉU: {defense_content}\n\nPESQUISA: {research_content}\n\nProduza análise judicial preliminar com fatos alegados, controvérsias, provas relevantes, questões jurídicas pendentes e conclusão provisória. Não profira sentença definitiva sem fontes e provas verificadas.", provider)


def run_full_simulation(process: Process, provider: AIProvider | None = None):
    plaintiff = run_plaintiff_agent(process, provider)
    defense = run_defense_agent(process, plaintiff["content"], provider)
    research = run_research_agent(process, plaintiff["content"], defense["content"], provider)
    judge = run_judge_agent(process, plaintiff["content"], defense["content"], research["content"], provider)
    return {"process": process.number, "agents": [plaintiff, defense, research, judge]}
