"use client";

import { useState } from "react";
import { ArrowRight, Gavel, Scale, ShieldCheck, Sparkles, Loader2, Send, Users, FileText, Landmark, GitBranch, MessageSquare } from "lucide-react";

const phases = ["Distribuição", "Petição inicial", "Contestação", "Réplica", "Instrução", "Análise judicial", "Sentença"];
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Role = "spectator" | "plaintiff_attorney" | "defense_attorney" | "prosecutor" | "judge" | "juror";

const roles: { id: Role; title: string; description: string }[] = [
  { id: "spectator", title: "Observador", description: "Acompanhe o julgamento sem representar uma parte." },
  { id: "plaintiff_attorney", title: "Representante do autor", description: "Atue pela parte autora durante a simulação." },
  { id: "defense_attorney", title: "Representante do réu", description: "Atue pela defesa da parte ré." },
  { id: "prosecutor", title: "Ministério Público", description: "Atue como promotor quando houver hipótese de atuação." },
  { id: "judge", title: "Magistrado", description: "Conduza a audiência e profira decisões na simulação." },
  { id: "juror", title: "Jurados", description: "Participe da deliberação em simulações com Tribunal do Júri." },
];

export default function Home() {
  const [started, setStarted] = useState(false);
  const [inChat, setInChat] = useState(false);
  const [caseText, setCaseText] = useState("");
  const [area, setArea] = useState("consumer");
  const [plaintiff, setPlaintiff] = useState("Autor da simulação");
  const [defendant, setDefendant] = useState("Réu da simulação");
  const [includeMP, setIncludeMP] = useState(false);
  const [selectedRole, setSelectedRole] = useState<Role>("spectator");
  const [processId, setProcessId] = useState("");
  const [processNumber, setProcessNumber] = useState("");
  const [characters, setCharacters] = useState<any[]>([]);
  const [messages, setMessages] = useState<any[]>([]);
  const [chatText, setChatText] = useState("");
  const [panel, setPanel] = useState<"details" | "people" | "documents" | "appeals" | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function startProcess() {
    if (!caseText.trim()) return;
    setLoading(true); setError("");
    try {
      const response = await fetch(`${API_URL}/api/v1/processes`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ area, plaintiff, defendant, facts: caseText.trim(), include_mp: includeMP }) });
      if (!response.ok) throw new Error("Não foi possível criar o processo.");
      const process = await response.json();
      setProcessId(process.id); setProcessNumber(process.number); setCharacters(process.characters || []); setStarted(true);
    } catch (err) { setError(err instanceof Error ? err.message : "Erro ao iniciar o processo."); }
    finally { setLoading(false); }
  }

  async function enterCourtroom() {
    setLoading(true); setError("");
    try {
      const response = await fetch(`${API_URL}/api/v1/processes/${processId}/courtroom/session`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ role: selectedRole }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Não foi possível abrir a sessão.");
      setMessages(data.messages || []); setInChat(true);
    } catch (err) { setError(err instanceof Error ? err.message : "Erro ao abrir a sessão."); }
    finally { setLoading(false); }
  }

  async function sendMessage() {
    if (!chatText.trim()) return;
    const content = chatText.trim(); setChatText(""); setError("");
    try {
      const response = await fetch(`${API_URL}/api/v1/processes/${processId}/courtroom/session/${selectedRole}/messages`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ content }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Não foi possível enviar a mensagem.");
      setMessages(prev => [...prev, data]);
    } catch (err) { setError(err instanceof Error ? err.message : "Erro ao enviar mensagem."); }
  }

  const roleName = roles.find(r => r.id === selectedRole)?.title || "Observador";
  const areaName = { consumer: "Direito do Consumidor", civil: "Direito Civil", labor: "Direito do Trabalho", criminal: "Direito Penal" }[area as "consumer" | "civil" | "labor" | "criminal"];

  return <main className="shell">
    <header className="topbar"><div className="brand"><div className="brand-mark"><Scale size={20}/></div><div><strong>TRIBUNAL VIRTUAL</strong><span>Simulação jurídica</span></div></div><div className="status"><span className="status-dot"/> Sistema operacional</div></header>

    {!started && <section className="hero"><div className="eyebrow"><Sparkles size={15}/> INTELIGÊNCIA ARTIFICIAL + DIREITO BRASILEIRO</div><h1>Um tribunal para<br/><em>simular casos jurídicos.</em></h1><p className="lead">Crie um processo e entre em uma sala de julgamento onde você escolhe seu papel e interage com personagens jurídicos fictícios.</p><div className="features"><div><Gavel size={19}/><span><b>Tribunal interativo</b>Chat, audiência, testemunhas e participantes.</span></div><div><ShieldCheck size={19}/><span><b>Processo por etapas</b>Recursos e instâncias fazem parte da simulação.</span></div></div><div className="case-card"><div className="card-label">NOVO PROCESSO</div><label>Área jurídica</label><select value={area} onChange={e=>setArea(e.target.value)}><option value="consumer">Direito do Consumidor</option><option value="civil">Direito Civil</option><option value="labor">Direito do Trabalho</option><option value="criminal">Direito Penal</option></select><label>Autor</label><input value={plaintiff} onChange={e=>setPlaintiff(e.target.value)}/><label>Réu</label><input value={defendant} onChange={e=>setDefendant(e.target.value)}/><label>Relato dos fatos</label><textarea value={caseText} onChange={e=>setCaseText(e.target.value)} placeholder="Descreva os fatos do caso que será simulado..." rows={5}/><label className="checkbox-row"><input type="checkbox" checked={includeMP} onChange={e=>setIncludeMP(e.target.checked)}/><span><b>Incluir Ministério Público</b><small>Ative quando a simulação envolver atuação do MP.</small></span></label>{error && <div className="error">{error}</div>}<button onClick={startProcess} disabled={!caseText.trim() || loading}>{loading ? <><Loader2 size={17}/> Criando processo...</> : <>Criar processo <ArrowRight size={17}/></>}</button><small>Ambiente educacional. Nomes e decisões são fictícios.</small></div></section>}

    {started && !inChat && <section className="role-page"><div className="process-head"><div><div className="eyebrow">PROCESSO CRIADO</div><h2>Processo nº {processNumber}</h2><p>{areaName} · escolha seu papel antes de entrar na sala</p></div></div><div className="role-grid">{roles.map(role=><button key={role.id} className={selectedRole===role.id?"role-card selected":"role-card"} onClick={()=>setSelectedRole(role.id)}><strong>{role.title}</strong><span>{role.description}</span></button>)}</div>{error && <div className="error">{error}</div>}<button className="primary-action" onClick={enterCourtroom} disabled={loading}>{loading ? "Abrindo sala..." : <>Entrar na sala de julgamento <MessageSquare size={17}/></>}</button><p className="fictional-note">Você poderá consultar o processo, participantes, documentos, testemunhas, jurados e recursos durante a sessão.</p></section>}

    {started && inChat && <section className="courtroom"><div className="court-head"><div><div className="eyebrow">SALA DE JULGAMENTO · 1ª INSTÂNCIA</div><h2>Processo nº {processNumber}</h2><p>{roleName} · {areaName}</p></div><button className="ghost" onClick={()=>setInChat(false)}>Trocar papel</button></div><div className="court-tools"><button onClick={()=>setPanel(panel==="details"?null:"details")}><FileText size={16}/> Processo</button><button onClick={()=>setPanel(panel==="people"?null:"people")}><Users size={16}/> Participantes</button><button onClick={()=>setPanel(panel==="documents"?null:"documents")}><Landmark size={16}/> Audiência</button><button onClick={()=>setPanel(panel==="appeals"?null:"appeals")}><GitBranch size={16}/> Recursos e instâncias</button></div>{panel && <aside className="court-panel">{panel==="details" && <><h3>Detalhes do processo</h3><p><b>Classe:</b> Simulação de {areaName}</p><p><b>Autor:</b> {plaintiff}</p><p><b>Réu:</b> {defendant}</p><p><b>Instância:</b> 1ª instância</p><p><b>Fase:</b> Distribuição / preparação da audiência</p></>}{panel==="people" && <><h3>Pessoas no julgamento</h3>{characters.map((c,i)=><div className="person" key={i}><b>{c.title} {c.name}</b><small>{c.profession}</small></div>)}<div className="person"><b>Testemunhas</b><small>Testemunhas das partes serão chamadas durante a instrução.</small></div>{area==="criminal" && <div className="person"><b>7 jurados</b><small>Composição simulada do Conselho de Sentença.</small></div>}</>}{panel==="documents" && <><h3>Audiência e instrução</h3><div className="person"><b>Testemunhas</b><small>Depoimentos e perguntas poderão ser conduzidos durante a fase de instrução.</small></div><div className="person"><b>Perícia</b><small>Um perito judicial pode ser chamado quando a matéria exigir conhecimento técnico.</small></div><div className="person"><b>Júri</b><small>Em simulações criminais configuradas para júri, os jurados participarão da deliberação.</small></div></>}{panel==="appeals" && <><h3>Recursos e instâncias</h3><p>Após uma decisão recorrível, a simulação poderá abrir um recurso e encaminhar o processo para a instância competente.</p><button className="secondary-action">Preparar recurso</button><button className="secondary-action">Escalar para 2ª instância</button></>}</aside>}
      <div className="phase-strip">{phases.map((phase,i)=><span className={i===0?"active":""} key={phase}>{phase}</span>)}</div><div className="chat-window"><div className="chat-title"><span><MessageSquare size={17}/><b>Plenário virtual</b></span><small>As mensagens fazem parte da simulação.</small></div><div className="messages">{messages.map((m,i)=><div className={m.kind==="user"?"message user":"message"} key={m.id || i}><small>{m.sender}</small><p>{m.content}</p></div>)}</div><div className="composer"><textarea value={chatText} onChange={e=>setChatText(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage()}}} placeholder="Digite sua manifestação, pergunta ou intervenção..." rows={2}/><button onClick={sendMessage} disabled={!chatText.trim()}><Send size={17}/> Enviar</button></div></div><div className="notice">Tribunal Virtual é uma simulação educacional. A aplicação não representa tribunal oficial, não produz decisões reais e não substitui orientação profissional.</div></section>}
  </main>;
}
