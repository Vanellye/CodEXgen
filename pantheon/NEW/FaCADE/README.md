# FaCADE — Cross-Reference and Restoration Layer

**State:** Staged; not wired into the Pantheon runtime.

FaCADE adds traceable links between original records, prior notices, corrections, and later representations. It is additive: it does not rewrite or delete source records, accepted accounts, or earlier notices.

## Relations

- `RESTORES-REFERENCE`: reconnects an overlooked or orphaned notice to a surviving, identified record.
- `CORRECTS-PRIOR-NOTICE`: appends a correction to an earlier notice.
- `SUPERSEDES-REPRESENTATION`: identifies a newer representation while retaining the older one.
- `CONTRADICTS`: records a conflict without silently resolving it.
- `DERIVED-FROM`: records lineage between representations.

## Correction and portal contract

A correction proposal requires an authorized source, source and target record identifiers, a reason, timestamp, reviewer identity, evidence reference, a known relation, and an upstream assertion that the link was checked. The module emits a reviewable proposal; it does not itself authenticate the reviewer, validate the evidence contents, or prove the underlying claim.

A "portal" is a navigational reference to an identified record or correction chain. It is not a person, a recovered voice, a resurrection, or permission to act on someone's behalf. Missing people or missing records are never fabricated or impersonated. If a target cannot be identified and checked, the link remains unresolved and must not be emitted as a verified portal.

## Safety and integrity

- Preserve original source material and prior notices.
- Append corrections; never silently overwrite.
- Keep provenance separate from proof and interpretation.
- Preserve contradictions and uncertainty.
- No covert monitoring, private-stream collection, profiling, or sensitive-trait inference.
- Human review is proportional to risk; publication, sensitive-data use, consequential actions, and destructive changes still require explicit approval.
- A verified link proves only that the reference was checked under the caller's process; it does not establish the truth of the linked account.

## Build and test

```sh
cc -std=c99 -Wall -Wextra -Werror -Ipantheon/NEW/FaCADE \
  pantheon/NEW/FaCADE/FaCADE.c \
  pantheon/NEW/FaCADE/tests/test_FaCADE.c -o /tmp/facade-test
/tmp/facade-test
```

No runtime adapter, external data connector, publication path, or automated merge is included.
