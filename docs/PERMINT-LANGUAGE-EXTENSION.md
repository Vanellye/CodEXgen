# Permint — Permanent Adaptive L·Language Extension

**Status:** Proposed language extension; not enabled by the bđyt v0.1 interpreter  
**Parent method:** `ÆŤ8Ð`  
**Ethical layer:** Cauldron Ethics (`§`)  
**Language identity:** `Permint` — permanent in lineage, adaptive by versioned proposal

## Intent

Permint defines a durable language identity whose vocabulary and interpretations may grow without rewriting its origin, silently changing prior meanings, or treating adoption as permission to execute. "Permanent" means that the identity and its history remain addressable; it does not mean that any one definition is immutable or beyond review. Adaptation creates a new, attributable version.

This document proposes seven operators. The operators are specifications only. They do not add execution behavior to `scripts/bdyt.sh` until a separately reviewed implementation is approved.

## Seven proposed operators

| Operator | Proposed name | Meaning | Required boundary |
|---|---|---|---|
| `***` | Cauldron Ethics inhibitor | Evaluate a proposal against the ethical gate; report `ALLOW_FOR_REVIEW`, `BLOCK`, or `REVIEW_REQUIRED` with reasons | Never grants authorization; an inhibitor can block but cannot dispatch |
| `#` | Origin annotation | Attach a human-readable note or provenance reference to a proposal | Annotation is not executable code, evidence of truth, or consent |
| `&^&^&` | Sixfold mirror | Review six ethical stages in forward order and their corresponding reverse/recovery checks | Missing evidence or failed checks produce `REVIEW_REQUIRED`; no automatic progression |
| `×` | Composition | Combine two named proposal references into a new derived proposal | New identity; parents remain unchanged; no source overwrite |
| `^&&&^` | Evidence coalescence | Group related findings into one view while preserving each finding, digest, and origin reference | Presentation-only grouping; never deletes, merges, or rewrites source records |
| `÷` | Partition | Divide a proposal/reference into named parts for separate review | Derived parts retain parent provenance; original remains unchanged |
| `()` | Permint declaration | Declare or adopt a named Permint language identity/version and record its lineage | Append-only declaration; adaptation requires a new version and review, never silent reinterpretation |

### Proposed statement forms

These forms are illustrative and are not accepted by the current v0.1 interpreter:

```text
*** proposal_id
# "Origin note: retain the original source and its digest"
&^&^& proposal_id
× combined_proposal left_proposal right_proposal
^&&&^ finding_group
÷ left_part right_part proposal_id
() Permint "L·Language"
```

The current bđyt `×` and `÷` operators already create in-memory derived text values. They do not write to source files. Their Permint meanings above are proposal-level lineage semantics; they do not authorize repository, cloud, network, or device actions.

## Sixfold mirror and Cauldron Ethics (§)

The mirror checks these six stages in order:

1. **Intent** — Is the purpose stated and bounded?
2. **Consent** — Is action-specific authorization present, current, and attributable?
3. **Evidence** — Are source, digest, uncertainty, and supporting records preserved?
4. **Forward** — Is the proposed transformation explicit, bounded, and reviewable?
5. **Reverse** — Is there a tested recovery or compensating path that preserves the original?
6. **Review** — Can a person inspect the result, lineage, and receipt?

The reverse mirror checks the corresponding recovery obligations in reverse order: reviewability, recovery, forward-change accounting, evidence restoration, consent revocation, and intent revalidation. A failed or missing check is a blocker or review finding—not a reason to skip a stage.

The inhibitor reports status only. It cannot create consent, elevate privileges, grant itself an exception, or turn a detected trigger into authorization.

## ÆŤ8Ð and Forward Faculty

The existing `ÆŤ8Ð` method remains: receive, validate, fingerprint, compare, review, and issue a receipt. Permint records its method version and parent lineage with every proposed adaptation.

**Forward Faculty** may suggest a next transformation, identify missing evidence, and prepare a reversible proposal. It cannot approve its own proposal, commit repository changes, upload records, call external services, or actuate a device.

`ƏæŘ` is retained as a literal reversible-method identifier pending an explicit user-authored expansion. Its required properties are evidence preservation, explicit authorization, and a recoverable reverse path. No acronym expansion is inferred here.

Incoming sound or other signals are treated as evidence to inspect—not commands to execute.

## Permint permanence and adaptation

- The Permint identity is stable; each accepted vocabulary or semantic change receives a new version.
- Prior versions and their definitions remain addressable and are never silently overwritten.
- An adaptation records its authorizing human decision, parent version, changed definitions, rationale, tests, and digest.
- "Ever adopted" means a version may be explicitly adopted as a continuing language baseline; it does not mean every future proposal is automatically accepted.
- "Always adaptive" means proposals can be submitted and reviewed indefinitely; it does not mean the running interpreter mutates itself.
- A new definition that conflicts with an earlier one must declare the conflict and version boundary.

## Safety and implementation boundary

- Proposal parsing, if later implemented, must be deterministic and bounded; no `eval`, shell expansion, hidden worker, recursive trigger, or implicit network route.
- No source file is modified by these proposed operators.
- No operator commits, merges, uploads, dispatches, changes permissions, or actuates hardware.
- A report, mirror pass, or Permint declaration is not an authorization token.
- Any future executable implementation requires separate tests, code review, and explicit approval before it is connected to runtime behavior.

## Test expectations

A future implementation must test:

1. All seven tokens are recognized only in their documented forms.
2. `***` blocks or requests review when any required ethical check is absent; it never grants consent.
3. `&^&^&` evaluates all six stages and their reverse obligations; a missing stage cannot be treated as passed.
4. `×` and `÷` create new derived identities and preserve their parents.
5. `^&&&^` groups findings without deleting or rewriting any finding.
6. `#` remains inert annotation and cannot smuggle executable content.
7. `()` creates a versioned Permint declaration; prior versions remain unchanged.
8. Forward Faculty cannot approve or execute its own proposal.
9. A before/after SHA-256 check proves source files remain unchanged.
10. No network, cloud upload, repository mutation, or device action occurs.

The current test script checks that this specification and its seven operator definitions remain present. It does not claim that these proposed operators are executable.
