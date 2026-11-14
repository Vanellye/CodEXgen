# PONS Growth Contract

## Immutable foundation

- Canonical anchor ID: 7f7a43a973a96a06dd432bf94843213d09133323
- Canonical anchor branch: zero-dissipation-anchor
- Pinned anchor commit: df5ead3b55cfabd0ba40e902b4080946cba794dc

This identity is a fixed compatibility boundary. New work is additive and versioned. Do not rewrite the anchor branch, replace its identifier, or silently reinterpret historical evidence.

## Component lifecycle

Every new component follows this lifecycle:

1. PROPOSED — source path, version/ref, owner, purpose, and interface declared.
2. PINNED — exact source bytes are hashed and added to a reviewed manifest.
3. VERIFIED — a trusted manifest-signature verifier accepts the manifest and PONS recomputes a matching source digest.
4. READY — operational health is independently observed and provenance is VERIFIED.
5. DEGRADED — provenance remains valid but operational checks report reduced capability.
6. HOLD — mismatch, policy violation, invalid anchor, or explicit human hold.
7. UNKNOWN — missing source, missing pin, missing verifier, or missing evidence.

No component may self-promote to VERIFIED or READY. Missing evidence remains UNKNOWN. A mismatch remains HOLD.

## Manifest and trust roots

The file pons/trust-manifest.template.json is intentionally empty. It is not a trust manifest and cannot authorize a component. A production manifest must:
- bind the canonical anchor ID and commit;
- identify every component by stable ID, exact source ref, exact source path, and SHA-256;
- have a version and signer key ID;
- be signed by an independently managed key;
- be verified by a host-provided, vetted signature-verification implementation;
- be reviewed and pinned outside the component being authorized.

The Python loader accepts a host-supplied signature-verification callback. The Android loader accepts a host-supplied verifier interface. The C99 adapter accepts a host-supplied SHA-256 implementation and a reviewed manifest pin. CI uses a deterministic fake digest only to test control flow; it is explicitly NOT cryptography. No production signing key or cryptographic provider is embedded in this repository.

## Extension interfaces

A new language/runtime must add an adapter rather than changing the canonical contract. The adapter must expose:
- stable component ID and semantic version;
- exact source reference and path;
- provenance verification;
- operational status;
- capability declarations;
- explicit HOLD/UNKNOWN reasons;
- append-only evidence events;
- tests for mismatch, missing evidence, alternate anchor, and unauthorized execution.

Adapters must not receive implicit filesystem, network, process, Git-write, deployment, or device authority from PONS. PONS status is not an authorization grant for unrelated capabilities.

## Evidence and corrections

Preserve original bytes, source refs, timestamps, digest values, reviewer references, and prior observations. Corrections are new events referencing the superseded event; do not erase history. Transmission frames and receipts carry the canonical PONS anchor identity (anchor ID, branch, and pinned commit). Each transmission evidence event records request/response digests and an optional superseded evidence ID; the in-memory ledger retains earlier events. This is an append-only process-local history, not durable storage. The Python JSONL ledger is hash-chained and append-only through its API, but it is not tamper-proof storage or a trusted timestamp. Production deployments must add protected storage, authenticated appenders, signed checkpoints, backup/restore tests, and key rotation.

## Progressive-growth slots

Reserve component namespaces, not hard-coded assumptions:
- eria.* — ERIA runtime and services
- pantheon.* — Pantheon modules and governance
- stride.* — Stride engines and sensors
- corde.* — Corðə interpreter and language tooling
- audio.* — audio capture, processing, playback, and transmission
- android.* — Android app and platform adapters
- termux.* — Termux adapters and host services
- generated.* — generated artifacts

A new namespace may be introduced by a reviewed manifest version. Old component IDs and evidence remain addressable.

## Current boundary: what is and is not complete

Implemented:
- Python PONS registry, hash-chained ledger, replay verification, and guarded execution helper.
- Signed-manifest loading interface in Python, with host-provided verifier.
- Android PONS digest gate, immutable pin snapshot, signed-manifest factory interface, and effective-state registry.
- Pantheon Android review path requires canonical PONS proof.
- WAV endpoint, playback, and in-memory transceiver require component-specific PONS READY proof. Transmission frames/receipts are bound to the canonical anchor, and the in-memory evidence ledger appends superseding observations without deleting prior entries.
- C99 PONS digest-verification adapter; Pantheon NEW C narrative entry point now requires a PONS proof.
- Python, Kotlin, and C contract tests.

Not yet production-complete:
- No actual signing key, trusted signer policy, or production signature verifier is configured.
- No reviewed manifest with real source digests has been provisioned; the template is intentionally empty.
- Android application startup has not yet loaded a production manifest or wired every ViewModel/service.
- Every Pantheon C module other than NEW is not yet individually gated.
- Python service entry points and generated modules have not yet been registered with real pins.
- Git Freedom bridge and actual Git mutation authorization remain separate and must be integrated without granting PONS blanket write authority.
- Stride, Corðə, Termux, and physical hardware runtimes require their exact source refs and test evidence before registration.
- Repository branch protection for the canonical anchor must be enabled by a repository administrator; API access in this integration did not enable it.

This is an extensible integration foundation, not a declaration that absent runtime evidence or administrative controls have been solved.
