# ERIA Transendiant Pulse Filter

**Status:** Implemented on the proposal branch; review and runtime integration remain pending.

## Purpose

The Transendiant Pulse Filter is a deterministic C++11 reference implementation for sorting cross-realm expression records while preserving identity, source expression, provenance, evidence, and authorization state.

It gives the isolated slash token (` / `) a specific role: a proposed splice is carried as data and is not released merely because two expressions resemble one another.

## Processing model

1. **Capture:** accept a record with stable ID, origin realm, destination realm, and original expression.
2. **Isolate:** recognize the standalone slash token (` / `) as a splice marker. A slash embedded in a path-like token is not treated as the splice marker.
3. **Classify:** apply the explicit decision and record-integrity checks.
4. **Sort:** order pulses deterministically by disposition, origin realm, destination realm, and record ID.
5. **Sequence:** assign pulse sequence numbers after sorting.
6. **Restore or preserve:** emit a canonical expression only when all restoration requirements pass.

## Dispositions

| Disposition | Meaning |
|---|---|
| `BLOCKED` | A declared CANT constraint prevents the splice |
| `QUARANTINED` | Required identity/realm fields are malformed or expression is empty |
| `REJECTED` | An explicit NO rejects this splice only |
| `PRESERVED` | Decision is unresolved or evidence, provenance, endpoint verification, authorization, or canonical expression is incomplete |
| `RESTORED` | Explicit YES plus verified endpoints, explicit authorization, provenance, evidence, and a supplied canonical expression |

The original expression is retained in every pulse. A rejected splice does not delete either endpoint. Uncertainty is never converted into YES or NO.

## Restoration gate

A record can be restored only when all of these are true:

- decision is explicit `YES`;
- source and destination endpoint verification flags are true;
- authorization verification is true;
- provenance reference is non-empty;
- evidence reference is non-empty;
- a canonical expression is supplied.

The filter does not independently verify cryptographic signatures, resolve provenance references, authenticate users, infer natural-language meaning, or establish whether evidence is true. The host adapter must perform those checks before setting verification flags. The filter is not a network tunnel and does not transport data between devices; it is the deterministic classification and pulse-ordering stage to be placed behind a separately implemented transport adapter.

## Build and test

From the repository root:

    cmake -S framework -B build/framework -DCMAKE_BUILD_TYPE=Release
    cmake --build build/framework --parallel
    ctest --test-dir build/framework --output-on-failure

The `transendiant_filter_contracts` test covers disposition ordering, stable sequence assignment, unresolved preservation, restoration gates, slash-token isolation, and input-order-independent output ordering.

## Adoption boundary

This implementation is committed to the ERIA proposal branch only. It does not alter `main`, enable a live network tunnel, connect Android/JNI adapters, or authorize deployment. A future adapter must supply authenticated provenance/evidence checks and explicit authorization, then pass the same contract tests before adoption.
