import json
import random
import uuid
from .ai_provider import AIProvider, get_provider

# Used only as broad inspiration when no AI provider is available. With Gemini,
# the model is intentionally free to invent the specific case.
_AREA_HINTS = {
    "consumer": ["serviços digitais", "bancos e pagamentos", "saúde suplementar", "telefonia", "transporte", "turismo", "seguros", "comércio eletrônico", "educação privada", "veículos", "energia", "imobiliário de consumo"],
    "civil": ["contratos", "responsabilidade civil", "família", "sucessões", "condomínio", "vizinhança", "direito de imagem", "propriedade", "locação", "societário", "obrigações", "indenização"],
    "labor": ["jornada", "remuneração", "rescisão", "assédio", "acidente de trabalho", "equiparação", "terceirização", "teletrabalho", "estabilidade", "insalubridade", "comissões", "discriminação"],
    "criminal": ["crimes patrimoniais", "crimes contra a pessoa", "fraudes", "crimes digitais", "trânsito", "violência doméstica", "tráfico", "corrupção", "lavagem de dinheiro", "crimes ambientais", "crimes empresariais", "tribunal do júri"],
}


def _fallback(area: str, case_type: str, include_mp: bool, jury: bool) -> dict:
    hints = _AREA_HINTS.get(area, _AREA_HINTS["civil"])
    subject = random.choice(hints)
    return {
        "title": f"Caso simulado sobre {subject}",
        "plaintiff": "Parte autora fictícia",
        "defendant": "Parte ré fictícia",
        "facts": f"Caso educacional fictício relacionado a {subject}, com controvérsia a ser desenvolvida durante a instrução.",
        "legal_issue": "Questão jurídica a ser delimitada a partir dos fatos e das provas.",
        "evidence": ["documentos", "comunicações", "depoimentos", "eventual prova técnica"],
        "witnesses": random.randint(2, 5),
        "expert_needed": area in {"civil", "labor", "consumer"} and random.choice([True, False]),
        "include_mp": include_mp or area == "criminal",
        "jury": bool(jury),
        "procedure": "Tribunal do Júri" if jury else "procedimento compatível com a matéria",
    }


def _parse(text: str) -> dict:
    raw = text.strip()
    if raw.startswith("```json"): raw = raw[7:]
    if raw.startswith("```"): raw = raw[3:]
    if raw.endswith("```"): raw = raw[:-3]
    data = json.loads(raw.strip())
    required = ("title", "plaintiff", "defendant", "facts", "legal_issue", "evidence", "witnesses", "expert_needed", "include_mp", "jury", "procedure")
    missing = [k for k in required if k not in data]
    if missing: raise ValueError(f"Resposta do gerador sem campos: {', '.join(missing)}")
    return data


def generate_case(area: str, case_type: str, include_mp: bool, jury: bool, provider: AIProvider | None = None) -> dict:
    active = provider or get_provider()
    if active.__class__.__name__ == "LocalFallbackProvider":
        return _fallback(area, case_type, include_mp, jury)

    seed = uuid.uuid4().hex
    hints = _AREA_HINTS.get(area, _AREA_HINTS["civil"])
    random_hint = random.choice(hints)
    prompt = f"""Crie um caso jurídico brasileiro inteiramente fictício para um simulador educacional.\nÁrea escolhida: {area}.\nTema informado pelo usuário: {case_type}.\nSemente desta geração: {seed}.\nExemplo de subárea apenas como inspiração, não como restrição: {random_hint}.\nMinistério Público solicitado: {include_mp}.\nTribunal do Júri solicitado: {jury}.\n\nIMPORTANTE: você é responsável por escolher o caso. Não use um banco fixo de casos e não fique preso ao exemplo de subárea. A cada geração escolha livremente um conflito diferente, podendo combinar instituições, relações jurídicas, ambientes, fatos, valores, consequências, provas, personagens, teses e questões processuais. Duas gerações com a mesma área devem poder resultar em casos completamente diferentes.\n\nVarie deliberadamente, entre gerações, pelo menos vários destes elementos: natureza do conflito, relação entre as partes, objeto litigioso, cronologia, local, causa do problema, extensão do dano, tipo e qualidade das provas, existência de testemunhas, necessidade de perícia, tese defensiva, questão preliminar, comportamento das partes, repercussão econômica ou pessoal e resultado processual possível. Evite clichês repetidos. Não faça apenas a troca de nomes em um mesmo enredo.\n\nVocê pode escolher qualquer situação plausível dentro da área, inclusive uma situação pouco comum, desde que juridicamente coerente. O tema do usuário é uma orientação ampla, não um título obrigatório. Quando 'Aleatório' for informado, ignore qualquer preferência temática e escolha livremente.\n\nRetorne SOMENTE JSON válido, sem markdown, com exatamente estes campos: title, plaintiff, defendant, facts, legal_issue, evidence (array de strings), witnesses (integer entre 2 e 6), expert_needed (boolean), include_mp (boolean), jury (boolean), procedure.\n\nTodos os nomes, números, datas, locais e fatos devem ser fictícios. Não copie processos reais, pessoas reais, decisões, ementas ou textos de sites jurídicos. Pode se inspirar genericamente na diversidade de conflitos existentes no direito brasileiro, mas produza uma narrativa original. Se a matéria não admitir Júri, jury deve ser false. include_mp deve refletir a necessidade jurídica real, salvo quando o usuário o solicitar expressamente."""
    response = active.generate(
        system="Você é um roteirista jurídico especializado em criar casos fictícios variados para simulação processual brasileira. Sua prioridade é diversidade narrativa e jurídica, não repetição de templates.",
        prompt=prompt,
    )
    try:
        return _parse(response.text)
    except Exception as exc:
        raise RuntimeError(f"Falha ao interpretar o caso gerado pela IA: {exc}") from exc
