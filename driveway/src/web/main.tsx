import React from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

function App() {
  const [points, setPoints] = React.useState("25");
  const [result, setResult] = React.useState("25 points = $25.00 USD (valuation only)");
  const [status, setStatus] = React.useState("API status: checking");
  React.useEffect(() => { fetch("http://localhost:8787/health").then(r => r.json()).then(() => setStatus("API status: online")).catch(() => setStatus("API status: offline — start npm run dev")); }, []);
  async function calculate() {
    const response = await fetch("http://localhost:8787/api/valuation", { method:"POST", headers:{"content-type":"application/json"}, body:JSON.stringify({points:Number(points)}) });
    const data = await response.json();
    setResult(data.error ?? `${data.points} POINT = $${Number(data.amount).toFixed(2)} USD · valuation only`);
  }
  return <main className="shell">
    <nav><div className="brand"><span className="mark">D</span> driveway<span className="dot">.io</span></div><span className="pill">STARTER STUDIO</span></nav>
    <section className="hero"><p className="eyebrow">LEDGER INFRASTRUCTURE, WITHOUT THE FRICTION</p><h1>Build the ledger.<br/><em>Drive the workflow.</em></h1><p className="sub">A reusable foundation for accounts, journals, app workflows and integrations.</p><div className="status">{status}</div></section>
    <section className="grid">
      <article className="panel wide"><div className="panel-head"><div><p className="eyebrow">WORKSPACE / OVERVIEW</p><h2>AshLedger preview</h2></div><span className="tag">READ-ONLY DEMO</span></div><div className="metrics"><div><small>Journal entries</small><strong>0</strong></div><div><small>Ledger mode</small><strong>Double-entry</strong></div><div><small>Posting</small><strong>Disabled</strong></div></div><div className="notice">No live wallet is connected. No funds can move from this starter.</div></article>
      <article className="panel"><p className="eyebrow">VALUATION SANDBOX</p><h2>Points → USD</h2><label>Point amount<input value={points} onChange={e=>setPoints(e.target.value)} inputMode="decimal"/></label><button onClick={calculate}>Calculate valuation</button><p className="result">{result}</p><small>Demo policy: 1 point = $1 USD. Not a provider redemption rate.</small></article>
      <article className="panel wide"><p className="eyebrow">BUILD WITH DRIVEWAY DSL</p><h2>Describe your ledger</h2><pre>{'project "AshLedger"\nledger "primary":\n  currency USD\n  mode double_entry\n  immutable true\n\nrule "points_value":\n  1 POINT = 1 USD\n  valuation_only true'}</pre><p className="muted">The parser and typed ledger engine are included in this starter.</p></article>
    </section>
    <footer>Driveway.io · TypeScript + Kotlin · Human approval before financial execution</footer>
  </main>;
}
createRoot(document.getElementById("root")!).render(<App />);
