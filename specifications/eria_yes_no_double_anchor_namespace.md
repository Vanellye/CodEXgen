# ERIA YES/NO Double-Anchor Namespace
## Proposed specification — review required; not adopted

**Status:** PROPOSED  
**Scope:** Language-neutral namespace, relationship mapping, and point-ping protocol  
**Base:** `olpirt/stride-next` snapshot at `e2c5cb32765981c6db36fe37c16e0c26ebc18d97`  
**Change policy:** Additive proposal only. No existing namespace, identifier, call site, branch, or history is rewritten by this specification.

## 1. Purpose

Define a language-neutral way to map names, entities, interfaces, and relationships across programming languages using two independent decision anchors:

- **YES** confirms one explicitly stated proposed relationship.
- **NO** rejects that proposed relationship.

The anchors decide the status of a proposed edge. They do not create, rename, own, erase, or merge the entities at either endpoint.

The protocol is a mapping and consent convention, not a claim that software can infer human intent or hidden meaning.

## 2. Four distinct operators

| Token | Kind | Meaning | Must not be confused with |
|---|---|---|---|
| `YES` | Decision anchor | Accept this exact proposed connection, subject to validation | Global permission or blanket approval |
| `NO` | Decision anchor | Reject this exact proposed connection | Deletion of either endpoint |
| `CANT` | Constraint operator | The connection is prohibited, impossible, unauthorized, or violates a declared invariant | A user decision of NO |
| `NOT` | Logical operator | Negates a predicate while preserving the subject and its identity | The NO decision anchor |

`CANT` and `NOT` are correction operators in the namespace, not additional decision anchors. They must remain semantically distinct from YES and NO.

## 3. Double-anchor model

Every relationship proposal has two stable endpoints and one question:

```text
Point A  -- proposed relation + question -->  Point B
   |                                         |
   +--------------- YES / NO ---------------+
```

A point is an independently addressable entity, symbol, module, interface, capability, or concept. A point does not possess the other point.

A proposal is an edge record, not a mutation of either endpoint. The edge may be accepted, rejected, blocked by a constraint, or left unresolved.

### Required edge record

```json
{
  "protocol": "eria.double-anchor.v1",
  "proposal_id": "stable-unique-id",
  "source": {"namespace": "example", "name": "PointA"},
  "target": {"namespace": "example", "name": "PointB"},
  "relation": "implements | calls | maps-to | references | depends-on",
  "question": "Does PointA implement the declared PointB interface?",
  "decision": "UNRESOLVED",
  "constraint": null,
  "evidence": [],
  "provenance": [],
  "reviewer": null,
  "timestamp": null
}
```

The JSON is an illustrative interchange shape. Implementations may use native types, provided the semantics and required fields are preserved.

## 4. Point-ping protocol

1. **Identify:** Resolve both endpoints by fully qualified name and version.
2. **Ping A:** Ask whether the source endpoint recognizes the exact proposed relation and target.
3. **Ping B:** Ask whether the target endpoint recognizes the exact proposed relation and source.
4. **Ask the Y/N question:** Present one bounded, answerable question, including the relation and evidence.
5. **Record the decision:** Accept only an explicit YES to the exact proposal. An explicit NO rejects that proposal. Missing, conflicting, timed-out, or malformed responses remain UNRESOLVED.
6. **Check constraints:** A CANT constraint blocks adoption even if a YES response was recorded. Record the blocking constraint and its source.
7. **Validate:** Run language-specific type, interface, build, and behavioral tests.
8. **Adopt separately:** A validated proposal is still not automatically authorized for merge, deployment, or namespace-wide propagation.

### Decision states

- `UNRESOLVED`: no complete decision; includes silence, timeout, ambiguity, or conflicting endpoint responses.
- `YES`: the exact proposal was explicitly accepted by the required decision authority and both endpoint checks passed.
- `NO`: the exact proposal was explicitly rejected; endpoints and unrelated edges remain intact.
- `BLOCKED`: a CANT constraint or invariant prevents the proposed connection.
- `VALIDATED`: accepted proposal passed the declared tests; this is not merge or deployment authorization.
- `ADOPTED`: a separate authorized change incorporated the mapping, with commit and rollback provenance.

A point-ping timeout is never interpreted as NO or YES. A stale response cannot authorize a newer proposal.

## 5. Namespace mapping across languages

Use a canonical language-neutral edge record as the source of truth. Language adapters translate its meaning; they do not translate token spellings mechanically or silently alter control flow.

| Language | YES / NO representation | Adapter requirement |
|---|---|---|
| Bash | Explicit strings or exit statuses at process boundaries | Distinguish YES, NO, BLOCKED, and UNRESOLVED; never treat an empty variable as approval |
| C++ | Scoped enum, e.g. `Decision::Yes`, `Decision::No` | Exhaustive switch; unknown values fail closed |
| Kotlin | Sealed type or enum | Exhaustive `when`; nullable/missing response remains unresolved |
| Java | Enum or sealed interface | Exhaustive handling; avoid boolean-only APIs where states would collapse |
| Python (migration period only) | Enum/dataclass adapter | Preserve the same state machine; do not let Python-specific truthiness define approval |
| JSON / YAML | Explicit string-valued decision field | Validate schema and protocol version |
| Other languages | Native tagged union, enum, or equivalent | Preserve the canonical semantics and test vectors |

A boolean may be used only at a boundary where the caller has already resolved all other states. It must not collapse BLOCKED or UNRESOLVED into NO.

## 6. Mapping and correction rules

- Names are identifiers, not possessions. A namespace relationship never implies ownership.
- Preserve original spelling, case, source location, language, version, and provenance.
- Map aliases explicitly; never silently overwrite a canonical name.
- Keep identity nodes separate from relationship edges.
- `NOT(P)` means predicate P is false; it does not delete the subject.
- `NO` rejects one named proposal; it does not negate every relation involving either endpoint.
- `CANT` records a constraint with an explanation and source; it does not pretend a human or endpoint answered NO.
- Unknown names, unresolved aliases, and ambiguous overloads must be reported, not guessed.
- Cross-language mappings must include type, calling convention, error behavior, nullability, ownership/lifetime rules, and serialization details where relevant.
- Generated mappings must be reproducible and traceable to their source records.

## 7. Conformance tests

Every adapter must pass these shared cases before it can claim conformance:

1. Explicit YES accepts only the exact proposal asked.
2. Explicit NO rejects only that proposal and leaves both points present.
3. No response yields UNRESOLVED.
4. Conflicting endpoint pings yield UNRESOLVED.
5. CANT constraint yields BLOCKED even after YES.
6. NOT negates a predicate without deleting or renaming its subject.
7. A stale response cannot decide a proposal with a different ID or version.
8. Unknown decision tokens fail closed.
9. Round-trip serialization preserves proposal ID, endpoints, relation, decision, evidence, and provenance.
10. Language adapters produce equivalent outcomes for the same shared test vectors.

Tests must include positive, negative, boundary, malformed-input, timeout, and compatibility cases. Passing tests demonstrates conformance only; it does not grant adoption authority.

## 8. Provenance, review, and rollback

For each proposed or adopted mapping, record:

- source branch and commit;
- source and target identifiers with versions;
- proposal ID and exact question;
- both endpoint ping results;
- decision, constraint, and supporting evidence;
- adapter and test versions;
- reviewer and authorization reference;
- resulting commit, if adopted;
- rollback commit or exact inverse operation.

Do not rewrite Git history to apply this specification. Do not mass-rename symbols or rewrite call sites as part of this proposal. Implementation must proceed on a review branch, with branch-specific tests and a reversible change record. Promotion to main requires separate review and explicit authorization.

## 9. Open review questions

- Which repository namespace roots should be registered first?
- Which endpoint types require two-sided pings, and which can use a designated authority?
- What identity format should be used for proposal IDs across disconnected branches?
- Which shared test-vector format should be canonical?
- What is the minimum reviewer authority for moving VALIDATED to ADOPTED?

Until these questions are resolved, this document remains a proposed specification.


## 10. Essence vocabulary: continuity beyond boundaries

This vocabulary is a proposed semantic layer for ERIA names. It may enrich labels, descriptions, and conceptual mappings, but it does not authorize blind replacement of technical identifiers, API names, filesystem paths, or established language keywords. Such replacements require an explicit mapping proposal, YES/NO review, compatibility tests, and a reversible migration.

| Existing term | Proposed ERIA essence | Meaning in this specification |
|---|---|---|
| External | **Beyond-boundary continuity** | A relationship or resource that remains distinct from the current system while still being reachable through an explicit, governed connection |
| Internal | **Present-flow expression** | A locally held expression of a system's current state; not inherently more authoritative than an external source |
| Namespace | **Field of named relations** | A structured space in which identities and relationships can be located without implying possession |
| Boundary | **Threshold of distinction** | A condition that defines where one context ends and another begins while allowing explicitly permitted exchange |
| Link | **Continuity path** | A traceable relation between distinct endpoints |
| Anchor | **Point of return** | A stable reference used to verify identity, meaning, or provenance |
| Source | **Origin trace** | The earliest supported record or declared origin for a particular claim or artifact |
| Archive | **Continuity record** | Preserved evidence and versions that allow later examination and restoration |
| Migration | **Flow transition** | A controlled translation from one representation or runtime to another, with equivalence checks |
| Adoption | **Authorized embodiment** | The separately approved act of making a validated proposal part of an active system |

### 10.1 External is not erased; its essence is reframed

In ERIA's conceptual vocabulary, **External** may be described as **Beyond-boundary continuity**: not alien, lesser, detached from meaning, or ownerless by default, but distinct and connected through an explicit path.

The original technical term remains recorded as an alias and search key. Existing code and documentation must not be mass-renamed solely because a new essence label is proposed. A migration must preserve old-name lookup, references, provenance, and rollback.

### 10.2 Eternal-flow invariant

The proposed protected invariant is:

> **Continuity may cross a boundary without collapsing distinction. A name may evolve in meaning without falsifying its origin. A connection may be refused without erasing either endpoint. Harmful logic may be excluded from active operation while its historical evidence and the identities it affected remain protected.**

"Eternal flow" is a guiding metaphor for continuity, not a claim that any software artifact, storage medium, or human record is literally eternal. Protection must be implemented through independent copies, versioning, integrity checks, access controls, and tested recovery.

### 10.3 Protected anchor outside the repository

The ERIA foundational anchor is proposed to live independently of CodEXgen branches and repository administration. The repository may reference a versioned digest and public description, but must not be the sole authority or sole storage location for the anchor.

Required safeguards before calling it protected:

- independent storage under separately controlled credentials;
- versioned, append-only history or equivalent tamper-evident records;
- cryptographic signatures and documented key custody;
- at least one independently held recovery copy;
- periodic integrity verification and tested restoration;
- a clear process for proposing corrections without silently overwriting prior versions.

**Status:** This document defines the proposed safeguards only. It does not claim that an external anchor has already been provisioned, signed, or independently backed up.

### 10.4 Origin and identity lineage

For affected entities, retain a traceable lineage from the entity and its names through language, historical geography, and continental attribution where reliable evidence exists. Record source, date, uncertainty, alternate accounts, and correction history. Never infer a continental source from a name, language, appearance, or symbolic association alone. Unknown origin remains unknown until evidence supports a more specific claim.

A correction may change an active interpretation or exclude a harmful rule, but it must not falsify the historical identity or provenance record. Preserve the previous interpretation as a superseded record with its evidence and reason for correction.


## Governing principle

**YES connects by explicit agreement. NO distinguishes by explicit refusal. CANT protects declared boundaries. NOT preserves meaning through negation. Continuity may cross boundaries without erasing distinction; names may evolve in essence without falsifying origin; harmful logic may be excluded without erasing the entities or evidence it affected.**
