from dataclasses import dataclass
from enum import Enum

class Instance(str, Enum):
    FIRST="first"; SECOND="second"; STJ="stj"; STF="stf"
class UserRole(str, Enum):
    JUDGE="judge"; PLAINTIFF_ATTORNEY="plaintiff_attorney"; DEFENSE_ATTORNEY="defense_attorney"; PROSECUTOR="prosecutor"; LEGAL_RESEARCHER="legal_researcher"; WITNESS="witness"; EXPERT="expert"; JUROR="juror"
@dataclass(frozen=True)
class CourtroomParticipant:
    id:str; name:str; title:str; role:UserRole; profession:str="Participante jurídico"; active:bool=True; fictional:bool=True
_FIRST_NAMES=["Helena","Rafael","Mariana","André","Camila","Marcelo","Beatriz","Ricardo","Juliana","Gustavo","Fernanda","Eduardo"]
_LAST_NAMES=["Duarte","Monteiro","Freitas","Vasconcelos","Nogueira","Almeida","Barros","Mendes","Carvalho","Ribeiro","Teixeira","Castro"]
_PROF={UserRole.JUDGE:"Magistratura",UserRole.PLAINTIFF_ATTORNEY:"Advocacia",UserRole.DEFENSE_ATTORNEY:"Advocacia",UserRole.PROSECUTOR:"Ministério Público",UserRole.LEGAL_RESEARCHER:"Pesquisa jurídica",UserRole.WITNESS:"Testemunha",UserRole.EXPERT:"Perícia judicial",UserRole.JUROR:"Conselho de Sentença"}
def build_courtroom(*,include_mp=False,jury=False,instance=Instance.FIRST):
    names=(f"{f} {l}" for f in _FIRST_NAMES for l in _LAST_NAMES); used=set()
    def make(role,title):
        name=next(n for n in names if n not in used); used.add(name); return CourtroomParticipant(f"{role.value}_{len(used)}",name,title,role,_PROF[role])
    result=[make(UserRole.JUDGE,"Juiz de Direito"),make(UserRole.PLAINTIFF_ATTORNEY,"Advogado(a) do Autor"),make(UserRole.DEFENSE_ATTORNEY,"Advogado(a) do Réu"),make(UserRole.LEGAL_RESEARCHER,"Pesquisador(a) Jurídico(a)")]
    if include_mp: result.append(make(UserRole.PROSECUTOR,"Promotor(a) de Justiça"))
    if jury:
        for _ in range(7): result.append(make(UserRole.JUROR,"Jurados do Conselho de Sentença"))
    return result
class InterventionAssessment(str,Enum):
    IRRELEVANT="irrelevant"; PERTINENT="pertinent"; DECISIVE="decisive"; ABUSIVE="abusive"
@dataclass(frozen=True)
class CourtroomDecision:
    assessment:InterventionAssessment; allowed:bool; judge_response:str; requires_record:bool; reason:str
def assess_intervention(*,role,turn_role,content):
    text=content.strip().lower()
    if not text:return CourtroomDecision(InterventionAssessment.IRRELEVANT,False,"A intervenção não contém conteúdo suficiente para análise.",False,"mensagem vazia")
    if any(x in text for x in ("idiota","cala a boca","vai se ferrar","filho da","otário","otaria")):return CourtroomDecision(InterventionAssessment.ABUSIVE,False,"A parte deve manter o respeito e a urbanidade.",False,"linguagem incompatível")
    terms=("documento","prova","testemunha","contrato","laudo","artigo","lei","fato","depoimento","contradi","omiss","processo","prazo","competência","nulidade","evidência","perícia")
    relevant=any(x in text for x in terms) or len(text)>=160
    if turn_role==role:return CourtroomDecision(InterventionAssessment.PERTINENT if relevant else InterventionAssessment.IRRELEVANT,True,"A palavra está com a parte. Prossiga com sua manifestação.",relevant,"dentro da vez")
    if relevant:
        decisive=any(x in text for x in ("contradiz","prova que","demonstra que","documento original","falsidade","incompatível","erro material","omissão relevante","nulidade")) or len(text)>=320
        return CourtroomDecision(InterventionAssessment.DECISIVE if decisive else InterventionAssessment.PERTINENT,True,"A intervenção fora da ordem apresenta pertinência com a controvérsia. A palavra é concedida para esclarecimento e a manifestação será registrada.",True,"exceção por relevância")
    return CourtroomDecision(InterventionAssessment.IRRELEVANT,False,"A palavra permanece com quem está se manifestando. A intervenção não apresenta pertinência suficiente neste momento.",False,"fora da vez")
