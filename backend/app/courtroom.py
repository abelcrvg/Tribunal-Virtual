from dataclasses import dataclass
from enum import Enum


class InterventionAssessment(str, Enum):
    IRRELEVANT = "irrelevant"
    PERTINENT = "pertinent"
    DECISIVE = "decisive"
    ABUSIVE = "abusive"


@dataclass(frozen=True)
class CourtroomDecision:
    assessment: InterventionAssessment
    allowed: bool
    judge_response: str
    requires_record: bool
    reason: str


def assess_intervention(*, role: str, turn_role: str, content: str) -> CourtroomDecision:
    text = content.strip().lower()
    if not text:
        return CourtroomDecision(InterventionAssessment.IRRELEVANT, False, "A intervenção não contém conteúdo suficiente para análise.", False, "mensagem vazia")
    abusive_markers = ("idiota", "cala a boca", "vai se ferrar", "filho da", "otário", "otaria")
    if any(term in text for term in abusive_markers):
        return CourtroomDecision(InterventionAssessment.ABUSIVE, False, "A parte deve manter o respeito e a urbanidade. Evite novas intervenções dessa natureza.", False, "linguagem incompatível com a sessão")
    relevant_terms = ("documento", "prova", "testemunha", "contrato", "laudo", "artigo", "lei", "fato", "depoimento", "contradi", "omiss", "processo", "prazo", "competência", "nulidade", "evidência", "perícia")
    is_relevant = any(term in text for term in relevant_terms) or len(text) >= 160
    if turn_role == role:
        return CourtroomDecision(InterventionAssessment.PERTINENT if is_relevant else InterventionAssessment.IRRELEVANT, True, "A palavra está com a parte. Prossiga com sua manifestação.", is_relevant, "manifestação dentro da vez")
    if is_relevant:
        decisive_markers = ("contradiz", "prova que", "demonstra que", "documento original", "falsidade", "incompatível", "erro material", "omissão relevante", "nulidade")
        assessment = InterventionAssessment.DECISIVE if any(term in text for term in decisive_markers) or len(text) >= 320 else InterventionAssessment.PERTINENT
        return CourtroomDecision(assessment, True, "A intervenção, embora realizada fora da ordem de fala, apresenta pertinência com a controvérsia. A palavra é concedida para esclarecimento e a manifestação será registrada nos autos.", True, "exceção por relevância processual")
    return CourtroomDecision(InterventionAssessment.IRRELEVANT, False, "A palavra permanece com a parte que está se manifestando. A intervenção não apresenta, neste momento, pertinência suficiente para alterar a ordem da audiência.", False, "fora da vez e sem relevância identificada")
