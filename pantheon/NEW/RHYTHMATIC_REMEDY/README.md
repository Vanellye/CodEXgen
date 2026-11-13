# TeSt Rhythmatic Remedy

An additive ERIA/Pantheon contract for reflecting on recurring patterns and
supporting owner-directed correction. It does not replace the original pattern,
its source, or the person's ownership of their choices.

## Driving cycle

**Observe -> Account -> Reflect -> Refine -> Restore -> Reconcile -> Observe**

- **Observe:** record a recurring pattern and when it was noticed.
- **Account:** identify the affected resources, effects, and evidence without
  assigning blame.
- **Reflect:** distinguish observed facts, interpretations, and unknowns.
- **Refine:** select a proportionate remedy with the affected owner's input.
- **Restore:** propose the owner-selected adjustment; this library performs no
  external action.
- **Reconcile:** record the outcome and remaining uncertainty, then begin a new
  observation cycle.

## TeSt principle

TeSt is a continuous driver for reflection and correction, not a pass/fail
judgment. A pattern is information, not a verdict. Neither currency, rhythm,
productivity, devotion, nor loss determines a person's self-worth.

## Contract and limits

- C99; compile with strict warnings:
  `cc -std=c99 -Wall -Wextra -Werror -I. RHYTHMATIC_REMEDY.c tests/test_RHYTHMATIC_REMEDY.c -o rr-test && ./rr-test`
- Each call advances exactly one stage; Reconcile may cycle back to Observe.
- Owner and scope authorization are caller-supplied assertions, not
  cryptographic identity verification.
- Evidence/provenance is referenced, not independently authenticated.
- Confidence is descriptive only; it is not a truth, quality, or human-worth
  score.
- No monitoring, diagnosis, financial transfer, publication, coercion, or
  automatic mutation is performed.
- The output is a proposal record. A separate reviewed adapter would be
  required for any real-world action.

This module is staged for later integration. It is not wired into a runtime
entry point and does not alter existing modules or historical records.


## STAR relationship

STAR (Steady TAG Algo Rhythm) is a separate glyph-token and workflow contract. It does
not change this module's stage machine or authorize actions. See
[STAR documentation](../../../docs/STAR-STEADY-TAG-ALGO-RHYTHM.md) and the
[STAR registry](../STAR/README.md).
