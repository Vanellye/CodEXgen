# ERIA MÂNI #MÊN — Logic, Gateway, and Creation Pathway

**Status:** Proposed architecture specification  
**Branch:** Feature-scoped development; no Main mutation implied  
**Runtime effect:** None until separately implemented and authorized

## Purpose

MÂNI #MÊN is a creation gateway for turning defined **SUBSTANCE (S)** into creative **ART** through bounded **ARTIFICE**: tools, transformations, compositions, and processes that shape source material into an artifact.

The name is an ERIA project identifier. It does not imply an external authority or autonomous entitlement. Its permissions come only from explicit, scoped grants.

## 1. Core creation logic

The pipeline is:

`SUBSTANCE (S) → ARTIFICE → ART`

- **SUBSTANCE (S):** source material, observations, concepts, data, user-supplied media, or approved inputs.
- **ARTIFICE:** the declared method of transformation: composition, arrangement, synthesis, editing, rendering, or other creative operation.
- **ART:** the resulting work, draft, model, design, sound, image, text, or other artifact.

Every transformation records source lineage, method/version, parameters, creator or responsible agent, and output identity. Derived work must not be represented as the untouched original.

## 2. MÂNI #MÊN logic gateway

The gateway validates each creation request before work proceeds:

1. **Intent:** identify the requested artifact and intended use.
2. **Substance:** identify permitted inputs and their provenance.
3. **Method:** select an allowed artifice and bounded transformation.
4. **Rights:** verify permissions for source use, derivative creation, and destination.
5. **Quality:** run applicable integrity, format, and safety checks.
6. **Disposition:** classify the result as draft, saved, approved, or blocked.

Missing or conflicting rights, unclear source provenance, or invalid output requirements cause a fail-closed result.

## 3. Mini ArTs — composable creative units

A **Mini ArT** is a small, independently identifiable creative component that can be composed with other components.

Examples include:
- a motif, phrase, rhythm, texture, color palette, shape, or visual element;
- a scene, movement, transition, sample, or sound layer;
- a reusable code-generated design element or procedural asset.

Each Mini ArT carries:
- unique identifier and version;
- source/provenance references;
- creator and rights metadata;
- transformation history;
- compatibility and quality checks;
- permitted reuse and transmission scope.

Compositions retain references to their constituent Mini ArTs. Reuse does not erase attribution or grant broader rights than the source permissions allow.

## 4. TRAN(s)Mission pathway

**TRAN(s)Mission** is the controlled movement of an artifact between stages, modules, people, or approved destinations.

Transmission is separated into:
- **internal handoff:** movement between authorized local components;
- **export package:** a prepared artifact and provenance manifest;
- **external delivery:** a distinct action requiring destination-specific authorization.

A generated artifact is not automatically transmitted externally. A trigger, completed render, or saved file is not by itself permission to publish, upload, send, or dispatch.

## 5. TransenDance pathway

**TransenDance** names the iterative transformation pathway through which an artifact may evolve across forms or stages.

A pathway records:
- prior artifact and version;
- intended transformation;
- resulting artifact and version;
- differences and quality checks;
- preserved source lineage;
- approval state for the next stage.

Evolution may create new derivatives, but must not rewrite the identity or history of earlier works. Each stage remains traceable and recoverable where technically possible.

## 6. OTTO Creation cycle — AUTO / SAVE / MAN

### AUTO — create
Generate or transform within the declared intent, source rights, tool limits, and delegated scope. AUTO may produce drafts and candidate Mini ArTs. It may not grant itself permissions, bypass checks, or perform external delivery.

### SAVE — preserve
Save to an explicitly configured local or approved destination. Record the artifact, version, source manifest, method, timestamp, and validation status. Preserve originals and avoid destructive overwrite. If the destination is not configured or authorized, keep the result as an unsaved draft and report the limitation.

### MAN — human stewardship
A human reviews, edits, accepts, rejects, or authorizes the next consequential step. Record the decision and its scope. Human approval is required for publication, external transmission, rights-sensitive reuse, protected-source changes, or other consequential actions.

The stages may repeat as `AUTO → SAVE → MAN → AUTO`, but no stage silently implies the next stage's authorization.

## 7. State model

Allowed artifact states:
- `PROPOSED` — request or concept received;
- `DRAFT` — generated, not yet accepted;
- `VALIDATED` — required checks passed;
- `SAVED` — preserved at an authorized destination;
- `APPROVED` — human acceptance recorded for a stated scope;
- `TRANSMISSION_READY` — package prepared, not yet sent;
- `TRANSMITTED` — delivery confirmed by the authorized destination;
- `BLOCKED` — required rights, evidence, validation, or approval missing.

State changes must be explicit and auditable. Never label a merely prepared package as transmitted.

## 8. Rights, safeguards, and integration

- Apply least privilege to source access, creation, storage, and delivery.
- Preserve original material, lineage, attribution, and revision history.
- Respect licenses, consent, privacy, and third-party rights.
- Separate generation, saving, human approval, and external transmission.
- Keep external actions disabled unless separately authorized for a specific destination and purpose.
- Provide a stop/cancel path and a recovery plan for destructive or irreversible operations.
- Do not allow generated content to rewrite its own permissions or policy.
- Retain the existing Pheônix, Sure-rarity, THANKs, and Cosmic Law checks; this gateway does not bypass them.

## 9. Implementation boundary

This document defines architecture and governance only. It does not install a runtime, create credentials, grant storage or network permissions, activate autonomous transmission, or publish any artifact. Those capabilities require separate implementation, tests, and explicit authorization.

## Change record

- Introduces MÂNI #MÊN as a substance-to-art creation gateway.
- Defines Mini ArTs, TRAN(s)Mission, TransenDance, and the OTTO AUTO / SAVE / MAN cycle.
- Preserves human stewardship, provenance, and explicit authorization boundaries.
