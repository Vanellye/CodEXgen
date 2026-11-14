# Âï conversation layer

Âï is integrated above Æị as a deterministic, evidence-grounded retrieval layer registered with PONS and invoked through ERIA/PANTHEON.
It is not an LLM and does not invent answers. The browser endpoint delegates to the Pantheon command adapter, which resolves Âï through PONS. Each question triggers a fresh,
read-only Æị inspection of the selected repository-relative file.

## Local API

Start the loopback service from the repository root:

    PYTHONPATH=tools python tools/eria_aei_server.py --root . --port 8765

The browser interface is at http://127.0.0.1:8765/.

### Ask Âï

    curl -sS -X POST http://127.0.0.1:8765/api/ai/ask \
      -H 'Content-Type: application/json' \
      -d '{"path":"README.md","question":"Summarize this file"}'

The browser route is translated to the Pantheon command form:

    ai.ask README.md --question "Summarize this file"

The response contains:
- answer and evidence status;
- source-relative path, format, size, and SHA-256;
- JSON-pointer-like evidence locations and bounded values;
- explicit limitations and non-authoritative source/derived classification.

Questions asking for a summary receive a structural summary. Other questions
retrieve matching terms from Æị's parsed preview. When evidence is absent, Âï
returns insufficient_evidence rather than guessing.

Credential-like paths are refused. Path traversal and symlink protections,
file size limits, and SQLite read-only mode are inherited from Æị. The service
binds to 127.0.0.1 and applies Host and Origin checks. No repository, database,
or Git-history writes are performed.

## Current capability boundary

This version is evidence-grounded retrieval, not free-form generative reasoning,
semantic embeddings, or a trained model. It answers only from the selected file
and the bounded data Æị returns. A future model-backed adapter would need a
separately configured provider, explicit data-sharing consent, and the same
source citations and authority boundaries.
