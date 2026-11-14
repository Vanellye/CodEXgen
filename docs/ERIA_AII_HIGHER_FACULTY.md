# Âï Conversational Intelligence over Higher Faculty Results

Âï now consumes the fresh Æị Higher Faculty output and the corresponding original source bytes.

## Interface

The ERIA HTML interface exposes **Ask Âï**. The local API accepts:

```http
POST /api/ai/higher-faculty
Content-Type: application/json

{
  "path": "tools/example.py",
  "question": "Explain the security implications.",
  "comparison_path": "tools/legacy_example.py"
}
```

`comparison_path` is optional. The conversation adapter also supports:

```text
ai.higher tools/example.py --question "Why does this function exist?"
ai.higher tools/example.py --question "Identify conflicting implementations."
ai.higher tools/example.py --question "Compare original source with English translation."
ai.higher tools/example.py --question "Compare these implementations." --compare tools/legacy_example.py
```

## Supported analyses

- **Purpose:** Python AST extracts function/class declarations, docstrings, calls, and return expressions. Without documentation, Âï labels purpose as inferred.
- **Dependencies:** extracts direct import/include/require declarations from the inspected source. It does not claim to resolve transitive or runtime-loaded dependencies.
- **Conflicts:** bounded repository scan finds same-name function/class declarations in other eligible source files. Same names are review candidates, not proof of semantic conflict.
- **Security:** line-anchored static pattern checks flag dynamic execution, shell/process use, network access, SQL mutations, credential-like assignments, and unsafe deserialization. These are indicators, not confirmed vulnerabilities.
- **Improvement:** returns prioritized, reviewable mitigation/refactoring proposals. It does not write code.
- **Comparison:** pairs the source SHA-256 and line-anchored Higher Faculty English interpretations; optional second source comparison includes hashes, shared symbol names, and bounded line-difference summaries.

## PONS and preservation

PONS remains instantiated and ON. Âï resolves through the existing PONS service registry. The analysis does not create capability grants, execute code, edit repository files, alter Git history, or modify SQLite source records. The server records an audit event containing source path/hash, requested analysis dimensions, whether a comparison was requested, and PONS state.

All derived interpretations remain `NON_AUTHORITATIVE`. Source integrity verification is not semantic verification.

## Current limits

This is deterministic AST/lexical analysis, not a generative LLM, full compiler, call-graph engine, dependency resolver, or complete security analyzer. Python function extraction uses AST; other languages use lexical declaration patterns. Results must be reviewed by a human. Compilation and runtime tests remain separate validation gates.
