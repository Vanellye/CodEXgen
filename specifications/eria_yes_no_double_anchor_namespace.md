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

## Governing principle

**YES connects by explicit agreement. NO distinguishes by explicit refusal. CANT protects declared boundaries. NOT preserves meaning through negation. The namespace maps relationships without making ownership out of connection.**
