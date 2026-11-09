# Stride Consent & Human Review Interface

**Status:** UI and local record flow implemented; automated tests and device verification pending.  
**Branch:** `olpirt/stride-next`  
**Applies to:** essential assent and consequential Stride workflows.

## Purpose

Translate the seven readiness layers in [Essence Alignment](ESSENCE-ALIGNMENT.md) into a practical pause-and-review interface. The interface is supportive, not a test of morality, faith, intelligence, courage, or personal worth.

## Interface behavior

The Consent tab presents:

1. Safety and dignity.
2. Purpose and meaning.
3. Evidence and uncertainty.
4. Consequences and boundaries.
5. Freedom from pressure.
6. Choice and reversibility.
7. Human accountability.

Each layer begins unchecked. A user must affirm that the point was explained and understood before the assent path can continue. These are self-attestations, not proof that understanding has occurred. The app does not calculate a readiness score.

The assent action is blocked unless:
- all seven layer checks are selected;
- a purpose/action summary is present;
- a human reviewer is named;
- the reviewer explicitly confirms their review; and
- the voluntary-choice checkbox is selected.

Decline and pause are first-class outcomes. Decline does not require reviewer confirmation. Pause records no assent and says that the workflow may be revisited only if the person chooses. The voluntary-choice checkbox is cleared after recording an outcome.

## Childhood innocence and consequential decisions

The Consent screen displays the project's childhood-innocence principle: every child has dignity before understanding, choice, or speech; silence is not permission; vulnerability is not availability; dependence is not ownership. The spiritual phrase “bearing the mark of God's thumb” is presented as a faith-based value statement, not as a technical or scientific claim.

For child-related consequential decisions, the design requires protection, patience, truth, compassion, and accountable human care. Seek meaningful, age-appropriate assent where possible and legally required adult permission; neither substitutes for the other. A child's assent does not transfer the adult duty of care to the child. Pause when safety, understanding, voluntariness, or authority is unclear. Never infer consent from silence, compliance, behavioral data, or biometrics.

**Important implementation boundary:** this is currently principle text and a general-purpose consent interface. The app does not identify a participant's age, enforce guardian authorization, verify reviewer independence, determine legal capacity, or provide safeguarding escalation. Do not use it as a child-protection or legal-consent system.

## Local audit record

The app writes a minimal event to the app-private SQLite database `stride_consent_review.db`:
- timestamp;
- outcome (`ASSENTED`, `DECLINED`, or `PAUSED`);
- seven boolean layer flags;
- reviewer name/role; and
- purpose/action summary.

No participant name, age, biomarker, or free-form personal narrative is requested by this screen. Keep the purpose summary concise and do not enter sensitive personal, medical, or child-protection details. The database is app-private but **not encrypted by this implementation**; device backup, app removal, and access by a person controlling the device are outside this screen's guarantees. Records remain on-device and are not transmitted by this feature.

## Human and youth safeguards

The reviewer checkbox is an accountability declaration, not identity verification, independence verification, or proof of competence. The app cannot verify that the reviewer is a different person from the participant. A real deployment must define who may review which decisions and provide an independent safeguarding route where required.

The UI text describes youth-specific expectations, but guardian authorization, age-aware routing, mandated reporting, safeguarding escalation, and jurisdiction-specific legal checks are **not implemented**. Do not use this prototype as a child-protection, clinical-consent, or legal-consent system.

## Implementation status

| Control | Status |
|---|---|
| Seven separate, initially unchecked layer controls | Implemented |
| Hard pause when any layer is incomplete | Implemented |
| Explicit voluntary-choice control | Implemented |
| Separate reviewer name and review declaration | Implemented |
| Decline and pause outcomes | Implemented |
| Local SQLite event history | Implemented |
| No readiness score or inferred assent | Implemented by design |
| Reviewer identity / independence verification | Not implemented |
| Guardian permission and youth workflow | Not implemented |
| Sensitive-record encryption and retention controls | Not implemented |
| Automated unit/UI tests | Pending |
| Device and accessibility testing | Pending |
| Independent safeguarding/legal review | Pending |

## Acceptance tests to add

1. Fresh screen: all seven layers and both assent/reviewer controls are unchecked.
2. Attempt assent with each individual layer omitted: action remains paused and no `ASSENTED` row is written.
3. Attempt assent without purpose, reviewer name, reviewer declaration, or voluntary choice: no assent row is written.
4. Complete all required controls: exactly one `ASSENTED` row is stored.
5. Decline with no layer checks: a `DECLINED` row is stored and no assent is implied.
6. Pause at any point: a `PAUSED` row is stored and voluntary choice is cleared.
7. Reopen history: outcomes and seven flags are displayed from local storage.
8. Confirm no network request is made by the consent feature.
9. Verify text scaling, screen-reader labels, keyboard navigation, and small-screen scrolling on supported Android versions.

## Release gate

This is a first implementation of the interface contract, not proof that a consequential process is safe or legally valid. Before production use, add automated tests, data minimization/retention controls, appropriate encryption, role-aware human review, and independent safeguarding review. Keep the feature local-first and fail closed whenever an essential check is incomplete.
