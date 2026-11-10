# Legacy Preservation & Independent Peering Protocol

**Status:** Governing project protocol  
**Working branch:** `olpirt/stride-next`  
**Scope:** Legacy source, branches, artifacts, extracted components, interfaces, dependencies, and future integrations.

## Commitment

Preserve original source and provenance. Identify interfaces, dependencies, and historical behavior. Keep legacy artifacts immutable as historical evidence. Allow extracted components to evolve independently. Establish compatibility through explicit, tested peering. Never interpret age or isolation as permission to erase.

This protocol applies before a legacy component is refactored, extracted, replaced, wrapped, ported, or connected to another component. It complements, and does not replace, repository-specific security, privacy, licensing, safety, and release requirements.

## Six requirements

### 1. Preserve original source and provenance

- Record repository, branch or tag, exact commit SHA, path, author/attribution where available, and retrieval date.
- Preserve original history and source context; do not rewrite, silently normalize, or overwrite the historical artifact.
- Record licenses, notices, third-party origin, and known restrictions.
- Distinguish observed provenance from assumptions or incomplete records.
- If provenance cannot be established, mark it unknown and hold consequential reuse pending review.

### 2. Identify interfaces, dependencies, and historical behavior

Before changing or extracting a component, document:

- public APIs, command-line contracts, file formats, schemas, events, and network interfaces;
- direct and transitive dependencies, toolchain versions, runtime assumptions, and platform constraints;
- callers, consumers, side effects, persistence behavior, error handling, and permission boundaries;
- historical behavior, including edge cases and known defects that consumers may rely on;
- tests, CI coverage, compatibility promises, and gaps in evidence.

A dependency map is a hypothesis until confirmed against source, build metadata, runtime evidence, or tests. Label unknowns explicitly.

### 3. Keep legacy artifacts immutable as historical evidence

- Store the original artifact and its provenance as a read-only reference.
- Record hashes or other integrity evidence where practical.
- Put corrections, annotations, adapters, and migration outputs in new paths or commits.
- Link every derivative to the exact source artifact and transformation.
- Never silently replace the historical source with a “fixed” copy.
- If an artifact must be quarantined for safety or legal reasons, preserve a controlled audit record and restrict access as appropriate; immutability does not require unsafe public distribution.

### 4. Allow extracted components to evolve independently

- Give an extracted component a clear identity, owner/steward, version, source lineage, and documented interface.
- Separate its new implementation from the preserved legacy artifact.
- Permit independent tests, release cadence, dependency choices, and maintenance.
- Keep adapters or compatibility shims explicit and removable.
- Do not make extraction imply transfer of ownership, authority, or permission to rewrite the source.

### 5. Establish compatibility through explicit, tested peering

Peering is a documented relationship between independently maintained components. It is not a merge, inheritance, or ownership claim.

Before peering, require:

1. a named interface and version or schema;
2. an explicit dependency and data-flow map;
3. authorization for any consequential transfer or write;
4. contract tests for inputs, outputs, errors, and boundary behavior;
5. compatibility tests for supported versions and platforms;
6. provenance and integrity checks for exchanged artifacts;
7. security, privacy, licensing, and recovery review appropriate to the connection;
8. a human-readable decision record, including limitations and rollback/disconnection steps.

A passing test proves only the tested scope. Do not claim full compatibility from a compile, a single integration test, or a successful build of one consumer.

### 6. Never interpret age or isolation as permission to erase

- Age, inactivity, divergence, missing CI, unrelated ancestry, or lack of a current maintainer is not deletion authority.
- Mark uncertain or unsupported components as unknown, stale, isolated, or held; do not label them defective without evidence.
- Keep source branches and histories intact while evaluating future integration.
- Any removal, archival, destructive migration, or access restriction requires its own authorization, impact assessment, and preservation plan.

## Required peering record

Each proposed relationship should record:

| Field | Required evidence |
|---|---|
| Legacy source | Repository, ref, exact SHA, path, provenance |
| Historical behavior | Interfaces, consumers, dependencies, observed behavior |
| Extracted component | New path/repository, version, lineage, steward |
| Peering contract | API/schema version, direction, data exchanged, permissions |
| Verification | Contract tests, compatibility matrix, CI links, exact tested SHAs |
| Risks and unknowns | Security, privacy, licensing, runtime, migration limitations |
| Decision | Approved / held / rejected, reviewer, date, rationale |
| Recovery | Rollback, disconnect, restore, and evidence-retention procedure |

Missing evidence must remain visible. A proposal may be recorded as a preservation target or future-peering candidate without being certified compatible.

## Relationship to CodEXgen project records

- [Branch Braid](BRANCH-BRAID.md) maps independent branch histories, candidate pairings, overlap, and evidence gates. This protocol governs how legacy source is preserved while any future peering is evaluated.
- [Pair Integration Plan](PAIR-INTEGRATION-PLAN.md) identifies file-level overlaps and proposed reconciliation. Its plan is not permission to merge or copy source content.
- [Seed Pits](../pantheon/seed-pits/README.md) preserve failures, corrections, provenance, and verification amendments. Legacy defects and successful repairs must both remain traceable.
- [Resonance Stewardship](RESONANCE-STEWARDSHIP.md) governs consent, bounded propagation, traceable origin, and the separation of metaphor, digital information, and measured physical phenomena.
- The project discussion identifies `d067870e` as the historical success reference for the initial Stride bridge recovery and Android APK verification. Its full commit SHA could not be resolved against the currently accessible GitHub repository snapshot during this update, so this short identifier is retained as an unverified cross-reference rather than a clickable commit citation. It is not evidence of repository-wide repair or universal legacy compatibility.

## Current implementation boundary

This document establishes governance and review criteria. It does not itself perform a repository-wide legacy inventory, certify every branch, establish compatibility between every module, or authorize merges, ref updates, deletions, deployments, or external transfers.

The initial bridge and APK verification remain a bounded implementation milestone. Repository-wide repair and future peering require separate inventories, exact source snapshots, tests, review, and evidence.

## Governing statement

**Preservation is not stagnation. Independence is not incompatibility. Integration is not ownership.**

Legacy is preserved; peering is earned through explicit interfaces, authorization, and reproducible evidence.
