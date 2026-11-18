# Pantheon Language — Contract-First Specification (Draft 0.1)

## Status

This document defines the intended source language direction for Pantheon. It is a language specification draft, not a compiler or executable runtime. Existing Pantheon modules remain C99 contract implementations, and the Android boundary remains Kotlin until a compiler, parser, conformance suite, and reviewed adapters exist. Do not rename working source files or claim that C99/Kotlin has been transpiled into Pantheon.

## Design goals

- Declarative, readable authorization and data-contract definitions.
- Explicit provenance, exact scope, consent, safety, security, ownership, compatibility, and human approval requirements.
- Fail-closed evaluation: missing or conflicting evidence yields HOLD.
- Proposal-only by default; no implicit file, process, network, Git, wallet, hardware, publishing, or deployment side effects.
- Deterministic evaluation with inspectable evidence and audit records.
- Human authorization remains external to the language and must be authenticated by a trusted adapter.

## Draft syntax

A Pantheon source file uses the .ptn extension. The following is illustrative syntax for the Planting Seeds policy; it is not yet accepted by a parser.

    policy PlantingSeeds version "0.1" {
      seed {
        require intent
        require source.reference
        require source.sha256
        require provenance.reference
        require target
        require scope.requested == scope.authorized
        require consent.verified
        require security.verified
        require safety.verified
        require ownership.verified
        require compatibility.verified
        require approval.reference
        require approval.verified
      }
      on missing_or_conflicting_evidence { decision HOLD }
      on all_requirements_satisfied {
        decision PROPOSAL_ONLY
        forbid execute
        forbid mutate
        forbid publish
        forbid transmit
        require human_review
      }
    }

## Evaluation semantics

1. Parse and type-check without side effects.
2. Resolve every evidence reference through a trusted adapter.
3. Treat caller-provided Boolean values as claims until authenticated.
4. Compare requested and authorized scopes exactly; no wildcard expansion.
5. Return HOLD for absent, invalid, expired, unverifiable, or conflicting evidence.
6. Return PROPOSAL_ONLY only when all declared requirements pass.
7. Never treat PROPOSAL_ONLY as an execution grant.
8. Emit a deterministic decision record with source and target hashes.

## Implementation boundary

The current C99 I-INJECT module is the reference contract for proposal validation. The Kotlin Android runtime gate is a separate review boundary. Neither is a Pantheon compiler. A future compiler must pass parser, type, semantic, negative, fuzz, and cross-implementation conformance tests before any production adapter can consume .ptn files.

## Platform limits

Pantheon cannot remove Android's application sandbox, Termux permissions, filesystem access controls, battery/background execution policy, or hardware security boundaries. It can declare requested capabilities and reject unauthorized use; trusted operating-system APIs and explicit user grants remain necessary.