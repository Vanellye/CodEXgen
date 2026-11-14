# ERIA — WANTEVER × WANTs Evolution Engine

**Status:** proposed integration contract  
**Target branch:** `integration/wantever-propagation`  
**Related specifications:** `WANTEVER-SUBSTANCE-AND-PROPAGATION.md`, `ERIA-INVENTORY-OF-INVITED-INVENTION.md`, `PLATFORM-FOUNDATION-CONTRACTS.md`  
**Purpose:** turn stated wants and identified gaps into small, reviewable, evidence-backed engineering prompts and recognize verified progress.

> Let intention suggest the next step. Let evidence earn the reward. Let people retain authority over change.

## 1. Integration meaning

This specification joins two complementary concepts:

- **WANTEVER** is the composition and propagation discipline: preserve origins, transform compatible contributions, validate the result, and propose adoption without erasing branch identity.
- **WANTs** are explicit desired outcomes: a goal, the reason it matters, its scope, and the conditions by which completion can be recognized.
- **WITHOUT** records a known gap or deliberate omission.
- **WONT** records a stated willingness or intended direction.
- **Mini-driving prompts** break a WANT into the smallest useful next engineering action.
- **Rewards** recognize evidence-backed progress, not activity volume, prompt count, speed, or unverified claims.

A WANT is an input to planning, not permission to modify a repository or dispatch externally. A mini-prompt is a proposal until a person or separately authorized workflow accepts it.

## 2. Unified flow

```text
WANT / WITHOUT / WONT
          |
          v
  Preserve source + scope
          |
          v
  WANTEVER composition
          |
          v
  Decompose into mini-prompts
          |
          v
  Review one bounded next step
          |
          v
  Implement in isolated change
          |
          v
  Test + inspect + record provenance
          |
          v
  Human acceptance / rejection
          |
          v
  Reward verified contribution
          |
          +----> next mini-prompt (new proposal)
```

The loop may recommend another task after a verified result. It must not recursively execute prompts, broaden scope, or dispatch external actions on its own.

## 3. WANT record

Each WANT is stored as a structured, versioned record:

| Field | Meaning |
|---|---|
| `want_id` | Stable unique identifier |
| `statement` | Exact desired outcome in the contributor's words |
| `source` | Originator or source artifact |
| `scope` | Repository, branch, paths, platform, and exclusions |
| `rationale` | Why the outcome matters |
| `status` | `proposed`, `accepted`, `in_progress`, `blocked`, `verified`, `rejected`, or `withdrawn` |
| `constraints` | Technical, safety, privacy, license, and resource limits |
| `acceptance` | Observable completion criteria |
| `provenance` | Source revision, timestamp, and transformations |
| `authorization_ref` | Exact approval for consequential changes, or null |

Never infer a WANT from silence, telemetry, reward behavior, or another person's activity. Preserve the exact source statement separately from normalized summaries.

## 4. Mini-driving prompt model

A mini-driving prompt is one bounded unit of work. It should be small enough to review and validate independently.

Required fields:

- `prompt_id`: stable identifier;
- `want_id`: parent WANT;
- `objective`: one concrete action;
- `context_refs`: exact source files, commits, contracts, and evidence;
- `scope`: allowed paths and operations;
- `exclusions`: what must not change;
- `deliverable`: expected artifact or decision;
- `acceptance_checks`: measurable tests or review questions;
- `risk_level`: low, medium, or high with rationale;
- `authorization`: required approval and scope;
- `recovery`: revert or compensation procedure;
- `status`: proposed, ready, active, blocked, completed, or rejected.

### Prompt decomposition rules

1. Start with the user's stated WANT; do not silently replace it with an inferred goal.
2. Inspect existing code and contracts before proposing a change.
3. Split independent concerns into separate prompts.
4. Prefer one bounded file or interface change where practical.
5. Include the exact baseline revision and relevant file references.
6. State assumptions and unknowns explicitly.
7. Define tests before implementation.
8. Stop and ask for review when scope, permissions, or evidence are insufficient.
9. After each accepted result, recompute the next prompt from the updated source revision.
10. Never treat generated prompts as authorization to write, merge, deploy, or dispatch.

### Prompt template

```text
WANT: <exact desired outcome>
WHY: <user-provided rationale>
BASELINE: <repository, branch, exact commit>
NEXT MINI-STEP: <one bounded action>
IN SCOPE: <paths, interfaces, permitted operations>
OUT OF SCOPE: <explicit exclusions>
DELIVERABLE: <expected change>
VERIFY: <tests and acceptance criteria>
PROVENANCE: <source and evidence to preserve>
AUTHORIZATION: <required approval; none means proposal only>
RECOVERY: <revert or compensation plan>
```

## 5. Prompt quality and existing engine integration

The existing `PromptReportEngine` in `PromptOptimizationReport.kt` provides deterministic, heuristic, text-only prompt quality feedback. It checks goal clarity, context, constraints, output specification, validation, and safety/uncertainty.

The evolution layer should compose with that engine rather than replace or misrepresent it:

- Use its report to suggest clearer prompt wording.
- Preserve the contributor's original WANT.
- Add mini-prompt-specific scope, baseline, evidence, and recovery fields.
- Do not treat its numeric score as truth, permission, quality certification, or proof of completion.
- Do not claim that prompt analysis changes model weights, learns autonomously, or modifies source code.

A high-quality prompt can still describe a bad idea. Domain review and tests remain necessary.

## 6. Evidence-based reward model

Rewards are acknowledgements for verified contribution. They must be transparent, bounded, non-transferable by default, and independent of access permissions.

Suggested event categories:

| Event | Suggested points | Evidence required |
|---|---:|---|
| Clear WANT and acceptance criteria | 1 | Reviewed, complete WANT record |
| Useful gap or contradiction identified | 1 | Reproducible evidence/reference |
| Mini-prompt accepted as well-scoped | 1 | Human review |
| Focused test added and passing | 2 | Test output tied to exact revision |
| Implementation accepted | 3 | Reviewed diff and passing required checks |
| Provenance or recovery improvement | 2 | Verified lineage or recovery test |
| Defect found and responsibly reported | 2 | Reproducible issue, regardless of who introduced it |

These values are defaults for discussion, not a live currency or entitlement. A project may change them through a reviewed policy version.

Reward rules:

- Award only once per stable event ID to prevent duplicate credit.
- Link every award to a WANT, prompt, exact revision, evidence, and reviewer or trusted verifier.
- Failed tests, speculative claims, generated text volume, repeated retries, and speed alone earn no completion reward.
- A valid defect report may be rewarded even when it reveals that a prior change failed.
- Never penalize a person for pausing, declining, reporting a safety issue, or withdrawing a WANT.
- Rewards do not grant repository roles, secrets, permissions, deployment rights, or authority over another person's work.
- Keep corrections append-only; revoke or adjust an award only through a documented, reviewable correction event.

## 7. Evolution ledger

Record progress as append-only events:

```yaml
event_id: <stable-id>
event_type: <want-created|prompt-proposed|prompt-accepted|test-passed|change-accepted|reward-awarded|correction>
want_id: <want-id>
prompt_id: <prompt-id-or-null>
source:
  repository: Vanellye/CodEXgen
  branch: integration/wantever-propagation
  revision: <exact-commit>
artifact_digest: <digest-or-null>
evidence:
  - <test-or-review-reference>
decision:
  status: <proposed|verified|rejected|corrected>
  reviewer: <identity-or-automated-check>
reward:
  points: 0
  policy_version: <version>
authorization_ref: <scoped-approval-or-null>
created_at: <timezone-aware-timestamp>
supersedes: <prior-event-id-or-null>
```

A correction creates a new event linked to the earlier event; it does not erase history. Store no credentials or unnecessary personal data in the ledger.

## 8. Relationship to platform foundation contracts

- `PlatformManifest` declares that the WANT evolution capability exists and identifies its version.
- `PlatformContract` defines typed WANT, mini-prompt, evidence, and reward events.
- `EngineRegistry` discovers the prompt analyzer, decomposition engine, verifier, and reward ledger as separate engines.
- `WANTEVER` supplies provenance-preserving composition and propagation rules.
- `WANTs` supply contributor-directed outcomes.
- `STRIDE` may coordinate approved work units but may not expand their scope.
- `PANTHEON` validates capabilities and policy gates.
- `MEMORIA` preserves source records, prompt lineage, verification, and correction events.
- `FORGE` implements only the accepted mini-step and produces reviewable artifacts.

These are role definitions. They do not assert that the runtime integrations are already implemented.

## 9. Acceptance tests

1. Preserve the original WANT text and source when a normalized prompt is generated.
2. Reject a mini-prompt without a parent WANT, baseline revision, or bounded scope.
3. Ensure prompt decomposition cannot add paths or operations beyond its parent scope.
4. Ensure a prompt report score cannot authorize execution or earn a completion reward.
5. Ensure a failed or missing test cannot produce a verified-completion event.
6. Ensure rewards are idempotent by event ID.
7. Ensure rewards never change permissions or access roles.
8. Ensure a correction appends a new ledger event and retains the prior event.
9. Ensure a changed source revision invalidates stale verification evidence.
10. Ensure no prompt loop dispatches externally or recursively executes the next prompt without separately scoped authorization.

## 10. Rollout

1. Adopt this contract as the shared design reference.
2. Define Kotlin data models for WANT, MiniPrompt, EvidenceRecord, and RewardEvent.
3. Extend deterministic prompt analysis to emit a structured mini-prompt proposal.
4. Add a local, append-only in-memory evolution ledger and idempotency tests.
5. Add human accept/reject controls before any code-writing engine is invoked.
6. Connect GENESIS/FORGE to accepted work units and PANTHEON/STRIDE to policy-checked orchestration.
7. Add persistence and cross-platform transport only after schema, privacy, and security review.

## 11. Implementation boundary

This document is a proposed integration contract. It does not implement a live reward economy, autonomous coding loop, model training, repository write permission, external dispatch, merge, or deployment. Those require separate code changes, tests, and scoped approval. The current branch change is documentation-only.

## 12. Kotlin reference pipeline added

The integration branch now contains a provider-neutral Kotlin orchestration layer at
`app/src/main/java/com/vanellye/eria/evolution/WantEvolutionPipeline.kt`.

- `MiniPromptDriver` decomposes each acceptance criterion into a bounded prompt.
- `WantEngine` coordinates the pipeline.
- `GenesisEngine` proposes a platform scaffold without writing files.
- `ForgeEngine` prepares a reviewable candidate without committing, pushing, or deploying.
- `PantheonEngine` evaluates policy before execution.
- `HumanApprovalGate` authenticates and atomically consumes a single-use approval.
- `StrideEngine` is the only mutating execution boundary and receives the exact approval.
- `EvolutionVerifier` checks the execution receipt and evidence.
- `RewardLedger` records an idempotent reward only after verification.

The unit-test source is
`app/src/test/java/com/vanellye/eria/evolution/WantEngineTest.kt`. It covers proposal-only preparation, missing or mismatched approval, policy denial, out-of-scope paths, expired approval, replay rejection, and evidence-gated rewards.

**Implementation status:** the orchestration contracts and test source are committed. Concrete GENESIS, FORGE, PANTHEON, and STRIDE adapters are still required; the Android app does not yet instantiate this pipeline. Tests have not been run in this change session. The approval gate must be backed by an authenticated, persistent, atomic single-use approval store before production use. The in-memory reward ledger is a reference implementation, not durable storage.

## 13. NEXUS knowledge discovery and direction

The [ERIA NEXUS contract](NEXUS.md) defines how WANT-driven branch discovery records
what is known, how it is known, where its source is held, and what bounded direction
may follow. The read-only Kotlin reference types are in
`app/src/main/java/com/vanellye/eria/evolution/WantBranchIntelligence.kt`.

NEXUS discovery results are review candidates only. They do not change branch refs,
copy source, authorize adoption, or bypass the human approval gate defined above.
