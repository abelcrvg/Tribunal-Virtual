"use client";

import { useState } from "react";
import { ArrowRight, Gavel, Scale, ShieldCheck, Sparkles, Loader2 } from "lucide-react";

const phases = ["Distribuição", "Petição inicial", "Contestação", "Réplica", "Análise judicial", "Sentença"];
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [started, setStarted] = useState(false);
  const [caseText, setCaseText] = useState("");
  const [area, setArea] = useState("consumer");
  const [plaintiff, setPlaintiff] = useState("Autor da simulação");
  const [defendant, setDefendant] = useState("Réu da simulação");
  const [processNumber, setProcessNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function startProcess() {
    if (!caseText.trim()) return;
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_URL}/api/v1/processes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ area, plaintiff, defendant, facts: caseText.trim() }),
      });
      if (!response.ok) throw new Error("Não foi possível criar o processo.");
      const process = await response.json();
      setProcessNumber(process.number);
      setStarted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao iniciar o processo.");
    } finally {
      setLoading(false);
    }
  }

  return <main className="shell">
    <header className="topbar"><div className="brand"><div className="brand-mark"><Scale size={20} strokeWidth={1.8}/></div><div><strong>TRIBUNAL VIRTUAL</strong><span>Simulação jurídica</span></div></div><div className="status"><span className="status-dot"/> Sistema operacional</div></header>
    {!started ? <section className="hero"><div className="eyebrow"><Sparkles size={15}/> INTELIGÊNCIA ARTIFICIAL + DIREITO BRASILEIRO</div><h1>Um tribunal para<br/><em>simular casos jurídicos.</em></h1><p className="lead">Crie um processo, apresente os fatos e acompanhe uma simulação conduzida por agentes de IA com papéis jurídicos distintos.</p><div className="features"><div><Gavel size={19}/><span><b>Múltiplos agentes</b>Advocacia, pesquisa e magistratura.</span></div><div><ShieldCheck size={19}/><span><b>Fundamentação</b>Legislação como fonte verificável.</span></div></div><div className="case-card"><div className="card-label">NOVO PROCESSO</div><label>Área jurídica</label><select value={area} onChange={e=>setArea(e.target.value)}><option value="consumer">Direito do Consumidor</option><option value="civil">Direito Civil</option><option value="labor">Direito do Trabalho</option><option value="criminal">Direito Penal</option></select><label>Autor</label><input value={plaintiff} onChange={e=>setPlaintiff(e.target.value)} placeholder="Nome do autor"/><label>Réu</label><input value={defendant} onChange={e=>setDefendant(e.target.value)} placeholder="Nome do réu"/><label>Relato dos fatos</label><textarea value={caseText} onChange={e=>setCaseText(e.target.value)} placeholder="Descreva os fatos do caso que será simulado..." rows={5}/>{error && <div className="error">{error}</div>}<button onClick={startProcess} disabled={!caseText.trim() || loading}>{loading ? <><Loader2 size={17} className="spin"/> Criando processo...</> : <>Iniciar simulação <ArrowRight size={17}/></>}</button><small>Ambiente educacional. A simulação não constitui decisão judicial ou aconselhamento jurídico.</small></div></section> : <section className="process-page"><div className="process-head"><div><div className="eyebrow">PROCESSO SIMULADO</div><h2>Processo nº {processNumber}</h2><p>Direito do Consumidor · Fase de distribuição</p></div><button className="ghost" onClick={()=>setStarted(false)}>Novo processo</button></div><div className="timeline">{phases.map((phase,i)=><div className={i===0?"phase active":"phase"} key={phase}><span>{i+1}</span>{phase}</div>)}</div><div className="workspace"><article className="panel facts"><div className="panel-title">FATOS APRESENTADOS</div><p><strong>{plaintiff}</strong> × <strong>{defendant}</strong></p><p>{caseText}</p></article><aside className="panel agents"><div className="panel-title">AGENTES DO TRIBUNAL</div>{[["⚖","Magistrado","IA judicial · neutra"],["§","Advogado do autor","IA de argumentação"],["§","Advogado do réu","IA de defesa"],["⌕","Pesquisador jurídico","Legislação e precedentes"]].map(a=><div className="agent" key={a[1]}><i>{a[0]}</i><span><b>{a[1]}</b><small>{a[2]}</small></span></div>)}</aside></div><div className="notice">Processo criado no backend. A próxima etapa conectará os agentes de IA ao processo com rastreabilidade das fontes utilizadas.</div></section>}
  </main>;
}
