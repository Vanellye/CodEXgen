# ORCHID Chronoglyph — Living Language and Transient Compatibility

Status: proposal committed on an isolated feature branch; implementation and runtime validation pending.

## Intent

ORCHID is a versioned, multilingual symbolic language system. It defines glyph identities, geometry, semantics, localized lexical forms, composition rules, keyboard integration contracts, and portable lineage.

The Chronoglyph generation introduces a time-flexible language model: linear, cyclic, branching, layered, elastic-scale, reversible, and unresolved temporal descriptions. These are representational models, not claims that physical time can be reversed or that possible futures are predetermined.

## Governance change: PONS decoupling

This ORCHID subsystem has no PONS runtime, package, API, approval token, or authorization dependency. PONS is not required to parse, render, search, translate, or locally compose language expressions.

PONS removal is scoped to the ORCHID subsystem introduced by this branch. It does not authorize deleting or disabling PONS elsewhere in CodEXgen or unrelated systems.

Human review remains required before publishing a shared canonical vocabulary release, changing canonical meanings, or distributing a keyboard update. Local drafts and personal dictionaries may be created without central approval. Release decisions are explicit, attributable, reversible by issuing a successor release, and recorded in an append-only release ledger. No secret or hidden write path is permitted.

## Transient compatibility scope

ORCHID must operate in both persistent and transient environments:

- Long-lived installations with a complete local registry.
- Short-lived application sessions and browser tabs.
- Ephemeral containers, temporary virtual machines, and disposable workspaces.
- Volatile-memory-only execution where no durable write is available.
- Offline and intermittently connected devices.
- Low-storage and constrained-resource devices.
- Keyboard processes that may be killed and restarted at any time.
- Temporary guest profiles and isolated application sandboxes.

Transient operation must not imply permanent retention. A session may use an in-memory registry snapshot, a bounded cache, or a user-exported package. If storage disappears, the runtime must report which drafts or local changes were not persisted. It must never claim that an in-memory change has been archived.

## Runtime profiles

1. EPHEMERAL: memory-only; no disk writes; all changes are session-scoped and clearly marked volatile.
2. CACHE: bounded local cache; source release ID and digest retained with each cached snapshot; cache may be evicted safely.
3. OFFLINE: read-only canonical snapshot plus optional local draft overlay; synchronization occurs only when explicitly enabled.
4. PERSISTENT: durable registry, export/import, integrity checks, and version migration.
5. DISTRIBUTED: signed release packages and multi-device synchronization; conflicts are surfaced, never silently merged.

## Canonical expression model

Each symbol record separates identity from rendering and localization:

- immutable symbol ID
- canonical name and semantic definition
- primary and extended meanings
- temporal category and composition constraints
- geometry revision and deterministic vector source
- localized labels, keywords, pronunciation metadata, and translation review state
- parent, successor, and source lineage
- release version and content digest
- compatibility and accessibility metadata

Unicode is a transport/rendering choice, not the canonical identity. Where no suitable Unicode character exists, use bundled font assets or an explicitly scoped private-use mapping. Never claim private-use characters are universally interoperable.

## Multilingual and keyboard compatibility

Adapters should expose a stable, language-neutral API:

- search(query, locale, mode)
- resolve(symbol_id)
- suggest(context, locale, user_preferences)
- compose(symbol_ids, locale)
- render(symbol_id, profile)
- export(snapshot, format)
- import(package, policy)

Initial localization targets: English, Spanish, French, German, Portuguese, Arabic, Hindi, Japanese, Simplified Chinese, Traditional Chinese, and Korean. This is a target matrix, not a claim of completed translations. RTL, shaping, combining marks, input method composition, accessibility labels, and font fallback require locale-specific tests.

Android IME, desktop input, web editor, and application SDK are separate adapters over the same registry contract. No adapter may silently rewrite user text or change system keyboard settings without an explicit user action.

## Temporal expression families

The initial Chronoglyph-01 vocabulary is retained as a versioned baseline:
VORA (⧖), ELUN (⫶), THÉRA (⤙), AVÉR (⤚), NŌVEX (⧓), SÉLVA (⫰), RŪVEN (⧔), KÉRIN (⫷), MŌRIN (⧉), DÉXEN (⤺), ŌRIEL (⧗), ZÉPHIR (⫯).

The next expansion must give every new symbol a new canonical ID. Glyph reuse with a different meaning requires a distinct identity and collision review. Existing definitions are never overwritten.

## Safety, privacy, and resource limits

- Local search and composition should work without uploading user text.
- Contextual suggestions are opt-in and may be disabled.
- No covert keystroke collection, telemetry of typed content, or inference of sensitive traits.
- Resource usage is bounded: cache size, suggestion count, parser depth, expression length, and synchronization payload.
- Untrusted language packages are data, never executable code.
- Digests detect content changes relative to a trusted digest; they do not prove authorship or truth.
- Missing storage, locale coverage, glyph support, or network connectivity must be reported honestly.

## Acceptance criteria

- Same canonical record ID survives scale, device, renderer, and session changes.
- Deterministic serialization produces stable digests for identical canonical records.
- Ephemeral mode performs no durable writes.
- Cache eviction does not corrupt canonical identity or lineage.
- Offline mode clearly distinguishes canonical data from local drafts.
- Import/export round trips preserve IDs, semantic fields, and lineage.
- Locale tests cover RTL, shaping, combining marks, fallback, and accessibility labels.
- Keyboard adapters never modify text without user confirmation.
- Release validation rejects duplicate IDs, broken parent references, invalid successor chains, and semantic overwrite.
- No ORCHID module imports or calls PONS.

## Non-goals

This specification does not claim literal persistence beyond physical time or space, universal rendering on every device, complete translation coverage, a production compiler, a deployed keyboard, or verified runtime compatibility. Those require implementation and test evidence.
