from dataclasses import dataclass
from enum import Enum


class AppealType(str, Enum):
    APPEAL = "apelação"
    MOTION_FOR_CLARIFICATION = "embargos_de_declaracao"
    INTERLOCUTORY_APPEAL = "agravo_de_instrumento"
    INTERNAL_APPEAL = "agravo_interno"
    SPECIAL_APPEAL = "recurso_especial"
    EXTRAORDINARY_APPEAL = "recurso_extraordinario"


@dataclass(frozen=True)
class AppealResult:
    admissible: bool
    type: AppealType
    destination: str
    reason: str


def analyze_appeal(*, case_area: str, decision_type: str, appellant_role: str, appeal_type: AppealType) -> AppealResult:
    if appellant_role not in {"plaintiff", "defendant", "public_prosecutor", "third_party"}:
        return AppealResult(False, appeal_type, "", "O solicitante não possui legitimidade configurada para este recurso na simulação.")

    if appeal_type == AppealType.MOTION_FOR_CLARIFICATION:
        return AppealResult(True, appeal_type, "Juízo ou órgão que proferiu a decisão", "Recurso destinado a esclarecer obscuridade, eliminar contradição, suprir omissão ou corrigir erro material, conforme o cenário simulado.")

    if appeal_type == AppealType.APPEAL:
        if decision_type not in {"sentence", "final_decision"}:
            return AppealResult(False, appeal_type, "", "A apelação não foi considerada cabível para o tipo de decisão informado.")
        return AppealResult(True, appeal_type, "Tribunal de Justiça ou Tribunal Regional Federal competente", "Admissibilidade preliminar simulada para decisão de primeiro grau.")

    if appeal_type == AppealType.SPECIAL_APPEAL:
        return AppealResult(True, appeal_type, "Superior Tribunal de Justiça", "A simulação encaminha o recurso para análise de admissibilidade e posterior julgamento quando presentes seus pressupostos.")

    if appeal_type == AppealType.EXTRAORDINARY_APPEAL:
        return AppealResult(True, appeal_type, "Supremo Tribunal Federal", "A simulação encaminha o recurso para análise de admissibilidade quando houver questão constitucional relevante.")

    return AppealResult(True, appeal_type, "Órgão competente conforme a fase processual", "Recurso encaminhado para análise de admissibilidade pelo órgão competente.")
