# ERIA Source-Generation Lineage Commitment

**Status:** Proposed source-generation contract; documentation only.  
**Applies to:** Generated source code, generated configuration, generated signal-processing artifacts, and other derived source records.

## Purpose

Every generated artifact must carry a verifiable lineage commitment linking it to its inputs, generation operation, generator identity, and resulting bytes. The commitment makes derivation inspectable; it does not claim authorship, trustworthiness, correctness, or permission to execute.

The original source remains immutable and distinct from every generated derivative.

## Required lineage record

A generation record should include:

- `lineage_schema_version`
- `generation_id` — unique identifier for this generation event
- `artifact_id` — unique identifier for the generated artifact
- `parent_artifact_ids` — exact IDs of all direct inputs; empty only for explicitly declared first-party/original generation
- `input_digests` — algorithm and digest for each exact input byte sequence
- `output_digest` — algorithm and digest for the exact generated output bytes
- `generator_id` and `generator_version` — stable module identity and version/build identity
- `template_or_model_id` and version, when applicable
- `parameters_digest` — digest of canonicalized generation parameters; avoid storing secrets
- `created_at` — UTC timestamp, with clock source/quality where relevant
- `source_repository`, `source_commit`, and `source_path`, when applicable
- `authorization_ref` and exact approved scopes for consequential generation steps
- `validation_results` — checks performed and their outcomes
- `signature_status` — explicit state such as `not_present`, `verified`, or `invalid`; never infer a signature
- `previous_lineage_record_digest` — link to the preceding record in an append-only lineage chain, when one exists

## Commitment construction

1. Preserve and identify every input before generation.
2. Hash the exact input bytes using a named, approved digest algorithm.
3. Canonicalize generation metadata and parameters before hashing them. The canonicalization format and version must be recorded.
4. Generate the output as a new artifact; do not overwrite an input or reuse its identity.
5. Hash the exact output bytes and bind that digest to the generation record.
6. Link the record to its parent lineage records by their stable IDs and digests.
7. Append the new record to the lineage history. Corrections create successor records rather than rewriting prior lineage.
8. Verify all referenced parent records and digests before accepting the commitment.

A digest proves byte identity relative to the bytes hashed. It does not prove who supplied the input, who operated the generator, whether the generator was uncompromised, or whether the output is safe.

## Line-level traceability

For transformations that need fine-grained review, an optional line map may associate output line ranges with parent artifact IDs and input line ranges. Line maps must identify the diff or mapping algorithm and version. They are advisory provenance metadata: formatting, generated code, macros, templates, and non-one-to-one transformations can make line correspondence incomplete or ambiguous.

Never claim exact line ancestry when the mapping is unavailable or uncertain. Mark unmapped lines as generated or unresolved.

## Authorization boundary

- `source.propose` permits proposing a generation plan only.
- `source.generate` permits a specified generator to create a named derivative from identified inputs in an identified environment.
- `source.store` permits persistence to the approved store.
- `repository.modify`, `execute`, `publish`, and `transmit` remain separate permissions.

A generation commitment is evidence of lineage, not an authorization token. Creating a proposal or computing a digest does not authorize generation, storage, execution, repository mutation, publication, or transmission. Missing, expired, mismatched, or ambiguous authorization fails closed.

## Verification and failure behavior

Reject or quarantine a generated artifact when:

- an input or parent lineage record is missing;
- a referenced digest does not match the exact bytes;
- the generator identity/version or parameter commitment is absent where required;
- the output digest does not match the artifact;
- the lineage chain contains a cycle or invalid parent reference;
- authorization does not cover the exact generation operation and target;
- a signature is claimed but cannot be verified.

On failure, preserve the original inputs and any already-created output as a clearly marked untrusted proposal; do not silently promote, execute, or transmit it.

## Relationship to existing ERIA components

- **Source collection** records caller-supplied source and its digest. Collection is not generation.
- **Source storage** persists a previously collected record under its separate authorization scope.
- **Internal sound signal pathway** should use the same parent/derivative principle: each processing output references the input signal ID and digest, generator/module identity, and output digest.
- **ĎÏÎ§Ŝ** governs permission to perform the operation; lineage commitment records what the operation derived.

## Implementation status

This document defines a contract only. It does not add a generation engine, signature service, append-only database, cryptographic identity provider, or runtime enforcement. Integrate the record type and verifier only after schema compatibility, canonicalization, storage integrity, and negative authorization tests are reviewed.
