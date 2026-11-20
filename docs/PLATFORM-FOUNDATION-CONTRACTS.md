# ERIA — Universal Platform Foundation Contracts

**Status:** proposed, language-neutral interface specification  
**Target:** `integration/wantever-propagation`  
**Scope:** platform and data-platform identity, interoperability, and engine discovery  
**Implementation status:** this document defines contracts; it does not claim runtime enforcement.

## 1. Design invariants

1. A platform has a stable identity independent of its display name, repository, deployment, or hosting provider.
2. A manifest describes a platform; it does not authorize execution.
3. A contract describes compatibility and communication; it does not grant access.
4. An engine registry describes discoverable engines; registration does not imply trust or permission to invoke.
5. Data schemas are versioned, typed, unit-aware, and explicit about null, absent, unknown, and invalid values.
6. Imported manifests, contracts, engine metadata, and payloads are untrusted until validated.
7. Every consequential operation is scoped to an explicit authorization record.
8. Source identity, version, digest, and transformation provenance are retained.
9. Failure is explicit. No silent fallback, implicit external dispatch, or automatic privilege expansion.
10. Platform adapters preserve independent implementations rather than forcing a shared runtime.

## 2. PlatformManifest

A `PlatformManifest` is the declarative identity and capability description for one platform or data platform.

### Required fields

| Field | Type | Meaning |
|---|---|---|
| `manifest_version` | semantic version | Version of this manifest schema |
| `platform_id` | stable URI or reverse-DNS identifier | Immutable platform identity |
| `name` | string | Human-readable name |
| `platform_version` | semantic version | Version of the platform implementation |
| `kind` | enum | `application`, `service`, `data-platform`, `library`, `runtime`, or `composite` |
| `owner` | identity reference | Responsible organization or maintainer identity |
| `interfaces` | interface references | Contracts implemented or consumed |
| `capabilities` | capability declarations | What the platform can offer, not what it may automatically do |
| `dependencies` | dependency declarations | Required platform, engine, or schema dependencies |
| `data` | data declarations | Data products, schemas, classifications, and retention metadata |
| `runtime` | runtime constraints | Required language/runtime/OS and supported versions |
| `provenance` | provenance record | Source repository/ref/revision and content digest |

Optional fields include description, documentation links, tags, deployment profiles, health endpoints, and extension metadata. Unknown extension fields must be namespaced.

### Example

```yaml
manifest_version: "1.0.0"
platform_id: "urn:eria:platform:knowledge-hub"
name: "Knowledge Hub"
platform_version: "0.1.0"
kind: "data-platform"
owner:
  type: "organization"
  id: "urn:eria:owner:project-team"
interfaces:
  provides:
    - contract_id: "urn:eria:contract:records"
      version: "^1.0"
  consumes: []
capabilities:
  - id: "records.read"
    mode: "local"
  - id: "records.write"
    mode: "local"
dependencies: []
data:
  products:
    - id: "knowledge-record"
      schema: "urn:eria:schema:knowledge-record"
      schema_version: "1.0.0"
      classification: "internal"
      retention: "policy-defined"
runtime:
  language: "kotlin"
  minimum_version: "17"
provenance:
  repository: "Vanellye/CodEXgen"
  ref: "integration/wantever-propagation"
  revision: "<exact-commit-sha>"
  digest: "<sha256>"
```

Placeholders are illustrative and must be replaced with verified values before publication.

## 3. PlatformContract

A `PlatformContract` defines the compatibility boundary between a provider and a consumer. It is transport-neutral: HTTP, events, in-process calls, files, and message brokers are adapters, not the contract itself.

### Required fields

| Field | Type | Meaning |
|---|---|---|
| `contract_id` | stable URI | Contract identity |
| `contract_version` | semantic version | Contract version |
| `provider` | platform/interface reference | Provider identity |
| `consumer` | platform/interface reference or wildcard policy | Intended consumer scope |
| `operations` | operation definitions | Named request/response or event shapes |
| `schemas` | schema references | Input, output, and event schemas |
| `compatibility` | policy | Supported version negotiation rules |
| `security` | policy | Authentication, authorization, and data handling requirements |
| `delivery` | delivery semantics | Ordering, idempotency, retry, timeout, and acknowledgement |
| `errors` | typed error catalog | Stable error codes and recovery guidance |
| `provenance` | provenance record | Contract source and digest |

Each operation defines its effect class: `read`, `write`, `compute`, or `external`. External effects require a separately scoped authorization. Retry policy must not repeat non-idempotent effects without an idempotency key or explicit operator decision.

### Compatibility rules

- Patch versions must preserve the published contract.
- Minor versions may add optional fields or operations without changing existing meanings.
- Major versions may make breaking changes and require explicit migration.
- Consumers must reject unsupported major versions.
- Producers must not silently reinterpret units, identifiers, timestamps, or nullability.
- Negotiation failure is explicit and must not downgrade security or permissions.

## 4. EngineRegistry

An `EngineRegistry` is a discovery and lifecycle interface for engines. It does not execute arbitrary code during registration or discovery.

### EngineDescriptor

| Field | Type | Meaning |
|---|---|---|
| `engine_id` | stable URI | Engine identity |
| `engine_version` | semantic version | Engine version |
| `engine_kind` | string/enum | Generator, validator, transformer, adapter, runtime, or other declared role |
| `implements` | contract references | Contracts implemented |
| `capabilities` | capability declarations | Declared functions and effect classes |
| `dependencies` | versioned references | Required engines, runtimes, and schemas |
| `entrypoint` | opaque reference | Host-resolved implementation reference; never eval'd from untrusted metadata |
| `trust` | verification record | Publisher, digest, signature status, and trust decision |
| `lifecycle` | state | `discovered`, `validated`, `available`, `suspended`, or `retired` |

### Registry operations

- `register(descriptor, provenance)`: validate and record metadata; never execute the engine.
- `resolve(engineId, versionConstraint)`: return a compatible descriptor or a typed resolution error.
- `list(capabilityFilter)`: discover engines without invoking them.
- `validate(engineId, policyContext)`: evaluate schema, provenance, dependency, and policy requirements.
- `invoke(engineId, request, authorization)`: request execution through a host-controlled adapter after validation and authorization.
- `suspend(engineId, reason)`: prevent new invocations while preserving history.
- `retire(engineId, successor)`: mark unavailable and preserve a successor relationship.

The registry must enforce unique engine identities per publisher namespace, immutable published versions, explicit revocation, and audit records for state changes. Registry metadata is not a sandbox; execution isolation belongs to the host runtime.

## 5. Shared data envelope

Cross-platform messages use a versioned envelope:

```json
{
  "envelope_version": "1.0.0",
  "message_id": "urn:uuid:<unique-id>",
  "source_platform": "urn:eria:platform:source",
  "target_platform": "urn:eria:platform:target",
  "contract_id": "urn:eria:contract:records",
  "contract_version": "1.0.0",
  "operation": "records.read",
  "created_at": "2026-11-13T00:00:00Z",
  "correlation_id": "urn:uuid:<correlation-id>",
  "idempotency_key": null,
  "payload_schema": "urn:eria:schema:record-query",
  "payload_version": "1.0.0",
  "payload": {},
  "provenance": {
    "source_revision": "<commit-or-release>",
    "content_digest": "<sha256>"
  },
  "authorization_ref": null
}
```

A null authorization reference means no consequential action is authorized. Read-only local processing may be separately permitted by host policy; external dispatch and writes require explicit scope. Timestamps must include timezone. Units belong in the payload schema or explicit value objects, never inferred from magnitude.

## 6. Relationship to ERIA engines

- **GENESIS** creates candidate manifests and platform scaffolds.
- **FORGE** constructs implementation artifacts from validated templates and contracts.
- **PONS** resolves provider-neutral interfaces and dependency bindings.
- **PANTHEON** validates contracts, capabilities, and policy boundaries.
- **STRIDE** coordinates lifecycle work and invokes approved engines through host adapters.
- **FACULTY** provides analysis and planning; recommendations are not permissions.
- **MEMORIA** preserves provenance, revisions, and append-only correction records.
- **VELUM** hides provider-specific implementations behind stable interfaces.

These are architectural role assignments, not claims that each engine is currently implemented.

## 7. Acceptance tests

1. Reject a manifest missing `platform_id`, `manifest_version`, or provenance.
2. Reject duplicate platform identity/version records with conflicting digests.
3. Reject a contract whose operation references an undeclared schema.
4. Reject incompatible major contract versions.
5. Reject an engine descriptor with an unverified or mismatched content digest.
6. Confirm registration and discovery do not execute engine code.
7. Reject invocation when the engine is suspended, dependencies are unresolved, or authorization is absent/out of scope.
8. Confirm external-effect operations require explicit authorization and idempotency handling.
9. Confirm unknown, null, absent, and invalid data values remain distinguishable.
10. Confirm every transformation and registry state change is auditable and recoverable.

## 8. Adoption sequence

1. Review this language-neutral specification and settle identifiers and schema versioning.
2. Implement immutable value models and validators in the existing host language.
3. Add a deterministic in-memory registry before persistent or remote registry adapters.
4. Add local-only contract negotiation and adapter tests.
5. Connect GENESIS and FORGE to manifest/contract generation.
6. Connect PONS and STRIDE only after validation and authorization gates pass.
7. Add persistence, signing, remote transport, and deployment adapters as separately reviewed increments.

## 9. Non-goals and safety boundary

This contract does not create credentials, grant repository permissions, deploy services, open network listeners, execute generated code, or authorize external dispatch. It does not claim a registry is a security sandbox. Those capabilities require explicit host implementation, tests, threat modeling, and separately scoped authorization.
