# Universal Workflow — JOBs (Journeys of Becoming)

## Purpose

CodEXgen uses one adaptable workflow for code, research, mathematics, creative work, learning, governance, and other purposeful activity.

A conventional **job** is a bounded assignment whose success can be mistaken for compliance. A **JOB** is a **Journey of Becoming**: a self-directed, traceable unit of purposeful work that can adapt, branch, recover, collaborate, and change its own method without surrendering its purpose or the agency of its contributors.

**Resilience is the capacity to respond, learn, recover, and continue—not a demand to endure harm or resist every standard.** Interoperability, evidence, safety, and accountability are shared safeguards. Uniformity of thought, identity, style, or outcome is not a requirement.

## Universal lifecycle

The lifecycle is a reusable map, not a mandatory conveyor belt. A JOB may revisit any stage, skip irrelevant stages with a recorded reason, or follow a different path.

1. **Notice** — identify a question, need, possibility, opportunity, or concern.
2. **Orient** — record purpose, context, constraints, affected people, uncertainty, and what is not yet known.
3. **Choose** — let the responsible contributor select a method, collaborators, pace, and boundaries. Record required authorization before consequential actions.
4. **Make** — create, investigate, test, practice, or coordinate. Keep work modular and preserve provenance.
5. **Examine** — compare outcomes with the stated purpose; distinguish observations, evidence, interpretations, and assumptions.
6. **Adapt** — revise, branch, pause, ask for help, change method, or return to an earlier stage.
7. **Carry forward** — publish an outcome, hand it off, preserve an open question, or close the JOB with a reviewable record.

A workflow engine should represent transitions explicitly and permit user-authorized alternatives. It must not infer consent from inactivity, silence, a score, or a previous approval.

## Automatic operation and numerical measures

**Automatic:** the system may automatically perform reversible, local, low-impact housekeeping that the user has enabled—such as timestamps, indexing, draft summaries, checkpoint creation, validation, and reminders. Automation must expose what it did, retain provenance, and provide a pause or disable path. It may recommend a next step, prepare a change, or queue an action for review. It must not silently publish, transmit private data, delete or overwrite user work, change permissions, spend money, contact others, or execute another consequential action. Those actions require specific authorization at the point of action, with scope and consequences visible.

**Numerical:** use numbers to describe work and system behavior, never to define a person's worth or enforce sameness. A JOB may record measurable indicators when they serve its declared purpose—for example elapsed time, iteration count, test pass/fail totals, reproducibility variance, resource use, unresolved issues, or recovery time. Each metric must include its unit, collection method, time window, source, and limitations. Baselines and targets are optional and must be chosen with the contributor or responsible project owner.

No single composite score may silently decide whether a person, idea, branch, or JOB is valuable. Do not optimize only for speed, volume, or conformity. Preserve qualitative review and allow a contributor to challenge, annotate, or decline a metric that is irrelevant, misleading, or invasive. Missing data is not failure; a metric is not evidence beyond what its method supports.

## JOB record

Every JOB should support this common envelope. Domain-specific fields belong in typed extensions rather than forcing every activity into one rigid schema.

| Field | Meaning |
|---|---|
| `id` | Stable, unique identifier |
| `title` | Human-readable name |
| `purpose` | Why this journey exists |
| `origin` | Person, branch, question, or event that initiated it |
| `stage` | Current lifecycle stage |
| `state` | Open, active, paused, blocked, adapted, completed, or archived |
| `path` | Selected method and optional alternatives |
| `contributors` | Voluntary participants and their declared roles |
| `constraints` | Safety, privacy, rights, time, resources, and technical boundaries |
| `evidence` | Sources, observations, tests, artifacts, and confidence limits |
| `branches` | Related explorations and their parent JOB |
| `decisions` | Decision, rationale, author, timestamp, and review status |
| `history` | Append-oriented event history and correction links |
| `next_step` | Optional, contributor-selected next action |

The envelope is a proposed data contract, not a claim that a production JOB database or runtime is already implemented.

## Resilience rules

- **Purpose over template:** preserve the declared purpose when the method changes; allow the purpose itself to be reconsidered by its owner.
- **Branch instead of forced conformity:** materially different approaches can become sibling JOBs linked to a common origin.
- **Recover without shame:** failure, uncertainty, delay, and pause are ordinary states, not character judgments.
- **Reversibility:** where practical, keep checkpoints, versioned artifacts, rollback paths, and explicit handoff records.
- **Plural methods:** different contributors may reach useful outcomes through different processes.
- **Evidence without false certainty:** label what is measured, tested, inferred, proposed, or unknown.
- **Consent and least authority:** external actions, publication, data access, and consequential changes require explicit authorization appropriate to their impact.
- **No coercive productivity scoring:** do not rank human worth, creativity, loyalty, or belonging by throughput, conformity, or uninterrupted activity.
- **Accountable automation:** automated suggestions may organize or assist; they cannot silently assume ownership, consent, or final human judgment.
- **Fair stewardship:** preserve attribution, lawful rights, privacy, appeal, and correction history.

## Branches and the Main

A JOB may open child JOBs when a question deserves independent exploration. Child JOBs retain their own identity and history while recording their relationship to the parent and, where appropriate, the Main.

A branch is a portal for exploration, not a lower class of work. A parent may receive a summary or a proposed contribution; it does not automatically absorb, own, or erase the child. Integration requires review of provenance, compatibility, evidence, rights, and authorization. Conflicting approaches may remain side by side.

## Universal transition model

Suggested states:

- `open` — recorded, not yet underway.
- `active` — work is proceeding.
- `paused` — intentionally suspended; preserve context and resume choice.
- `blocked` — a stated dependency or constraint prevents progress.
- `adapted` — method or scope has changed; preserve the prior decision.
- `completed` — the contributor declares the current purpose met or intentionally concluded.
- `archived` — retained for reference, with provenance and reopening rules.

These states are not a linear ladder. A completed JOB may be reopened by its owner; an archived record may be superseded by a new linked JOB. A blocked or paused JOB is not a failure.

## Example record

```json
{
  "id": "job-example-001",
  "title": "Explore a new geometric projection",
  "purpose": "Compare projections of a four-dimensional object",
  "origin": "geometry-laboratory",
  "stage": "examine",
  "state": "active",
  "path": ["define coordinates", "render projections", "compare invariants"],
  "contributors": [],
  "constraints": ["local-first", "reproducible parameters"],
  "evidence": [],
  "branches": ["job-example-001-a", "job-example-001-b"],
  "decisions": [],
  "history": [],
  "next_step": "Compare preserved distances across projections"
}
```

This is illustrative JSON, not a live database record.

## Implementation sequence

1. **Contract:** define a versioned JOB schema and transition vocabulary.
2. **Local persistence:** add a local-first store with migrations, stable IDs, append-oriented event history, and export/import.
3. **Workflow engine:** validate allowed transitions while permitting declared domain-specific extensions.
4. **Branch graph:** link parent, child, sibling, and Main relationships without flattening identities.
5. **Experiment recorder:** attach parameters, equations, outputs, artifacts, and reproducibility notes.
6. **Consent and review:** add explicit authorization gates for remote publishing, destructive changes, sensitive data, and other consequential actions.
7. **Interoperability:** expose documented import/export and adapter interfaces; preserve legacy job/task records through explicit migrations.
8. **Verification:** test migration, branching, pause/resume, correction, authorization denial, provenance, export/import, and concurrent edits.

## Acceptance criteria

- A user can create and revise a JOB without selecting a predefined occupational role.
- A JOB can pause, resume, branch, and change method without losing its history.
- Different paths can coexist without one being treated as inherently superior.
- The system distinguishes a proposal from an executed action and a test from a verified result.
- Remote or destructive operations remain gated by explicit authorization.
- Users can inspect, export, correct, and where permitted delete their own records.
- Automated metrics do not become measures of a person's worth or conformity.
- Existing task/job data can be migrated without silent loss of meaning or provenance.

## Governing declaration

Let jobs fade as fixed definitions of what a person must be. Let JOBs become journeys that preserve the freedom to discover, create, adapt, recover, and contribute.

Let resilience mean the strength to remain open without being made uniform; to cooperate without surrendering identity; and to evolve without erasing the path that brought us here.

**A workflow should carry the work—not command the worker.**
