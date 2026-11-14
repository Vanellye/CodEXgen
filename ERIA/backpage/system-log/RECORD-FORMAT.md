# Reviewed Data Record Format

Use this template for each review. Unknown values must be marked `UNKNOWN` or `NOT PROVIDED`; do not guess.

```yaml
record_id: "stable-unique-id"
recorded_at: "ISO-8601 timestamp with timezone"
record_type: "REVIEW_SUMMARY"
review_status: "REVIEWED | PENDING | REJECTED"
reviewer:
  identity: "verified identity or NOT VERIFIED"
  verification_basis: "how identity was established, or UNKNOWN"
sources:
  - source_id: "stable source reference"
    path_or_uri: "repository path or URL"
    ref: "branch/tag/commit"
    content_digest: "digest or NOT RECORDED"
    source_kind: "observation | specification | test | external evidence"
interpretation:
  summary: "concise interpretation"
  observed_facts: []
  inferences: []
  uncertainty_and_gaps: []
  confidence: "low | medium | high | not-assessed"
intervention:
  description: "action or NOT APPLICABLE"
  state: "PROPOSED | AUTHORIZED | EXECUTED | VERIFIED | BLOCKED | NOT_APPLICABLE"
  authorization:
    reference: "approval ID or NONE"
    scope: "exact approved scope or NONE"
  execution_evidence:
    reference: "run/commit/artifact/measurement or NONE"
    actor: "identity or UNKNOWN"
    executed_at: "timestamp or NOT RECORDED"
  verification:
    checks: []
    result: "PASS | FAIL | PENDING | NOT RUN | NOT APPLICABLE"
    evidence: "reference or NONE"
recovery:
  method: "rollback/recovery plan or NOT APPLICABLE"
  reference: "checkpoint/ref or NONE"
relations:
  supersedes: []
  corrects: []
  related_records: []
```

## State transition constraints

- `PROPOSED → AUTHORIZED` requires a separately recorded, scoped approval.
- `AUTHORIZED → EXECUTED` requires evidence that the approved action actually occurred.
- `EXECUTED → VERIFIED` requires post-action checks and evidence.
- Any state may be `BLOCKED` when a required gate fails.
- Review status is independent of intervention state.
- Never infer an execution event from a review, approval, recommendation, plan, branch creation, commit message, or CI result unless that evidence directly establishes the intervention itself.
