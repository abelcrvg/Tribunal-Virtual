from dataclasses import dataclass
from .court_session import Appeal, AppealStatus

@dataclass(frozen=True)
class AppealReview:
    admitted: bool
    reason: str
    reviewing_body: str

def review_appeal(appeal: Appeal) -> AppealReview:
    if not appeal.reason.strip():
        return AppealReview(False,"O recurso não apresenta fundamentação suficiente para a simulação.","Órgão de admissibilidade")
    if appeal.target_instance.value == "second":
        body="Câmara julgadora do Tribunal de Justiça"
    elif appeal.target_instance.value == "stj":
        body="Turma do Superior Tribunal de Justiça"
    else:
        body="Turma do Supremo Tribunal Federal"
    return AppealReview(True,"Recurso admitido para julgamento simulado, sem antecipar o mérito.",body)
