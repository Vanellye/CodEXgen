# Pantheon Native Runtime

Pantheon is the native execution core for CodEXgen/Stride. The first milestone establishes a C++11 runtime contract, a Stride framework adapter, and a host-testable foundation. It does not yet claim that every Python module has been ported.

## Architecture

- **Core runtime** — deterministic module registration and execution with explicit input/output records.
- **Framework adapter** — translates existing Stride feature maps into Pantheon inputs without changing the legacy Python API.
- **Android bridge** — the Android JNI target links the same runtime library; no Python interpreter is required by the native core.
- **Migration modules** — each Python capability is ported separately and compared against Python reference fixtures.
- **Compatibility period** — Python remains the reference implementation until native parity tests pass.

## Port order

1. Stride faculty engine: perception scoring, deterministic idea combinations, bounded scalar adaptation, digital channel planning.
2. Medium/signal simulator: bounded digital waveform generation and illustrative medium models.
3. Rise/Wisdom bridge: idempotent event identity and durable record semantics.
4. Adaptive governance: cosine-distance calculation, correction policy, telemetry schema and deterministic outcomes. External LLM judging remains an injected interface, not a fake native implementation.
5. Code generation: deterministic template output with path and identifier validation.
6. Semantic memory: storage/query adapter boundary; embeddings remain provider-injected and must not be represented as native semantic understanding.

## Compatibility and safety

- C++11 is the required language level for the current Android API 11 profile.
- The runtime is side-effect-free by default. File, network, sensor, and physical-device operations require explicit adapters and caller authorization.
- Digital frequency values are metadata/simulation inputs only. No biological, DNA/RNA, consciousness, or physical-emission effect is claimed.
- Existing SQLite schemas and serialized records must be preserved or migrated with versioned, tested migrations.
- Do not delete Python source until parity tests and an explicit removal review pass.

## Verification

Host tests should compile with a standard C++11 compiler. Android CI must continue to build `:app:assembleDebug`. A successful commit alone is not proof of a successful build or APK artifact.
