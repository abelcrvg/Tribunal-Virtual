from dataclasses import dataclass
import random


@dataclass(frozen=True)
class Character:
    name: str
    title: str
    profession: str
    role: str
    fictional: bool = True


FIRST_NAMES = [
    "Helena", "Rafael", "Mariana", "André", "Camila", "Marcelo",
    "Beatriz", "Ricardo", "Juliana", "Gustavo", "Fernanda", "Eduardo",
]
LAST_NAMES = [
    "Duarte", "Monteiro", "Freitas", "Vasconcelos", "Nogueira", "Almeida",
    "Barros", "Mendes", "Carvalho", "Ribeiro", "Teixeira", "Castro",
]


def _name(rng: random.Random, used: set[str]) -> str:
    available = [f"{first} {last}" for first in FIRST_NAMES for last in LAST_NAMES if f"{first} {last}" not in used]
    if not available:
        raise RuntimeError("Não foi possível gerar um nome fictício único")
    return rng.choice(available)


def build_characters(seed: int | None = None, include_mp: bool = False) -> list[Character]:
    rng = random.Random(seed)
    used: set[str] = set()

    def add(title: str, profession: str, role: str) -> Character:
        name = _name(rng, used)
        used.add(name)
        return Character(name, title, profession, role)

    characters = [
        add("Dr.", "Juiz de Direito", "magistrate"),
        add("Dra.", "Advogada", "plaintiff_attorney"),
        add("Dr.", "Advogado", "defense_attorney"),
        add("Dra.", "Pesquisadora Jurídica", "legal_researcher"),
    ]

    if include_mp:
        characters.insert(3, add("Dr.", "Promotor de Justiça", "public_prosecutor"))

    return characters
