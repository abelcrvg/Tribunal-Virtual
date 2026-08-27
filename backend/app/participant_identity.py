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
    names={UserRole.PLAINTIFF_ATTORNEY:"Advogado da parte autora",UserRole.DEFENSE_ATTORNEY:"Advogado da parte ré",UserRole.PROSECUTOR:"Representante do Ministério Público",UserRole.JUDGE:"Magistrado da sessão",UserRole.JUROR:"Membro do conselho de sentença"}
    return UserIdentity(user_id,names.get(role,"Observador"),role)
