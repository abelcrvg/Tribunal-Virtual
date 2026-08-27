from dataclasses import dataclass
from enum import Enum
from random import Random


class ParticipantRole(str, Enum):
    MAGISTRATE = "magistrate"
    PLAINTIFF_ATTORNEY = "plaintiff_attorney"
    DEFENSE_ATTORNEY = "defense_attorney"
    PUBLIC_PROSECUTOR = "public_prosecutor"
    WITNESS = "witness"
    EXPERT = "expert"
    JUROR = "juror"
    CLERK = "clerk"


@dataclass(frozen=True)
class Participant:
    id: str
    name: str
    title: str
    role: ParticipantRole
    active: bool = True
    fictional: bool = True


FIRST = ["Helena", "Rafael", "Mariana", "André", "Camila", "Marcelo", "Beatriz", "Ricardo", "Juliana", "Gustavo", "Fernanda", "Eduardo", "Paulo", "Renata", "Daniel", "Larissa"]
LAST = ["Duarte", "Monteiro", "Freitas", "Vasconcelos", "Nogueira", "Almeida", "Barros", "Mendes", "Carvalho", "Ribeiro", "Teixeira", "Castro", "Moraes", "Pereira"]


def generate_participants(seed: int, include_mp: bool = False, jury: bool = False, witnesses: int = 2, experts: int = 0) -> list[Participant]:
    rng = Random(seed)
    names = iter(f"{f} {l}" for f in FIRST for l in LAST)
    used: set[str] = set()

    def make(role: ParticipantRole, title: str) -> Participant:
        name = next(n for n in names if n not in used)
        used.add(name)
        return Participant(f"{role.value}_{len(used)}", name, title, role)

    result = [
        make(ParticipantRole.MAGISTRATE, "Juiz de Direito"),
        make(ParticipantRole.PLAINTIFF_ATTORNEY, "Advogado(a) do Autor"),
        make(ParticipantRole.DEFENSE_ATTORNEY, "Advogado(a) do Réu"),
        make(ParticipantRole.CLERK, "Servidor(a) da Secretaria"),
    ]
    if include_mp:
        result.append(make(ParticipantRole.PUBLIC_PROSECUTOR, "Promotor(a) de Justiça"))
    for _ in range(max(0, witnesses)):
        result.append(make(ParticipantRole.WITNESS, "Testemunha"))
    for _ in range(max(0, experts)):
        result.append(make(ParticipantRole.EXPERT, "Perito(a)"))
    if jury:
        for _ in range(7):
            result.append(make(ParticipantRole.JUROR, "Jurados do Conselho de Sentença"))
    return result
