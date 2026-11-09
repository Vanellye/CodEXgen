# Pantheon Native Runtime

Pantheon is the native execution core for CodEXgen/Stride. The first milestone establishes a C++11 runtime contract, a Stride framework adapter, and a host-testable foundation. It does not yet claim that every Python module has been ported.

## Universal workflow — JOBs

CodEXgen's universal workflow treats a JOB as a **Journey of Becoming**, not a fixed occupational role or conformity target. The lifecycle is adaptable, supports pause/recovery and independent branches, and preserves purpose, evidence, provenance, consent, and contributor agency. See [Universal Workflow — JOBs](../docs/UNIVERSAL-WORKFLOW-JOBS.md). This is currently a documented design contract; runtime implementation and tests remain separate milestones.

## Architecture

- **Core runtime** — deterministic module registration and execution with explicit input/output records.
- **Framework adapter** — translates existing Stride feature maps into Pantheon inputs without changing the legacy Python API.
- **Android bridge** — the Android JNI target links the same runtime library; no Python interpreter is required by the native core.
- **Migration modules** — each Python capability is ported separately and compared against Python reference fixtures.
- **Gateway origin** — the Faculty Engine integration commit is carried as immutable provenance; the Gateway Router ranks authorized and safe execution paths by compatibility, readiness, and reliability.
- **Compatibility period** — Python remains the reference implementation until native parity tests pass.
- **38/38 control gate** — control modules are fail-closed until all 38 numbered standards pass with evidence references and an authenticated owner approval is supplied. The gate authorizes only in-process module invocation; it does not grant system-wide or physical-device control. See [Control Authorization Standard](CONTROL_AUTHORIZATION.md).
- **Principle 43 — The Cleansing of Thought** — protects the distinction between thoughts, intentions, and actions; safeguards mental privacy; keeps reflection voluntary; and separates spiritual guidance from clinical claims. Compliance requires mapped controls, passing acceptance tests, and recorded human review. See [Principle 43](PRINCIPLE-43.md).
- **Principle 44 — The Devotion of Whole-Being Renewal** — grounds renewal in dignity, voluntary devotion, compassion, and care for body and mind. See [Principle 44](PRINCIPLE-44.md).
- **Principle 45 — The Covenant of Truthful Stewardship** — requires evidence-based judgments, independent review, correction, appeal, and accountability for human and automated decision-makers. See [Principle 45](PRINCIPLE-45.md).
- **Principle 46 — The Guiding Lights** — calls for guidance without domination, intergenerational learning, continual refinement of the Main, and stewardship without possession. See [Principle 46](PRINCIPLE-46.md).
- **Rise & Fall Directives** — deterministic ơ (RISE), ọ (FALL), and WARDEN policy combining declared principles with evidence; symbolic propagation is not physical quantum entanglement. See [Rise & Fall Directives](../docs/RISE-FALL-DIRECTIVES.md).
- **JGit capability checkpoint** — Android components obtain the shared Git Freedom Bridge through `GitFreedomBridge.shared(context)`. Its JGit dependency is pinned to `3.7.1.201504261725-r`, anchored to origin checkpoint `f63e166e11aee325fe0ea8504672f19134d2768b`. This is app-process capability discovery, not unrestricted operating-system or cross-device control. See [JGit Compatibility Checkpoint](../docs/JGIT-COMPATIBILITY-CHECKPOINT.md).

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
- See [Gateway Origin](GATEWAY_ORIGIN.md) for the provenance and routing policy.

## Verification

Host tests should compile with a standard C++11 compiler. Android CI must continue to build `:app:assembleDebug`. A successful commit alone is not proof of a successful build or APK artifact.
