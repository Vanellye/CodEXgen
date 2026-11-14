# Oprozal — Hybrid Advisory and Code-Faculty Expansion

## Status

Initial deterministic advisory implementation. It is not a separately hosted LLM and does not autonomously modify or execute repository code.

## Architecture

Oprozal is a fourth, independently callable advisory mindframe with a shared intake path for Æị, Âï, Ēx, and ERIA runtime signals. The `OprozalMindframe` interface permits a separately configured model-backed implementation later. The default `RuleBasedOprozalMindframe` is deterministic and transparent.

## Deficiency reactions

Signals are classified as missing evidence, missing capability, runtime latency, build failure, dependency risk, test coverage gap, security concern, storage pressure, contradiction, or unknown. Each signal produces a diagnosis, recommendation, candidate faculties, verification steps, source references, confidence label, and human-review requirement.

## Code-faculty expansion

The coordinator can draft faculty proposals for evidence analysis, conversation explanation, independent critique, test generation, build diagnostics, dependency compatibility, performance profiling, security review, provenance audit, and synthesis planning.

A proposal is metadata and a review artifact only. It is not compiled, loaded, executed, or installed by this module. Runtime profiling is recommended before latency optimization; generated source code must be handled by a separate isolated runner and quality analyzer.

## PONS and preservation

- All faculty proposals default to `REVIEW_REQUIRED`.
- `actionTaken` is always false in this module.
- No shell, process, filesystem writer, network client, Git client, dynamic evaluation, or classloader is exposed.
- PONS scope is recorded as `eria.faculty.propose`; the actual trusted grant verifier and execution boundary must remain in the existing PONS integration.
- Existing source evidence and Git history are referenced, not rewritten.
- Integrate this module into the conversation entry point only after the host's actual `Conversation.ask()` and storage contracts are inspected.

## Verification

Run:

```bash
./gradlew :app:testDebugUnitTest
```

The tests cover signal intake, runtime-latency advice, review-only proposals, signal/advice binding, and low-confidence handling for unknown events.
