# ERIA Higher Faculty Inspection Pipeline

The ERIA conversation server exposes a local, read-only source translation path:

- UI action: **Translate source**
- HTTP: `POST /api/translate` with `{"path":"repository/relative/file.py"}`
- Conversation command: `aei.translate <repository-relative-path>`

The pipeline runs in this fixed order:

1. **Discovery** — recognize a bounded set of source constructs and retain line numbers and original line text.
2. **Antithesis** — flag possible unfinished work, dynamic execution, process/shell use, network calls, and database mutations for human review. These flags are prompts for inspection, not verdicts.
3. **Verification** — compare the source's SHA-256 digest from Æị inspection with a fresh read. This verifies byte stability only; compilation, tests, and semantic correctness are not asserted.
4. **Creation** — produce line-anchored candidate English explanations, each marked `INTERPRETATION` and `NON_AUTHORITATIVE`.

## PONS state

PONS is instantiated by the ERIA application and its status endpoint reports `service_state=ON`. Its existing capability policy is unchanged: missing or unverified approval remains HOLD, and `execution_enabled=false`. Translation and inspection do not grant execution, repository-write, or transmission permissions.

## Preservation and audit

- Source files are read only; the translator does not write a translated copy.
- Git history is not changed by the pipeline.
- Existing SQLite source records are not updated by translation.
- The ERIA server appends a `higher_faculty_translation` audit event with source path, source digest, finding count, antithesis flag count, and stage names.
- The returned translation is a response payload; acceptance into the code-to-English index remains a separate human-reviewed step.

## Limits

This first adapter is deterministic lexical recognition, not a full parser, compiler, static analyzer, or generative language model. A clean Antithesis scan does not prove correctness. The C++ Faculty Engine and this Termux/Python ERIA adapter are separate implementations pending a shared native binding and parity tests.
