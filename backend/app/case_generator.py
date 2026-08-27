import json
import random
from .ai_provider import AIProvider, AIResponse, get_provider

_CASE_BANK={
 "consumer": [
  ("Vício oculto em equipamento eletrônico", "Mariana Duarte", "TecnoVale Comércio Ltda.", "A autora comprou um notebook que apresentou falha grave após quatro meses de uso. A assistência técnica alegou mau uso, mas um laudo particular apontou defeito preexistente. A controvérsia envolve responsabilidade do fornecedor, extensão do dano e restituição do valor."),
  ("Cobrança indevida após cancelamento de serviço", "Rafael Monteiro", "ConectaMais S.A.", "O autor cancelou um serviço de assinatura e recebeu cobranças posteriores durante três meses. Há protocolos de atendimento e registros de pagamento. A ré sustenta falha cadastral e afirma ter estornado parte dos valores."),
 ],
 "civil": [
  ("Responsabilidade por queda em estabelecimento comercial", "Camila Freitas", "Mercado Central de Caxias Ltda.", "A autora caiu em um corredor de supermercado onde havia líquido no piso sem sinalização. Funcionários prestaram atendimento e uma câmera registrou parte do ocorrido. A ré contesta a extensão dos danos e a existência de culpa."),
  ("Descumprimento de contrato de prestação de serviços", "André Vasconcelos", "Horizonte Eventos Ltda.", "O autor contratou uma empresa para organizar um evento e afirma que serviços essenciais não foram entregues. A empresa sustenta que houve alteração unilateral do contrato pelo contratante e cobra valores adicionais."),
 ],
 "labor": [
  ("Horas extras e controle de jornada", "Beatriz Nogueira", "Logística Rápida Brasil Ltda.", "A reclamante afirma que trabalhava além da jornada registrada e que mensagens corporativas comprovam parte da rotina. A empresa sustenta que os registros eletrônicos são confiáveis e que havia compensação de jornada."),
  ("Rescisão e verbas trabalhistas controvertidas", "Gustavo Almeida", "Serviços Alfa Operações Ltda.", "O reclamante contesta a modalidade de desligamento e afirma haver verbas não pagas. A empresa apresenta documentos de rescisão e sustenta que todos os valores foram quitados."),
 ],
 "criminal": [
  ("Furto qualificado e controvérsia sobre reconhecimento", "Ministério Público", "Eduardo Carvalho", "O Ministério Público atribui ao acusado a subtração de equipamentos de uma loja durante a madrugada. Há imagens de baixa resolução, depoimento de uma testemunha e apreensão de objeto semelhante ao utilizado no fato. A defesa questiona o reconhecimento e a cadeia de custódia."),
  ("Lesão corporal e versões conflitantes", "Ministério Público", "Marcelo Ribeiro", "Após uma discussão em frente a um estabelecimento, a vítima sofreu lesões. Duas testemunhas apresentam versões parcialmente divergentes e há gravação parcial de uma câmera. A defesa sustenta legítima defesa e questiona a sequência dos acontecimentos."),
 ],
}

def _fallback(area:str, case_type:str, include_mp:bool, jury:bool) -> dict:
    options=_CASE_BANK.get(area,_CASE_BANK["civil"])
    title,plaintiff,defendant,facts=random.choice(options)
    witnesses=3 if area in {"civil","consumer","labor"} else 4
    return {
      "title": title, "plaintiff": plaintiff, "defendant": defendant, "facts": facts,
      "legal_issue": "A controvérsia será delimitada durante a instrução, com contraditório e análise das provas apresentadas.",
      "evidence":["documentos contratuais ou administrativos","registros de atendimento ou comunicação","depoimentos das testemunhas","eventual prova técnica, se necessária"],
      "witnesses": witnesses, "expert_needed": area in {"civil","labor","criminal"},
      "include_mp": include_mp or area=="criminal", "jury": jury,
      "procedure": "procedimento comum" if not jury else "Tribunal do Júri",
    }

def _parse(text:str) -> dict:
    raw=text.strip().replace("```json","",1).replace("```","",1).strip()
    data=json.loads(raw)
    required=("title","plaintiff","defendant","facts","legal_issue","evidence","witnesses","expert_needed","include_mp","jury","procedure")
    missing=[k for k in required if k not in data]
    if missing: raise ValueError(f"Resposta do gerador sem campos: {', '.join(missing)}")
    return data

def generate_case(area:str, case_type:str, include_mp:bool, jury:bool, provider:AIProvider|None=None) -> dict:
    active=provider or get_provider()
    if active.__class__.__name__=="LocalFallbackProvider":
        return _fallback(area,case_type,include_mp,jury)
    prompt=f"""Gere um caso jurídico brasileiro inteiramente fictício para uma simulação educacional. Área: {area}. Preferência temática: {case_type}. Ministério Público solicitado: {include_mp}. Tribunal do Júri solicitado: {jury}.\n\nRetorne SOMENTE JSON válido, sem markdown, com exatamente estes campos: title, plaintiff, defendant, facts, legal_issue, evidence (array de strings), witnesses (integer entre 2 e 6), expert_needed (boolean), include_mp (boolean), jury (boolean), procedure.\n\nO caso deve ser plausível, ter fatos concretos, conflito realista, provas contraditórias e personagens suficientes para uma audiência. Não use pessoas reais, processos reais ou dados pessoais reais. Não invente números de processos, decisões ou citações jurisprudenciais. Se a área não comportar júri, jury deve ser false. O campo procedure deve descrever o rito de forma genérica e juridicamente coerente."""
    response=active.generate(system="Você é o gerador de casos fictícios de um simulador educacional do processo judicial brasileiro. Sua saída será consumida por software.",prompt=prompt)
    try:
        return _parse(response.text)
    except Exception as exc:
        raise RuntimeError(f"Falha ao interpretar o caso gerado pela IA: {exc}") from exc
