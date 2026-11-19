# ERIA Code-to-English Index

**Source repository:** `Vanellye/CodEXgen`  
**Source branch inspected:** `feature/pantheon-planting-seeds-termux-2026-11-13`  
**Index type:** human-readable guide to the inspected source files  
**Purpose:** explain what the source code says and what its implemented behavior supports.

> This is a descriptive index, not a compiler, formal specification, proof of runtime behavior, or claim that every feature is operational. English explanations below are derived from the named source files. Names and comments are preserved where they carry project meaning. Where a name suggests more than the code implements, the implementation boundary is stated.

## 1. How to read this index

| Source construct | Plain-English reading |
|---|---|
| `class Foo` | Defines a named object type and the behavior attached to it. |
| `data class Foo(...)` (Kotlin) | Defines a value-like record whose listed fields hold its data. |
| `enum class Foo` / `enum Foo` | Defines a closed list of named states or categories. |
| `fun foo(...)` / `def foo(...)` | Defines an operation that can be called with the listed inputs. |
| `interface Foo` / `fun interface Foo` | Defines a contract that an implementation must satisfy. |
| `object Foo` (Kotlin) | Defines one globally accessible singleton object. |
| `@Composable` | Marks a Kotlin function that describes UI for Jetpack Compose. |
| `StateFlow<T>` | Exposes a stream of current state updates to observers. |
| `sqlite3.connect(...)` | Opens a SQLite database connection. |
| `subprocess.run([...])` | Starts a child process with the explicitly supplied argument list. |
| `require(condition)` | Rejects input when the condition is false. |
| `return` | Ends the current function and gives its result to the caller. |
| `try / except` | Attempts work and handles selected failures. |
| `sha256(bytes)` | Computes a SHA-256 digest of the exact supplied bytes. |
| `INSERT ... ON CONFLICT` | Inserts a database row or updates the matching row according to the SQL clause. |
| `PRIMARY KEY` | Identifies a row uniquely in a table. |
| `CHECK(...)` | Makes SQLite reject rows that violate the stated condition. |

## 2. Application and Android UI

### `app/src/main/java/com/vanellye/eria/MainActivity.kt`

**English purpose:** The Android entry screen. It starts the Compose UI, shows ERIA status, and switches between the conversation WebView and the native repository dashboard.

- `onCreate`: Android calls this when the activity is created.
- `setContent`: builds the Compose interface.
- `pageStatus`: text shown for the conversation connection state.
- `loading`: controls whether the progress indicator is visible.
- `reloadKey`: changes to recreate the WebView and reload its page.
- `showRepositoryDashboard`: selects either the native dashboard or conversation page.
- `AndroidView`: embeds the Android WebView inside Compose.
- WebView JavaScript and DOM storage are enabled for the local web application; file/content access and multiple windows are disabled in the inspected setup.

**Boundary:** This file hosts the UI. It does not itself implement repository indexing or database synchronization.

### `app/src/main/java/com/vanellye/eria/EriaServerConfig.kt`

**English purpose:** Central place for the conversation server address.

- `HOST`: configured server host.
- `PORT`: configured server port.
- `BASE_URL`: full root URL assembled as a constant.

**Observed configuration:** `http://111.1.1.1:1111/`. This is a literal configuration value, not proof that a server is reachable at that address.

### `app/src/main/java/com/vanellye/eria/RepositoryDashboardScreen.kt`

**English purpose:** Native dashboard for viewing repository and ERIA service information.

- `ERIA_API`: local API base URL, currently `http://127.0.0.1:8765`.
- `REFRESH_INTERVAL_MS`: periodic refresh interval (15 seconds).
- `SEARCH_DEBOUNCE_MS`: delay used to avoid firing a search on every keystroke.
- `DashboardTab`: the five dashboard areas: Overview, Files, Provenance, Audit, and PONS.
- `RepositoryFile`: path, size, hash, and extension shown for a repository file.
- `AuditEvent`: one audit record with event, status, detail, and timestamp.
- `AuthorizationRequest`: a PONS request shown with capability, scope, reason, status, and time.
- `RepositoryDashboardScreen`: owns UI state and coordinates API reads.

**Boundary:** The dashboard is a client of the local API. It does not independently prove that every displayed source record is authoritative.

### `app/src/main/java/com/vanellye/eria/CodeGenScreen.kt`

**English purpose:** A Compose screen for entering a module name and requesting generated source text.

- `CodeGenRoute`: connects the screen to its ViewModel and collects its state.
- `moduleName`: text entered by the user.
- `onGenerateClick`: requests generation using the configured base class and attributes.
- `CodeGenScreen`: stateless presentation layer; draws the input, button, loading state, generated code, or error.

### `app/src/main/java/com/vanellye/eria/CodeGenViewModel.kt`

**English purpose:** Performs code generation away from the UI thread and publishes the result.

- `uiState`: observable state with Idle, Loading, Success, or Error.
- `generateCode`: rejects a blank module name, sets Loading, generates source on a background dispatcher, and then publishes Success or Error.
- `buildModuleSource`: renders a Python class with a constructor and requested attributes.

**Boundary:** The generator creates source text. It does not compile or execute that generated Python module.

## 3. Data, writing, and transmission contracts

### `app/src/main/java/com/vanellye/eria/contracts/DataEnvelope.kt`

**English purpose:** Defines a structured data record and validates its shape, metadata, and authorization fields.

- `DataQuality`: labels data as VALID, STALE, OUT_OF_RANGE, UNCALIBRATED, SENSOR_FAULT, or UNKNOWN.
- `AuthorizationStatus`: says NOT_AUTHORIZED, AUTHORIZED, or DECLINED.
- `MonotonicTime`: a clock value plus the clock domain that produced it.
- `DataProvenance`: optional source reference, source commit, source digest, signer, and signature status.
- `DataTransformation`: records an operation name/version and optional parameter/output digests.
- `DataAuthorization`: records status, approved scopes, and an approval reference.
- `DataEnvelope`: combines the record ID, schema version, source, observation time, payload, units, quality, provenance, transformations, authorization, validation, retention, and optional monotonic time.
- `DataEnvelopeValidator.validate`: returns a list of readable validation errors. An empty list means the implemented checks passed.

**Important distinction:** The source comment explicitly separates validation from authorization. A valid data record does not itself grant permission to perform an operation. A signature status field is metadata; this validator does not by itself authenticate a signer.

### `app/src/main/java/com/vanellye/eria/contracts/SkribedAndTransmission.kt`

**English purpose:** Keeps original written content separate from edited or translated versions, and defines an integrity-checked in-memory transmission contract.

- `WritingVariantKind`: ORIGINAL, CORRECTED, INTERPRETED, or TRANSLATED.
- `WritingProvenance`: optional author, source, and creation references.
- `WritingVariant`: derived text plus operation, operation version, and output digest.
- `SkribedDocument`: stores original UTF-8 bytes and their SHA-256 digest. The original is not replaced by a derivative.
- `derive`: creates a non-original variant and requires an operation name and version.
- `TransmissionFrame`: holds transmission/correlation/source IDs and a defensive copy of payload bytes.
- `hasValidIntegrity`: checks whether the payload still matches its SHA-256 digest.
- `TransmissionReceipt`: records request and response digests and response bytes.
- `InternalTransmissionEndpoint`: local receive contract.
- `InMemoryTransmissionTransceiver`: checks integrity, gives the endpoint a copied frame, and returns a receipt.

**Boundary:** The inspected transceiver is explicitly in-process. It does not provide sockets, webhooks, media players, hardware actuators, or external destinations.

### `app/src/main/java/com/vanellye/eria/pantheon/PantheonRuntimeGate.kt`

**English purpose:** Checks whether a data envelope can be prepared for human review.

- `PantheonGateStatus`: names the HOLD reasons and REVIEW_READY result.
- `PantheonReview`: returns the gate result, record ID, requested scope, approval reference, validation errors, and whether an action was taken.
- `prepareReview`: validates the envelope, checks authorization, checks exact scope, and requires human review confirmation.
- `actionTaken`: remains false in the returned review object.

**Boundary:** REVIEW_READY means a proposal may be presented to a person. It is not execution permission. The file comment states that this adapter has no executor, provider client, filesystem writer, process launcher, network client, or Git mutation capability.

## 4. Repository conversation and PONS

### `tools/eria_repository_conversation.py`

**English purpose:** Read-only command-line repository inspector and conversational router.

- `VERSION`: engine version string (1.1 in the inspected source).
- `MAX_BYTES`: maximum size for a file opened for inspection (1,000,000 bytes).
- `MAX_HITS`: maximum number of search matches returned (30).
- `SKIP_DIRS`: generated, dependency, and metadata directories excluded from traversal.
- `SECRET_NAME` / `SECRET_VALUE`: patterns used to skip likely secret-named files and redact matching secret-like values.
- `Repository.__init__`: confirms the selected path belongs to a Git working tree and resolves the repository root.
- `Repository.git`: allows only status, branch, log, ls-files, remote, tag, and rev-parse commands.
- `Repository.files`: lists tracked and non-ignored untracked paths.
- `Repository.show`: reads one bounded, non-binary file inside the repository root and redacts matching secret-like values.
- `Repository.search`: searches eligible text files and returns bounded matching lines.
- `fmt`: maps common file extensions to human-readable format names.
- `Conversation.ask`: routes natural-language requests to read-only status, branch, commit history, remote-name, tag, file inventory, search, and optional PANTHEON commands.

**Boundary:** The allowlist is read-only. The remote command returns names rather than URLs to avoid credential disclosure. This engine is an inspector, not a Git write/deployment tool.

### `tools/eria_conversation_server.py`

**English purpose:** Serves the ERIA HTML conversation UI and exposes local HTTP endpoints backed by the repository conversation engine and SQLite.

- `Store`: manages chat messages, repository index metadata, audit events, and PONS requests.
- `index_repository`: indexes eligible repository paths and computes SHA-256 for files up to 5 MiB.
- `add_audit`: appends an audit event.
- `audit_history`: reads recent audit records.
- `provenance`: returns indexed path metadata and source hashes.
- `search_files`: searches indexed paths using a parameterized SQL query.
- `Handler.do_GET`: serves the UI and read endpoints such as status, history, files, provenance, and audit.
- `Handler.do_POST`: accepts chat, index refresh, and PONS request creation.
- `App`: connects the repository, conversation engine, and database.
- `main`: validates loopback binding and starts the HTTP server.

**Boundary:** The inspected server deliberately binds to loopback. Its PONS requests are recorded as HOLD proposals; the endpoint does not approve grants. The server's own comments state that no arbitrary SQL, shell, or filesystem-write endpoint is exposed.

### `tools/eria_pantheon/pons.py`

**English purpose:** Defines the PONS dependency registry, source/derived provenance envelope, and exact-scope capability decision types.

- `Decision`: HOLD, PROPOSAL_ONLY, or REVIEW_READY.
- `Lifetime`: singleton or transient service lifetime.
- `BridgeEnvelope`: keeps source identity and source digest alongside optional derived digest, transformations, and provenance. Both source and derived authority default to NON_AUTHORITATIVE.
- `from_bytes`: creates an envelope and hashes the original bytes.
- `with_derived`: returns a new envelope describing derived bytes without replacing or promoting the source.
- `CapabilityGrant.permits`: requires the exact capability, non-empty approval reference, adapter verification assertion, and exact requested/approved scope match.
- `Pons`: registers caller-supplied factories and resolves dependencies; resolution itself has no implicit network, filesystem, process, Git, or hardware behavior.

**Boundary:** The module's docstring explicitly says this is an application-level contract boundary, not an OS sandbox, identity provider, cryptographic verifier, or Pantheon compiler/runtime. An adapter assertion is not cryptographic proof.

### `tools/eria_pantheon/interface.py`

**English purpose:** Routes a small set of text commands into the PONS bridge and repository inspector.

- `status`: reports PONS state, repository root, conversation connection, and whether the code-bypass module can be imported.
- `handle`: accepts integration/bridge/PONS status, repository questions, and code-bypass requests.
- `_code_bypass`: requires a repository-relative regular text file and a reason; checks the path stays inside the repository; invokes the bypass processor with translator and transmitter callbacks that deliberately raise if called; then builds a provenance envelope.

**Boundary:** The bypass command is not a general code translator. Its stated behavior is to preserve code bytes while bypassing translation/transmission and recording an audit result.

## 5. Other inspected source modules

### `tools/eria_invention_events.py`

**English purpose:** Invention/event persistence module identified in the repository tree. This index has not inspected its full implementation; consult that file before relying on detailed behavior.

### `python/adaptive_governance.py`

**English purpose:** Defines telemetry records, a SQLite telemetry store, a correction-frequency calculation, a prompt tuner, and an orchestration class.

- `InteractionTrace`: groups prompt, response, embedding, and correction count fields.
- `AdaptiveTelemetryDatabase`: creates a telemetry table, appends event metrics, and calculates the fraction of recent events marked SELF_CORRECTION.
- `AdaptivePromptTuner.adjust_prompt`: changes prompt wording according to the supplied correction rate.
- `AutonomousGovernanceOrchestrator`: begins the adaptive governance orchestration implementation.

**Boundary:** The module imports NumPy. The index does not claim it has been executed or that its adaptive policy is validated.

### `python/code_generator.py`

**English purpose:** Deterministically renders a Python model module from a specification.

- `DEFAULT_SPEC`: default module name, attributes, and base class.
- `ModuleSpecification`: data describing a module to generate.
- `CodeGeneratorEngine.render_template`: creates the Python source text.
- `build_module`: writes the generated file only when its content differs from the existing file.
- `main`: parses the output directory and generates the default module.

**Boundary:** Unlike the Android CodeGenViewModel, this Python generator writes a generated file to its output directory. It does not execute the generated module.

### `security/red-write-only/tools/storage_adapter.py`

**English purpose:** Implements a guarded, create-only filesystem adapter.

- `CreateOnlyStorageAdapter`: accepts a trusted root directory descriptor, authorization guard, and audit sink.
- `create`: checks content type and size, asks the guard for an authorization decision, records the decision before attempting a write, and refuses denied operations.
- Directory traversal uses no-follow directory opens; file creation uses exclusive create so an existing file is not overwritten.
- The file is synced before success is returned.

**Boundary:** This is a constrained create-only writer, not a general update/delete interface. It depends on the host supplying a trusted root descriptor and an append-only audit sink.

### `pantheon/FACTUAL_LOGIC/FACTUAL_LOGIC.h`

**English purpose:** Declares C-compatible evidence classification labels and a function to format an evidence label.

- `EriaClaimClass`: UNCLASSIFIED, OBSERVED, SOURCE_REPORTED, CORROBORATED, HYPOTHESIS, and INTERPRETATION.
- `EriaFactStatus`: success and several failure/insufficient-evidence statuses.
- `EriaFactClaim`: claim text and its source, provenance, and support references.
- `eria_fact_describe`: declared function that formats an evidence label.

**Boundary:** The header comment says formatting an evidence label does not authenticate a source or prove a claim true. This file is a declaration; implementation must be inspected separately.

## 6. Repository path map

The following paths were present in the inspected source branch tree. Their inclusion is a navigation aid; entries not described in sections 2–5 have not been semantically reviewed in this pass.

### Android application
- `app/src/main/AndroidManifest.xml`
- `app/src/main/java/com/vanellye/eria/`
- `app/src/main/java/com/vanellye/eria/contracts/`
- `app/src/main/java/com/vanellye/eria/pantheon/`
- `app/src/main/res/values/`
- `app/src/test/java/com/vanellye/eria/`

### Compose UI sources
- `compose/CodeGenScreen.kt`
- `compose/CodeGenUiState.kt`
- `compose/CodeGenViewModel.kt`

### Python and generated modules
- `python/adaptive_governance.py`
- `python/code_generator.py`
- `python/semantic_vector_memory.py`
- `generated_modules/userprofile_module.py`

### ERIA tools
- `tools/eria_conversation.html`
- `tools/eria_conversation_server.py`
- `tools/eria_repository.html`
- `tools/eria_repository_conversation.py`
- `tools/eria_pantheon/interface.py`
- `tools/eria_pantheon/pons.py`
- `tools/eria_invention_events.py`
- `tools/eria_ttt_bypass.py`

### PANTHEON C/C++ headers and test runner
- `pantheon/FACTUAL_LOGIC/FACTUAL_LOGIC.h`
- `pantheon/IC/IC.h`
- `pantheon/NEW/`
- `pantheon/run-contract-tests.sh`

### Security boundary tools
- `security/red-write-only/tools/execution_boundary_guard.py`
- `security/red-write-only/tools/storage_adapter.py`
- `security/red-write-only/tools/validate_policy.py`
- `security/red-write-only/tests/`

### Termux scripts
- `termux/eria-root-audit.sh`
- `termux/eria-root-inventory.sh`
- `termux/eria-show-files.sh`
- `termux/genesis-termux.sh`

## 7. Cross-cutting English glossary

| Code / project term | Plain-English meaning in this repository |
|---|---|
| ERIA | Application and repository-intelligence system name used by this project. |
| PANTHEON | Project namespace for runtime and contract components; names alone do not imply a compiler or execution engine. |
| PONS | Dependency registry and capability/provenance bridge. |
| HOLD | Stop here; the requested operation is not cleared to proceed. |
| PROPOSAL_ONLY | A proposal exists, but it is not an approved execution. |
| REVIEW_READY | Validated proposal can be presented for human review; not execution permission. |
| provenance | Information identifying where a record came from and how it was derived. |
| source digest | Hash used to identify the exact source bytes. |
| derived record | A transformed representation kept distinct from the original source. |
| source authority | Whether the source is treated as authoritative; inspected PONS envelope defaults this to NON_AUTHORITATIVE. |
| scope | The exact resource or action covered by a permission request. |
| capability | A named ability that must be explicitly granted for a matching scope. |
| audit event | A timestamped record of an operation or decision. |
| create-only | May create a new file if absent; does not replace an existing file. |
| read-only Git inspection | Queries Git state without changing branches, commits, refs, or the working tree. |
| bypass | In the inspected adapter, preserve code bytes while skipping translation/transmission and recording the reason. |

## 8. Translation and evidence rules

1. Explain the code that exists; do not translate a name into a capability the implementation does not contain.
2. Preserve exact identifiers, file paths, enum values, and important error/status strings.
3. Separate source code, comments, inferred intent, and verified runtime behavior.
4. Keep original bytes and hashes distinct from translated or interpreted text.
5. Label a generated English explanation as a derivative, with the source path and source revision attached.
6. If the implementation is only a declaration, stub, interface, or test fixture, say so.
7. Do not treat words such as secure, factual, autonomous, verified, or ready as proof without the relevant implementation and tests.
8. Update this index when source paths or content change; do not silently overwrite the previous indexed revision.

## 9. Coverage and limitations

This is a first-pass index of the feature branch's source tree, based on the files explicitly inspected for this document. It is not a line-by-line translation of every source file. The repository tree also contains other Kotlin, Python, C/C++, shell, HTML, and test files that require their own source inspection before they can be accurately translated.

The index does not claim:
- that the Android app was built or run;
- that the local ERIA server was reachable;
- that the PONS contracts provide operating-system isolation or cryptographic identity;
- that declared C/C++ functions have working implementations;
- that every feature described by comments is implemented;
- that tests passed unless a test run result is separately recorded.

## 10. Source revision record

| File | Source branch | Blob SHA-1 |
|---|---|---|
| `MainActivity.kt` | `feature/pantheon-planting-seeds-termux-2026-11-13` | `8d8807e253df0766791bc1c6f4b7b187fbe735e7` |
| `CodeGenViewModel.kt` | same | `de0945e089ba2e1d06a8c23ae53f674454d83051` |
| `CodeGenScreen.kt` | same | `8d5638690e5688e6a15427f361b5802f92b34ed7` |
| `EriaServerConfig.kt` | same | `f1d2a2b825756bd395dc6fe9ec410b207fdc93e6` |
| `RepositoryDashboardScreen.kt` | same | `6471b3335778790338bea3676fdbe53a8bf59142` |
| `DataEnvelope.kt` | same | `f86686d1fd0a745461c46226105e80832a9624d6` |
| `SkribedAndTransmission.kt` | same | `abbb251d5d832441698c478652d0187adf0770a4` |
| `PantheonRuntimeGate.kt` | same | `fe022967f8c1f02ad5ca2b5fe214f5426749688b` |
| `eria_repository_conversation.py` | same | `b1e91d17c10890191fcea8910832bce50c584b7a` |
| `eria_conversation_server.py` | same | `b98510d2ab5ddc55f0c6a925eb42339ed9c7ef03` |
| `pons.py` | same | `e9418cc805aaa195f9ac2b8d1896eaf68de86008` |
| `interface.py` | same | `c20947301bea5284096bf0e20ddad6e27802becc` |
| `adaptive_governance.py` | same | `b0a4635e3498fc8838c93ba28c0e151613349a5c` |
| `code_generator.py` | same | `309c52afdcd2c44619cdaf5a1f28b6ab7c1bdc7a` |
| `storage_adapter.py` | same | `418b0129007fa180d60642c7202ea5f9e4b11c93` |
| `FACTUAL_LOGIC.h` | same | `e45c0d0782fa808cba5af915c5cf3453f3265c5d` |

---

**Index status:** First-pass source-grounded English guide. Expand file-by-file as additional source is inspected.
