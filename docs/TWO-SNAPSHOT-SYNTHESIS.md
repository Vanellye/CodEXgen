# Two-Snapshot Synthesis: Evidence Before Integration

## Compared snapshots

- Main snapshot: `a02629956deda7db4416cdbb1bc9b3c5badf90a0`
- Stride snapshot: `a8c6a90efc09e27afbead0f07191e17bf4faa431`
- Repository: `Vanellye/CodEXgen`
- Common ancestor reported by GitHub compare: `a02629956deda7db4416cdbb1bc9b3c5badf90a0`
- Relationship: divergent; Stride snapshot is 285 commits ahead and 3 commits behind the Main snapshot in this comparison.

This is a comparison record, not a merge. Neither history is rewritten, and neither snapshot is declared the owner of the other.

## What the evidence says

### Main snapshot

The Main snapshot is a smaller Android Compose/Kotlin baseline with its own Gradle Kotlin DSL configuration. It includes the legacy hypothetical Python module with malformed numeric expressions.

### Stride snapshot

The Stride snapshot contains a much broader implementation trail, including:

- Android API 11 native Views/Java compatibility work and JNI/C++ bridge work
- Git Freedom bridge and workspace import
- Pantheon C++ runtime and contract tests
- portable framework and host simulator
- Geometry knowledge/laboratory material
- local-first Stride JOB lifecycle, transfer, history, and reconciliation
- Holified Inception contextual reader and evidence distinctions
- consent review and stewardship documentation
- independent branch CI and provenance/legacy-peering guidance

These are observed repository contents and commit subjects, not a claim that every feature is production-ready.

## Important divergence: Android build architecture

The Stride snapshot removes the Kotlin/Compose Gradle Kotlin DSL files and introduces Groovy Gradle configuration and a Java Views application entry point. The Main snapshot still has Kotlin/Compose source and Kotlin DSL build configuration.

Therefore, copying the router or the whole Stride tree into Main without an integration plan risks a mixed or inconsistent Android build. The router must be evaluated against the target build system and API profile, not simply copied because it exists on the Stride side.

## Important divergence: legacy syntax

The Stride history includes a later edit to `hypotheticals/bio_resonance_fiction.py` that changes the malformed expressions to:

- `range(0, 16, 2)`
- `int(level * 20)`
- `level * 1.1`

That makes the expressions syntactically valid, but the chosen numeric semantics are assumptions. The module itself identifies its content as fiction. The Main snapshot retains the malformed glyphs. Preserve both states as evidence; review the intended values and fictional output semantics before proposing a repair to Main.

## Shared principles that can be carried forward without merging code

1. Preserve source history and provenance.
2. Treat branches as independent contributors; map and test interfaces before peering.
3. Keep proposed interpretations separate from original recorded events.
4. Require explicit authorization for consequential writes.
5. Prefer reversible, additive changes and independent validation.
6. Keep speculative or fictional content clearly labeled; do not promote it to scientific evidence.
7. Keep human review and user consent visible at integration boundaries.

## Integration sequence

1. Review this comparison and confirm the intended target build architecture.
2. Validate the router in isolation, including Android compile, authentication lifecycle, transport, and workspace overwrite behavior.
3. Decide which Stride components have clear interfaces with Main; do not bulk-merge 285 commits.
4. For each selected component, make a small additive peering change with provenance, tests, and a rollback path.
5. Keep the legacy syntax repair separate until intended numeric semantics are confirmed.
6. Re-run CI on the exact candidate head and review each result before merge.

## Truth statement

A branch being newer, larger, or more capable does not make it universally correct. A baseline being called Main does not make it the owner of every contribution. The defensible synthesis is the set of claims that survive provenance checks, interface review, reproducible tests, and human scrutiny.

**No merge, deletion, force update, or source rewrite is performed by this synthesis record.**

## Shared principle: careful memory, free creation

This principle is intended to be reusable by Stride, the Git Freedom Bridge, and future CodEXgen branches without making Main the owner or authority over their identities.

> **Remember what matters. Preserve what happened. Leave room for what has never happened before.**

### Memory responsibilities

- Preserve original records, authorship, timestamps, source references, and provenance.
- Keep corrections, interpretations, and derived views separate from original events.
- Cross-reference related work without collapsing distinct branch or contributor identities.
- Retain decisions, lessons, dependencies, unresolved questions, and review history.
- Label evidence as verified, proposed, hypothetical, fictional, or unknown.
- Never silently rewrite or discard historical knowledge.

### Creation responsibilities

- Permit independent branches and experiments to explore directions not already represented in memory.
- Offer connections as suggestions, not as facts or commands.
- Allow components and ideas to evolve independently while retaining links to their origins.
- Do not require creative work to conform to a central branch's structure or vocabulary.
- Require explicit human authorization for consequential changes to shared state.

### Shared boundary

Memory may inform creation, but must not imprison it. Creation may extend history, but must not falsify it.

Main is a meeting point and shared index, not the owner of branch identity, authorship, or independent work. A branch may adopt this principle, adapt its implementation, or retain a different local expression while preserving provenance and compatibility at explicitly reviewed interfaces.

### Suggested implementation boundaries

These are separable capabilities, not mandatory directories or a central service:

- **Memory:** append-only records and historical references.
- **Context:** cross-references and relationships between records.
- **Provenance:** origin, authorship, timestamps, and evidence status.
- **Imagination:** independent proposals and creative exploration.
- **Reflection:** comparison, critique, and lessons learned.
- **Stewardship:** consent, review, and safeguards for consequential actions.

Each branch can implement, replace, or omit a capability independently. Peering requires a documented interface and relevant tests; it does not require shared internal implementation or surrender of branch identity.

## Three evidence gates for peering

These gates make the truth statement actionable. They are review practices, not a central authority or a requirement that every branch use the same internal design.

### 1. Provenance checks — where did this come from?

For each proposed component or change, record:

- Source repository, branch, and exact commit SHA.
- Original file path and, when relevant, the source blob or content hash.
- Author/contributor attribution where available; do not infer missing authorship.
- Whether the material is original, copied, adapted, generated, or externally supplied.
- Any license, attribution, or usage constraints that are known; mark unknowns for review.
- The transformations made during extraction or adaptation, with links to the untouched source.
- Evidence status: observed, tested, proposed, hypothetical, fictional, or unknown.

**Pass condition:** another reviewer can trace the candidate back to its origin and distinguish original material from later interpretation. Missing provenance is recorded as a gap, not filled by guesswork.

### 2. Interface review — how will the parts meet?

Before connecting components, document:

- The public inputs, outputs, events, and expected side effects.
- Data formats, version assumptions, error behavior, and resource/lifecycle ownership.
- Runtime, platform, build-tool, and dependency requirements.
- Permission boundaries, secrets handling, network access, and any destructive or externally visible operation.
- Compatibility adapters or version negotiation needed between the two sides.
- What remains independent and what is intentionally shared.
- A rollback or disable path that does not destroy either source.

Review both directions: what the candidate expects from its host, and what it exposes to other components. Prefer a narrow adapter over copying an entire branch or making one branch adopt another's internal architecture.

**Pass condition:** the boundary is understandable, bounded, and reviewable; incompatible assumptions and unresolved risks are explicitly listed. A documented interface is not proof of runtime compatibility.

### 3. Reproducible tests — can another person verify it?

For each candidate, preserve:

- Exact source commit and test commit SHA.
- Toolchain, runtime, SDK, dependency versions, and relevant configuration.
- Exact commands or workflow used, including required environment variables with secret values omitted.
- Test fixtures and expected outcomes; use deterministic fixtures where possible.
- Results for unit, integration, compatibility, security-sensitive, and build checks as applicable.
- Logs or artifact references, timestamps, and artifact hashes where available.
- Known skipped tests, flaky tests, platform gaps, and manual-only checks.

A test result applies only to the exact commit and environment recorded. A passing compile does not prove correct behavior, security, or device compatibility. A skipped or unavailable test is **not verified**, not a pass.

**Pass condition:** an independent reviewer can rerun the stated checks and compare outcomes against the recorded evidence. Any non-reproducible result remains qualified.

### Review outcome

Use one of four explicit outcomes for each proposed peering:

- **Ready for limited trial:** all relevant gates have evidence; remaining limitations are bounded and accepted.
- **Needs revision:** a specific provenance, interface, or test gap can be corrected.
- **Hold for evidence:** source, behavior, compatibility, or risk is not yet understood.
- **Do not peer:** the change conflicts with consent, safety, licensing, integrity, or an independent branch's stated boundaries.

A pass never authorizes a merge by itself. The affected contributors retain their own decision rights, and consequential shared changes still require explicit authorization.

