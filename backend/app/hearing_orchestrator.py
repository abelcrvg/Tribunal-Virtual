from dataclasses import dataclass
from .agent_registry import agent_for
from .court_session import CourtPhase, CourtSession
from .simulation import run_registered_agent

@dataclass(frozen=True)
class Turn:
    role: str
    instruction: str

PHASE_TURNS = {
    CourtPhase.OPENING: [Turn("judge", "Abra formalmente a audiência, identifique o rito e explique objetivamente a controvérsia central. Não redija sentença nem saneamento completo.") , Turn("clerk", "Registre a abertura e faça os registros formais necessários, sem decidir questões de mérito.")],
    CourtPhase.PLAINTIFF: [Turn("plaintiff_attorney", "Atue como advogado do autor e apresente a manifestação inicial adequada à fase. Use o nome fictício do advogado e não invente fatos."), Turn("judge", "Ouça a parte autora, formule eventual questão processual necessária e dê encaminhamento à manifestação da defesa.")],
    CourtPhase.DEFENSE: [Turn("defense_attorney", "Atue como advogado do réu e apresente a defesa adequada à controvérsia, enfrentando os argumentos efetivamente registrados."), Turn("plaintiff_attorney", "Faça réplica ou manifestação de resposta aos pontos novos da defesa, sem antecipar a sentença."), Turn("judge", "Delimite questões processuais e pontos controvertidos que realmente dependam de instrução.")],
    CourtPhase.WITNESS_PLAINTIFF: [Turn("judge", "Chame a testemunha indicada pelo autor, faça a qualificação e as perguntas iniciais pertinentes."), Turn("witness", "Preste depoimento como testemunha do autor, limitando-se ao que a personagem poderia saber pessoalmente."), Turn("defense_attorney", "Faça perguntas à testemunha do autor, buscando esclarecer ou contraditar pontos relevantes."), Turn("judge", "Registre o depoimento e resolva eventuais questões surgidas durante a inquirição.")],
    CourtPhase.WITNESS_DEFENSE: [Turn("judge", "Chame a testemunha indicada pela defesa e faça a qualificação e perguntas iniciais."), Turn("witness", "Preste depoimento como testemunha da defesa, respeitando estritamente os fatos que poderia conhecer."), Turn("plaintiff_attorney", "Faça perguntas à testemunha da defesa, explorando contradições e pontos controvertidos."), Turn("judge", "Registre o depoimento e encerre a instrução testemunhal desta etapa.")],
    CourtPhase.EXPERT: [Turn("judge", "Apresente o objeto da perícia e os quesitos relevantes, sem substituir o perito na conclusão técnica."), Turn("expert", "Apresente o laudo ou esclarecimentos técnicos, distinguindo fatos observados, método e conclusões técnicas."), Turn("plaintiff_attorney", "Formule quesitos ou pedidos de esclarecimento pertinentes ao laudo."), Turn("defense_attorney", "Formule quesitos ou pedidos de esclarecimento pertinentes ao laudo."), Turn("judge", "Registre os esclarecimentos e determine o prosseguimento processual adequado.")],
    CourtPhase.MP: [Turn("prosecutor", "Manifeste-se institucionalmente sobre os pontos relevantes, somente se sua intervenção for cabível no caso."), Turn("judge", "Registre a manifestação do Ministério Público e determine o próximo ato processual.")],
    CourtPhase.CLOSING: [Turn("plaintiff_attorney", "Apresente alegações finais da parte autora, enfrentando fatos, provas e teses relevantes."), Turn("defense_attorney", "Apresente alegações finais da defesa, enfrentando fatos, provas e teses relevantes."), Turn("judge", "Declare encerrados os debates e prepare o processo para deliberação ou sentença, conforme o rito.")],
    CourtPhase.DELIBERATION: [Turn("juror", "Delibere sobre os fatos e provas, indicando de forma fundamentada os pontos que considera provados ou não provados."), Turn("judge", "Registre a deliberação e encaminhe o feito para a decisão cabível.")],
    CourtPhase.JUDGMENT: [Turn("judge", "Produza a sentença ou decisão final fundamentada, enfrentando os pedidos, argumentos, provas e questões processuais efetivamente registradas.")],
}

def next_agent_turn(session: CourtSession):
    turns = PHASE_TURNS.get(session.phase, [])
    return turns[session.turn_index] if session.turn_index < len(turns) else None

def run_next_agent(process, session, provider=None):
    turn = next_agent_turn(session)
    if turn is None or agent_for(turn.role) is None:
        return None
    result = run_registered_agent(process, turn.role, turn.instruction, provider)
    session.accept_turn()
    return result
