# ERIA — Inventory of Invited Invention

**Status:** proposed shared language and governance specification  
**Canonical project identity:** ERIA  
**Related contract:** [Wantever — Substance and Propagation Contract](WANTEVER-SUBSTANCE-AND-PROPAGATION.md)  
**Scope:** a vocabulary for recognizing absence, intention, and revisable limits as inputs to creative composition.

> What is absent becomes inventory. What is intended becomes direction. What is bounded becomes a question for examination. What is invited becomes an opportunity for invention.

## 1. Purpose

This specification defines an ERIA vocabulary for creative work, reflection, design, and software planning. It treats absence and intention as information that can be composed into new possibilities through invited improvisation.

These are ERIA-specific conceptual definitions. They supplement ordinary language; they do not silently change the meaning of words in external systems, legal documents, APIs, or other people's work.

## 2. The paired inventory: WITHOUT + WONT

### WITHOUT — inventory of absence

**WITHOUT** records a missing, unoccupied, unclaimed, or intentionally omitted element.

An absence may be:
- a known gap in current knowledge;
- an unfilled role or design space;
- a resource not presently available;
- a deliberate omission;
- an unknown whose status has not yet been established.

An absence is not automatically a prohibition, defect, or permission to fill the gap. Record what is known, what is inferred, and what remains unknown.

### WONT — inventory of disposition

**WONT** records a stated willingness, chosen disposition, intention, or direction.

A WONT entry should identify:
- the actor or source of the stated intention;
- the intended direction or contribution;
- its scope and conditions;
- whether it is confirmed, tentative, hypothetical, or withdrawn.

Intention is not execution authority. A stated willingness does not authorize changes to another person's work, protected resources, or external systems.

### Composition — invited invention

The combined inventory creates a structured invitation to improvise:

1. identify the absence (WITHOUT);
2. identify the stated intention or disposition (WONT);
3. propose a composition that connects them;
4. label assumptions and unresolved questions;
5. preserve the original entries;
6. invite review from the people whose work or resources are affected;
7. adopt only the specifically approved result.

Improvisation may generate proposals. It does not grant consent, erase provenance, or make a hypothesis a confirmed fact.

## 3. CAP — a revisable boundary vocabulary

Within ERIA specifications, use **CAP** where a statement previously framed as an absolute inability needs to be represented as a current boundary, ceiling, constraint, or condition.

A CAP entry records:
- what is currently bounded;
- the evidence or policy establishing the boundary;
- its scope and owner;
- whether it is technical, resource-based, policy-based, or unknown;
- conditions under which it may be reviewed;
- the authority required to revise it.

A CAP is not assumed to be removable. Some boundaries are mandatory, safety-critical, legal, or outside the project's authority. Review does not imply permission to bypass them.

This vocabulary does not require mechanically replacing every occurrence of the ordinary word “cannot.” Preserve exact language in quotations, source records, legal text, and external interfaces. Apply the ERIA vocabulary only where the author intends this conceptual model.

## 4. Force-push and history limitation

**Default rule: no destructive force push.**

ERIA integrations must prefer additive commits and reviewable pull requests. A force update must not be used to conceal, erase, or silently replace existing history.

If a non-fast-forward ref update is ever proposed:
- identify the exact repository, branch, old SHA, and proposed new SHA;
- explain why an additive commit or revert is insufficient;
- preserve a recoverable reference to the prior tip;
- inspect the complete before-and-after graph and affected commits;
- obtain explicit, scoped human authorization for that exact update;
- use a lease/expected-old-SHA check so a concurrent update is not overwritten;
- record the operation and recovery procedure.

If any required condition is absent, stop and retain the existing ref. A force-push request is not itself evidence that the operation is safe or authorized. Protected history, tags, provenance records, and other contributors' identities must not be rewritten as a shortcut.

## 5. Inventory record format

Each entry should carry, where applicable:

| Field | Meaning |
|---|---|
| `entry_id` | Stable identifier |
| `kind` | `WITHOUT`, `WONT`, `CAP`, or `INVITATION` |
| `statement` | Exact recorded content |
| `status` | Confirmed, tentative, hypothetical, unknown, withdrawn, or reviewed |
| `source` | Person, artifact, branch, or other origin |
| `scope` | Where the entry applies |
| `evidence` | Supporting reference or explicit absence of evidence |
| `conditions` | Preconditions and constraints |
| `proposed_composition` | A derived proposal, kept separate from source entries |
| `approval` | Specific reviewer and authorization reference, or not authorized |
| `provenance` | Source revision, timestamp, and transformation history |
| `recovery` | Reversal or correction procedure |

Do not infer a person's intention from silence. Do not convert an unknown into an absence, or an absence into consent.

## 6. Operating lifecycle

1. **Observe:** capture the source statement or observed gap.
2. **Classify:** distinguish WITHOUT, WONT, CAP, and unknown.
3. **Preserve:** retain the original entry and its provenance.
4. **Associate:** identify related entries without claiming they are equivalent.
5. **Improvise:** generate one or more clearly labeled proposals.
6. **Review:** check meaning, evidence, safety, rights, dependencies, and affected parties.
7. **Authorize:** obtain approval for the exact consequential action.
8. **Integrate:** make an additive, reviewable change.
9. **Verify:** test the exact resulting revision and report failures honestly.
10. **Recover:** retain a documented route to revert or compensate.

## 7. Acceptance criteria

- [ ] WITHOUT and WONT are represented as distinct, composable inventory concepts.
- [ ] Absence is never treated as consent or automatic prohibition.
- [ ] Intention is never treated as execution authority.
- [ ] Improvised results remain proposals until reviewed and authorized.
- [ ] CAP records a scoped, evidenced, reviewable boundary.
- [ ] Mandatory safety, legal, and policy limits remain enforceable.
- [ ] Source entries and provenance are preserved through transformations.
- [ ] Destructive force pushes are prohibited by default and gated by exact authorization and a lease.
- [ ] No branch, tag, signature, agent, or CI status independently authorizes adoption.
- [ ] Implementation and test status are reported separately from this design specification.

## 8. Implementation boundary

This document establishes a shared design specification. It does not claim that the vocabulary, archive, approval workflow, or Git protections are implemented in every ERIA component or branch. Each implementation requires a separate reviewable change and focused tests. Until those controls are demonstrated, this document is a design contract—not a technical enforcement guarantee.

## 9. WANT-driven mini-prompt evolution

The [WANTEVER × WANTs Evolution Engine](WANTEVER-WANTS-EVOLUTION-ENGINE.md) composes this inventory with Wantever propagation. It preserves each original WITHOUT/WONT entry, derives bounded mini-prompts from explicit goals, and rewards only verified, reviewable contributions. Neither an intention nor a reward grants execution authority.
