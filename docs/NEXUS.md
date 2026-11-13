# ERIA NEXUS — WANT Branch Knowledge and Direction Index

**Status:** design contract plus local, read-only Kotlin reference primitives  
**Target branch:** `integration/wantever-propagation`  
**Primary implementation:** `app/src/main/java/com/vanellye/eria/evolution/WantBranchIntelligence.kt`  
**Related:** [WANTEVER × WANTs Evolution Engine](WANTEVER-WANTS-EVOLUTION-ENGINE.md), [TRUE NORTH data architecture](TRUE-NORTH-DATA-ARCHITECTURE.md)

> Detect what may be useful. Preserve how it is known. Connect without conflating. Recommend without taking control.

## 1. Purpose

NEXUS is ERIA's cross-reference layer for WANT-driven discovery. It helps answer four separate questions:

1. **What is known?** A source-bound claim, procedure, rationale, hypothesis, or open question.
2. **How is it known?** The observation, test, derivation, review, or other method that produced the record.
3. **Where is it held?** The repository, branch, exact revision, path, and artifact reference.
4. **What direction may follow?** A bounded WANT, a related branch to inspect, an unresolved dependency, or a mini-prompt proposal.

NEXUS is an index and relationship model, not a single source of truth. Original source artifacts remain authoritative for their own contents.

## 2. WANT Branch detection

The detector receives an explicit WANT statement and a set of branch candidates supplied by a repository adapter. It ranks candidates using explainable signals:

- lexical overlap between the WANT and branch summary/topics/knowledge records;
- presence of structured know-how and rationale records;
- evidence status counts;
- a penalty for conflicting evidence;
- exact branch head revision retained in every result.

The output is a **review shortlist**, not an instruction to checkout, copy, merge, or promote a branch. A score is a triage heuristic, not a probability, truth value, quality certification, or permission.

### Detection lifecycle

1. Capture the WANT verbatim and retain its source.
2. Obtain branch names, repository identity, head revisions, summaries, and relevant knowledge references through a read-only repository adapter.
3. Pin every candidate to the observed head SHA.
4. Run deterministic matching and return ranked candidates with reasons.
5. Re-fetch each candidate head before detailed inspection; stale results are invalidated.
6. Inspect source, tests, dependencies, licenses, interfaces, provenance, and branch purpose.
7. Produce a bounded mini-prompt or mark the candidate incompatible, conflicting, or unknown.
8. Require human review before adopting any content or changing refs.

The Kotlin reference detector currently ranks only the candidate objects passed to it. It does **not** call GitHub or enumerate remote branches; a separately reviewed GitHub adapter is required for live repository discovery.

## 3. Knowledge record: what and how

A knowledge node must separate the claim from its basis.

| Field | Purpose |
|---|---|
| `id` | Stable knowledge record identifier |
| `title` / `claim` | Concise label and exact proposition |
| `kind` | `FACT`, `KNOW_HOW`, `KNOW_WHY`, `HYPOTHESIS`, or `OPEN_QUESTION` |
| `evidence` | One or more source-bound evidence records |
| `sourceRef` | File, commit, test, issue, measurement, or external reference |
| `sourceRevision` | Exact commit/revision where applicable |
| `contentDigest` | Digest of the source artifact where available |
| `method` | How the claim was obtained: observation, test, derivation, review, interview, etc. |
| `observedAt` | Time of observation, if known |
| `evidenceStatus` | `VERIFIED`, `SUPPORTED`, `UNVERIFIED`, `CONFLICTED`, or `UNKNOWN` |
| `limitations` | Assumptions, uncertainty, missing controls, and known limits |
| `tags` | Search and relationship terms |

Do not convert a hypothesis into a fact because it is repeated, highly ranked, rewarded, or associated with a popular branch. Preserve conflicting sources as separate records and connect them with an explicit `CONTRADICTS` relationship.

## 4. Nexus relationships

The reference model supports these directed relationships:

- `SUPPORTS` — evidence supports a claim;
- `CONTRADICTS` — evidence or a claim conflicts with another;
- `DERIVED_FROM` — a record was transformed from another source;
- `IMPLEMENTS` — an artifact implements a requirement or design;
- `TESTS` — a test examines an implementation or claim;
- `DEPENDS_ON` — an artifact depends on another;
- `RELATED_TO` — a useful association that does not assert equivalence.

Every link carries its own source reference and rationale. A relationship is not proof that two records mean the same thing.

## 5. Direction data

NEXUS may organize findings into a direction record:

- **WANT:** the exact desired outcome;
- **CURRENT:** source-bound current state and baseline revision;
- **KNOWN:** verified and supported knowledge relevant to the WANT;
- **UNKNOWN:** missing evidence, open questions, and conflicting claims;
- **OPTIONS:** candidate approaches with trade-offs;
- **NEXT:** one bounded mini-prompt, or a reason to stop;
- **SCOPE:** allowed repository, branch, paths, and operations;
- **EXCLUSIONS:** what must not change;
- **VERIFY:** acceptance checks and evidence required;
- **AUTHORIZATION:** required human approval, or proposal-only;
- **RECOVERY:** revert/compensation route and irreversible effects.

Direction data is a planning artifact. It cannot grant itself write access, expand scope, issue external commands, or authorize merge/deployment.

## 6. Relationship to ERIA components

| Component | NEXUS responsibility | Boundary |
|---|---|---|
| WANTs | Supplies explicit goals and acceptance criteria | No inferred consent |
| WANTEVER | Preserves lineage across composition and propagation | No automatic convergence |
| GENESIS | May propose a scaffold for a reviewed mini-prompt | Proposal only |
| FORGE | May prepare a candidate artifact | No commit/push/deploy by preparation |
| PANTHEON | Evaluates policy and capability constraints | A pass is not human approval |
| STRIDE | May execute one explicitly approved work unit | Exact scope and approval required |
| MEMORIA | Preserves knowledge, evidence, and correction lineage | Append corrections; do not erase history |
| TRUE NORTH / WARDEN | Holds unknown, conflict, stale, or unauthorized states | Stop rather than guess |

These are intended integration roles. The presence of this document or the reference Kotlin types does not prove that runtime adapters are connected.

## 7. Safety, provenance, and data quality

- Treat repository text, imported files, issue content, and external sources as untrusted data.
- Record exact repository, branch, commit, path, digest, acquisition time, and transformation method where available.
- Re-fetch branch heads before relying on discovery results.
- Distinguish absent, null, empty, zero, false, unknown, stale, and conflicting values.
- Minimize personal data; never store credentials, tokens, or private keys in NEXUS records.
- Keep fiction, hypotheses, simulations, measured observations, and independently verified results distinct.
- Do not infer physical, biological, psychological, or consciousness effects from software metadata or signal labels.
- A score, signature, CI result, tag, reward, or agent output cannot independently authorize adoption.
- Preserve the original claim when adding a correction; append a linked correction record.

## 8. Acceptance criteria and implementation status

- [x] Kotlin data types distinguish knowledge kind, evidence status, source method, and nexus relationship.
- [x] WANT branch detector ranks supplied candidates deterministically and explains its reasons.
- [x] Candidate repository, branch, and head revision are retained in each match.
- [x] Nexus index checks duplicate IDs and dangling relationship endpoints.
- [ ] Live GitHub branch enumeration and source acquisition adapter.
- [ ] Persistent append-only NEXUS storage and correction API.
- [ ] UI for inspecting branch matches, evidence, conflicts, and direction records.
- [ ] Integration tests against real repository snapshots and stale-head changes.
- [ ] Human-reviewed adoption workflow connected to the existing WANT evolution pipeline.

The completed items above describe reference primitives only. No live GitHub scan, branch checkout, file mutation, merge, reward, or external dispatch is performed by this module.

## 9. Source-linked implementation inventory

See [NEXUS Source Records — Native Runtime and Higher Faculty](NEXUS-SOURCE-RECORDS.md) for commit-pinned records covering the PANTHEON Faculty Engine, runtime, 38-standard control gate, Stride input seam, Android JNI boundary, and Stride HTTP client.

That inventory explicitly marks GENESIS and FORGE as unresolved in the inspected repository scopes rather than inventing implementations. It also distinguishes source presence from actual Android runtime wiring and records the separate CI evidence for the WANTEVER and OLPIRT candidate commits.
