from dataclasses import dataclass
from .agent_registry import agent_for
from .court_session import CourtPhase, CourtSession
from .simulation import run_registered_agent

@dataclass(frozen=True)
class Turn:
    role: str
    instruction: str

PHASE_TURNS = {
    CourtPhase.OPENING: [
        Turn("judge", "Conduza oralmente a abertura da audiência. Identifique expressamente o participante humano pelo nome e pelo papel que ele escolheu. Registre a presença, explique brevemente o ato e indique quem terá a palavra primeiro. Não redija termo, ata, decisão ou sentença."),
        Turn("clerk", "Faça apenas o registro oral/formal necessário da audiência, em manifestação curta. Não produza termo ou documento completo."),
    ],
    CourtPhase.PLAINTIFF: [
        Turn("plaintiff_attorney", "Atue oralmente como advogado do autor. Apresente a manifestação adequada à fase, de forma natural e como fala em audiência. Não redija petição completa."),
        Turn("judge", "Conduza oralmente a audiência após a manifestação do autor. Se necessário, faça pergunta processual pertinente e encaminhe o ato seguinte. Não redija decisão completa."),
    ],
    CourtPhase.DEFENSE: [
        Turn("defense_attorney", "Atue oralmente como advogado do réu. Apresente a defesa adequada à fase, enfrentando somente fatos, provas e argumentos efetivamente registrados nos autos. Não redija contestação ou petição completa."),
        Turn("plaintiff_attorney", "Atue oralmente como advogado do autor e responda aos pontos novos da defesa. Faça réplica oral ou manifestação de resposta, sem antecipar sentença."),
        Turn("judge", "Conduza oralmente o encerramento desta etapa. Delimite brevemente as questões que precisam de prova ou providência. Não produza decisão saneadora completa."),
    ],
    CourtPhase.WITNESS_PLAINTIFF: [
        Turn("judge", "Chame a testemunha indicada pelo autor, faça sua qualificação e formule perguntas iniciais pertinentes. Fale oralmente, sem produzir termo."),
        Turn("witness", "Preste depoimento oral como testemunha do autor, limitando-se ao que a personagem poderia saber pessoalmente."),
        Turn("defense_attorney", "Faça oralmente perguntas à testemunha do autor, buscando esclarecer ou contraditar pontos relevantes. Não escreva petição."),
        Turn("judge", "Registre oralmente o encerramento desta oitiva e determine o próximo ato."),
    ],
    CourtPhase.WITNESS_DEFENSE: [
        Turn("judge", "Chame a testemunha indicada pela defesa, faça sua qualificação e formule perguntas iniciais pertinentes. Fale oralmente, sem produzir termo."),
        Turn("witness", "Preste depoimento oral como testemunha da defesa, respeitando estritamente os fatos que poderia conhecer pessoalmente."),
        Turn("plaintiff_attorney", "Faça oralmente perguntas à testemunha da defesa, explorando contradições e pontos controvertidos."),
        Turn("judge", "Registre oralmente o encerramento desta oitiva e determine o próximo ato."),
    ],
    CourtPhase.EXPERT: [
        Turn("judge", "Apresente oralmente o objeto da perícia e os pontos que precisam de esclarecimento. Não redija laudo ou decisão completa."),
        Turn("expert", "Atue como perito judicial e apresente oralmente os principais achados, método e conclusões técnicas, exclusivamente com base nos autos."),
        Turn("plaintiff_attorney", "Formule oralmente perguntas ou pedidos de esclarecimento pertinentes ao laudo."),
        Turn("defense_attorney", "Formule oralmente perguntas ou pedidos de esclarecimento pertinentes ao laudo."),
        Turn("judge", "Registre oralmente os esclarecimentos e determine o prosseguimento adequado."),
    ],
    CourtPhase.MP: [
        Turn("prosecutor", "Manifeste-se oralmente pelo Ministério Público somente se sua intervenção for cabível no caso. Seja objetivo e não produza peça escrita."),
        Turn("judge", "Registre oralmente a manifestação do Ministério Público e determine o próximo ato. Não produza sentença."),
    ],
    CourtPhase.CLOSING: [
        Turn("plaintiff_attorney", "Apresente oralmente as alegações finais da parte autora, enfrentando fatos, provas e teses relevantes. Não escreva memoriais completos."),
        Turn("defense_attorney", "Apresente oralmente as alegações finais da defesa, enfrentando fatos, provas e teses relevantes. Não escreva memoriais completos."),
        Turn("judge", "Declare oralmente encerrados os debates e encaminhe o processo para deliberação ou sentença, conforme o rito."),
    ],
    CourtPhase.DELIBERATION: [
        Turn("juror", "Delibere oralmente sobre fatos e provas, indicando de forma fundamentada os pontos provados ou não provados. Não produza documento judicial."),
        Turn("judge", "Registre oralmente a deliberação e encaminhe o feito para a decisão cabível."),
    ],
    CourtPhase.JUDGMENT: [
        Turn("judge", "Agora, e somente nesta fase, produza a sentença ou decisão final fundamentada, enfrentando pedidos, argumentos, provas e questões processuais efetivamente registrados nos autos."),
    ],
}

def next_agent_turn(session: CourtSession):
    turns = PHASE_TURNS.get(session.phase, [])
    # O participante humano controla o próprio turno. Continuar julgamento
    # nunca deve fazer a IA falar no lugar do usuário.
    while session.turn_index < len(turns):
        turn = turns[session.turn_index]
        if turn.role == session.user_role.value:
            return None
        if agent_for(turn.role) is None:
            session.turn_index += 1
            continue
        return turn
    return None

def peek_turn(session: CourtSession):
    turns = PHASE_TURNS.get(session.phase, [])
    if session.turn_index >= len(turns):
        return None
    return turns[session.turn_index]

def run_next_agent(process, session, provider=None):
    turn = next_agent_turn(session)
    if turn is None:
        return None
    result = run_registered_agent(process, turn.role, turn.instruction, provider)
    session.accept_turn()
    return result
