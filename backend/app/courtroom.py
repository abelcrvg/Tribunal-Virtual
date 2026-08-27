from dataclasses import dataclass
from enum import Enum
from uuid import uuid4


class Instance(str, Enum):
    FIRST = "first_instance"
    SECOND = "second_instance"
    STJ = "stj"
    STF = "stf"


class UserRole(str, Enum):
    SPECTATOR = "spectator"
    PLAINTIFF_ATTORNEY = "plaintiff_attorney"
    DEFENSE_ATTORNEY = "defense_attorney"
    PROSECUTOR = "prosecutor"
    JUDGE = "judge"
    JUROR = "juror"


class ParticipantType(str, Enum):
    JUDGE = "judge"
    ATTORNEY = "attorney"
    PROSECUTOR = "prosecutor"
    DEFENDANT = "defendant"
    PLAINTIFF = "plaintiff"
    WITNESS = "witness"
    EXPERT = "expert"
    CLERK = "clerk"
    JUROR = "juror"
    APPELLATE_JUDGE = "appellate_judge"
    REPORTING_JUDGE = "reporting_judge"


class InterventionAssessment(str, Enum):
    IRRELEVANT = "irrelevant"
    PERTINENT = "pertinent"
    DECISIVE = "decisive"
    ABUSIVE = "abusive"


@dataclass(frozen=True)
class Participant:
    id: str
    name: str
    role: ParticipantType
    side: str | None = None
    fictional: bool = True


@dataclass(frozen=True)
class CourtroomDecision:
    assessment: InterventionAssessment
    allowed: bool
    judge_response: str
    requires_record: bool
    reason: str


def build_courtroom(include_mp: bool = False, jury: bool = False, instance: Instance = Instance.FIRST) -> list[Participant]:
    if instance == Instance.SECOND:
        participants = [
            Participant(str(uuid4()), "Desembargador Presidente", ParticipantType.APPELLATE_JUDGE),
            Participant(str(uuid4()), "Desembargadora Relatora", ParticipantType.REPORTING_JUDGE),
            Participant(str(uuid4()), "Desembargador Vogal", ParticipantType.APPELLATE_JUDGE),
            Participant(str(uuid4()), "Representante do recorrente", ParticipantType.ATTORNEY),
            Participant(str(uuid4()), "Representante do recorrido", ParticipantType.ATTORNEY),
            Participant(str(uuid4()), "Servidor da secretaria", ParticipantType.CLERK),
        ]
        if include_mp:
            participants.insert(3, Participant(str(uuid4()), "Procurador de Justiça", ParticipantType.PROSECUTOR))
        return participants

    participants = [
        Participant(str(uuid4()), "Magistrado responsável", ParticipantType.JUDGE),
        Participant(str(uuid4()), "Representante do autor", ParticipantType.ATTORNEY, "plaintiff"),
        Participant(str(uuid4()), "Representante do réu", ParticipantType.ATTORNEY, "defense"),
        Participant(str(uuid4()), "Servidor da secretaria", ParticipantType.CLERK),
        Participant(str(uuid4()), "Testemunha da parte autora", ParticipantType.WITNESS, "plaintiff"),
        Participant(str(uuid4()), "Testemunha da parte ré", ParticipantType.WITNESS, "defense"),
        Participant(str(uuid4()), "Perito judicial", ParticipantType.EXPERT),
    ]
    if include_mp:
        participants.insert(3, Participant(str(uuid4()), "Promotor de Justiça", ParticipantType.PROSECUTOR))
    if jury:
        participants.extend(Participant(str(uuid4()), f"Jurado {i:02d}", ParticipantType.JUROR) for i in range(1, 8))
    return participants


def assess_intervention(*, role: str, turn_role: str, content: str) -> CourtroomDecision:
    text = content.strip().lower()
    if not text:
        return CourtroomDecision(InterventionAssessment.IRRELEVANT, False, "A intervenção não contém conteúdo suficiente para análise.", False, "mensagem vazia")

    relevant_terms = ("documento", "prova", "testemunha", "contrato", "laudo", "artigo", "lei", "fato", "depoimento", "contradi", "omiss", "processo")
    is_relevant = any(term in text for term in relevant_terms) or len(text) >= 120
    abusive_markers = ("idiota", "cala a boca", "mentiroso", "mentirosa")
    is_abusive = any(term in text for term in abusive_markers)

    if is_abusive:
        return CourtroomDecision(InterventionAssessment.ABUSIVE, False, "A parte deve manter o respeito e a urbanidade. A intervenção não será considerada nestes termos.", False, "linguagem incompatível com a sessão")
    if turn_role == role:
        return CourtroomDecision(InterventionAssessment.PERTINENT if is_relevant else InterventionAssessment.IRRELEVANT, True, "A palavra está com a parte. Prossiga com sua manifestação.", is_relevant, "manifestação dentro da vez")
    if is_relevant:
        return CourtroomDecision(InterventionAssessment.DECISIVE if len(text) >= 220 else InterventionAssessment.PERTINENT, True, "A intervenção, embora realizada fora da ordem de fala, apresenta pertinência com a controvérsia. A palavra é concedida para esclarecimento.", True, "exceção por relevância processual")
    return CourtroomDecision(InterventionAssessment.IRRELEVANT, False, "A palavra permanece com a parte que está se manifestando. A intervenção não apresenta, neste momento, pertinência suficiente para alterar a ordem da audiência.", False, "fora da vez e sem relevância identificada")
