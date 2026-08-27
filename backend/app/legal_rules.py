from dataclasses import dataclass
from .models import CaseArea

@dataclass(frozen=True)
class RuleSet:
    area: CaseArea
    label: str
    sources: tuple[str, ...]

RULESETS={
    CaseArea.CIVIL: RuleSet(CaseArea.CIVIL,"Direito Civil",("Código Civil (Lei 10.406/2002)","Código de Processo Civil (Lei 13.105/2015)")),
    CaseArea.CONSUMER: RuleSet(CaseArea.CONSUMER,"Direito do Consumidor",("Código de Defesa do Consumidor (Lei 8.078/1990)","Código de Processo Civil (Lei 13.105/2015)")),
    CaseArea.LABOR: RuleSet(CaseArea.LABOR,"Direito do Trabalho",("CLT (Decreto-Lei 5.452/1943)","Constituição Federal", "Código de Processo Civil, quando aplicável")),
    CaseArea.CRIMINAL: RuleSet(CaseArea.CRIMINAL,"Direito Penal",("Código Penal (Decreto-Lei 2.848/1940)","Código de Processo Penal (Decreto-Lei 3.689/1941)","Constituição Federal")),
}

def rules_for(area: CaseArea) -> RuleSet:
    return RULESETS[area]
