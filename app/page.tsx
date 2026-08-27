"use client";

import { useEffect, useState } from "react";
import { Sparkles, Loader2, Send, Users, FileText, Landmark, GitBranch, MessageSquare, Bot, LockKeyhole, Play, LogOut, History, Trash2 } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const SESSION_STORAGE_KEY = "tribunal-virtual-session";
const USER_NAME_KEY = "tribunal-virtual-user-name";
const HISTORY_KEY = "tribunal-virtual-history";
const phaseIds = ["opening","plaintiff","defense","witness_plaintiff","witness_defense","expert","mp","closing","deliberation","judgment","closed"];
const phases = ["Abertura","Autor","Defesa","Testemunhas","Perícia","MP","Alegações","Deliberação","Sentença"];
type Role = "judge"|"plaintiff"|"defendant"|"plaintiff_attorney"|"defense_attorney"|"prosecutor"|"legal_researcher"|"witness"|"expert"|"juror"|"clerk";
const roles:{id:Role;title:string;description:string}[] = [
 {id:"plaintiff",title:"Parte autora",description:"Atue diretamente em nome do autor."},
 {id:"defendant",title:"Parte ré",description:"Atue diretamente em nome do réu."},
 {id:"plaintiff_attorney",title:"Advogado do autor",description:"Represente tecnicamente a parte autora."},
 {id:"defense_attorney",title:"Advogado do réu",description:"Represente tecnicamente a defesa."},
 {id:"prosecutor",title:"Promotor de Justiça",description:"Atue pelo Ministério Público quando cabível."},
 {id:"witness",title:"Testemunha",description:"Preste depoimento e responda à inquirição."},
 {id:"expert",title:"Perito judicial",description:"Apresente laudo e esclarecimentos técnicos."},
 {id:"judge",title:"Magistrado",description:"Conduza a audiência e profira decisões."},
 {id:"juror",title:"Jurados",description:"Participe do conselho de sentença no júri."},
 {id:"clerk",title:"Servidor da secretaria",description:"Pratique atos formais e registros da audiência."},
 {id:"legal_researcher",title:"Pesquisador jurídico",description:"Analise fontes e questões jurídicas para a simulação."},
];
const caseTypes = ["Aleatório","Responsabilidade do fornecedor","Cobrança indevida","Contrato e inadimplemento","Dano moral e material","Acidente e responsabilidade civil","Família e guarda","Divórcio e partilha","Sucessões e inventário","Direito imobiliário","Trabalhista e horas extras","Rescisão e verbas trabalhistas","Acidente de trabalho","Empresarial e societário","Licitação e Administração Pública","Servidor público","Previdenciário","Crime patrimonial","Lesão corporal","Tribunal do Júri","Criminal econômico"];
type HistoryItem = {processId:string;processNumber:string;role:Role;area:string;caseType?:string;userName:string;updatedAt:string};

function escapeHtml(value:string){return value.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\"/g,"&quot;").replace(/'/g,"&#039;");}
function sanitizeHtml(raw:string){
 if(typeof window === "undefined") return escapeHtml(raw);
 const doc = new DOMParser().parseFromString(raw,"text/html");
 doc.querySelectorAll("script,style,iframe,object,embed,form,link,meta").forEach(el=>el.remove());
 doc.querySelectorAll("*").forEach(el=>Array.from(el.attributes).forEach(attr=>{
   const n=attr.name.toLowerCase();
   if(n.startsWith("on")) el.removeAttribute(attr.name);
   if(["href","src","xlink:href"].includes(n)&&/^\s*javascript:/i.test(attr.value)) el.removeAttribute(attr.name);
 }));
 return doc.body.innerHTML;
}
function richContent(content:string){
 let raw=content.replace(/\\#/g,"#").replace(/\\\*/g,"*");
 if(/<\/?[a-z][\s\S]*>/i.test(raw)) return sanitizeHtml(raw);
 let html=escapeHtml(raw);
 html=html.replace(/^###\s+(.+)$/gm,"<h3>$1</h3>").replace(/^##\s+(.+)$/gm,"<h2>$1</h2>").replace(/^#\s+(.+)$/gm,"<h1>$1</h1>").replace(/^---+$/gm,"<hr>").replace(/\*\*(.+?)\*\*/g,"<strong>$1</strong>").replace(/\*(.+?)\*/g,"<em>$1</em>");
 const lines=html.split("\n"); let out=""; let listType="";
 const close=()=>{if(listType){out+=`</${listType}>`;listType="";}};
 for(const line of lines){
   if(/^\d+\.\s+/.test(line)){if(listType!=="ol"){close();out+="<ol>";listType="ol";}out+=`<li>${line.replace(/^\d+\.\s+/,"")}</li>`;continue;}
   if(/^[-*]\s+/.test(line)){if(listType!=="ul"){close();out+="<ul>";listType="ul";}out+=`<li>${line.replace(/^[-*]\s+/,"")}</li>`;continue;}
   close();
   if(!line.trim()) continue;
   if(/^<h[1-3]>/.test(line)||line==="<hr>") out+=line; else out+=`<p>${line}</p>`;
 }
 close(); return out;
}

export default function Home(){
 const [started,setStarted]=useState(false),[inChat,setInChat]=useState(false),[area,setArea]=useState("consumer"),[caseType,setCaseType]=useState("Aleatório"),[includeMP,setIncludeMP]=useState(false),[jury,setJury]=useState(false),[selectedRole,setSelectedRole]=useState<Role>("plaintiff_attorney"),[processId,setProcessId]=useState(""),[processNumber,setProcessNumber]=useState(""),[characters,setCharacters]=useState<any[]>([]),[messages,setMessages]=useState<any[]>([]),[chatText,setChatText]=useState(""),[phase,setPhase]=useState("opening"),[identity,setIdentity]=useState<any>(null),[panel,setPanel]=useState<"details"|"people"|"documents"|"appeals"|null>(null),[loading,setLoading]=useState(false),[agentLoading,setAgentLoading]=useState(false),[error,setError]=useState(""),[userName,setUserName]=useState(""),[history,setHistory]=useState<HistoryItem[]>([]);

 useEffect(()=>{
   const savedName=localStorage.getItem(USER_NAME_KEY)||""; setUserName(savedName);
   try{const savedHistory=JSON.parse(localStorage.getItem(HISTORY_KEY)||"[]");if(Array.isArray(savedHistory))setHistory(savedHistory);}catch{localStorage.removeItem(HISTORY_KEY)}
   const raw=localStorage.getItem(SESSION_STORAGE_KEY);if(!raw)return;
   try{const saved=JSON.parse(raw);if(!saved.processId||!saved.role)return;(async()=>{try{const [pr,sr,pp]=await Promise.all([fetch(`${API_URL}/api/v1/processes/${saved.processId}`),fetch(`${API_URL}/api/v1/processes/${saved.processId}/courtroom/session/${saved.role}`),fetch(`${API_URL}/api/v1/processes/${saved.processId}/participants`)]);if(!pr.ok||!sr.ok)throw new Error();const p=await pr.json(),d=await sr.json();setProcessId(saved.processId);setProcessNumber(p.number);setArea(p.area);setIncludeMP(Boolean(p.include_mp));setJury(Boolean(p.jury));setSelectedRole(saved.role);setIdentity(d.identity||null);setMessages(d.messages||[]);setPhase(d.phase||"opening");if(pp.ok)setCharacters(await pp.json());setStarted(true);setInChat(true);}catch{localStorage.removeItem(SESSION_STORAGE_KEY);}})();}catch{localStorage.removeItem(SESSION_STORAGE_KEY)}
 },[]);

 function saveHistory(item:HistoryItem){
   setHistory(prev=>{const next=[item,...prev.filter(x=>x.processId!==item.processId)].slice(0,30);localStorage.setItem(HISTORY_KEY,JSON.stringify(next));return next;});
 }
 function rememberName(value:string){setUserName(value);localStorage.setItem(USER_NAME_KEY,value);}

 async function startProcess(){
   if(!userName.trim()){setError("Informe seu nome para iniciar a simulação.");return;}
   rememberName(userName.trim());setLoading(true);setError("");
   try{const r=await fetch(`${API_URL}/api/v1/processes`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({area,case_type:caseType,include_mp:includeMP,jury:area==="criminal"&&jury})});const d=await r.json();if(!r.ok)throw new Error(d.detail||"Não foi possível gerar o processo.");setProcessId(d.id);setProcessNumber(d.number);const pr=await fetch(`${API_URL}/api/v1/processes/${d.id}/participants`);const list=pr.ok?await pr.json():[];setCharacters(list);const first=roles.find(r=>list.some((p:any)=>p.role===r.id));const firstRole=(first?.id||"plaintiff_attorney") as Role;setSelectedRole(firstRole);saveHistory({processId:d.id,processNumber:d.number,role:firstRole,area,caseType,userName:userName.trim(),updatedAt:new Date().toISOString()});setStarted(true);}catch(e){setError(e instanceof Error?e.message:"Erro ao gerar o processo.")}finally{setLoading(false)}
 }

 async function openHistory(item:HistoryItem){
   setLoading(true);setError("");
   try{const [pr,sr,pp]=await Promise.all([fetch(`${API_URL}/api/v1/processes/${item.processId}`),fetch(`${API_URL}/api/v1/processes/${item.processId}/courtroom/session/${item.role}`),fetch(`${API_URL}/api/v1/processes/${item.processId}/participants`)]);if(!pr.ok||!sr.ok)throw new Error("Não foi possível recuperar este julgamento.");const p=await pr.json(),d=await sr.json();setProcessId(item.processId);setProcessNumber(p.number||item.processNumber);setArea(p.area);setIncludeMP(Boolean(p.include_mp));setJury(Boolean(p.jury));setSelectedRole(item.role);setIdentity(d.identity||null);setMessages(d.messages||[]);setPhase(d.phase||"opening");if(pp.ok){const list=await pp.json();setCharacters(list.participants||[]);}rememberName(item.userName||userName);localStorage.setItem(SESSION_STORAGE_KEY,JSON.stringify({processId:item.processId,processNumber:p.number||item.processNumber,role:item.role}));saveHistory({...item,processNumber:p.number||item.processNumber,updatedAt:new Date().toISOString()});setStarted(true);setInChat(true);}catch(e){setError(e instanceof Error?e.message:"Erro ao recuperar o julgamento.")}finally{setLoading(false)}
 }

 function removeHistory(processIdToRemove:string){const next=history.filter(x=>x.processId!==processIdToRemove);setHistory(next);localStorage.setItem(HISTORY_KEY,JSON.stringify(next));}

 async function enterCourtroom(){
   if(!userName.trim()){setError("Informe seu nome para entrar no julgamento.");return;}
   rememberName(userName.trim());setLoading(true);setError("");
   try{const r=await fetch(`${API_URL}/api/v1/processes/${processId}/courtroom/session`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({role:selectedRole,user_id:userName.trim()})});const d=await r.json();if(!r.ok)throw new Error(d.detail||"Não foi possível abrir a sessão.");setIdentity(d.identity||null);setMessages(d.messages||[]);setPhase(d.phase||"opening");setInChat(true);localStorage.setItem(SESSION_STORAGE_KEY,JSON.stringify({processId,processNumber,role:selectedRole}));saveHistory({processId,processNumber,role:selectedRole,area,caseType,userName:userName.trim(),updatedAt:new Date().toISOString()});await nextSpeaker();}catch(e){setError(e instanceof Error?e.message:"Erro ao abrir a sessão.")}finally{setLoading(false)}
 }

 function leaveCourtroom(){localStorage.removeItem(SESSION_STORAGE_KEY);setInChat(false);setStarted(false);setPanel(null);setMessages([]);setChatText("");setIdentity(null);setError("");setProcessId("");setProcessNumber("");setCharacters([]);setPhase("opening");}

 async function sendMessage(){if(!chatText.trim()||agentLoading)return;const content=chatText.trim();setChatText("");setError("");try{const r=await fetch(`${API_URL}/api/v1/processes/${processId}/courtroom/session/${selectedRole}/messages`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({content})});const d=await r.json();if(!r.ok)throw new Error(d.detail||"Não foi possível enviar a manifestação.");setMessages(p=>[...p,d.message,...(d.ruling?[d.ruling]:[])].filter(Boolean));setPhase(d.phase||phase);saveHistory({processId,processNumber,role:selectedRole,area,caseType,userName:userName.trim(),updatedAt:new Date().toISOString()});}catch(e){setError(e instanceof Error?e.message:"Erro ao enviar mensagem.")}}

 async function nextSpeaker(){setAgentLoading(true);setError("");try{const r=await fetch(`${API_URL}/api/v1/processes/${processId}/courtroom/session/${selectedRole}/agents/next`,{method:"POST"});const d=await r.json();if(!r.ok)throw new Error(d.detail||"Não foi possível continuar o julgamento.");setPhase(d.phase||phase);if(d.message)setMessages(p=>[...p,d.message].filter(Boolean));if(d.agent?.content)setMessages(p=>[...p,{id:`agent-${Date.now()}`,sender:d.agent.name||d.agent.agent,kind:"agent",content:d.agent.content,role:d.agent.role}]);saveHistory({processId,processNumber,role:selectedRole,area,caseType,userName:userName.trim(),updatedAt:new Date().toISOString()});}catch(e){setError(e instanceof Error?e.message:"Erro ao continuar o julgamento.")}finally{setAgentLoading(false)}}

 async function loadParticipants(){try{const r=await fetch(`${API_URL}/api/v1/processes/${processId}/courtroom/participants`);const d=await r.json();if(!r.ok)throw new Error(d.detail);setCharacters(d.participants||[]);setPanel("people")}catch(e){setError(e instanceof Error?e.message:"Erro ao carregar participantes.")}}

 const availableRoles=roles.filter(r=>characters.length===0||characters.some((p:any)=>p.role===r.id));
 const roleName=roles.find(r=>r.id===selectedRole)?.title||"Participante";
 const areaName={consumer:"Direito do Consumidor",civil:"Direito Civil",labor:"Direito do Trabalho",criminal:"Direito Penal"}[area as "consumer"|"civil"|"labor"|"criminal"];
 const phaseIndex=Math.max(0,phaseIds.indexOf(phase));

 return <main className="shell">
 {!started?<section className="hero"><div className="eyebrow"><Sparkles size={15}/> INTELIGÊNCIA ARTIFICIAL + DIREITO BRASILEIRO</div><h1>Um tribunal para<br/><em>simular casos jurídicos.</em></h1><p className="lead">A IA cria o processo inteiro: caso, partes, conflito, provas, testemunhas e demais personagens. Você escolhe apenas a área ou tema que quer estudar.</p><div className="case-card"><div className="card-label">NOVO PROCESSO</div><label>Seu nome</label><input value={userName} onChange={e=>rememberName(e.target.value)} placeholder="Como deseja ser identificado na simulação?" autoComplete="name"/><small style={{display:"block",marginTop:6}}>Seu nome será usado para identificar você durante o julgamento e fica salvo apenas neste navegador.</small><label>Tipo de caso</label><select value={caseType} onChange={e=>{setCaseType(e.target.value);if(["Tribunal do Júri","Crime patrimonial","Lesão corporal","Criminal econômico"].includes(e.target.value)){setArea("criminal");setJury(e.target.value==="Tribunal do Júri")}else if(e.target.value!=="Aleatório")setJury(false)}}>{caseTypes.map(x=><option key={x}>{x}</option>)}</select><label>Área jurídica</label><select value={area} onChange={e=>{setArea(e.target.value);if(e.target.value!=="criminal")setJury(false)}}><option value="consumer">Direito do Consumidor</option><option value="civil">Direito Civil</option><option value="labor">Direito do Trabalho</option><option value="criminal">Direito Penal</option></select><label className="checkbox-row"><input type="checkbox" checked={includeMP} onChange={e=>setIncludeMP(e.target.checked)}/><span><b>Permitir atuação do Ministério Público</b><small>A IA decide quando a intervenção institucional é cabível.</small></span></label>{area==="criminal"&&<label className="checkbox-row"><input type="checkbox" checked={jury} onChange={e=>setJury(e.target.checked)}/><span><b>Tribunal do Júri</b><small>Inclui conselho de sentença e atos próprios do júri.</small></span></label>}{error&&<div className="error">{error}</div>}<button onClick={startProcess} disabled={loading||!userName.trim()}>{loading?<><Loader2 size={17}/> Gerando caso...</>:<>Gerar processo com IA <Sparkles size={17}/></>}</button><small>Nenhum fato, nome de parte ou documento é informado por você. A IA cria o cenário da simulação.</small></div>{history.length>0&&<div style={{maxWidth:760,margin:"28px auto 0",padding:"22px",border:"1px solid rgba(255,255,255,.1)",borderRadius:18,background:"rgba(255,255,255,.025)"}}><div style={{display:"flex",alignItems:"center",justifyContent:"space-between",gap:12,marginBottom:16}}><div><div className="eyebrow"><History size={15}/> HISTÓRICO</div><h3 style={{margin:"6px 0 0"}}>Seus julgamentos</h3></div><small>{history.length} processo{history.length===1?"":"s"}</small></div>{history.map(item=><div key={item.processId} style={{display:"flex",alignItems:"center",justifyContent:"space-between",gap:14,padding:"14px 0",borderTop:"1px solid rgba(255,255,255,.07)"}}><div style={{minWidth:0}}><b>Processo nº {item.processNumber}</b><div style={{marginTop:4,fontSize:13,opacity:.7}}>{item.area==="consumer"?"Direito do Consumidor":item.area==="civil"?"Direito Civil":item.area==="labor"?"Direito do Trabalho":"Direito Penal"} · {roles.find(r=>r.id===item.role)?.title||item.role}</div></div><div style={{display:"flex",gap:8,flexShrink:0}}><button className="secondary-action" onClick={()=>openHistory(item)} disabled={loading}><Play size={15}/> Retomar</button><button className="secondary-action" onClick={()=>removeHistory(item.processId)} title="Remover do histórico"><Trash2 size={15}/></button></div></div>)}</div>}</section>
 :!inChat?<section className="role-page"><div className="process-head"><div><div className="eyebrow">PROCESSO GERADO</div><h2>Processo nº {processNumber}</h2><p>{areaName} · caso criado integralmente pela IA</p></div></div><div className="role-grid">{availableRoles.map(role=><button key={role.id} className={selectedRole===role.id?"role-card selected":"role-card"} onClick={()=>setSelectedRole(role.id)}><strong>{role.title}</strong><span>{role.description}</span></button>)}</div>{error&&<div className="error">{error}</div>}<div className="notice"><LockKeyhole size={15}/><span>Depois de entrar no julgamento, seu papel fica bloqueado nesta simulação. Para trocar de papel, gere outro processo.</span></div><button className="primary-action" onClick={enterCourtroom} disabled={loading||!selectedRole||!userName.trim()}>{loading?"Abrindo sala...":<>Entrar na sala de julgamento <MessageSquare size={17}/></>}</button></section>
 :<section className="courtroom"><div className="court-head"><div><div className="eyebrow">SALA DE JULGAMENTO · 1ª INSTÂNCIA</div><h2>Processo nº {processNumber}</h2><p>{identity?.display_name||userName||roleName} · {areaName} · fase: {phases[Math.min(phaseIndex,phases.length-1)]}</p></div><button className="secondary-action" onClick={leaveCourtroom} disabled={agentLoading}><LogOut size={16}/> Sair do julgamento</button></div><div className="court-tools"><button onClick={()=>setPanel(panel==="details"?null:"details")}><FileText size={16}/> Processo</button><button onClick={loadParticipants}><Users size={16}/> Participantes</button><button onClick={()=>setPanel(panel==="documents"?null:"documents")}><Landmark size={16}/> Audiência</button><button onClick={()=>setPanel(panel==="appeals"?null:"appeals")}><GitBranch size={16}/> Recursos e instâncias</button></div>{panel&&<aside className="court-panel">{panel==="details"&&<><h3>Detalhes do processo</h3><p><b>Classe:</b> Simulação de {areaName}</p><p><b>Processo:</b> Gerado integralmente pela IA</p><p><b>Instância:</b> 1ª instância</p><p><b>Você:</b> {identity?.display_name||userName||roleName}</p></>}{panel==="people"&&<><h3>Pessoas no julgamento</h3>{characters.map((c,i)=><div className="person" key={c.id||i}><b>{c.title} {c.name}</b><small>{c.profession||"Participante fictício"}</small></div>)}</>}{panel==="documents"&&<><h3>Condução da audiência</h3><div className="person"><b>Debate livre</b><small>Você pode se manifestar a qualquer momento. O juízo controla a ordem e a pertinência.</small></div><button className="secondary-action" onClick={nextSpeaker} disabled={loading||agentLoading}>{agentLoading?"IA em manifestação...":"Continuar julgamento"}</button><div className="person"><b>Próximo ato</b><small>O botão gera a próxima manifestação do orador previsto, sem pular automaticamente para outra fase.</small></div></>}{panel==="appeals"&&<><h3>Recursos e instâncias</h3><p>Depois de uma decisão recorrível, a parte legitimada poderá protocolar o recurso cabível.</p><button className="secondary-action">Preparar recurso</button></>}</aside>}<div className="phase-strip">{phases.map((p,i)=><span className={i<=phaseIndex?"active":""} key={p}>{p}</span>)}</div><div className="chat-window"><div className="chat-title"><span><MessageSquare size={17}/><b>Plenário virtual</b></span><small>{agentLoading?<><Bot size={13}/> IA em manifestação</>:"Debate livre · controle processual"}</small></div><div className="messages">{messages.map((m:any,i:number)=><div className={m.kind==="user"?"message user":"message"} key={m.id||i}><small>{m.sender||m.actor}</small><div className="message-content" dangerouslySetInnerHTML={{__html:richContent(m.content||"")}} /></div>)}</div><div className="composer"><textarea value={chatText} onChange={e=>setChatText(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage()}}} placeholder="Digite sua manifestação, pergunta ou intervenção..." rows={2}/><button onClick={sendMessage} disabled={!chatText.trim()||agentLoading}><Send size={17}/> Enviar</button></div></div>{error&&<div className="error">{error}</div>}<div className="notice"><Landmark size={15}/><span>O botão <b>Continuar julgamento</b> não troca de fase por conta própria: ele solicita apenas o próximo orador/ato previsto. A fase muda somente quando os atos daquela etapa terminam.</span></div></section>}
 </main>;
}
