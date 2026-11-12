# ERIA Suspension Thread and Installed-Player Adapter

**Status:** Initial domain contracts; not a deployed player modification or durable service.

## Purpose

Create a traceable suspension thread from a transmission, preserve the transmission's source identity, and cross-reference related records without collapsing verified evidence, inference, and unknowns.

## Suspension thread

- TransmissionOrigin retains transmission ID, source reference, receive time, and payload digest.
- SuspensionThread is an immutable state model with ACTIVE, SUSPENDED, and CLOSED states.
- Events are appended to the returned thread state; callers must persist them in an append-only journal before treating them as durable.
- Resume requires a human-confirmation assertion, a non-empty approval reference, and the exact scope suspension.resume:<threadId>.
- Cross-references retain their evidence state. A VERIFIED link requires an evidence reference; INFERRED and UNKNOWN remain explicitly distinct.
- Corrections add new events and references. They do not rewrite the originating transmission.

## Installed-player deep-mod boundary

InstalledPlayerAdapter is deliberately observation-only. It represents a compatibility point for a player that exposes a supported media session. PlayerControlProposalFactory can create a reviewable pause/resume proposal, but every proposal has executionEnabled=false.

No code in this change:
- modifies or replaces the installed player;
- injects code, hooks private processes, uses root, or automates accessibility controls;
- sends media commands, changes audio routing, or bypasses player permissions;
- reads private player storage or extracts credentials.

A real Android adapter would need a documented, user-enabled platform interface (for example, a player-published media session), least-privilege permissions, clear user disclosure, and a separate reviewed implementation. Unsupported players remain unsupported; no compatibility is assumed.

## Verification and production gaps

The unit tests cover origin preservation, hold/resume scope checks, cross-reference evidence states, and proposal-only player integration. They do not authenticate a human approver or prove the truth of a source reference.

Before production use, add:
1. a durable append-only event store with integrity protection and recovery tests;
2. authenticated approval verification, not a caller-supplied Boolean;
3. timestamp parsing and replay/ordering protections;
4. a concrete, documented Android media-session observer for supported players;
5. separate user-consented command execution only if later required and reviewed;
6. targeted Gradle unit tests and Android permission/session tests.

No automatic resume, external player mutation, background service, JNI bridge, or runtime activation is enabled by these contracts.
