from uuid import UUID
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .agent_orchestrator import build_agent_instruction, register_agent_reply
from .case_store import store
from .case_memory import get_case_memory
from .court_session import CourtPhase, CourtSession, MessageKind
from .courtroom import Instance, UserRole, build_courtroom, assess_intervention
from .hearing_orchestrator import run_next_agent
from .hearing_rules import decide_intervention, InterventionDisposition
from .judicial_review import review_intervention
from .participant_identity import build_user_identity
from .processes import get_process
router=APIRouter(prefix="/api/v1/processes/{process_id}/courtroom",tags=["courtroom"])
_sessions:dict[str,CourtSession]={}; _identities={}
class SessionCreate(BaseModel): role:UserRole; user_id:str=Field(default="local-user",min_length=1,max_length=120)
class MessageCreate(BaseModel): content:str=Field(min_length=1,max_length=10000)
class AgentCreate(BaseModel): role:UserRole; sender:str=Field(min_length=2,max_length=120); content:str=Field(min_length=1,max_length=10000)
class AppealCreate(BaseModel): type:str=Field(min_length=2,max_length=100); reason:str=Field(min_length=10,max_length=5000)
def _session(pid:UUID,role:UserRole):
    s=_sessions.get(f"{pid}:{role.value}")
    if s is None: raise HTTPException(404,"Sessão não encontrada")
    return s
@router.post("/session")
def create_session(process_id:UUID,data:SessionCreate):
    p=get_process(process_id)
    if p is None: raise HTTPException(404,"Processo não encontrado")
    key=f"{process_id}:{data.role.value}"; s=CourtSession(id=key,process_id=str(process_id),user_role=data.role); _identities[key]=build_user_identity(data.user_id,data.role)
    judge=next((x for x in build_courtroom(include_mp=p.include_mp,jury=p.area.value=="criminal",instance=Instance.FIRST) if x.role==UserRole.JUDGE),None); name=judge.name if judge else "Magistrado"
    s.add_message(name,MessageKind.RULING,"Declaro aberta a sessão. As partes deverão observar a ordem de fala e a urbanidade.",UserRole.JUDGE); s.add_message("Sistema",MessageKind.SYSTEM,f"Sessão iniciada para {_identities[key].display_name}. O debate é livre; intervenções relevantes fora da vez poderão ser apreciadas.")
    _sessions[key]=s; store.add(str(process_id),"session_opened",name,"Sessão aberta","pertinent")
    return {"session_id":key,"identity":_identities[key].__dict__,"role":data.role,"instance":s.instance,"phase":s.phase,"allowed_roles":list(s.allowed_roles),"messages":s.messages}
@router.get("/participants")
def participants(process_id:UUID,instance:Instance=Instance.FIRST):
    p=get_process(process_id)
    if p is None: raise HTTPException(404,"Processo não encontrado")
    return {"instance":instance,"participants":[x.__dict__ for x in build_courtroom(include_mp=p.include_mp,jury=p.area.value=="criminal",instance=instance)]}
@router.get("/session/{role}")
def get_session(process_id:UUID,role:UserRole):
    s=_session(process_id,role); identity=_identities.get(s.id); return {"session_id":s.id,"identity":identity.__dict__ if identity else None,"role":s.user_role,"instance":s.instance,"phase":s.phase,"allowed_roles":list(s.allowed_roles),"messages":s.messages,"appeals":s.appeals}
@router.post("/session/{role}/messages")
def send_message(process_id:UUID,role:UserRole,data:MessageCreate):
    s=_session(process_id,role); p=get_process(process_id); turn=next(iter(s.allowed_roles)).value if s.allowed_roles else "none"; preliminary=assess_intervention(role=role.value,turn_role=turn,content=data.content)
    facts=get_case_memory(str(process_id)).context(); history=[str(x) for x in s.messages]; judicial=review_intervention(content=data.content,assessment=preliminary.assessment.value,facts=facts,history=history,phase=s.phase.value)
    allowed=role in s.allowed_roles
    if not allowed and judicial.action=="ADVERTIR":
        m=s.reprimand(); store.add(str(process_id),"reprimand","Magistrado",judicial.explanation,"normal"); return {"accepted":False,"message":m,"reason":"out_of_turn","judicial_review":judicial.__dict__,"allowed_roles":list(s.allowed_roles)}
    identity=_identities.get(s.id); sender=identity.display_name if identity else role.value; m=s.add_message(sender,MessageKind.USER,data.content,role,preliminary.assessment.value); store.add(str(process_id),"hearing_message",sender,data.content,preliminary.assessment.value)
    if not allowed:
        r=s.add_message("Magistrado",MessageKind.RULING,judicial.explanation,UserRole.JUDGE,preliminary.assessment.value); return {"accepted":True,"message":m,"ruling":r,"exception":True,"judicial_review":judicial.__dict__,"phase":s.phase,"allowed_roles":list(s.allowed_roles)}
    s.accept_turn(); return {"accepted":True,"message":m,"phase":s.phase,"allowed_roles":list(s.allowed_roles),"assessment":preliminary.assessment.value}
@router.post("/session/{role}/agents")
def agent_message(process_id:UUID,role:UserRole,data:AgentCreate):
    s=_session(process_id,role)
    if data.role not in s.allowed_roles: raise HTTPException(400,f"O papel {data.role.value} não possui a palavra nesta fase.")
    context=get_case_memory(str(process_id)).context(); instruction=build_agent_instruction(s,data.role,context); reply=register_agent_reply(s,data.role,data.sender,data.content); s.accept_turn(); return {"message":reply.__dict__,"instruction_context":instruction,"phase":s.phase,"allowed_roles":list(s.allowed_roles)}
@router.post("/session/{role}/agents/next")
def automatic_agent_turn(process_id:UUID,role:UserRole):
    s=_session(process_id,role); p=get_process(process_id)
    if p is None: raise HTTPException(404,"Processo não encontrado")
    try: result=run_next_agent(p,s)
    except Exception as exc: raise HTTPException(502,f"Falha no agente de IA: {exc}") from exc
    if result is None: return {"advanced":False,"phase":s.phase,"message":"Não há outro agente automático configurado para esta fase."}
    return {"advanced":True,"phase":s.phase,"agent":result}
@router.post("/session/{role}/advance")
def advance_phase(process_id:UUID,role:UserRole):
    s=_session(process_id,role); order=list(CourtPhase); i=order.index(s.phase)
    if i>=len(order)-1: raise HTTPException(400,"A audiência já foi encerrada.")
    s.phase=order[i+1]; s.turn_index=0; content=f"Passamos à fase: {s.phase.value}."; store.add(str(process_id),"phase_change","Magistrado",content,"pertinent"); m=s.add_message("Magistrado",MessageKind.RULING,content,UserRole.JUDGE); return {"phase":s.phase,"allowed_roles":list(s.allowed_roles),"message":m}
@router.post("/session/{role}/appeals")
def file_appeal(process_id:UUID,role:UserRole,data:AppealCreate):
    s=_session(process_id,role)
    try: appeal=s.file_appeal(data.type,data.reason)
    except (PermissionError,ValueError) as exc: raise HTTPException(400,str(exc)) from exc
    store.add(str(process_id),"appeal_filed",role.value,data.reason,"pertinent"); return {"accepted":True,"appeal":appeal,"message":"Recurso protocolado para análise de admissibilidade pelo órgão competente."}
