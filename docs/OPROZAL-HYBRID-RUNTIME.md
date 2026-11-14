# Oprozal Hybrid Runtime Integration

## Integration point

The local Termux server routes `POST /api/chat` through `Conversation.ask()`. The conversation engine now runs the Oprozal deficiency classifier after the existing read-only repository response and appends an advisory only when the incoming question signals a gap, lack, delay, lag, build failure, dependency concern, security issue, missing evidence, contradiction, or storage pressure.

The server's existing SQLite message history stores the assistant response, including the rendered Oprozal advisory. Each structured advice record carries the inspected Git HEAD revision and marks its evidence authority as `NON_AUTHORITATIVE`.

## Hybrid mindframe contract

`OprozalAdvisor.assess(question, source_revision, source_agent)` is independently callable by Æị, Âï, Ēx, or the runtime. The default implementation is deterministic and transparent. It is not an LLM and does not claim autonomous model cognition. A future provider can replace the advisor behind this contract while preserving the output schema and guardrails.

## Faculty expansion

Supported faculty proposals include:
- Performance profiling
- Build diagnostics
- Test generation
- Dependency compatibility
- Security review
- Evidence-gap analysis
- Provenance audit
- Independent critique
- Synthesis planning
- Conversation explanation

The advisor recommends faculty and validation steps; it does not synthesize, compile, load, or execute generated code. Runtime optimization is gated on profiling evidence.

## PONS boundary and preservation

Every advice record marks PONS as `HOLD` for `eria.faculty.propose`, requires human approval, and explicitly records that code execution, repository mutation, and Git mutation did not occur. The existing PONS service remains the authority for authorization requests; Oprozal does not mint or approve grants.

No main-branch writes, history rewrites, source-record deletion, shell execution, or network dispatch are introduced by this integration.

## Tests

`tests/test_eria_oprozal.py` covers supported deficiency classes, profile-first latency guidance, missing-capability faculty proposals, unknown/low-confidence handling, source revision attribution, and the actual `Conversation.ask()` integration.
