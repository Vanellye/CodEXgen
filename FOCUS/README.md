# FOCUS — English Repository Guide

**Purpose:** give a plain-English map of ERIA, starting with the work that is most necessary to protect people, source integrity, and reliable operation.

**Source anchor:** `2590ef3001d0f79b7cef7955c97c0894f0e31283`  
**Repository:** `Vanellye/CodEXgen`  
**Status:** navigation and interpretation index; not an approval, deployment, or execution instruction.

## Read in order of necessity

### 0. Stop conditions and safety boundaries — read first

These files define what the system must not do without authority.

- [Code ethics](../docs/CODE-ETHICS.md) — human authority, least privilege, provenance, evidence, privacy, reversibility, and fail-closed behavior.
- [PONS remote approval contract](../docs/PONS-REMOTE-APPROVAL.md) — how signed, time-limited, capability-scoped approvals are checked; a verifier is not itself permission to write.
- [Isolated execution](../docs/ERIA_ISOLATED_EXECUTION.md) — the fixed-command, one-use approval, temporary-workspace runner and its limits.
- [TRUE NORTH implementation status](../docs/TRUE-NORTH-IMPLEMENTATION-STATUS.md) — branch-specific implementation evidence and known limitations.

**Immediate source issue at this anchor:** `tools/eria_aei_server.py` contains malformed literal backslash-`n` sequences in route-dispatch code. Repair only the verified code separators; preserve legitimate newline escapes inside strings. Keep the original bytes and record the candidate hash separately. This index does not apply that repair.

### 1. Preserve original data and its history

- [Data Vault](../docs/ERIA_DATA_VAULT.md) — commit-anchored acquisition, original-byte objects, and append-only provenance manifests.
- [Storage guide](../storage/README.md) — inbox, acquisition records, compiled inspection snapshots, manifests, and settings.
- [Repository engineering](../docs/ERIA_REPOSITORY_ENGINEERING.md) — repository-level design and preservation practices.
- [Root filesystem inventory](../docs/ROOT-FILESYSTEM-INVENTORY.md) — inventory and organization context.

**Plain English:** keep the original file unchanged; store translations, indexes, repairs, and interpretations as separate derived records. Link every derived record to the exact source path, commit, and digest.

### 2. Translate source into understandable English

- [Higher Faculty inspection](../docs/ERIA_HIGHER_FACULTY_INSPECTION.md) — reads source and creates line-anchored English explanations.
- [Âï higher-faculty conversation](../docs/ERIA_AII_HIGHER_FACULTY.md) — asks questions about purpose, dependencies, conflicts, security indicators, improvements, and comparisons.
- [Æị local interface](../docs/AEI-LOCAL-INTERFACE.md) — local browser bridge for read-only inspection.
- [AI / higher-faculty source](../tools/eria_pantheon/ai.py) — conversational analysis adapter.
- [Higher-faculty source](../tools/eria_pantheon/higher_faculties.py) — deterministic source-to-English analysis pipeline.
- [Pantheon interface source](../tools/eria_pantheon/interface.py) — command routing into the ERIA capabilities.

**Interpretation rule:** an English explanation is a review aid, not the source of truth. Mark inferred meaning as inferred. Static indicators are not proof of malicious intent, emotion, or actual runtime behavior.

### 3. Understand approvals, patching, and data movement

- [Approval verifier](../tools/eria_pantheon/approval.py) — validates signed capability grants, scope, expiry, and replay constraints.
- [PONS policy module](../tools/eria_pantheon/pons.py) — reports and enforces application-level authorization decisions.
- [Exact patch executor](../tools/eria_pantheon/patch_executor.py) — bounded exact-patch path; must remain blocked without matching approval.
- [Isolated runner source](../tools/eria_pantheon/isolated_runner.py) — fixed allowlisted commands in an isolated temporary workspace.
- [Relay lifecycle source](../tools/eria_pantheon/relay_lifecycle.py) — lifecycle coordination for the local relay.
- [Data vault source](../tools/eria_pantheon/data_vault.py) — source acquisition and provenance storage.

**Current governance for this work:** candidate commits may be made on feature branches and reviewed integration branches. Keep `main` unchanged. Do not inject patches, execute privileged operations, or deploy development builds until the applicable PONS approval is verified.

### 4. Application interfaces and device integration

- `interfaces/` — browser interfaces and local portals.
- `tools/eria_aei_server.py` — local Æị HTTP bridge; inspect and repair before relying on the anchor version.
- `tools/eria_conversation_server.py` — local conversational server.
- `termux/` — Android/Termux integration and operating instructions.
- `app/` — Android application source.
- [Android client guide](../README-ANDROID-ERIA.md) — package identity, server connection, and build requirements.

### 5. Build, tests, and generated output

- `.github/workflows/` — CI and manually dispatched validation workflows.
- `tests/` — repository-level regression tests.
- `tools/tests/` — Higher Faculty and conversational-analysis tests.
- `pantheon/tests/` — Pantheon contract tests.
- `compose/` and `generated_modules/` — generated or mirrored outputs; confirm their source-of-truth rules before editing them directly.
- `gradle/`, `build.gradle.kts`, and `settings.gradle.kts` — Android build configuration.

A passing workflow proves only the steps it actually ran. Check the workflow's test-discovery paths before treating a test suite as covered.

### 6. Research, hypotheses, and legacy material

- `hypotheticals/` — explicitly hypothetical material; do not relabel it as verified evidence.
- `docs/` — architecture, governance, history, and subsystem explanations.
- `EDIFY.md`, `HEROES.md`, `NEW.md`, and other narrative records — preserve as source material; translate or summarize separately rather than silently rewriting them.

## Plain-English directory map

| Repository path | What it contains |
|---|---|
| `app/` | Android application code |
| `compose/` | generated/mirrored Kotlin source |
| `docs/` | architecture, governance, and operating guides |
| `generated_modules/` | generated code output |
| `hypotheticals/` | explicitly hypothetical examples |
| `interfaces/` | HTML user interfaces |
| `pantheon/` | Pantheon runtime and language contracts |
| `python/` | Python tools, demos, and generators |
| `security/` | security-related assets and controls |
| `shared/` | shared application components |
| `storage/` | acquisition and derived-data directories |
| `termux/` | Android shell integration |
| `tests/` | repository-level tests |
| `tools/` | ERIA servers, adapters, analyzers, and utilities |

## English translation record format

For each future translated or explained source item, record:

- source repository-relative path;
- source commit and Git blob identity;
- source SHA-256;
- language and detected format;
- line range or symbol name;
- plain-English explanation;
- whether the explanation is observed, inferred, or unknown;
- confidence and review state;
- derived-record hash and parent lineage.

Never replace the original source with its English explanation. Keep source and interpretation as separate artifacts.

## SAVEs principle

**Save All Victory's Everything.**

> Preserve the victory. Preserve the journey. Preserve the source.

Store achievements, failed attempts, repairs, evidence, and their lineage without overwriting the original history. The `ị/` marker is a diagnostic lineage/story marker, not a substitute for valid source syntax or functional newline escapes.

---

This guide is a prioritized starting index, not a claim that every file has already been translated or independently verified. Expand it from the actual repository tree and update the evidence status as each source is reviewed.
