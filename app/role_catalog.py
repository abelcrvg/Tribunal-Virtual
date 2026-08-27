from dataclasses import dataclass

@dataclass(frozen=True)
class RoleDefinition:
    key: str
    label: str
    category: str
    description: str

ROLES = (
    RoleDefinition("judge", "Juiz(a)", "Magistratura", "Conduz a audiência e decide questões processuais."),
    RoleDefinition("prosecutor", "Promotor(a) de Justiça", "Acusação", "Atua pelo Ministério Público quando sua intervenção for cabível."),
    RoleDefinition("prosecutor_assistant", "Assistente de Acusação", "Acusação", "Atua em apoio à acusação nos processos em que for cabível."),
    RoleDefinition("plaintiff_lawyer", "Advogado(a) do Autor", "Advocacia", "Representa a parte autora."),
    RoleDefinition("defendant_lawyer", "Advogado(a) do Réu", "Advocacia", "Representa a parte ré."),
    RoleDefinition("public_defender", "Defensor(a) Público(a)", "Defesa", "Atua na defesa técnica quando cabível."),
    RoleDefinition("plaintiff", "Autor(a)", "Partes", "Parte que formula a pretensão."),
    RoleDefinition("defendant", "Réu/Ré", "Partes", "Parte contra quem a pretensão é dirigida."),
    RoleDefinition("victim", "Vítima", "Partes", "Participa como vítima quando o caso possuir essa figura processual."),
    RoleDefinition("witness", "Testemunha", "Prova", "Presta depoimento sobre fatos que presenciou ou conhece."),
    RoleDefinition("expert", "Perito(a) Judicial", "Prova", "Produz ou esclarece prova técnica."),
    RoleDefinition("technical_assistant", "Assistente Técnico", "Prova", "Atua tecnicamente em apoio a uma das partes."),
    RoleDefinition("juror", "Jurador(a)", "Tribunal do Júri", "Integra o Conselho de Sentença quando houver Júri."),
    RoleDefinition("clerk", "Servidor(a) da Secretaria", "Apoio", "Registra e pratica atos de secretaria."),
    RoleDefinition("bailiff", "Oficial(a) de Justiça", "Apoio", "Cumpre atos de comunicação e diligências judiciais."),
    RoleDefinition("appeal_judge", "Desembargador(a)", "2ª Instância", "Atua no julgamento de recursos em tribunal."),
)

ROLE_MAP = {role.key: role for role in ROLES}

def get_roles():
    return [role.__dict__ for role in ROLES]
