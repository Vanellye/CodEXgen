# Oprozal Faculty Forge

## Current stage

This stage connects Oprozal's deficiency advice to a reviewable faculty proposal, a non-executing source preflight, and an evidence-aware quality report.

## Pipeline

1. `OprozalAdvisor` classifies a deficiency and proposes a faculty.
2. `eria_oprozal_forge.py` binds the proposal to the current Git revision.
3. `eria_oprozal_preflight.py` validates a repository-relative Python source path, size, digest, and Python AST syntax. It does not import, compile to bytecode, or execute the candidate.
4. `eria_quality_analyzer.py` evaluates only the supplied evidence and emits explicit gates for provenance, syntax, execution boundary, source-write boundary, and PONS authorization.
5. The packet remains a review artifact. No source or Git mutation occurs.

## Why execution remains disabled

The repository's existing red-write-only policy explicitly denies execution. The existing PONS capability contract is proposal-only and requires an injected trusted signature verifier for write authorization. This feature does not invent a verifier, treat a boolean as a signature, or bypass that policy.

A true execution stage requires a separately reviewed Linux sandbox (for example, an unprivileged namespace-based runner with network isolation, read-only source mounts, bounded resources, and disposable output), plus an independently verified, expiring, revocable PONS grant for the exact candidate digest and test scope. Until both exist, only static preflight is available.

## CLI

```bash
PYTHONPATH=tools python tools/eria_oprozal_forge.py \
  --repo . \
  --question "Runtime latency needs profiling" \
  --source tools/eria_oprozal.py
```

Output is JSON on stdout. It is not persisted automatically. Source authority remains NON_AUTHORITATIVE; PONS remains HOLD; execution, source writes, and Git writes remain disabled.
