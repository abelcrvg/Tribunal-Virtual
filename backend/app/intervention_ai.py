from .ai_provider import get_provider

def assess_with_context(content:str,facts:str,history:list[str],phase:str)->str:
    prompt=f"Fase: {phase}\nFatos: {facts}\nHistórico: {history[-12:]}\nIntervenção: {content}\nClassifique apenas como IRRELEVANTE, PERTINENTE ou DECISIVA. Considere pertinência jurídica, relação com fatos/provas e eventual questão processual. Não trate alegação como fato comprovado."
    try:
        result=get_provider().generate(system="Você é assessor judicial imparcial. Não decida o mérito. Responda primeiro com uma única categoria exata: IRRELEVANTE, PERTINENTE ou DECISIVA. Depois explique brevemente.",prompt=prompt)
        text=result.text.upper();
        if "DECISIVA" in text:return "decisive"
        if "PERTINENTE" in text:return "pertinent"
    except Exception: pass
    return "normal"
