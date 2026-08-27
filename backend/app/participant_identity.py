from dataclasses import dataclass
from .courtroom import UserRole

@dataclass(frozen=True)
class UserIdentity:
    user_id: str
    display_name: str
    controlled_role: UserRole
    is_human: bool = True

@dataclass(frozen=True)
class AgentIdentity:
    agent_id: str
    display_name: str
    role: UserRole
    is_human: bool = False

def build_user_identity(user_id: str, role: UserRole) -> UserIdentity:
    names={
        UserRole.JUDGE:"Magistrado da sessão",UserRole.PLAINTIFF:"Parte autora",UserRole.DEFENDANT:"Parte ré",
        UserRole.PLAINTIFF_ATTORNEY:"Advogado da parte autora",UserRole.DEFENSE_ATTORNEY:"Advogado da parte ré",
        UserRole.PROSECUTOR:"Representante do Ministério Público",UserRole.LEGAL_RESEARCHER:"Pesquisador jurídico",
        UserRole.WITNESS:"Testemunha",UserRole.EXPERT:"Perito judicial",UserRole.JUROR:"Membro do conselho de sentença",
        UserRole.CLERK:"Servidor da secretaria",
    }
    return UserIdentity(user_id,names.get(role,"Participante da simulação"),role)
