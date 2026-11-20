# TRUE LIGHTWORK WAVE-MAVEN
## Ɣơ narrative-to-operable architecture note

**Status:** Proposed, reviewable observer architecture  
**Branch:** `feature/gamma-finance-arm-runflow`  
**Scope:** Source-linked narratives, read-only event observation, local terminal presentation, and readiness notifications  
**Authority:** This note does not grant repository, web, provider, wallet, trading, or external-system permissions.

### 1. Design interpretation

"TRUE LIGHTWORK WAVE-MAVEN" is a project name for a traceable progression from origin to evidence and reviewed learning. "Capacitors" represent accumulated, independently verifiable capability evidence; they are not physical energy stores. "Intergalactic terminals" are a presentation metaphor for a namespaced local observer interface; no interplanetary transport or beyond-time measurement is claimed.

The system measures only recorded events. It may order events by an authored sequence and display timestamps that actually exist. Missing timestamps remain unknown. It does not interpolate a missing timeline, infer hidden activations, or convert a narrative claim into a runtime fact.

### 2. Existing source contracts inspected

The implementation connects to these existing repository sources:

| Existing source | Verified role | Integration boundary |
|---|---|---|
| `docs/ERIA-RUNFLOW-OPERATING-PROTOCOL.md` | Origin → Intent → Authorization → Execution → Evidence → Review → Recovery → Learning → New Growth | Canonical narrative state model; documentation alone does not start a background process |
| `pantheon/NEW/README.md` | Consent-based narrative proposal layer | Staged; not wired into runtime |
| `app/src/main/java/com/vanellye/eria/pantheon/PantheonRuntimeGate.kt` | Android envelope validation and review presentation | `actionTaken=false`; no executor or provider/network writer |
| `pantheon/IC/README.md` | Integration Core gate contract | Caller-supplied checks are not cryptographic proof or execution authorization |
| `docs/BRANCH-DIRECTORY-ACOUSTIC.md` | Historical source/branch cross-reference | Records past branch names; does not prove they remain live |
| `docs/TRUE-NORTH-IMPLEMENTATION-STATUS.md` | Historical branch implementation snapshot | Evidence about the recorded snapshot, not current runtime |
| `Ɣơ/finance/src/gamma_finance/runflow.py` | Prepare-only withdrawal proposal lifecycle | No live executor; proposal is not an order |

The historical directory references `pantheon/signed-package-exchange` (PR #13), `pantheon/source-digest-engine` (PR #11), and `pantheon/cpp-html-consent-engine`. They are preserved as lineage pointers, not silently copied or activated.

### 3. Proposed repository modules

`Ɣơ/operations/` contains:
- **.coddoc reader:** validates a versioned JSON narrative record, hashes its bytes, and preserves source references.
- **timeline observer:** prints authored event order and explicit timestamps; unknown time remains `NOT_RECORDED`.
- **operable registry:** distinguishes proposed, staged, read-only, PREPARE_ONLY, and NOT_IMPLEMENTED modules.
- **readiness capacitor:** requires all declared checks plus independently verified human review; it is a boolean gate, not a numeric confidence score.
- **local terminal:** lists, validates, and displays records; it has no command execution or external dispatch.
- **Repository Eyes:** recursively maps the checked-out repository into eight onion layers, hashes only eligible bounded files, marks sensitive paths/content and symlinks as red holds, and classifies binaries/unknown formats for review.
- **offline dashboard:** `Ɣơ/operations/ui/index.html` renders a supplied inventory JSON or .coddoc record locally; it has no network calls or upload path.
- **watch policy:** GitHub repository events are read-only; Firecrawl is disabled until individually approved hostnames exist.
- **notification adapter:** sends email only when the registry record is explicitly READY_TO_OPEN and all checks pass. SMTP credentials are supplied as GitHub Actions secrets, never committed.

### 4. Narrative record model

Each `.coddoc` event retains:
- stable event ID and authored sequence;
- recorded occurrence time or null;
- source references and evidence classification;
- source observation kept separate from interpretation;
- status and artifact digest where available.

Corrections are additive. Do not overwrite a prior observation to make a newer interpretation appear original. A digest checks byte integrity; it does not prove truth, permission, independence, or completeness.

### 5. Operable readiness

An artifact may become **READY_TO_OPEN** only when:
1. the .coddoc record validates;
2. Python tests, native build (when applicable), and read-only inventory pass on the exact commit;
3. a reviewable artifact exists within the repository;
4. source provenance is present;
5. an independent human reviewer is cryptographically verified and approves the exact artifact/scope;
6. the readiness record still states `live_execution_enabled=false`.

"Ready to open" means a person can inspect a bounded artifact. It is not permission to merge, publish, deploy, send money, or run an external process.

### 6. Trading and financial boundary

No automated live trading binary, broker adapter, exchange API, key store, or order-submission path is created here. A later paper-replay module may consume user-supplied historical datasets offline and label every result as simulated. Live trading is excluded until the independent security and authorization requirements in `Ɣơ/finance/SECURITY-AND-LIVE-GATE.md` are met and separately approved.

### 7. Web observation policy

Firecrawl is not enabled for every `.com`, `.org`, `.net`, `.co`, `.web`, or other TLD. TLD membership is not consent or permission. The adapter accepts only explicit exact hostnames, requires HTTPS, rejects local/private/reserved destinations, and validates the returned source and final redirect URLs against the same host allowlist. `.local` is blocked. The current allowlist is empty.

The labels **Fah**, **.wrkply**, and **Sunflowers** are preserved as unresolved source labels until their owners, URLs/API schemas, and intended data scopes are identified. The existing `.runflw` concept is mapped to the canonical ERIA Runflow protocol.

### 8. Run commands

From the repository root:

```sh
python -m pip install -e './Ɣơ/operations[test]'
PYTHONPATH='Ɣơ/operations/src' python -m gamma_ops.cli validate 'Ɣơ/operations/events/TRUE-LIGHTWORK-WAVE-MAVEN.coddoc'
PYTHONPATH='Ɣơ/operations/src' python -m gamma_ops.cli timeline 'Ɣơ/operations/events/TRUE-LIGHTWORK-WAVE-MAVEN.coddoc'
PYTHONPATH='Ɣơ/operations/src' python -m gamma_ops.cli catalog
PYTHONPATH='Ɣơ/operations/src' python -m gamma_ops.cli ready
PYTHONPATH='Ɣơ/operations/src' python -m gamma_ops.cli scan . --output /tmp/eria-repository-eyes.json
```

Open `Ɣơ/operations/ui/index.html` locally and select the generated JSON report to inspect the eight layers. The browser UI only reads the chosen file and renders text.

These commands read and display records only. They do not activate a watcher, crawl a website, authorize an action, launch a process, or place a trade.

### 9. Email readiness notification

The IC workflow has a notification job that reads the operable registry after validation jobs succeed. To enable email delivery, configure a repository variable `OPERABLE_NOTIFY_TO` and Actions secrets `OPERABLE_SMTP_HOST`, `OPERABLE_SMTP_PORT`, `OPERABLE_SMTP_USER`, `OPERABLE_SMTP_PASSWORD`, and `OPERABLE_SMTP_FROM`. A mail is sent only for records meeting the READY_TO_OPEN checks. Missing configuration produces a visible skip; it never claims a message was delivered.

### 10. Acceptance statement

The observer and narrative record are an additive integration layer. They preserve prior event lineage, expose uncertainty, and keep read-only observation distinct from authority. The current state is **NOT_READY** pending validation of these new files and independent review.
