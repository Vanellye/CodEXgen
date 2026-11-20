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

| Existing source | Verified role | Integration boundary |
|---|---|---|
| `docs/ERIA-RUNFLOW-OPERATING-PROTOCOL.md` | Origin → Intent → Authorization → Execution → Evidence → Review → Recovery → Learning → New Growth | Canonical narrative state model; documentation alone does not start a background process |
| `pantheon/NEW/README.md` | Consent-based narrative proposal layer | Staged; not wired into runtime |
| `app/src/main/java/com/vanellye/eria/pantheon/PantheonRuntimeGate.kt` | Android envelope validation and review presentation | `actionTaken=false`; no executor or provider/network writer |
| `pantheon/IC/README.md` | Integration Core gate contract | Caller-supplied checks are not cryptographic proof or execution authorization |
| `docs/BRANCH-DIRECTORY-ACOUSTIC.md` | Historical source/branch cross-reference | Records past branch names; does not prove they remain live |
| `docs/TRUE-NORTH-IMPLEMENTATION-STATUS.md` | Historical branch implementation snapshot | Evidence about the recorded snapshot, not current runtime |
| `Ɣơ/finance/src/gamma_finance/runflow.py` | Prepare-only withdrawal proposal lifecycle | No live executor; proposal is not an order |

Historical directory entries for `pantheon/signed-package-exchange` (PR #13), `pantheon/source-digest-engine` (PR #11), and `pantheon/cpp-html-consent-engine` remain lineage references only; they are not silently copied or activated.

### 3. Proposed repository modules

`Ɣơ/operations/` contains:
- **.coddoc reader:** validates a versioned JSON narrative record, hashes its bytes, and preserves source references.
- **timeline observer:** prints authored event order and explicit timestamps; unknown time remains `NOT_RECORDED`.
- **operable registry:** distinguishes proposed, staged, read-only, PREPARE_ONLY, and NOT_IMPLEMENTED modules.
- **readiness capacitor:** requires all declared checks plus independently verified human review; it is a boolean gate, not a numeric confidence score.
- **local terminal:** lists, validates, and displays records; it has no command execution or external dispatch.
- **Repository Eyes:** recursively maps a checked-out repository into eight onion layers, hashes only eligible bounded files, marks sensitive paths/content and symlinks as red holds, and classifies binaries/unknown formats for review.
- **offline multi-report dashboard:** `Ɣơ/operations/ui/index.html` opens multiple inventory JSON and .coddoc records in one session, labels every row by repository, and aggregates L0–L7.
- **installable PWA shell:** `manifest.webmanifest`, `service-worker.js` and the icon cache only local static UI assets. No repository data is uploaded or sent to a remote service.
- **watch policy:** GitHub repository events are read-only; Firecrawl is disabled until individually approved hostnames exist.
- **notification adapter:** sends email only for new READY_TO_OPEN transitions after independently signed review and all required checks. SMTP credentials are supplied only to the protected-main workflow, never pull-request code.

### 3A. Multi-repository Repository Eyes

Repository Eyes is a reusable local scanner, not a single-repository parser. Each run can attach the repository name, branch, checked-out commit SHA, PR head SHA, base SHA and event type. The scanner inspects only the selected checkout working tree; it does not assume that the PR head SHA equals the checkout SHA and does not infer other branches or linked repositories from one scan.

The offline dashboard accepts multiple Repository Eyes JSON reports and multiple .coddoc files in one session. It labels every row by repository identity, displays the recorded branch and commit context, and aggregates the L0–L7 layer counts while retaining distinct repository records. Missing identity metadata remains unknown, not guessed from directory names.

For local cross-repository review, obtain each repository independently, run `gamma_ops.cli scan` separately for each checkout with its exact identity arguments, and load all JSON reports into the dashboard. The current GitHub Actions workflow scans only `Vanellye/CodEXgen`; account-wide GitHub discovery or automatic scans of every repository are not yet implemented.

### 4. Narrative record model

Each `.coddoc` event retains a stable event ID and authored sequence, a recorded occurrence time or null, source references and evidence classification, an observation kept separate from interpretation, and its state. Corrections are additive. A digest checks byte identity; it does not prove truth, permission, independence or completeness.

### 5. Operable readiness

An artifact may become **READY_TO_OPEN** only when:
1. the .coddoc record validates;
2. Python tests, native build (when applicable), and read-only inventory pass on the exact commit;
3. a reviewable artifact exists within the repository;
4. source provenance is present;
5. an independent human reviewer approves the exact artifact/scope with an Ed25519 signature verified against a reviewer registry whose digest is pinned outside the PR-controlled tree;
6. the readiness record still states `live_execution_enabled=false`.

"Ready to open" means a person can inspect a bounded artifact. It is not permission to merge, publish, deploy, send money, or run an external process. An absent registry hash pin, invalid or revoked signature, stale approval, or digest/scope/commit mismatch produces HOLD.

### 6. Trading and financial boundary

No automated live trading binary, broker adapter, exchange API, key store or order-submission path is created here. A later paper-replay module may consume user-supplied historical datasets offline and label every result as simulated. Live trading is excluded until the independent security and authorization requirements in `Ɣơ/finance/SECURITY-AND-LIVE-GATE.md` are met and separately approved.

### 7. Web observation policy

Firecrawl is not enabled for every `.com`, `.org`, `.net`, `.co`, `.web` or other TLD. TLD membership is not consent or permission. The adapter accepts only explicit exact hostnames, requires HTTPS, rejects local/private/reserved destinations, and validates returned source and final redirect hostnames. `.local` is blocked. The current allowlist is empty.

The labels **Fah**, **.wrkply**, and **Sunflowers** remain unresolved until their owners, URLs/API schemas and intended data scopes are identified. `.runflw` maps to the canonical ERIA Runflow protocol.

### 8. Run commands

From the repository root:

```sh
python -m pip install -e './Ɣơ/operations[test]'
PYTHONPATH='Ɣơ/operations/src' python -m gamma_ops.cli validate 'Ɣơ/operations/events/TRUE-LIGHTWORK-WAVE-MAVEN.coddoc'
PYTHONPATH='Ɣơ/operations/src' python -m gamma_ops.cli timeline 'Ɣơ/operations/events/TRUE-LIGHTWORK-WAVE-MAVEN.coddoc'
PYTHONPATH='Ɣơ/operations/src' python -m gamma_ops.cli catalog
PYTHONPATH='Ɣơ/operations/src' python -m gamma_ops.cli ready
PYTHONPATH='Ɣơ/operations/src' python -m gamma_ops.cli scan . --repository 'owner/repository' --branch 'main' --commit-sha '<checked-out-sha>' --output /tmp/eria-repository-eyes.json
```

For a local installable app, run:

```sh
bash 'Ɣơ/operations/scripts/serve-ui.sh'
```

Then open `http://127.0.0.1:8765/` on the same device and use the browser's install option where available. Keep the local server running while the app is open. The service worker caches only the UI shell. The app reads user-selected report files locally, does not upload them, and does not fetch from websites. To compare repositories, repeat the scanner command for each local checkout and select the resulting reports together.

These commands read and display records only. They do not activate a watcher, crawl a website, authorize an action, launch a process, or place a trade.

### 9. Email readiness notification

Email is attempted only by the IC workflow after a push to protected `main` and after all required validation jobs pass; SMTP secrets are not exposed to pull-request code. To enable delivery, configure `OPERABLE_NOTIFY_TO`, protected repository variable `ERIA_REVIEWER_REGISTRY_SHA256` with the digest of the independently administered `Ɣơ/operations/registry/reviewers.json`, and Actions secrets `OPERABLE_SMTP_HOST`, `OPERABLE_SMTP_PORT` (SSL), `OPERABLE_SMTP_USER`, `OPERABLE_SMTP_PASSWORD`, and `OPERABLE_SMTP_FROM`. The notifier compares the prior registry to the current one and emails only on a new READY_TO_OPEN transition. Missing config or a missing/mismatched registry pin means HOLD; no email is reported as sent unless SMTP confirms success.

### 10. Acceptance statement

The observer and narrative record are additive integration layers. They preserve event lineage, expose uncertainty, and keep read-only observation distinct from authority. The current state is **NOT_READY** pending validation of the latest code and independent review.
