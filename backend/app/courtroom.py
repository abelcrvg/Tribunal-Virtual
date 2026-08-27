from dataclasses import dataclass
from enum import Enum
from uuid import uuid4


class Instance(str, Enum):
    FIRST = "first_instance"
    SECOND = "second_instance"
    STJ = "stj"
    STF = "stf"


class UserRole(str, Enum):
    SPECTATOR = "spectator"
    PLAINTIFF_ATTORNEY = "plaintiff_attorney"
    DEFENSE_ATTORNEY = "defense_attorney"
    PROSECUTOR = "prosecutor"
    JUDGE = "judge"
    JUROR = "juror"


class ParticipantType(str, Enum):
    JUDGE = "judge"
    ATTORNEY = "attorney"
    PROSECUTOR = "prosecutor"
    DEFENDANT = "defendant"
    PLAINTIFF = "plaintiff"
    WITNESS = "witness"
    EXPERT = "expert"
    CLERK = "clerk"
    JUROR = "juror"


@dataclass(frozen=True)
class Participant:
    id: str
    name: str
    role: ParticipantType
    side: str | None = None
    fictional: bool = True


def build_courtroom(include_mp: bool = False, jury: bool = False) -> list[Participant]:
    participants = [
        Participant(str(uuid4()), "Magistrado responsável", ParticipantType.JUDGE),
        Participant(str(uuid4()), "Representante do autor", ParticipantType.ATTORNEY, "plaintiff"),
        Participant(str(uuid4()), "Representante do réu", ParticipantType.ATTORNEY, "defense"),
        Participant(str(uuid4()), "Servidor da secretaria", ParticipantType.CLERK),
        Participant(str(uuid4()), "Testemunha da parte autora", ParticipantType.WITNESS, "plaintiff"),
        Participant(str(uuid4()), "Testemunha da parte ré", ParticipantType.WITNESS, "defense"),
        Participant(str(uuid4()), "Perito judicial", ParticipantType.EXPERT),
    ]
    if include_mp:
        participants.insert(3, Participant(str(uuid4()), "Promotor de Justiça", ParticipantType.PROSECUTOR))
    if jury:
        participants.extend(
            Participant(str(uuid4()), f"Juradoo {i:02d}", ParticipantType.JUROR)
            for i in range(1, 8)
        )
    return participants
