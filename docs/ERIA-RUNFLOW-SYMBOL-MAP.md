# ERIA Runflow — Symbol Map

**Status:** Companion symbol map to `docs/ERIA-RUNFLOW-OPERATING-PROTOCOL.md`  
**Relationship:** This document duplicates the Runflow's meaning in a compact symbolic notation. The operating protocol remains authoritative; this map does not add permissions, runtime behavior, or new state transitions.  
**Notation:** The symbols below are ERIA conventions defined here, not universal or externally standardized meanings.

## 1. The canonical flow

```text
◎ → ◇ → ✓? → ▶ → ◉ → ⌕ → ↶ → ✧ → 🌱
```

| Symbol | Runflow stage | Meaning |
|---|---|---|
| ◎ | Origin | Identify and trace the source |
| ◇ | Intent | Define desired outcome, scope, and constraints |
| ✓? | Authorization | Obtain explicit approval for the exact action |
| ▶ | Execution | Perform only the authorized action |
| ◉ | Evidence | Record observed results and their provenance |
| ⌕ | Review | Examine results against intent, invariants, and risks |
| ↶ | Recovery | Repair, reverse, or contain; test the path |
| ✧ | Learning | Extract and thumb-imprint a bounded lesson |
| 🌱 | New Growth | Carry reviewed, authorized learning forward |

The question mark in `✓?` is intentional: authorization is a question until explicit approval is received. It must never be inferred from silence, readiness, or successful validation.

## 2. The Thumb-imprint

```text
       👍
        │
◎ ──────┼────── ◉ ────── ✧
 origin │     evidence   lesson
        │
     provenance
```

**👍 The Thumb** is a symbolic oversight mark applied across the record. It connects a lesson to its origin and evidence so that later work can recognize the trace.

It means:
- mark the source;
- identify what was learned;
- point to supporting evidence;
- keep interpretation distinct from the original record.

It does not mean:
- ownership or possession;
- authorship transfer;
- authorization to change;
- proof that a claim is true;
- permission to erase or rewrite the source.

## 3. Task-state symbols

| State | Symbol | Operational meaning |
|---|---|---|
| DRAFT | ○ | Intent is forming; no action authorized |
| READY | ◇ | Scope is clear; awaiting authorization |
| AUTHORIZED | ✓ | Exact action and boundary approved |
| RUNNING | ▶ | Authorized action in progress |
| BLOCKED | ⛔ | An invariant, permission, dependency, or safety condition stops progress |
| UNRESOLVED | ? | Evidence is incomplete, ambiguous, conflicting, or unavailable |
| REVIEW | ⌕ | Execution stopped; evidence under examination |
| RECOVERY-REQUIRED | ⚠↶ | Containment or repair is needed |
| RECOVERED | ↶✓ | Recovery path exercised and result recorded |
| COMPLETE | ■ | Scope satisfied and required review completed |
| LEARNED | ✧ | Lesson thumb-imprinted with source and uncertainty |

These symbols label states; they do not themselves cause transitions. State changes must be recorded explicitly.

## 4. Boundary and evidence operators

| Notation | Meaning |
|---|---|
| `YES` | Explicit acceptance of one defined relationship or action |
| `NO` | Explicit rejection of that relationship; neither endpoint is erased |
| `CANT` | A constraint blocks a prohibited, impossible, or unauthorized coupling |
| `NOT(p)` | Negation of predicate `p`; the subject remains distinct |
| `?` | Unknown or unresolved; never silently converted to YES |
| `[source]` | Provenance pointer to the originating artifact or record |
| `[evidence]` | Pointer to observed evidence supporting a claim |
| `[recovery]` | Pointer to recovery instructions and test result |
| `Δ` | A proposed change; not yet authorization or adoption |
| `↩` | Return to an earlier state for clarification, renewed authorization, or recovery |

## 5. Stop conditions

```text
⛔  missing authorization
⛔  scope exceeded
⛔  critical evidence conflict
⛔  invariant threatened
⛔  harm may be propagating
        │
        ▼
   CONTAIN → REVIEW → AUTHORIZE CORRECTION → TEST RECOVERY
```

Containment is not silent correction. If a safe recovery test is unavailable, remain in RECOVERY-REQUIRED or UNRESOLVED and state why.

## 6. Evidence-status marks

| Mark | Meaning |
|---|---|
| PASS | Check was run and passed; cite its result |
| FAIL | Check was run and failed; preserve the result |
| NOT CHECKED | No check was performed |
| NOT AVAILABLE | Required evidence or capability could not be accessed |
| UNVERIFIED | A claim exists but has not been independently established |

Never use PASS as a synonym for intended, plausible, reviewed, or merely attempted.

## 7. Compact Runflow record

Use this symbolic record for a consequential task:

```text
RUNFLOW {
  origin:       ◎ [source]
  intent:       ◇ [outcome + scope]
  authorization: ✓? [actor + exact action + boundary]
  execution:    ▶ [action + result]
  evidence:     ◉ [observations + references]
  review:       ⌕ [findings + unresolved items]
  recovery:     ↶ [method + test status]
  learning:     ✧ 👍 [lesson + origin trace]
  growth:       🌱 [approved next use]
  state:        [one explicit task state]
}
```

Unknown values remain explicitly unknown. Do not fabricate a source, approver, test, or result to complete the form.

## 8. Governing axiom

**◎ Trace the origin. ◇ Clarify the intent. ✓? Ask before acting. ▶ Act within scope. ◉ Show the evidence. ⌕ Review the consequence. ↶ Test recovery. ✧ 👍 Imprint the lesson. 🌱 Grow without repeating harm.**

The symbol map is a reading aid. In any conflict, the ERIA Runflow Operating Protocol and the specific authorization record govern.
