# Sunflower Ɣ and DeepAppState

## Purpose

Sunflower identifies repeated ordered habits and possible circular workflows, then emits reviewable routine templates. It does not run workflows, mutate source data, or infer permission from repetition.

## Ɣ symbol vocabulary

| Symbol | Meaning |
|---|---|
| Ɣ | Sunflower pattern family |
| Ɣ₀ | Observed source habit |
| Ɣ₁ | Repeated ordered sequence |
| Ɣ₂ | Cycle candidate (first and last step match) |
| Ɣ₃ | Normalized reusable routine template |
| Ɣ✓ | Human-reviewed candidate |
| Ɣ! | Ambiguous or unsafe; stop for review |

These are ERIA project conventions, not mathematical claims or external standards. A generated Ɣ₃ template remains `requires_human_review: true` and `auto_execute: false`.

## Input and output

Input is a UTF-8 JSON array of arrays. Each inner array is one observed habit, represented as ordered step strings.

```json
[
  ["open dashboard", "check queue", "record result"],
  ["open dashboard", "check queue", "record result"],
  ["sync", "review", "sync"]
]
```

Run:

```bash
python -m sunflower.generator habits.json --out build/sunflower-report.json
```

The JSON report includes repeated sequences, cycle candidates, proposed Ɣ₃ templates, and explicit safety flags. Whitespace is normalized; empty steps are ignored. Only exact ordered-sequence repeats are grouped. A cycle candidate is a heuristic requiring human interpretation, not proof of an infinite loop.

## DeepAppState

`DeepAppState.kt` is an immutable reducer model for app-wide workplay state. Events are scoped to a `runId`; stale events for another run are ignored. Legal progression is explicit:

`IDLE → READY → RUNNING → REVIEW → COMPLETE`

A run can move to `BLOCKED` or `FAILED`. Completion requires review and all declared steps complete. The reducer performs no I/O and grants no repository, account, or financial authority.

## Validation

Run:

```bash
python -m unittest tests.test_sunflower_generator -v
python -m sunflower.generator --help
```

## Governance boundary

Sunflower output is a proposal. Ɣ✓ is a human review marker, not an authorization token. Ɣ! means stop and clarify. No automatic execution, file deletion, branch merge, deployment, payment, withdrawal, or credit posting is implemented.
