from dataclasses import dataclass

@dataclass(frozen=True)
class JudgeAction:
    action:str
    text:str

def action_for(classification:str)->JudgeAction:
    if classification=="decisive": return JudgeAction("grant_floor","A intervenção possui relevância elevada; o juízo concede a palavra e determina seu registro nos autos.")
    if classification=="pertinent": return JudgeAction("grant_floor","A intervenção é pertinente à controvérsia; o juízo concede a palavra e determina seu registro.")
    return JudgeAction("reprimand","A intervenção não apresenta pertinência suficiente para alterar a ordem da audiência; o juízo adverte a parte e mantém a ordem dos trabalhos.")
