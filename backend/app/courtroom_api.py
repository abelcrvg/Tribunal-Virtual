from datetime import timezone
import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .agent_orchestrator import build_agent_instruction, register_agent_reply
from .case_store import store
from .case_memory import get_case_memory
from .court_session import CourtPhase, CourtSession, MessageKind, ChatMessage
from .courtroom import Instance, UserRole, build_courtroom, assess_intervention
from .database import get_db
from .db_models import ProcessEventDB, ProcessSessionDB
from .hearing_orchestrator import run_next_agent, next_agent_turn, peek_turn
from .judicial_review import review_intervention
from .participant_identity import build_user_identity
from .persistence import get_process_db

router=APIRouter(prefix="/api/v1/processes/{process_id}/courtroom",tags=["courtroom"])
_sessions:dict[str,CourtSession]={}; _identities={}

class SessionCreate(BaseModel):
    role:UserRole
    user_id:str=Field(default="local-user",min_length=1,max_length=120)
class MessageCreate(BaseModel): content:str=Field(min_length=1,max_length=10000)
class AgentCreate(BaseModel):
    role:UserRole; sender:str=Field(min_length=2,max_length=120); content:str=Field(min_length=1,max_length=10000)
class AppealCreate(BaseModel):
    type:str=Field(min_length=2,max_length=100); reason:str=Field(min_length=10,max_length=5000)

def _process(pid:UUID,db:Session):
    process=get_process_db(db,str(pid))
    if process is None: raise HTTPException(404,"Processo não encontrado")
    return process

def _persist_message(db:Session,process_id:str,message:ChatMessage):
    payload={"id":message.id,"sender":message.sender,"kind":message.kind.value,"content":message.content,"role":message.role.value if message.role else None,"assessment":message.assessment,"created_at":message.created_at.isoformat()}
    db.add(ProcessEventDB(process_id=process_id,event_type="court_message",actor=message.sender,content=json.dumps(payload,ensure_ascii=False),assessment=message.assessment or "normal",created_at=message.created_at.astimezone(timezone.utc).replace(tzinfo=None)))
    db.commit()

def _persist_phase(db:Session,process_id:str,phase:CourtPhase):
    db.add(ProcessEventDB(process_id=process_id,event_type="phase_change",actor="Magistrado",content=f"Passamos à fase: {phase.value}.",assessment="pertinent"))
    db.commit()

def _restore_session(pid:UUID,role:UserRole,db:Session)->CourtSession|None:
    key=f"{pid}:{role.value}"
    events=db.scalars(select(ProcessEventDB).where(ProcessEventDB.process_id==str(pid),ProcessEventDB.event_type.in_(["court_message","phase_change"])).order_by(ProcessEventDB.created_at,ProcessEventDB.id)).all()
    if not events: return None
    s=CourtSession(id=key,process_id=str(pid),user_role=role)
    for event in events:
        if event.event_type=="phase_change":
            try: s.phase=CourtPhase(event.content.rsplit(": ",1)[-1].rstrip(".")); s.turn_index=0
            except ValueError: pass
            continue
        try: payload=json.loads(event.content)
        except (TypeError,ValueError): continue
        try: kind=MessageKind(payload["kind"]); msg_role=UserRole(payload["role"]) if payload.get("role") else None
        except (KeyError,ValueError): continue
        created_at=event.created_at.replace(tzinfo=timezone.utc) if event.created_at else None
        if payload.get("created_at"):
            try: created_at=__import__("datetime").datetime.fromisoformat(payload["created_at"].replace("Z","+00:00"))
            except ValueError: pass
        message=ChatMessage(payload.get("id",event.id),payload.get("sender",event.actor),kind,payload.get("content",event.content),msg_role,payload.get("assessment"),created_at or __import__("datetime").datetime.now(timezone.utc))
        s.messages.append(message)
        if kind in {MessageKind.USER,MessageKind.AGENT} and msg_role in s.allowed_roles: s.accept_turn()
        elif kind==MessageKind.RULING and msg_role==UserRole.JUDGE and payload.get("assessment")=="procedural": s.reprimands+=1; s.consecutive_invalid=min(s.consecutive_invalid+1,3)
    return s

def _session(pid:UUID,role:UserRole,db:Session):
    key=f"{pid}:{role.value}"; s=_sessions.get(key)
    if s is None:
        s=_restore_session(pid,role,db)
        if s is not None:
            _sessions[key]=s; locked=db.get(ProcessSessionDB,str(pid)); saved_user_id=locked.user_id if locked is not None and locked.user_id else "local-user"; _identities[key]=build_user_identity(saved_user_id,role)
    if s is None: raise HTTPException(404,"Sessão não encontrada")
    return s

def _advance_phase(db:Session,s:CourtSession,process_id:str):
    order=list(CourtPhase); i=order.index(s.phase)
    if i>=len(order)-1: return False
    s.phase=order[i+1]; s.turn_index=0
    content=f"Passamos à fase: {s.phase.value}."
    store.add(process_id,"phase_change","Magistrado",content,"pertinent")
    m=s.add_message("Magistrado",MessageKind.RULING,content,UserRole.JUDGE); _persist_message(db,process_id,m); _persist_phase(db,process_id,s.phase)
    return True

def _append_ai_result(db:Session,s:CourtSession,process_id:str,result):
    if not result or not result.get("content"):
        return None
    role_value=result.get("role")
    try: msg_role=UserRole(role_value) if role_value else None
    except ValueError: msg_role=None
    msg=s.add_message(result.get("name") or result.get("agent") or "Participante jurídico",MessageKind.AGENT,result["content"],msg_role)
    _persist_message(db,process_id,msg)
    return msg

def _run_one_agent(db:Session,s:CourtSession,process_id:str,process):
    result=run_next_agent(process and process, s)
    return _append_ai_result(db,s,process_id,result) if result else None

@router.post("/session")
def create_session(process_id:UUID,data:SessionCreate,db:Session=Depends(get_db)):
    p=_process(process_id,db); locked=db.get(ProcessSessionDB,str(process_id))
    if locked is not None and locked.role!=data.role.value: raise HTTPException(409,detail=f"O papel desta simulação já foi definido como {locked.role}. Não é possível trocá-lo depois do início do julgamento.")
    if locked is None: db.add(ProcessSessionDB(process_id=str(process_id),user_id=data.user_id,role=data.role.value)); db.commit()
    key=f"{process_id}:{data.role.value}"; existing=_sessions.get(key) or _restore_session(process_id,data.role,db)
    if existing is not None:
        _sessions[key]=existing; _identities.setdefault(key,build_user_identity(data.user_id,data.role)); return {"session_id":key,"identity":_identities[key].__dict__,"role":data.role,"instance":existing.instance,"phase":existing.phase,"allowed_roles":list(existing.allowed_roles),"messages":existing.messages}
    s=CourtSession(id=key,process_id=str(process_id),user_role=data.role); _identities[key]=build_user_identity(data.user_id,data.role)
    judge=next((x for x in build_courtroom(include_mp=p.include_mp,jury=p.jury,instance=Instance.FIRST) if x.role==UserRole.JUDGE),None); name=judge.name if judge else "Magistrado"
    participant_name=_identities[key].display_name
    role_label={UserRole.JUDGE:"Magistrado",UserRole.PLAINTIFF:"Parte autora",UserRole.DEFENDANT:"Parte ré",UserRole.PLAINTIFF_ATTORNEY:"Advogado(a) do Autor",UserRole.DEFENSE_ATTORNEY:"Advogado(a) do Réu",UserRole.PROSECUTOR:"Promotor(a) de Justiça",UserRole.LEGAL_RESEARCHER:"Pesquisador(a) Jurídico(a)",UserRole.WITNESS:"Testemunha",UserRole.EXPERT:"Perito(a) Judicial",UserRole.JUROR:"Jurado(a)",UserRole.CLERK:"Servidor(a) da Secretaria",UserRole.PUBLIC_DEFENDER:"Defensor(a) Público(a)",UserRole.PROSECUTOR_ASSISTANT:"Assistente de Acusação",UserRole.TECHNICAL_ASSISTANT:"Assistente Técnico",UserRole.VICTIM:"Vítima",UserRole.BAILIFF:"Oficial(a) de Justiça",UserRole.APPEAL_JUDGE:"Desembargador(a)"}.get(data.role,data.role.value)
    opening=f"Declaro aberta a sessão. O participante {participant_name} atuará nesta simulação na qualidade de {role_label}. As partes deverão observar a ordem de fala e a urbanidade."
    m=s.add_message(name,MessageKind.RULING,opening,UserRole.JUDGE); _persist_message(db,str(process_id),m)
    s.turn_index=1
    m=s.add_message("Sistema",MessageKind.SYSTEM,f"Participante da sessão: {participant_name} · {role_label}. O debate é livre; intervenções relevantes fora da vez poderão ser apreciadas."); _persist_message(db,str(process_id),m); _sessions[key]=s; store.add(str(process_id),"session_opened",name,"Sessão aberta","pertinent")
    return {"session_id":key,"identity":_identities[key].__dict__,"role":data.role,"instance":s.instance,"phase":s.phase,"allowed_roles":list(s.allowed_roles),"messages":s.messages}

@router.get("/participants")
def participants(process_id:UUID,instance:Instance=Instance.FIRST,db:Session=Depends(get_db)):
    p=_process(process_id,db); return {"instance":instance,"participants":[x.__dict__ for x in build_courtroom(include_mp=p.include_mp,jury=p.jury,instance=instance)]}

@router.get("/session/{role}")
def get_session(process_id:UUID,role:UserRole,db:Session=Depends(get_db)):
    locked=db.get(ProcessSessionDB,str(process_id))
    if locked is not None and locked.role!=role.value: raise HTTPException(409,"Esta simulação foi iniciada com outro papel.")
    s=_session(process_id,role,db); identity=_identities.get(s.id); return {"session_id":s.id,"identity":identity.__dict__ if identity else None,"role":s.user_role,"instance":s.instance,"phase":s.phase,"allowed_roles":list(s.allowed_roles),"messages":s.messages,"appeals":s.appeals}

@router.post("/session/{role}/messages")
def send_message(process_id:UUID,role:UserRole,data:MessageCreate,db:Session=Depends(get_db)):
    s=_session(process_id,role,db)
    expected=peek_turn(s); expected_role=expected.role if expected else None
    text=data.content.strip().lower(); normalized=" ".join(text.rstrip("?!., ").split())
    courtesy=normalized in {"posso falar meritissimo","posso falar, meritissimo","posso falar meritíssimo","posso falar, meritíssimo","boa tarde","bom dia","boa noite","olá","ola","ok"}
    if role.value != expected_role and courtesy:
        identity=_identities.get(s.id); sender=identity.display_name if identity else role.value; m=s.add_message(sender,MessageKind.USER,data.content,role,"pertinent"); _persist_message(db,str(process_id),m)
        response="Pode formular sua manifestação, desde que pertinente e respeitada a ordem dos trabalhos." if normalized.startswith("posso falar") else "Registrado. Aguarde a palavra ou utilize a manifestação quando o juízo a conceder."
        r=s.add_message("Magistrado",MessageKind.RULING,response,UserRole.JUDGE,"procedural"); _persist_message(db,str(process_id),r)
        return {"accepted":True,"message":m,"ruling":r,"exception":False,"phase":s.phase,"allowed_roles":list(s.allowed_roles),"expected_role":expected_role}
    preliminary=assess_intervention(role=role.value,turn_role=expected_role or "none",content=data.content); facts=get_case_memory(str(process_id)).context(); history=[str(x) for x in s.messages]; judicial=review_intervention(content=data.content,assessment=preliminary.assessment.value,facts=facts,history=history,phase=s.phase.value)
    allowed=role.value==expected_role
    if not allowed:
        if preliminary.assessment.value in {"pertinent","decisive"}:
            identity=_identities.get(s.id); sender=identity.display_name if identity else role.value; m=s.add_message(sender,MessageKind.USER,data.content,role,preliminary.assessment.value); _persist_message(db,str(process_id),m); r=s.add_message("Magistrado",MessageKind.RULING,"A intervenção foi registrada por sua pertinência, mas a palavra permanece com o participante designado para este ato.",UserRole.JUDGE,preliminary.assessment.value); _persist_message(db,str(process_id),r); return {"accepted":True,"message":m,"ruling":r,"exception":True,"judicial_review":judicial.__dict__,"phase":s.phase,"allowed_roles":list(s.allowed_roles),"expected_role":expected_role}
        m=s.reprimand(); _persist_message(db,str(process_id),m); return {"accepted":False,"message":m,"reason":"out_of_turn","judicial_review":judicial.__dict__,"allowed_roles":list(s.allowed_roles),"expected_role":expected_role}
    identity=_identities.get(s.id); sender=identity.display_name if identity else role.value; m=s.add_message(sender,MessageKind.USER,data.content,role,preliminary.assessment.value); _persist_message(db,str(process_id),m); store.add(str(process_id),"hearing_message",sender,data.content,preliminary.assessment.value); s.accept_turn()
    # A user message is itself the trigger for the next AI intervention.
    process=_process(process_id,db)
    next_turn=next_agent_turn(s)
    ai_message=None
    if next_turn is not None:
        try: ai_message=_run_one_agent(db,s,str(process_id),process)
        except Exception as exc: raise HTTPException(502,f"Falha no agente de IA: {exc}") from exc
    return {"accepted":True,"message":m,"ruling":ai_message,"phase":s.phase,"allowed_roles":list(s.allowed_roles),"assessment":preliminary.assessment.value,"expected_role":expected_role}

@router.post("/session/{role}/agents")
def agent_message(process_id:UUID,role:UserRole,data:AgentCreate,db:Session=Depends(get_db)):
    s=_session(process_id,role,db)
    if data.role not in s.allowed_roles: raise HTTPException(400,f"O papel {data.role.value} não possui a palavra nesta fase.")
    context=get_case_memory(str(process_id)).context(); instruction=build_agent_instruction(s,data.role,context); reply=register_agent_reply(s,data.role,data.sender,data.content); _persist_message(db,str(process_id),reply); s.accept_turn(); return {"message":reply.__dict__,"instruction_context":instruction,"phase":s.phase,"allowed_roles":list(s.allowed_roles)}

@router.post("/session/{role}/agents/next")
def automatic_agent_turn(process_id:UUID,role:UserRole,db:Session=Depends(get_db)):
    s=_session(process_id,role,db); p=_process(process_id,db)
    turn=next_agent_turn(s)
    if turn is None:
        expected=peek_turn(s)
        if expected is not None and expected.role==role.value:
            identity=_identities.get(s.id); msg={"id":"system-await","sender":"Sistema","kind":"system","content":f"A palavra está com {identity.display_name if identity else 'você'}. Faça sua manifestação ou pergunta no campo abaixo."}; return {"advanced":False,"awaiting_user":True,"phase":s.phase,"expected_role":role.value,"message":msg}
        if not _advance_phase(db,s,str(process_id)): return {"advanced":False,"phase":s.phase,"message":"O julgamento já foi encerrado."}
        turn=next_agent_turn(s)
        if turn is None:
            expected=peek_turn(s)
            if expected is not None and expected.role==role.value:
                identity=_identities.get(s.id); msg={"id":"system-await","sender":"Sistema","kind":"system","content":f"A palavra está com {identity.display_name if identity else 'você'}. Faça sua manifestação ou pergunta no campo abaixo."}; return {"advanced":True,"awaiting_user":True,"phase":s.phase,"expected_role":role.value,"message":msg}
            return {"advanced":True,"phase":s.phase,"message":"A fase foi avançada, aguardando o próximo ato."}
    try: msg=_run_one_agent(db,s,str(process_id),p)
    except Exception as exc: raise HTTPException(502,f"Falha no agente de IA: {exc}") from exc
    return {"advanced":True,"phase":s.phase,"agent":msg.__dict__ if msg else None}

@router.post("/session/{role}/advance")
def advance_phase(process_id:UUID,role:UserRole,db:Session=Depends(get_db)):
    s=_session(process_id,role,db)
    if not _advance_phase(db,s,str(process_id)): raise HTTPException(400,"A audiência já foi encerrada.")
    return {"phase":s.phase,"allowed_roles":list(s.allowed_roles),"message":s.messages[-1]}

@router.post("/session/{role}/appeals")
def file_appeal(process_id:UUID,role:UserRole,data:AppealCreate,db:Session=Depends(get_db)):
    s=_session(process_id,role,db)
    try: appeal=s.file_appeal(data.type,data.reason)
    except (PermissionError,ValueError) as exc: raise HTTPException(400,str(exc)) from exc
    store.add(str(process_id),"appeal_filed",role.value,data.reason,"pertinent"); return {"accepted":True,"appeal":appeal,"message":"Recurso protocolado para análise de admissibilidade pelo órgão competente."}
