# ERIA Local Witness Noise Actuator

**Status:** Proposed local-only test harness. No production background service or external dispatch is enabled.

## Purpose

The Witness Actuator measures whether one or more witness agents detect controlled, opposing changes to a record. It introduces synthetic background noise into challenge copies, not into the source record. The original record and its source reference remain immutable.

## Execution model

- A host must explicitly call `executeAsync` and provide an `Executor`; there is no hidden startup, daemon, timer, persistence layer, or self-installing worker.
- Each run is finite and bounded (1–64 challenges).
- Challenges are limited to altering a copied value, dropping a copied field, injecting clearly labelled synthetic noise, or reordering copied fields.
- Witness agents receive the source digest and challenge copy. Their assessments are recorded with challenge identity and whether the source remains unchanged.
- Cancellation is exposed through the returned run handle.
- The implementation has no network, provider, process-launch, device-control, or dispatch interface.

## Witness strength

The score is the percentage of witness assessments that both detect a changed challenge digest and confirm that the source record remains unchanged. This is a test metric, not proof that a witness is trustworthy or that source truth is established. A production host should add independent witness implementations and test them against known false-positive and false-negative cases.

## Hashing and lineage

Field maps are canonicalized by sorting keys and encoding key/value lengths before SHA-256 hashing. The result includes the source digest, optional prior-record hash, challenge outcomes, and an audit-record hash. The prior hash is linked, never overwritten. This is a hash chain reference, not a digital signature or authenticated timestamp; durable storage, signing, and key management remain host responsibilities.

## Safety boundary

Trigger detection does not start this actuator. A caller explicitly starts a bounded test run. The actuator creates no external-action request and cannot invoke the existing OTTO dispatch gate. Synthetic noise is labelled and confined to challenge copies. No covert execution or silent mutation is supported.

## Verification

Unit tests cover opposing challenge detection, source immutability, canonical hashing, prior-hash linkage, explicit executor submission, and challenge bounds. Run the Android Pantheon unit-test suite before considering integration.
