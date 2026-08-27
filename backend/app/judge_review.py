from dataclasses import dataclass
from .ai_provider import get_provider, AIResponse

@dataclass(frozen=True)
class JudicialReview:
    classification: str
    reasoning: str
    response: AIResponse

def review_intervention(*, content: str, facts: str, history: list[str], phase: str) -> JudicialReview:
    prompt = f"Fase: {phase}\nFatos: {facts}\nHistórico: {history[-20:]}\nIntervenção: {content}\n\nClassifique como IRRELEVANTE, PERTINENTE ou DECISIVA. Depois explique em poucas linhas a relação com os fatos, provas ou questão processual. Diferencie alegação de fato comprovado e não invente legislação ou precedentes."
    response = get_provider().generate(system="Você é assessor judicial imparcial. Não decida o mérito; avalie apenas a pertinência processual da intervenção.", prompt=prompt)
    text=response.text.upper()
    classification="decisive" if "DECISIVA" in text else "pertinent" if "PERTINENTE" in text else "normal"
    return JudicialReview(classification, response.text, response)
