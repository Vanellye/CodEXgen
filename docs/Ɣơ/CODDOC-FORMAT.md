# ERIA .coddoc format v1

A `.coddoc` file is UTF-8 JSON with the `.coddoc` extension. It is an append-oriented narrative/evidence document, not executable code.

Required top-level fields:
- `format`: `ERIA_CODDOC`
- `version`: integer `1`
- `document_id`, `title`, `narrative`, `source_scope`
- `runflow_state`: a state from the canonical ERIA Runflow protocol
- `events`: non-empty array of ordered source-linked observations

Each event requires a stable `event_id`, positive unique `sequence`, `evidence_class`, `source_refs`, `observation`, and `interpretation`. `occurred_at` is either an ISO-8601 timestamp including a timezone, or `null`.

Evidence classes:
- `SOURCE_TEXT`: text observed in a source artifact
- `CODE_REFERENCE`: a specific code path/ref
- `WORKFLOW_RESULT`: an observed workflow result
- `ARTIFACT_REFERENCE`: a generated artifact and digest
- `HISTORICAL_REFERENCE`: a historical branch/PR or snapshot pointer
- `USER_DEFINED_LABEL`: a term supplied by a user but not yet mapped to a source
- `UNKNOWN`: not established

Rules:
1. Sequence is authored narrative order; it is not fabricated wall-clock time.
2. Null time stays unknown. No interpolation is allowed.
3. Observation and interpretation remain separate.
4. Each consequential claim retains one or more source references.
5. A digest proves byte identity only, not truth or authority.
6. Corrections create new linked events; old records are preserved.
7. No .coddoc field grants approval, execution, ownership, or publication rights.
