import "./style.css";

const app = document.querySelector("#app");
app.innerHTML = `
  <header class="topbar">
    <a class="brand" href="#home" aria-label="Ŷæṛö home"><span class="brand-mark">Ŷ</span><span>Ŷæṛö</span></a>
    <nav><a href="#language">Language</a><a href="#workbench">Workbench</a><a href="/semantics.html">Currency + in2</a><a href="/lux.html">LUX Direction</a><a href="#quantum">Research</a><a href="#runway">Runway</a></nav>
    <a class="top-cta" href="#workbench">Open workbench <span>↗</span></a>
  </header>
  <main id="home">
    <section class="hero">
      <div class="hero-copy">
        <div class="eyebrow"><i></i> SOURCE-PRESERVING COMPUTATION</div>
        <h1>Keep the origin.<br><em>Transform the possible.</em></h1>
        <p class="lead">Ŷæṛö turns existing code into inspectable structure — preserving the original while deriving typed representations, experiments, and portable language tools.</p>
        <div class="hero-actions"><a class="button primary" href="#workbench">Explore the workbench <span>→</span></a><a class="text-link" href="#language">Read the language principles</a></div>
        <div class="hero-note"><span class="pulse"></span> Immutable source · Derived artifacts · Human-authorized promotion</div>
      </div>
      <div class="hero-art" aria-label="Abstract visualization of source code becoming structured symbolic units">
        <div class="orbit orbit-a"></div><div class="orbit orbit-b"></div>
        <div class="core"><span>△</span><small>IR / ATOM</small></div>
        <div class="float-card card-source"><small>ORIGINAL SOURCE</small><b>C · C++ · JS</b><span>sha256 verified</span></div>
        <div class="float-card card-derive"><small>DERIVED STRUCTURE</small><b>AST → IR</b><span>provenance linked</span></div>
        <div class="float-card card-proof"><small>VALIDATION</small><b>TEST + REVIEW</b><span>before promotion</span></div>
        <div class="glyph glyph-one">☆</div><div class="glyph glyph-two">∞</div><div class="glyph glyph-three">§</div>
      </div>
    </section>
    <section class="principles" id="language">
      <div class="section-head"><div><div class="eyebrow">THE LANGUAGE LAYER</div><h2>Small symbols. <em>Explicit meaning.</em></h2></div><p>Atomic means indivisible semantic units and all-or-nothing transformations — not a claim about physical atoms or hardware.</p></div>
      <div class="symbol-grid">
        <article><b>☆</b><h3>Explicit zero</h3><p>Absence is represented, never confused with missing data.</p></article>
        <article><b>△</b><h3>Triadic relation</h3><p>Three ordered operands form a first-class relation.</p></article>
        <article><b>∞</b><h3>Bounded continuation</h3><p>Lazy streams remain subject to declared resource limits.</p></article>
        <article><b>§</b><h3>Scoped meaning</h3><p>Names and effects live inside explicit boundaries.</p></article>
        <article><b>&</b><h3>Composition</h3><p>Typed units combine through checked interfaces.</p></article>
        <article><b>→</b><h3>Transformation</h3><p>Pure by default; effects must be declared and audited.</p></article>
      </div>
    </section>
    <section class="workbench" id="workbench">
      <div class="section-head"><div><div class="eyebrow">LIVE PROTOTYPE · NO EXECUTION</div><h2>From source to <em>structure.</em></h2></div><p>Paste a small code sample. The browser creates a token and provenance preview only; it does not compile or execute your input.</p></div>
      <div class="bench">
        <div class="editor">
          <div class="panel-head"><span>01 / SOURCE SNAPSHOT</span><span class="live-dot">LOCAL ONLY</span></div>
          <label for="source">Source sample</label>
          <textarea id="source" spellcheck="false">§analysis {
  △(source, syntax, evidence);
  source → ∴ immutable_ir;
}</textarea>
          <div class="editor-foot"><span id="source-count">0 characters</span><button id="analyze" class="button primary">Derive structure →</button></div>
        </div>
        <div class="output">
          <div class="panel-head"><span>02 / DERIVED ATOMS</span><span id="parse-state">AWAITING INPUT</span></div>
          <pre id="ir" aria-live="polite">{
  "status": "awaiting analysis",
  "source": "preserved in this page",
  "execution": "disabled"
}</pre>
          <div class="output-foot"><span>AST / IR PREVIEW</span><span>NO SOURCE WRITES</span></div>
        </div>
      </div>
      <p class="bench-disclaimer">This is a lexical prototype, not a full compiler. Unsupported syntax is not silently translated. Do not paste secrets or private source into a public deployment.</p>
    </section>
    <section class="research" id="quantum">
      <div class="research-copy"><div class="eyebrow">RESEARCH, NOT HYPE</div><h2>Classical foundations.<br><em>Quantum-aware experiments.</em></h2><p>Derived graphs and typed IR can become well-defined problem instances for quantum-inspired or quantum-computing research. Every experiment keeps a classical baseline and reports the same input, constraints, cost, and outcome quality.</p><ul><li>Source snapshots remain immutable.</li><li>Experiments run on isolated derived data.</li><li>No speedup or equivalence without evidence.</li></ul></div>
      <div class="research-panel"><div class="panel-head"><span>EXPERIMENT RECORD</span><span class="tag">PLANNED</span></div><div class="metric"><small>INPUT</small><b>Derived dependency graph</b></div><div class="metric"><small>BASELINE</small><b>Classical heuristic</b></div><div class="metric"><small>EXPERIMENT</small><b>Quantum-inspired / quantum backend</b></div><div class="metric"><small>CLAIM STATUS</small><b class="muted">Unproven until benchmarked</b></div></div>
    </section>
    <section class="runway" id="runway">
      <div class="runway-copy"><div class="eyebrow">CREATIVE PIPELINE</div><h2>Ideas become <em>visual artifacts.</em></h2><p>Connect Ŷæṛö to Runway Dev to generate concept images from your project briefs. The API key stays server-side; generation only starts when a person submits a prompt.</p><a class="text-link" href="https://dev.runway.com/" target="_blank" rel="noreferrer">Open Runway Dev ↗</a></div>
      <div class="runway-card"><div class="panel-head"><span>RUNWAY DEV / IMAGE GENERATION</span><span id="runway-status" class="tag">CHECKING</span></div><label for="visual-prompt">Creative brief</label><textarea id="visual-prompt" rows="3" maxlength="2000" placeholder="Describe a visual for the Ŷæṛö frontpage…">An abstract editorial visualization of source code becoming luminous geometric structures, deep navy, warm ivory, restrained cyan accents, wide composition.</textarea><button id="generate" class="button primary full">Generate concept image <span>↗</span></button><p id="runway-result" class="runway-result" aria-live="polite">Generation is disabled until RUNWAYML_API_SECRET is configured on the Vercel server.</p><small class="fineprint">Runway API billing is separate from Runway web-app credits. A successful submission may consume API credits.</small></div>
    </section>
  </main>
  <footer><a class="brand" href="#home"><span class="brand-mark">Ŷ</span><span>Ŷæṛö</span></a><span>Preserve origin. Make uncertainty visible. Keep every change accountable.</span><span>© 2026 Ŷæṛö</span></footer>
`;

const source = document.querySelector("#source");
const count = document.querySelector("#source-count");
const output = document.querySelector("#ir");
const state = document.querySelector("#parse-state");

function derive(sourceText) {
  const tokens = sourceText.match(/"(?:\\.|[^"\\])*"|☆|k|∞|△|§|∴|&|→|[A-Za-z_][A-Za-z0-9_]*|[{}(),;=]|[^\\s]/gu) || [];
  let depth = 0;
  for (const token of tokens) {
    if (token === "{") depth++;
    if (token === "}") depth--;
    if (depth < 0) throw new Error("Unexpected closing scope");
  }
  if (depth !== 0) throw new Error("Unclosed scope");
  const atoms = tokens.map((token, index) => ({
    id: `a${String(index + 1).padStart(4, "0")}`,
    kind: /^[A-Za-z_]/u.test(token) ? "identifier" : token.startsWith('"') ? "string-literal" : "symbol-or-delimiter",
    value: token,
    sourceSpan: { tokenIndex: index },
    executable: false
  }));
  return {
    language: "Ŷæṛö lexical IR preview",
    version: "0.1-draft",
    source: { characters: sourceText.length, sha256: "computed locally in a future signed build", preserved: true },
    atomCount: atoms.length,
    atoms,
    validation: { scopeBalance: "passed", semanticTypeCheck: "not implemented", equivalence: "not claimed" },
    execution: "disabled"
  };
}

source.addEventListener("input", () => { count.textContent = `${source.value.length} characters`; });
count.textContent = `${source.value.length} characters`;
document.querySelector("#analyze").addEventListener("click", () => {
  try {
    const result = derive(source.value);
    output.textContent = JSON.stringify(result, null, 2);
    state.textContent = "LEXICAL PASS";
    state.className = "success";
  } catch (error) {
    output.textContent = JSON.stringify({ status: "rejected", reason: error.message, sourcePreserved: true, execution: "disabled" }, null, 2);
    state.textContent = "SYNTAX ERROR";
    state.className = "error";
  }
});

const status = document.querySelector("#runway-status");
fetch("/api/runway-image", { method: "GET" }).then(async response => {
  const data = await response.json();
  status.textContent = data.configured ? "CONNECTED" : "NOT CONFIGURED";
  status.className = data.configured ? "tag success" : "tag";
}).catch(() => { status.textContent = "PREVIEW ONLY"; });

document.querySelector("#generate").addEventListener("click", async () => {
  const promptText = document.querySelector("#visual-prompt").value.trim();
  const result = document.querySelector("#runway-result");
  if (!promptText) { result.textContent = "Enter a creative brief first."; return; }
  result.textContent = "Submitting generation request…";
  try {
    const response = await fetch("/api/runway-image", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ promptText })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Runway request failed");
    result.textContent = `Runway accepted the request. Task ID: ${data.id}. Check the task in your Runway Dev project.`;
  } catch (error) {
    result.textContent = error.message;
  }
});
