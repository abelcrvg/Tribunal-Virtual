import json
import random
import uuid
from .ai_provider import AIProvider, get_provider

_AREA_HINTS = {
    "consumer": ["serviços digitais", "bancos e pagamentos", "saúde suplementar", "telefonia", "transporte", "turismo", "seguros", "comércio eletrônico", "educação privada", "veículos", "energia", "imobiliário de consumo", "fraudes contratuais", "dados pessoais", "marketplaces"],
    "civil": ["contratos", "responsabilidade civil", "família", "sucessões", "condomínio", "vizinhança", "direito de imagem", "propriedade", "locação", "societário", "obrigações", "indenização", "posse", "inventário", "danos ambientais privados"],
    "labor": ["jornada", "remuneração", "rescisão", "assédio", "acidente de trabalho", "equiparação", "terceirização", "teletrabalho", "estabilidade", "insalubridade", "comissões", "discriminação", "metas abusivas", "revista pessoal", "doença ocupacional"],
    "criminal": ["crimes patrimoniais", "crimes contra a pessoa", "fraudes", "crimes digitais", "trânsito", "violência doméstica", "tráfico", "corrupção", "lavagem de dinheiro", "crimes ambientais", "crimes empresariais", "tribunal do júri", "falsidade documental", "crimes contra a administração", "organização criminosa"],
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
        "expert_needed": random.choice([True, False]),
        "include_mp": include_mp or area == "criminal",
        "jury": bool(jury),
        "procedure": "Tribunal do Júri" if jury else "procedimento compatível com a matéria",
    }


def _parse(text: str) -> dict:
    raw = text.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    data = json.loads(raw.strip())
    required = ("title", "plaintiff", "defendant", "facts", "legal_issue", "evidence", "witnesses", "expert_needed", "include_mp", "jury", "procedure")
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Resposta do gerador sem campos: {', '.join(missing)}")
    return data


def _generate_with_web(active, system: str, prompt: str):
    """Gera um caso com grounding na Pesquisa Google sem copiar casos reais."""
    if active.__class__.__name__ != "GeminiProvider":
        return active.generate(system=system, prompt=prompt)
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise RuntimeError("Instale a dependência google-genai para usar o Gemini") from exc
    client = genai.Client(api_key=active.api_key)
    config = types.GenerateContentConfig(
        system_instruction=system,
        tools=[types.Tool(google_search=types.GoogleSearch())],
    )
    return client.models.generate_content(
        model=active.model,
        contents=prompt,
        config=config,
    )


def generate_case(area: str, case_type: str, include_mp: bool, jury: bool, provider: AIProvider | None = None) -> dict:
    active = provider or get_provider()
    if active.__class__.__name__ == "LocalFallbackProvider":
        return _fallback(area, case_type, include_mp, jury)

    seed = uuid.uuid4().hex
    hints = _AREA_HINTS.get(area, _AREA_HINTS["civil"])
    random_hint = random.choice(hints)
    prompt = f"""Você é responsável por criar um caso jurídico brasileiro ORIGINAL e inteiramente fictício para um simulador educacional.

Área escolhida: {area}
Tema/orientação do usuário: {case_type}
Semente única desta geração: {seed}
Subárea sugerida apenas para diversificar a pesquisa: {random_hint}
Ministério Público solicitado: {include_mp}
Tribunal do Júri solicitado: {jury}

ANTES DE CRIAR O CASO, use a Pesquisa Google para explorar a diversidade de conflitos jurídicos brasileiros relacionados à área e, quando útil, consulte fontes públicas de jurisprudência e notícias jurídicas. Você pode pesquisar tipos de controvérsia, situações fáticas, questões processuais e padrões de prova. Jusbrasil pode ser uma das referências públicas, mas não deve ser a única.

A pesquisa serve SOMENTE como inspiração para descobrir possibilidades. NÃO copie processos, nomes, números, decisões, ementas, trechos, fatos específicos, valores ou redações de casos encontrados na internet. O caso final deve ser uma narrativa nova e fictícia.

Você escolhe livremente a situação concreta. O tema do usuário é uma orientação, NÃO um roteiro. Se o tema for 'Aleatório', escolha qualquer subtema plausível da área.

A cada geração, procure deliberadamente uma situação substancialmente diferente das anteriores. Varie o máximo possível:
- tipo de conflito e relação jurídica;
- objeto litigioso;
- contexto e ambiente;
- cronologia e causa do conflito;
- perfil das partes;
- valores e consequências;
- documentos e qualidade das provas;
- testemunhas e o que cada uma sabe;
- necessidade ou não de perícia;
- teses antagônicas;
- questão preliminar ou incidente processual;
- possível atuação do Ministério Público;
- rito e atos processuais;
- dificuldades probatórias e contradições.

EVITE repetir modelos como “produto com defeito”, “cobrança indevida”, “horas extras” ou “furto” apenas trocando nomes. Prefira situações variadas, inclusive pouco óbvias, desde que juridicamente coerentes.

O caso deve ser suficientemente rico para uma audiência longa e permitir debate real entre os participantes. Inclua pelo menos uma controvérsia factual que possa gerar confronto entre prova oral/documental e outra questão que possa exigir raciocínio jurídico.

Retorne SOMENTE JSON válido, sem markdown e sem comentários, com exatamente estes campos:
title, plaintiff, defendant, facts, legal_issue, evidence, witnesses, expert_needed, include_mp, jury, procedure

evidence deve ser um array de strings.
witnesses deve ser um inteiro entre 2 e 6.
expert_needed deve ser booleano.
include_mp deve ser booleano e juridicamente coerente, exceto quando solicitado expressamente.
jury só pode ser true quando a matéria admitir Tribunal do Júri e houver pertinência com o caso.
procedure deve descrever de forma genérica o rito processual adequado.

Todos os nomes, datas, locais, números e demais dados identificadores devem ser fictícios."""

    system = "Você é um roteirista jurídico especializado em criar casos fictícios variados para simulação processual brasileira. Use a web apenas como pesquisa de diversidade de situações e produza sempre uma narrativa original."
    response = _generate_with_web(active, system, prompt)
    try:
        return _parse(getattr(response, "text", "") or "")
    except Exception as exc:
        raise RuntimeError(f"Falha ao interpretar o caso gerado pela IA: {exc}") from exc
