# Main-based correction review

This branch is based directly on the existing `main` commit. It does not
rewrite, merge, or replace `main`, and it does not create or update a
`master` branch.

## Included

- Instrument Connection and Integrated Circuit verification records.
- Evidence requirements for PASS outcomes and independent reviewer reference.
- Mirrored multiplication checks against the expected product.
- Oscillation diagnostics over supplied numeric samples.
- A logical main → round → master sequence audit that performs no Git branch
  mutation.
- Metadata-only WATER equipment inventory for pumps, valves, sensors, and
  treatment equipment. A reported connection is not a live connection.

## Explicitly excluded

The WATER lifecycle runflow is not copied into this branch because its current
implementation depends on `codexgen_contracts.envelope`, which is not present
on the current `main` tree. It remains on the separate `hypotheticals`
workstream pending a deliberate contract-port/review.

## Safety and release boundary

These modules inspect supplied records and values only. They do not connect to,
energize, program, or operate hardware. They do not authorize equipment
actuation, product release, or water-potability claims. Tests and evidence
records are not substitutes for qualified engineering validation.

## Review checklist

- [ ] Review verification checklists against the intended equipment and IC.
- [ ] Review numerical tolerances and edge cases in mirror multiplication.
- [ ] Review oscillation detection limits and interpretation.
- [ ] Review equipment metadata fields and source provenance.
- [ ] Run Python tests and all repository CI checks.
- [ ] Obtain independent review before any merge.
