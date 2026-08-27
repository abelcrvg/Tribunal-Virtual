from dataclasses import dataclass
from .ai_provider import get_provider

@dataclass(frozen=True)
class JudicialReview:
    action:str
    explanation:str
    provider:str
    model:str

def review_intervention(*,content:str,assessment:str,facts:dict|str,history:list[str],phase:str)->JudicialReview:
    prompt=(f"Fase: {phase}\nFatos e memória dos autos: {facts}\nHistórico: {history[-12:]}\n"
            f"Avaliação preliminar: {assessment}\nIntervenção: {content}\n"
            "Como magistrado da simulação, escolha apenas uma ação: ADVERTIR, CONCEDER_PALAVRA ou REGISTRAR. "
            "Explique em 2-4 frases. Não decida o mérito e não invente fatos, provas, leis ou precedentes. "
            "Apenas alegações devem ser tratadas como alegações, salvo existência de prova nos autos.")
    try:
        result=get_provider().generate(system="Você é um juiz fictício conduzindo uma audiência educacional baseada no direito brasileiro. Seja imparcial e contextual.",prompt=prompt)
        text=result.text.strip(); upper=text.upper()
        action="REGISTRAR" if "REGISTRAR" in upper else "CONCEDER_PALAVRA" if "CONCEDER_PALAVRA" in upper else "ADVERTIR"
        return JudicialReview(action,text,result.provider,result.model)
    except Exception:
        fallback={"decisive":"REGISTRAR","pertinent":"CONCEDER_PALAVRA"}.get(assessment,"ADVERTIR")
        return JudicialReview(fallback,"Decisão provisória baseada na avaliação contextual disponível.","fallback","deterministic")
