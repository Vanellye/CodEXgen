# Ŷæṛö Atomic Intermediate Representation

## Purpose

Provide a stable, typed representation for analysis and gradual migration of legacy C-family and JavaScript code. Every result is derived from a preserved source snapshot.

## Core records

- `SourceUnit`: repository-relative path, language, byte length, SHA-256, encoding, and immutable source revision.
- `SyntaxNode`: parser kind, source span, child node IDs, and parser version.
- `Atom`: immutable typed value or operation with a stable ID and source-span provenance.
- `Transform`: input artifact hashes, transformation ID/version, output hash, diagnostics, and test evidence.
- `EquivalenceClaim`: source/target hashes, test corpus, compiler/runtime versions, observed results, and explicit limitations.

## Atomicity contract

A transformation is committed only when all validation steps pass. A failed transformation leaves its inputs unchanged and publishes no partial output. Writes target a new artifact directory or branch. Human review is required before any generated patch is applied to maintained source.

## Initial symbolic vocabulary

| Symbol | Meaning | Runtime constraint |
|---|---|---|
| `☆` | zero / explicit absence | distinct from missing data |
| `k` | one / presence | typed boolean-like literal |
| `△` | triadic relation | exactly three ordered operands |
| `∞` | continuation / unbounded domain marker | represented lazily with explicit resource limits |
| `§` | scope / namespace boundary | lexical scope, not ambient authority |
| `&` | composition | type-checked composition |
| `→` | transformation | pure by default; effects declared |
| `∴` | derived result | carries provenance and evidence reference |

## Example

```yaero
§analysis {
  △(source, syntax, evidence);
  source → ∴ immutable_ir;
}
```

This example describes data relationships; it does not execute arbitrary source code.

## Interchange

Canonical interchange is UTF-8 JSON with a versioned schema. Byte-level profiles remain separate encodings. A parser must never infer a source language from a filename alone; it records the detection method and confidence.

## Required invariants

- Every derived node traces to a source revision and byte span, or is explicitly marked synthetic.
- No transform mutates the source snapshot.
- Resource bounds are mandatory for parsing, recursion, and lazy streams.
- Unknown syntax is preserved as an opaque node with diagnostics, not silently discarded.
- An IR version change requires fixtures and migration notes.
