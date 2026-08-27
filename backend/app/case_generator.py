import json
import random
import time
import uuid
from .ai_provider import AIProvider, get_provider

# The generator intentionally uses a large thematic matrix rather than a tiny
# fixed case bank. The categories are inspired by broad public judicial topics
# reported by CNJ/DataJud, while the concrete scenarios are always fictional.
_SCENARIO_BANK = {
    "consumer": [
        "cobrança recorrente após cancelamento de assinatura",
        "produto entregue diferente do anunciado",
        "produto usado vendido como seminovo em ótimo estado",
        "negativa de garantia por alegada oxidação",
        "fraude em cartão com contestação de transações",
        "compra online cancelada sem restituição integral",
        "atraso de entrega de medicamento de uso contínuo",
        "plano de internet com velocidade persistentemente inferior à contratada",
        "bagagem extraviada em viagem nacional",
        "cancelamento unilateral de reserva de hotel",
        "consórcio com cobrança de taxa controversa",
        "financiamento com débito automático não autorizado",
        "instalação de energia com cobrança retroativa discutida",
        "negativação por dívida já quitada",
        "seguro residencial com recusa de cobertura após sinistro",
        "seguro veicular com discussão sobre perda total",
        "veículo com defeito intermitente e histórico de assistência técnica",
        "eletrodoméstico com incêndio e discussão sobre defeito de fabricação",
        "curso online com promessa publicitária não cumprida",
        "serviço odontológico interrompido antes da conclusão",
        "cobrança de tarifa bancária não prevista em contrato",
        "aplicativo de transporte com cobrança contestada após corrida",
        "marketplace que reteve valores de vendedor e comprador",
        "reajuste de plano de saúde por faixa etária contestado",
        "telecomunicação com portabilidade não solicitada",
    ],
    "civil": [
        "vazamento entre apartamentos e danos ao imóvel vizinho",
        "queda em estacionamento privado com controvérsia sobre iluminação",
        "obra vizinha que provocou rachaduras em residência",
        "inadimplemento de contrato de reforma residencial",
        "rescisão de contrato de fotografia de casamento",
        "falha em prestação de serviço de mudança",
        "acidente entre veículos em cruzamento sem semáforo",
        "responsabilidade por animal que escapou de propriedade",
        "danos causados por árvore em área privada",
        "disputa sobre devolução de sinal em compra de imóvel",
        "vício de construção em imóvel recém-entregue",
        "cobrança de dívida com pagamento parcial e divergência de saldo",
        "uso indevido de imagem em publicidade local",
        "ofensa em rede social e pedido de indenização",
        "rompimento antecipado de contrato de locação comercial",
        "retenção de caução após devolução do imóvel",
        "erro em serviço de evento e perda de documentos",
        "acidente em academia e discussão sobre dever de segurança",
        "responsabilidade por queda de objeto de fachada",
        "contrato verbal de sociedade de fato com disputa patrimonial",
        "herança com alegação de ocultação de patrimônio",
        "anulação de negócio por erro ou vício de consentimento",
        "cobrança de comissão de corretagem controvertida",
        "conflito entre vizinhos por infiltração e obras estruturais",
        "danos materiais após interrupção indevida de serviço essencial",
    ],
    "labor": [
        "horas extras com registros de ponto eletrônico divergentes",
        "vínculo de emprego alegado em contrato de prestação autônoma",
        "justa causa por suposta quebra de confidencialidade",
        "comissões pagas parcialmente e metas alteradas",
        "intervalo intrajornada parcialmente suprimido",
        "adicional de insalubridade em ambiente industrial",
        "acidente de trabalho com discussão sobre treinamento",
        "doença ocupacional e nexo com atividade repetitiva",
        "assédio moral alegado por cobrança excessiva de metas",
        "equiparação salarial entre empregados da mesma equipe",
        "desvio de função com diferenças salariais",
        "terceirização e responsabilidade subsidiária",
        "rescisão indireta por atraso salarial",
        "verbas rescisórias pagas fora do prazo",
        "controle de jornada por aplicativo fora do estabelecimento",
        "trabalho em domingos e feriados com folgas controvertidas",
        "gratificação de função incorporada após longo período",
        "estabilidade provisória após acidente",
        "dispensa discriminatória alegada por empregado",
        "diferenças de FGTS apontadas em extratos",
        "participação nos lucros com critérios controvertidos",
        "teletrabalho e reembolso de despesas de infraestrutura",
        "tempo à disposição antes do registro de ponto",
        "vendedora com comissões e estornos por cancelamento",
        "banco de horas contestado por falta de acordo válido",
    ],
    "criminal": [
        "furto em estabelecimento com reconhecimento questionado",
        "roubo com reconhecimento fotográfico e ausência de outras provas diretas",
        "lesão corporal após discussão em via pública",
        "ameaça entre vizinhos com mensagens de aplicativo",
        "estelionato envolvendo anúncio falso na internet",
        "apropriação indébita de valores confiados para administração",
        "receptação de aparelho eletrônico com origem controvertida",
        "fraude documental relacionada a contrato particular",
        "acidente de trânsito com discussão sobre dolo eventual ou culpa",
        "dano ao patrimônio público durante manifestação",
        "crime ambiental relacionado a descarte irregular",
        "violação de dispositivo informático e autenticidade de registros",
        "peculato envolvendo servidor e prestação de contas",
        "corrupção passiva em contratação pública com prova indiciária",
        "lavagem de dinheiro com movimentações financeiras atípicas",
        "tráfico de drogas com discussão sobre cadeia de custódia",
        "posse de arma e controvérsia sobre contexto da apreensão",
        "violência doméstica com versões conflitantes e medidas protetivas",
        "crime contra a honra praticado em rede social",
        "falsidade ideológica em documento empresarial",
        "abandono material com controvérsia sobre capacidade financeira",
        "homicídio culposo no trânsito com perícia veicular",
        "homicídio tentado com versões divergentes sobre a dinâmica",
        "latrocínio com imagens de baixa qualidade e prova indireta",
        "crime tributário com discussão sobre dolo e constituição do crédito",
    ],
}

_FACT_PATTERNS = [
    "há documentos favoráveis aos dois lados",
    "existe uma testemunha presencial cuja versão é parcialmente divergente",
    "um documento importante foi produzido unilateralmente",
    "há registros digitais cuja autenticidade será discutida",
    "existe uma lacuna temporal relevante nos documentos",
    "uma das partes sustenta que recebeu informação diferente da que consta no contrato",
    "o fato principal ocorreu em mais de uma etapa, com versões diferentes sobre o momento decisivo",
    "há um ponto técnico que não pode ser resolvido apenas por prova documental",
    "uma das principais testemunhas possui relação profissional anterior com uma das partes",
    "há comunicação por aplicativo que pode alterar a interpretação dos fatos",
    "uma prova relevante somente foi apresentada depois de uma das manifestações processuais",
    "as partes concordam com o fato básico, mas divergem sobre sua causa e suas consequências",
]

_PROCEDURES = [
    "procedimento comum",
    "procedimento comum com prova pericial",
    "procedimento comum com prova testemunhal e documental",
    "rito compatível com demanda trabalhista de conhecimento",
    "processo criminal com instrução e prova oral",
    "Tribunal do Júri",
]

def _random_design(area: str, case_type: str, jury: bool) -> dict:
    rng = random.SystemRandom()
    themes = _SCENARIO_BANK[area]
    chosen = rng.sample(themes, k=min(3, len(themes)))
    pattern = rng.sample(_FACT_PATTERNS, k=3)
    counterparties = rng.choice([
        "pessoa física e empresa regional",
        "duas pessoas físicas",
        "consumidor e empresa de médio porte",
        "empregado e empresa de serviços",
        "morador e condomínio",
        "Ministério Público e pessoa investigada",
        "empresa e prestador autônomo",
        "proprietário e locatário",
    ])
    twists = rng.sample([
        "há uma cronologia contestada",
        "uma testemunha mudou parcialmente sua versão",
        "uma das partes admite parte dos fatos, mas nega o nexo causal",
        "há discussão sobre competência ou admissibilidade de prova",
        "existe prova técnica potencialmente decisiva",
        "um pedido acessório depende de quantificação de prejuízo",
        "há controvérsia sobre dano moral além do dano patrimonial",
        "um comportamento posterior pode influenciar a interpretação do ato original",
        "a boa-fé objetiva é relevante para pelo menos uma das teses",
        "há possibilidade real de conciliação, mas as posições estão inicialmente distantes",
    ], k=3)
    nonce = f"{time.time_ns()}-{uuid.uuid4()}"
    return {
        "themes": chosen,
        "patterns": pattern,
        "counterparties": counterparties,
        "twists": twists,
        "nonce": nonce,
        "procedure_hint": "Tribunal do Júri" if jury else rng.choice(_PROCEDURES[:5]),
        "requested_theme": case_type,
    }

def _fallback(area: str, case_type: str, include_mp: bool, jury: bool) -> dict:
    design = _random_design(area, case_type, jury)
    rng = random.SystemRandom()
    theme = design["themes"][0]
    title_prefix = {
        "consumer": "Ação consumerista",
        "civil": "Ação de responsabilidade civil",
        "labor": "Reclamação trabalhista",
        "criminal": "Ação penal",
    }[area]
    title = f"{title_prefix}: {theme.capitalize()}"
    plaintiff_names = ["Mariana Alves", "Rafael Teixeira", "Camila Duarte", "André Martins", "Juliana Ribeiro", "Lucas Ferreira"]
    defendants = ["Alvorada Serviços Ltda.", "Nova Horizonte Comércio S.A.", "Grupo Central Brasil Ltda.", "Empresa Monte Azul S.A.", "Pereira & Filhos Ltda."]
    if area == "criminal":
        plaintiff = "Ministério Público"
        defendant = rng.choice(["Eduardo Mendes", "Carlos Henrique Souza", "Felipe Martins", "João Victor Almeida"])
    else:
        plaintiff = rng.choice(plaintiff_names)
        defendant = rng.choice(defendants)
    return {
        "title": title,
        "plaintiff": plaintiff,
        "defendant": defendant,
        "facts": (
            f"Caso fictício baseado em um cenário de {theme}. "
            f"O litígio envolve {design['counterparties']}. "
            f"Durante os fatos, {design['patterns'][0]}, {design['patterns'][1]} e {design['patterns'][2]}. "
            f"Também se discute que {design['twists'][0]}, {design['twists'][1]} e {design['twists'][2]}."
        ),
        "legal_issue": "A controvérsia deverá ser delimitada pela prova produzida, pelas teses das partes e pelo rito aplicável.",
        "evidence": ["documentos do negócio ou da ocorrência", "comunicações entre as partes", "depoimentos", "eventual prova técnica"],
        "witnesses": rng.randint(2, 5),
        "expert_needed": area in {"consumer", "civil", "labor", "criminal"} and rng.random() > 0.25,
        "include_mp": include_mp or (area == "criminal" and rng.random() > 0.2),
        "jury": bool(jury and area == "criminal"),
        "procedure": design["procedure_hint"],
    }

def _parse(text: str) -> dict:
    raw = text.strip().replace("```json", "", 1).replace("```", "", 1).strip()
    data = json.loads(raw)
    required = ("title", "plaintiff", "defendant", "facts", "legal_issue", "evidence", "witnesses", "expert_needed", "include_mp", "jury", "procedure")
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Resposta do gerador sem campos: {', '.join(missing)}")
    return data

def generate_case(area: str, case_type: str, include_mp: bool, jury: bool, provider: AIProvider | None = None) -> dict:
    active = provider or get_provider()
    if active.__class__.__name__ == "LocalFallbackProvider":
        return _fallback(area, case_type, include_mp, jury)

    design = _random_design(area, case_type, jury)
    prompt = f"""
Crie UM processo judicial brasileiro completamente fictício para uma simulação educacional.

ÁREA: {area}
PREFERÊNCIA DO USUÁRIO: {case_type}
MP SOLICITADO: {include_mp}
JÚRI SOLICITADO: {jury}

VOCÊ RECEBEU UM PROJETO DE ALEATORIEDADE. USE-O PARA EVITAR REPETIÇÃO:
- Temas possíveis escolhidos agora: {design['themes']}
- Combinações de fatos: {design['patterns']}
- Perfil das partes: {design['counterparties']}
- Elementos de surpresa: {design['twists']}
- Rito sugerido: {design['procedure_hint']}
- Semente única da execução: {design['nonce']}

REGRAS DE DIVERSIDADE:
1. NÃO reutilize o modelo de casos comuns de "produto com defeito", "cobrança indevida", "horas extras" ou "furto" apenas trocando nomes.
2. Escolha uma combinação substantivamente diferente dentro da área. Varie fatos, relação jurídica, causa do conflito, tipo de prova, posição das partes, cenário e consequência.
3. Misture elementos inesperados, mas juridicamente plausíveis: conflitos digitais, vizinhança, contratos, sucessões, responsabilidade civil, família, administração pública, saúde, seguros, locação, propriedade, trânsito, provas técnicas, cadeia de custódia, entre outros compatíveis com a área.
4. Crie entre 2 e 6 testemunhas quando fizer sentido e use ao menos uma prova potencialmente controvertida.
5. Quando couber, introduza uma questão processual realista (competência, legitimidade, prescrição/decadência, nulidade, admissibilidade, ônus da prova, conexão, impugnação de documento etc.), mas não invente dispositivos legais específicos.
6. Os nomes, empresas, endereços, números e datas devem ser fictícios. Não copie nomes de pessoas reais.
7. Não reproduza um processo real, uma decisão real ou uma ementa real. Use referências públicas somente como inspiração temática.

IMPORTANTE SOBRE PESQUISA:
O conteúdo deve ser inspirado na variedade de assuntos do Judiciário brasileiro e em padrões públicos de litigiosidade, sem reproduzir processos reais. Não cite Jusbrasil, CNJ, tribunais ou URLs dentro do caso.

Retorne SOMENTE JSON válido, sem markdown, com exatamente estes campos:
title, plaintiff, defendant, facts, legal_issue, evidence (array de strings), witnesses (integer entre 2 e 6), expert_needed (boolean), include_mp (boolean), jury (boolean), procedure.
"""
    response = active.generate(
        system=(
            "Você é o gerador de casos de um simulador educacional de direito brasileiro. "
            "Seu principal objetivo é produzir casos variados, plausíveis e concretos. "
            "Priorize diversidade substantiva entre execuções. Nunca copie ou reproduza processo real."
        ),
        prompt=prompt,
    )
    try:
        data = _parse(response.text)
        # Respect hard constraints selected by the user/interface.
        data["jury"] = bool(data.get("jury") and area == "criminal" and jury)
        data["include_mp"] = bool(data.get("include_mp") or (area == "criminal" and include_mp))
        return data
    except Exception as exc:
        raise RuntimeError(f"Falha ao interpretar o caso gerado pela IA: {exc}") from exc
