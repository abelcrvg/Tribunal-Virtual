from dataclasses import dataclass
from uuid import uuid4

from .case_store import store
from .court_session import CourtPhase, CourtSession, MessageKind
from .courtroom import UserRole


@dataclass(frozen=True)
class AgentReply:
    id: str
    role: UserRole
    sender: str
    content: str
    phase: CourtPhase


PHASE_PROMPTS = {
    CourtPhase.OPENING: "Faça a abertura formal da audiência e apresente a questão central do processo.",
    CourtPhase.PLAINTIFF: "Atue como advogado do autor. Apresente a tese, fatos e pedidos relevantes ao processo.",
    CourtPhase.DEFENSE: "Atue como advogado do réu. Responda à tese da parte autora e destaque fatos ou provas favoráveis à defesa.",
    CourtPhase.WITNESS_PLAINTIFF: "Atue como testemunha indicada pelo autor. Responda de forma coerente com os fatos dos autos, sem inventar conhecimento pessoal.",
    CourtPhase.WITNESS_DEFENSE: "Atue como testemunha indicada pela defesa. Responda às perguntas considerando apenas o que a personagem poderia saber.",
    CourtPhase.EXPERT: "Atue como perito judicial. Explique tecnicamente os pontos submetidos à perícia, distinguindo conclusão técnica de opinião jurídica.",
    CourtPhase.MP: "Atue como Ministério Público quando sua participação for cabível. Analise a questão sob a perspectiva institucional e processual.",
    CourtPhase.CLOSING: "Apresente alegações finais objetivas, enfrentando os argumentos e provas relevantes que constam da memória do processo.",
    CourtPhase.DELIBERATION: "Participe da deliberação considerando exclusivamente os fatos, provas e questões registradas na simulação.",
    CourtPhase.JUDGMENT: "Redija uma decisão fundamentada, enfrentando as questões relevantes registradas durante a audiência.",
}


def build_agent_instruction(session: CourtSession, role: UserRole, case_context: dict) -> str:
    memory = case_context.get("events", [])[-15:]
    facts = case_context.get("disputed_facts", [])[-10:]
    return (
        f"Você é o agente jurídico do papel {role.value} em uma simulação educacional de processo brasileiro. "
        f"A fase atual é {session.phase.value}. {PHASE_PROMPTS.get(session.phase, 'Atue de acordo com a fase processual.')} "
        "Não invente documentos, leis, fatos ou depoimentos que não estejam disponíveis. "
        "Diferencie alegação de fato comprovado. Se uma manifestação anterior relevante contrariar sua posição, enfrente-a. "
        f"Questões controvertidas registradas: {facts}. Eventos recentes: {memory}."
    )


def register_agent_reply(session: CourtSession, role: UserRole, sender: str, content: str) -> AgentReply:
    message = session.add_message(sender, MessageKind.AGENT, content)
    store.add(session.process_id, "agent_message", sender, content, "pertinent")
    return AgentReply(message.id, role, sender, content, session.phase)
