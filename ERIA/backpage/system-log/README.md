# ERIA Backpage System Log

**Status:** reviewed-data recording contract. This directory is a documentation and audit layer; creating a record does not authorize or execute an intervention.

## Purpose

Store concise, traceable summaries of reviewed source data, its interpretation, and any associated intervention. Preserve original sources and their identities. Keep review, approval, execution, and verification as separate events.

## Required distinctions

Every record must classify an intervention using exactly one current state:

- `PROPOSED` — described for consideration; not authorized and not executed.
- `AUTHORIZED` — approval is recorded for a defined scope; execution is not implied.
- `EXECUTED` — evidence identifies the action, actor or system, time, target, and resulting artifact or outcome.
- `VERIFIED` — post-action checks support the stated result; cite the verification evidence.
- `BLOCKED` — a prerequisite, authorization, or safety gate is unmet.
- `NOT_APPLICABLE` — no intervention is proposed or required.

A review event alone may set review status to `REVIEWED`; it must never change intervention state to `EXECUTED` or `VERIFIED`.

## Record rules

1. Keep raw source data separate from interpretation and derived summaries.
2. Cite exact repository paths, refs, commit SHAs, external identifiers, and content digests where available.
3. State what was observed, what is inferred, what remains unknown, and confidence/limitations.
4. Record proposed interventions separately from completed actions.
5. An execution claim requires direct evidence; an authorization, plan, discussion, or passing review is not execution evidence.
6. A verification claim requires post-action evidence and the checks performed.
7. Corrections are appended as new linked records. Never silently overwrite a historical interpretation.
8. Minimize personal or sensitive data. Do not log credentials, tokens, private keys, or unnecessary identifiers.
9. A log entry documents events; it does not dispatch commands, change runtime state, or grant permissions.

## Record format

Use the fields in [RECORD-FORMAT.md](RECORD-FORMAT.md). Keep one dated review summary per review event under `records/`. Use stable record IDs and link corrections with `supersedes` or `corrects`.

## Current index

- [2026-11-13 reviewed architecture summary](records/2026-11-13-reviewed-architecture-summary.md)

**Implementation boundary:** this is an append-oriented documentation convention. It is not yet a runtime-enforced, tamper-evident event store. Git history provides repository version history but is not, by itself, proof of reviewer identity or intervention execution.
