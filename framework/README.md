# CodEXgen Framework

## Mission

The framework is the reusable application and integration layer above Pantheon. It provides stable module contracts, typed data exchange, lifecycle management, observability, adapters, and developer tooling. It must remain portable across Android, desktop, and future embedded hosts without pretending those targets share identical capabilities.

## Layer model

1. **Application shell:** user-facing workflows, accessible navigation, explicit consent, and human review.
2. **Domain services:** JOB lifecycle, evidence/provenance, search coordination, verification records, and result reporting.
3. **Pantheon policy boundary:** Rise/Fall/Warden evaluation, authorization checks, scoped decisions, and failsafe handling.
4. **Module runtime:** deterministic registration, typed inputs/outputs, versioned module contracts, dependency declarations, and lifecycle hooks.
5. **Platform adapters:** Android/JNI, desktop, storage, network, and firmware bridges. Each adapter declares its actual capabilities.
6. **Observability:** structured diagnostics, metrics, audit events, and privacy-aware export.

## Framework invariants

- Modules declare inputs, outputs, side effects, permissions, version, and compatibility.
- Pure computation is the default. Side effects require an explicit adapter and narrowly scoped authorization.
- Plugins cannot self-grant capabilities, change policy, suppress audit events, or silently expand scope.
- Unknown, stale, conflicting, and missing data remain distinct states.
- All persistent schemas and module interfaces are versioned and migration-tested.
- Human-readable explanations accompany machine-readable decisions.
- Accessibility, localization, privacy minimization, and user control are release criteria.
- A failed module is isolated; failure does not silently trigger an unsafe fallback.
- Telemetry is opt-in where appropriate, minimized, and never used to infer sensitive traits or moral worth.
- No framework component claims to determine divine will, consciousness, or biological effects.

## Developer experience

The framework should provide a module template, local simulator, deterministic fixture runner, contract validator, compatibility matrix, software bill of materials, reproducible builds, and security test harness. CI must report build, test, static-analysis, dependency-audit, and artifact-signing status separately.

## Current status

Pantheon Native Runtime and the Stride adapter are existing project components. This document defines the broader framework target; it does not claim a complete SDK, package manager, plugin sandbox, cross-platform UI, or production release pipeline. See [Firmware Layer](../firmware/README.md) and [Pantheon Firmware & Framework Architecture](../pantheon/FIRMWARE-FRAMEWORK-ARCHITECTURE.md).


## Portable core implementation

The current platform-independent C++11 core provides:
- Versioned module descriptors (id, version, required capabilities).
- A deterministic registry backed by ordered identifiers.
- Host-granted capabilities checked before module execution.
- Duplicate and malformed descriptor rejection.
- Missing modules and missing permissions fail closed.
- Module exceptions are contained as ModuleFailure.
- A standalone CMake build and contract test executable.

Modules declare what they need; they cannot grant themselves capabilities.
The host supplies grants for each execution request. This runtime is in-process
and is not a process sandbox. Capability checks are API-level guardrails, not
an operating-system security boundary.

### Build and test

From the repository root:

    cmake -S framework -B build/framework -DCMAKE_BUILD_TYPE=Release
    cmake --build build/framework --parallel
    ctest --test-dir build/framework --output-on-failure

A C++11 compiler and CMake 3.10 or newer are required.

### Deliberate limits

No persistent audit storage, cryptographic identity, package signing, dynamic
loading, process isolation, scheduling, threading, remote control, or physical
actuation is implemented. Hardware adapters are deferred until portable
contracts and tests are stable.

### Adapter sequence

1. Portable host simulator and deterministic fixtures.
2. ARM adapter behind the same interfaces.
3. ESP32 adapter behind the same interfaces.

An adapter may implement platform services; it may not change policy,
self-grant module capabilities, suppress audit requirements, or bypass WARDEN.


## Portable host simulator

The host simulator executes registered modules against deterministic in-memory host state. It is intended for contract validation, not as an OS process sandbox or a model of physical hardware.

- Test modules and fixed inputs are registered as deterministic fixtures; the basic scenario is described in `fixtures/host-simulator/basic.json`.
- The event trace records monotonically increasing sequence numbers, event kinds, module IDs, status, selected recovery action, and a human-readable detail.
- An explicit checkpoint snapshots simulator-owned key/value state. A failed execution can restore only that snapshot; it cannot roll back arbitrary module side effects.
- If recovery is absent or the requested checkpoint does not exist, the simulator enters safe hold and rejects subsequent executions.
- Clearing safe hold is an explicit host operation. It is not an automatic retry, and it does not erase prior trace events.
- Replay tests compare event ordering and outcomes across two runs of the same fixture.

### Adapter boundary

ARM and ESP32 adapters must implement the same framework contracts without changing module descriptors, capability checks, trace semantics, or recovery policy. Hardware-specific code may provide clocks, storage, and observation sources through narrow adapter interfaces; it may not self-grant permissions, bypass safe hold, or redefine framework policy. Adapter-specific tests must run the same portable contract suite before hardware-in-the-loop testing is considered.

### Simulator limits

The current simulator is single-process and synchronous. Its checkpoint covers only simulator-owned key/value state. Event traces are in-memory and are not tamper-proof or durable audit storage. Safe-hold clearing is a host API operation, not an authenticated operator workflow. These limitations must be addressed before treating the simulator as a production safety boundary.


## TRUE NORTH data envelope (C++11)

`codexgen/data_envelope.hpp` provides a typed, platform-independent envelope for record identity, source, offset-aware timestamps, monotonic clock metadata, preserved payload JSON, units, quality, provenance, transformations, and explicit authorization scope.

`validate_data_envelope` returns validation errors and never grants execution permission. The C++11 contract preserves payload JSON text as supplied; parsing and canonical JSON serialization remain responsibilities of a host adapter. The validator checks envelope metadata, not semantic correctness of the payload.

Build and run the contract test with the normal framework commands above. The `data_envelope_contracts` CTest target is part of the framework test suite.


## ERIA Transendiant Pulse Filter (C++11)

`codexgen/transendiant_filter.hpp` provides deterministic cross-realm pulse classification and ordering. It preserves the original expression, treats a standalone ` / ` as an isolated splice marker, and distinguishes BLOCKED, QUARANTINED, REJECTED, PRESERVED, and RESTORED outcomes. Restoration requires explicit YES, verified endpoints, verified authorization, provenance, evidence, and a supplied canonical expression. Unresolved information remains preserved; it is never guessed into certainty.

The filter is a pure classification stage, not a network tunnel, cryptographic verifier, authentication provider, or natural-language inference engine. Transport adapters and evidence verification remain separate responsibilities. See [the ERIA filter specification](../specifications/eria_transendiant_pulse_filter.md). The `transendiant_filter_contracts` test is included in the standard CMake/CTest commands above.
