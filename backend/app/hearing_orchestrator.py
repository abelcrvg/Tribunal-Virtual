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
        Turn("defense_attorney", "Atue como advogado do réu. Faça uma manifestação oral específica e argumentativa sobre os fatos e provas deste processo. Enfrente diretamente as alegações da parte autora e desenvolva uma tese defensiva própria. Não apenas anuncie que falará."),
        Turn("plaintiff_attorney", "Responda oralmente como advogado do autor aos argumentos efetivamente apresentados pela defesa. Ataque contradições, fatos, provas e fundamentos jurídicos concretos deste processo. Não produza petição."),
        Turn("judge", "Conduza oralmente a audiência reagindo ao debate que realmente ocorreu. Faça perguntas ou determine providências processuais concretas relacionadas aos pontos controvertidos. Não produza decisão genérica."),
    ],
    CourtPhase.WITNESS_PLAINTIFF: [
        Turn("judge", "Chame nominalmente a testemunha do autor, qualifique-a e faça perguntas concretas relacionadas aos fatos controvertidos deste processo."),
        Turn("witness", "Responda como a testemunha específica deste caso. Relate fatos que poderia ter presenciado pessoalmente, com detalhes coerentes com os autos. Não invente conhecimento técnico ou jurídico."),
        Turn("defense_attorney", "Faça perguntas concretas à testemunha do autor, explorando pontos favoráveis à defesa, contradições ou lacunas no depoimento que acabou de ocorrer."),
        Turn("judge", "Reaja ao depoimento e às perguntas que ocorreram. Esclareça pontos necessários e encerre a oitiva de forma natural, determinando o próximo ato."),
    ],
    CourtPhase.WITNESS_DEFENSE: [
        Turn("judge", "Chame nominalmente a testemunha da defesa, qualifique-a e formule perguntas concretas sobre os fatos controvertidos deste processo."),
        Turn("witness", "Responda como a testemunha específica da defesa, relatando apenas fatos que poderia conhecer pessoalmente e mantendo coerência com os autos e com perguntas anteriores."),
        Turn("plaintiff_attorney", "Faça perguntas concretas à testemunha da defesa, explorando contradições, limitações do conhecimento da testemunha e pontos favoráveis ao autor."),
        Turn("judge", "Reaja ao depoimento e às perguntas efetivamente feitas. Faça os esclarecimentos necessários e encerre a oitiva de maneira contextualizada."),
    ],
    CourtPhase.EXPERT: [
        Turn("judge", "Apresente ao perito os pontos técnicos concretos que precisam ser esclarecidos neste processo e formule perguntas específicas."),
        Turn("expert", "Atue como perito judicial deste processo. Explique método, elementos examinados, achados e conclusões técnicas com detalhes compatíveis com os autos. Não dê opinião jurídica e não responda genericamente."),
        Turn("plaintiff_attorney", "Faça perguntas técnicas concretas ao perito sobre os pontos que interessam à parte autora, reagindo às conclusões que ele acabou de apresentar."),
        Turn("defense_attorney", "Faça perguntas técnicas concretas ao perito sobre os pontos que interessam à defesa, reagindo às respostas e conclusões já apresentadas."),
        Turn("judge", "Esclareça eventuais pontos técnicos restantes e encerre a participação do perito de forma contextualizada, determinando o próximo ato."),
    ],
    CourtPhase.MP: [
        Turn("prosecutor", "Atue como Promotor de Justiça. Analise este caso concreto e manifeste-se somente se houver hipótese de intervenção do Ministério Público. Se houver, fundamente a manifestação nos fatos e na natureza do processo; se não houver, explique objetivamente por que a intervenção não é cabível. Fale como membro do MP, não como narrador."),
        Turn("judge", "Responda especificamente à manifestação do Ministério Público e determine a providência processual cabível neste caso. Não use fórmula genérica."),
    ],
    CourtPhase.CLOSING: [
        Turn("plaintiff_attorney", "Apresente alegações finais orais específicas deste processo, relacionando fatos, provas, depoimentos e teses jurídicas que realmente apareceram na audiência."),
        Turn("defense_attorney", "Apresente alegações finais orais específicas deste processo, enfrentando as provas e argumentos produzidos na audiência e sustentando a tese da defesa."),
        Turn("judge", "Encerre os debates reagindo ao que efetivamente foi dito pelas partes e encaminhe o processo para deliberação ou julgamento, sem antecipar a sentença."),
    ],
    CourtPhase.DELIBERATION: [
        Turn("juror", "Delibere sobre este processo concreto, analisando os fatos e provas efetivamente produzidos e explicando quais pontos considera provados ou não provados. Não invente fatos."),
        Turn("judge", "Analise a deliberação produzida e encaminhe o feito para a decisão cabível, mencionando os pontos concretos que serão considerados."),
    ],
    CourtPhase.JUDGMENT: [
        Turn("judge", "Produza a sentença final deste processo somente agora. Enfrente os pedidos, fatos, provas, depoimentos, argumentos e questões processuais que efetivamente constam do histórico. A decisão deve ser específica para este caso e fundamentada, sem placeholders ou texto genérico."),
    ],
}

def _transcript(session: CourtSession) -> str:
    if not session.messages:
        return "Nenhuma fala foi registrada ainda."
    lines = []
    for m in session.messages:
        role = m.role.value if m.role else "system"
        lines.append(f"{m.sender} [{role}]: {m.content}")
    return "\n".join(lines)

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
    if session.turn_index >= len(turns):
        return None
    return turns[session.turn_index]

def run_next_agent(process, session, provider=None):
    turn = next_agent_turn(session)
    if turn is None:
        return None
    transcript = _transcript(session)
    contextual_instruction = (
        f"{turn.instruction}\n\n"
        "LEIA TODA A TRANSCRIÇÃO DA AUDIÊNCIA ABAIXO ANTES DE RESPONDER. "
        "Sua fala deve ser uma continuação direta e contextual do que foi dito. "
        "Responda aos argumentos, perguntas, fatos e contradições já apresentados. "
        "Nunca reinicie a audiência, repita a abertura, invente uma nova versão do caso ou ignore a última fala. "
        "Você está falando agora como a personagem indicada no turno.\n\n"
        "TRANSCRIÇÃO INTEGRAL DA AUDIÊNCIA:\n"
        f"{transcript}"
    )
    result = run_registered_agent(process, turn.role, contextual_instruction, provider)
    session.accept_turn()
    return result
