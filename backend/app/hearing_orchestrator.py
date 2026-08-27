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
        Turn("judge", "Abra a audiência como magistrado. Identifique nominalmente o participante humano e o papel que ele escolheu. Conduza a abertura de forma natural, contextualizada ao processo e indique o próximo ato. Não use respostas genéricas nem marcadores técnicos."),
        Turn("clerk", "Atue como servidor da secretaria e faça somente o registro oral necessário para a abertura, contextualizado ao processo. Seja natural e específico; não produza uma ata completa."),
    ],
    CourtPhase.PLAINTIFF: [
        Turn("plaintiff_attorney", "Atue como advogado do autor. Faça uma manifestação oral específica sobre este processo, usando os fatos, documentos, pedidos e argumentos constantes dos autos. Não diga apenas que a palavra foi concedida; fale como o advogado."),
        Turn("judge", "Responda como magistrado ao que o advogado efetivamente acabou de dizer. Faça perguntas, esclareça pontos ou determine providências concretas conforme o caso. Não use respostas genéricas como CONCEDER_PALAVRA ou REGISTRAR."),
    ],
    CourtPhase.DEFENSE: [
        Turn("defense_attorney", "Atue como advogado do réu. Responda aos fatos, argumentos e provas efetivamente apresentados até agora. Construa e defenda a tese da ré, inclusive rebatendo diretamente a última manifestação. Fale como advogado, sem petição completa."),
        Turn("plaintiff_attorney", "Atue como advogado do autor e responda diretamente aos argumentos da defesa que acabaram de ser apresentados. Explore contradições, fatos, provas e fundamentos jurídicos concretos do histórico."),
        Turn("judge", "Reaja ao debate que realmente ocorreu. Faça uma intervenção judicial concreta, esclareça questão controvertida ou determine a providência adequada. Não reinicie a audiência nem repita teses já apresentadas."),
    ],
    CourtPhase.WITNESS_PLAINTIFF: [
        Turn("judge", "Chame nominalmente a testemunha do autor, qualifique-a e faça perguntas concretas relacionadas aos fatos controvertidos deste processo."),
        Turn("witness", "Responda como a testemunha específica deste caso. Relate fatos que poderia ter presenciado pessoalmente, com detalhes coerentes com os autos e com a transcrição."),
        Turn("defense_attorney", "Faça perguntas concretas à testemunha do autor, reagindo às respostas que ela acabou de dar e buscando esclarecer ou contraditar pontos relevantes."),
        Turn("judge", "Reaja às respostas e perguntas efetivamente ocorridas, faça os esclarecimentos necessários e encerre a oitiva de forma natural."),
    ],
    CourtPhase.WITNESS_DEFENSE: [
        Turn("judge", "Chame nominalmente a testemunha da defesa, qualifique-a e formule perguntas concretas sobre os fatos controvertidos."),
        Turn("witness", "Responda como a testemunha específica da defesa, usando apenas fatos que poderia conhecer pessoalmente e mantendo continuidade com a transcrição."),
        Turn("plaintiff_attorney", "Faça perguntas concretas à testemunha da defesa, reagindo ao depoimento e explorando contradições ou pontos favoráveis ao autor."),
        Turn("judge", "Reaja ao depoimento e às perguntas efetivamente feitas e encerre a oitiva de forma contextualizada."),
    ],
    CourtPhase.EXPERT: [
        Turn("judge", "Apresente ao perito os pontos técnicos concretos que precisam ser esclarecidos neste processo e formule perguntas específicas."),
        Turn("expert", "Atue como perito judicial deste processo. Explique método, elementos examinados, achados e conclusões técnicas de forma específica, coerente com os autos e com a transcrição. Não produza opinião jurídica."),
        Turn("plaintiff_attorney", "Faça perguntas técnicas concretas ao perito sobre as conclusões apresentadas, reagindo ao que ele efetivamente acabou de explicar."),
        Turn("defense_attorney", "Faça perguntas técnicas concretas ao perito, reagindo às respostas anteriores e buscando esclarecer pontos úteis à defesa."),
        Turn("judge", "Esclareça pontos técnicos restantes e encerre a participação do perito com base no que efetivamente foi discutido."),
    ],
    CourtPhase.MP: [
        Turn("prosecutor", "Atue como Promotor de Justiça e examine o caso concreto e toda a audiência. Manifeste-se somente na medida em que sua atuação seja cabível, enfrentando as questões reais do processo. Não use uma resposta-padrão."),
        Turn("judge", "Responda especificamente à manifestação do Ministério Público e determine a providência cabível para este processo, sem fórmulas genéricas."),
    ],
    CourtPhase.CLOSING: [
        Turn("plaintiff_attorney", "Apresente alegações finais orais específicas deste processo, relacionando os fatos, provas, depoimentos e teses que efetivamente apareceram durante a audiência."),
        Turn("defense_attorney", "Apresente alegações finais orais específicas deste processo, enfrentando o conteúdo produzido no debate e sustentando a tese da defesa."),
        Turn("judge", "Encerre os debates reagindo ao que efetivamente foi dito e encaminhe o processo ao julgamento conforme o rito. Não antecipe a sentença."),
    ],
    CourtPhase.DELIBERATION: [
        Turn("juror", "Delibere sobre este processo concreto com base nas provas e manifestações efetivamente produzidas, indicando de forma fundamentada os pontos que considera provados ou não provados."),
        Turn("judge", "Reaja à deliberação e encaminhe o feito para a decisão cabível, mencionando os pontos concretos que serão considerados."),
    ],
    CourtPhase.JUDGMENT: [
        Turn("judge", "Produza a sentença final deste processo somente agora. Decida com base no histórico integral da audiência e nos autos, enfrentando pedidos, fatos, provas, depoimentos, teses e questões processuais efetivamente registradas. Seja específico, fundamentado e coerente."),
    ],
}

def _transcript(session: CourtSession) -> str:
    if not session.messages:
        return "Nenhuma fala foi registrada ainda."
    return "\n".join(f"{m.sender} [{m.role.value if m.role else 'system'}]: {m.content}" for m in session.messages)

def next_agent_turn(session: CourtSession):
    turns = PHASE_TURNS.get(session.phase, [])
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
    return turns[session.turn_index] if session.turn_index < len(turns) else None

def run_next_agent(process, session, provider=None):
    turn = next_agent_turn(session)
    if turn is None:
        return None
    transcript = _transcript(session)
    contextual_instruction = (
        f"{turn.instruction}\n\n"
        "LEIA TODA A TRANSCRIÇÃO DA AUDIÊNCIA. Sua fala deve ser uma continuação direta do debate. "
        "Responda ao conteúdo da última manifestação e às informações relevantes acumuladas. "
        "Nunca reinicie a audiência, nunca repita a abertura e nunca troque de personagem. "
        "Não diga apenas que vai registrar, conceder palavra ou prosseguir: faça a manifestação, pergunta, resposta ou decisão concreta que a personagem faria.\n\n"
        "TRANSCRIÇÃO INTEGRAL:\n"
        f"{transcript}"
    )
    result = run_registered_agent(process, turn.role, contextual_instruction, provider, session=session)
    session.accept_turn()
    return result
