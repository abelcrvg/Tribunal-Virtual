from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from .agent_registry import AGENTS, agent_for
from .ai_provider import get_provider
from .database import get_db
from .models import Process
from .persistence import get_process_db
from .simulation import run_registered_agent
router=APIRouter(prefix="/api/v1/processes/{process_id}/agents",tags=["agents"])
class AgentRequest(BaseModel): instructions:str=Field(min_length=1,max_length=10000)
def _process(pid:UUID,db:Session)->Process:
    process=get_process_db(db,str(pid))
    if process is None: raise HTTPException(404,"Processo não encontrado")
    return process
@router.get("")
def list_agents(process_id:UUID,db:Session=Depends(get_db)):
    _process(process_id,db)
    return {"agents":[{"role":a.role.value,"name":a.display_name,"phases":a.phase_names} for a in AGENTS]}
@router.post("/{role}")
def invoke_agent(process_id:UUID,role:str,data:AgentRequest,db:Session=Depends(get_db)):
    process=_process(process_id,db)
    if agent_for(role) is None: raise HTTPException(404,"Agente não encontrado")
    try: return run_registered_agent(process,role,data.instructions,get_provider())
    except Exception as exc: raise HTTPException(502,f"Falha no provedor de IA: {exc}") from exc
