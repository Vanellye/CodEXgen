# NEXUS Source Records — Native Runtime and Higher Faculty

**Inspection target:** `Vanellye/CodEXgen`  
**Source branch:** `integration/olpirt-stride-next`  
**Pinned source revision:** `3d58239759539c19495274633ee309391e37ea1b`  
**Inspection mode:** read-only repository and source inspection  
**Purpose:** record implementation evidence and unresolved adapter gaps before any adoption proposal.

> A source file proves that code exists at a revision. It does not, by itself, prove runtime wiring, safety, correctness, or authorization.

## 1. Source-bound records

### NEXUS-PANTHEON-FACULTY-001 — Native Faculty Engine

- **Kind:** `KNOW_HOW`
- **Claim:** PANTHEON contains a native C++ Faculty Engine with perception scoring, deterministic idea recombination, bounded scalar prediction adaptation, and channel-plan generation.
- **Source:** [faculty_engine.cpp](https://github.com/Vanellye/CodEXgen/blob/3d58239759539c19495274633ee309391e37ea1b/pantheon/src/faculty_engine.cpp)
- **Contract:** [faculty_engine.hpp](https://github.com/Vanellye/CodEXgen/blob/3d58239759539c19495274633ee309391e37ea1b/pantheon/include/pantheon/faculty_engine.hpp)
- **Method:** source inspection; native test target exists at [faculty_engine_test.cpp](https://github.com/Vanellye/CodEXgen/blob/3d58239759539c19495274633ee309391e37ea1b/pantheon/tests/faculty_engine_test.cpp)
- **Evidence status:** `SUPPORTED` for source presence and declared behavior; not an independent assessment of all runtime effects.
- **Limitations:** channel planning is metadata/planning output; it is not proof of physical signal emission or biological effect.

### NEXUS-PANTHEON-RUNTIME-002 — Module runtime

- **Kind:** `KNOW_HOW`
- **Claim:** PANTHEON has a C++ module registry/runtime with ordinary execution and a separate controlled execution path.
- **Source:** [runtime.cpp](https://github.com/Vanellye/CodEXgen/blob/3d58239759539c19495274633ee309391e37ea1b/pantheon/src/runtime.cpp)
- **Contract:** [runtime.hpp](https://github.com/Vanellye/CodEXgen/blob/3d58239759539c19495274633ee309391e37ea1b/pantheon/include/pantheon/runtime.hpp)
- **Method:** source inspection.
- **Evidence status:** `SUPPORTED`.
- **Limitations:** the native runtime is not yet exposed as a Kotlin-callable execution API by the inspected JNI bridge.

### NEXUS-PANTHEON-POLICY-003 — 38-standard owner approval gate

- **Kind:** `KNOW_WHY`
- **Claim:** controlled PANTHEON execution requires exactly 38 distinct numbered standards, each passed with a non-empty evidence reference, and an authenticated owner approval.
- **Source:** [control_gate.cpp](https://github.com/Vanellye/CodEXgen/blob/3d58239759539c19495274633ee309391e37ea1b/pantheon/src/control_gate.cpp)
- **Contract:** [control_gate.hpp](https://github.com/Vanellye/CodEXgen/blob/3d58239759539c19495274633ee309391e37ea1b/pantheon/include/pantheon/control_gate.hpp)
- **Method:** source inspection; test target exists at [control_gate_test.cpp](https://github.com/Vanellye/CodEXgen/blob/3d58239759539c19495274633ee309391e37ea1b/pantheon/tests/control_gate_test.cpp)
- **Evidence status:** `SUPPORTED`.
- **Limitations:** `OwnerApproval` is an interface. Authentication and persistence depend on the concrete implementation supplied by the host. A boolean interface alone is not an identity system.

### NEXUS-STRIDE-SEAM-004 — Stride feature adapter

- **Kind:** `KNOW_HOW`
- **Claim:** the native Stride seam converts feature/value pairs into PANTHEON numeric input.
- **Source:** [stride_adapter.hpp](https://github.com/Vanellye/CodEXgen/blob/3d58239759539c19495274633ee309391e37ea1b/pantheon/include/pantheon/stride_adapter.hpp)
- **Method:** source inspection.
- **Evidence status:** `SUPPORTED`.
- **Limitations:** this is an input conversion helper. It does not schedule JOBs, manage checkpoints, perform lifecycle reconciliation, or itself invoke the PANTHEON runtime.

### NEXUS-ANDROID-JNI-005 — Existing native bridge boundary

- **Kind:** `FACT`
- **Claim:** the Android CMake target compiles the PANTHEON runtime, control gate, Faculty Engine, and gateway into `codexgen_pons`.
- **Source:** [app CMakeLists](https://github.com/Vanellye/CodEXgen/blob/3d58239759539c19495274633ee309391e37ea1b/app/src/main/cpp/CMakeLists.txt)
- **JNI source:** [olpirt_jni.cpp](https://github.com/Vanellye/CodEXgen/blob/3d58239759539c19495274633ee309391e37ea1b/app/src/main/cpp/jni/olpirt_jni.cpp)
- **Kotlin/Java bridge:** [OlpirtNativeBridge.java](https://github.com/Vanellye/CodEXgen/blob/3d58239759539c19495274633ee309391e37ea1b/app/src/main/java/com/vanellye/codexgen/nativebridge/OlpirtNativeBridge.java)
- **Method:** build-file and JNI source inspection.
- **Evidence status:** `SUPPORTED`.
- **Limitations:** current JNI exports status and gateway-origin functions only. It does not expose FacultyEngine calls, construct a PANTHEON Runtime, register FacultyModule, or invoke controlled execution from the Android app.

### NEXUS-STRIDE-HTTP-006 — Existing Stride service client

- **Kind:** `KNOW_HOW`
- **Claim:** Android has a separately running Stride HTTP client for faculty jobs, geometry attachments, job import, and artifact listing.
- **Source:** [StrideEngineClient.java](https://github.com/Vanellye/CodEXgen/blob/3d58239759539c19495274633ee309391e37ea1b/app/src/main/java/com/vanellye/codexgen/jobs/StrideEngineClient.java)
- **Method:** source inspection.
- **Evidence status:** `SUPPORTED`.
- **Limitations:** this client is a bearer-token HTTP adapter to a separate service. It is not the native PANTHEON runtime adapter. Remote URLs require HTTPS; cleartext is limited to localhost.

### NEXUS-GENESIS-007 — GENESIS implementation status

- **Kind:** `OPEN_QUESTION`
- **Claim:** no concrete GENESIS engine implementation or adapter was identified in the inspected branch trees and file searches.
- **Inspected scopes:** `main`, `integration/wantever-propagation`, `integration/olpirt-stride-next`, `eria/new-pantheon-staging`, and related PANTHEON staging sources.
- **Method:** read-only branch/file inventory and searches for implementation identifiers.
- **Evidence status:** `UNKNOWN` for repository-wide existence; implementation not established in inspected scopes.
- **Direction:** locate an authoritative GENESIS source branch/path and pin its exact head before writing an adapter. Do not create a fake implementation to satisfy the interface.

### NEXUS-FORGE-008 — FORGE implementation status

- **Kind:** `OPEN_QUESTION`
- **Claim:** no concrete FORGE engine implementation or adapter was identified in the inspected branch trees and file searches.
- **Inspected scopes:** `main`, `integration/wantever-propagation`, `integration/olpirt-stride-next`, `eria/new-pantheon-staging`, and related PANTHEON staging sources.
- **Method:** read-only branch/file inventory and searches for implementation identifiers.
- **Evidence status:** `UNKNOWN` for repository-wide existence; implementation not established in inspected scopes.
- **Direction:** locate an authoritative FORGE source branch/path and pin its exact head before writing an adapter. Do not substitute a stub for the real artifact-construction implementation.

## 2. Relationship map

| From | Relationship | To | Meaning |
|---|---|---|---|
| Faculty Engine | `IMPLEMENTS` | Higher Faculty proposal | Native computation exists; product-level adoption remains pending |
| Control Gate | `GATES` | Controlled Runtime execution | Requires complete evidence and owner approval |
| Stride adapter | `RELATED_TO` | PANTHEON Runtime | Converts inputs; does not provide lifecycle orchestration |
| JNI bridge | `DEPENDS_ON` | PANTHEON native library | Current exported calls are status/provenance only |
| GENESIS | `UNKNOWN` | NEXUS | Source implementation not located in inspected scopes |
| FORGE | `UNKNOWN` | NEXUS | Source implementation not located in inspected scopes |

## 3. Integration decision

**Current decision: HOLD — do not promote or merge this integration yet.**

Reasons:

1. Actual GENESIS and FORGE implementations have not been located.
2. PANTHEON native source is present, but Android JNI does not expose its Faculty or controlled execution functions.
3. The Stride feature adapter is only an input converter; the HTTP Stride client targets a separate service.
4. The existing `integration/olpirt-stride-next` merge candidate and the WANTEVER feature branch are separate histories and have not been validated together at one combined commit.
5. The current WANTEVER feature branch has passing Android unit tests, but those tests do not validate native PANTHEON/Stride integration.

## 4. Verification and approval record

- WANTEVER feature head tested: `e3a84a5960c5eaf79a9e747775423f15c3dc3be6`.
- GitHub Actions run: [Independent Branch CI #732](https://github.com/Vanellye/CodEXgen/actions/runs/43393377466).
- Android job: `Android debug APK build`, completed successfully.
- Exact commands logged: `./gradlew --no-daemon --stacktrace :app:testDebugUnitTest` and `:app:assembleDebug`.
- Native OLPIRT integration candidate: `3d58239759539c19495274633ee309391e37ea1b`.
- Its separate CI run: [Independent Branch CI #316](https://github.com/Vanellye/CodEXgen/actions/runs/42740293431), including Android NDK/CMake build.
- These are separate commits and runs, not a combined integration test.

No branch ref was changed by this inspection. No finding was promoted. No merge, force update, deployment, or runtime execution was performed.
