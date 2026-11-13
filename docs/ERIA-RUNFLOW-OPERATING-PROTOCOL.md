# ERIA Runflow — Operating Protocol

**Status:** Initialized as a documentation-level operating protocol  
**Authority:** Governs how ERIA work is proposed, reviewed, authorized, executed, and learned from. It does not grant repository, account, or external-system permissions.  
**Initial state:** READY FOR INPUT — no task is implicitly authorized or running.

## Governing purpose

Runflow carries an intention from origin to accountable action and back into learning. It must make progress legible without confusing a proposal with permission, an attempt with success, or a lesson with ownership of its source.

**Runflow axiom:** Recognize the origin. Clarify the intent. Obtain authorization. Act within scope. Examine evidence. Test recovery. Carry the lesson forward without repeating harm.

## Canonical cycle

**Origin → Iintênt → Authorization → Execution → Evidence → Review → Recovery → Learning → New Growth**

**Iintênt** is the ERIA-styled name for the Intent stage. It means the deliberately articulated inner aim made clear as an accountable outcome: what is sought, why it matters, what is in scope, and what must remain unchanged. The spelling is a named convention, not a claim of a separate force or an authorization. The ordinary term *Intent* remains its plain-language gloss.

1. **Origin** — identify the source of the request, artifact, idea, or change. Record known provenance; mark unknowns as unknown.
2. **Iintênt (Intent)** — state the desired outcome, scope, constraints, affected parties, and what must remain unchanged.
3. **Authorization** — obtain explicit approval for the specific consequential action. Approval is scoped; it does not silently extend to adjacent actions.
4. **Execution** — perform only the authorized action. Preserve branch identity, history, source records, and reversibility where applicable.
5. **Evidence** — record what actually happened, using source-backed observations. Separate observed facts, interpretation, assumptions, and unknowns.
6. **Review** — compare outcome with intent, invariants, permissions, and possible harms. A successful command is not automatically a correct result.
7. **Recovery** — identify and, where consequential, test a rollback, repair, or safe-containment path before declaring the work complete.
8. **Learning** — extract a bounded lesson, thumb-imprint its origin and evidence, and state uncertainty without rewriting the source.
9. **New Growth** — carry only reviewed and authorized learning into later work, with its provenance and limitations attached.

## State model

Every Runflow task has one explicit state:

- **DRAFT** — intent is being formed; no action is authorized.
- **READY** — scope, origin, constraints, and proposed action are clear; awaiting authorization.
- **AUTHORIZED** — the exact action and boundary have been approved.
- **RUNNING** — the authorized action is in progress.
- **BLOCKED** — an invariant, permission, dependency, or safety condition prevents continuation.
- **UNRESOLVED** — evidence is incomplete, ambiguous, conflicting, or unavailable.
- **REVIEW** — execution has stopped and evidence is being examined.
- **RECOVERY-REQUIRED** — an adverse or unexpected outcome needs containment or repair.
- **RECOVERED** — the recovery path has been exercised and its result recorded.
- **COMPLETE** — outcome reviewed, evidence recorded, required recovery checked, and scope satisfied.
- **LEARNED** — a lesson has been thumb-imprinted with its source and uncertainty for future reference.

State transitions are explicit. No timeout, silence, missing response, inferred intention, or tool success may be treated as authorization. BLOCKED and UNRESOLVED are legitimate outcomes, not failures to conceal.

## Authorization boundary

- A proposal is not permission.
- Validation is not adoption.
- Adoption is not deployment.
- A commit is not proof of runtime behavior.
- A successful execution is not proof of correctness.
- Permission for one action does not authorize a broader action.
- No branch merge, force update, release, deployment, external message, data deletion, or irreversible change occurs without explicit, action-specific authorization.
- If the scope changes materially, return to READY and obtain renewed authorization.

## Evidence and origin discipline

For each consequential task, record what is available:

- source/origin and exact artifact or branch;
- request and intended outcome;
- authorization and its scope;
- action actually performed;
- resulting commit, artifact, output, or state;
- checks performed and their observed results;
- affected parties, risks, and unresolved questions;
- recovery method and test result;
- lesson and thumb-imprint.

Do not invent missing fields. Distinguish **NOT CHECKED**, **NOT AVAILABLE**, **FAILED**, and **PASSED**. Never report a check as passed when it was not run or its result was not observed.

## The Thumb — oversight across the cycle

The Thumb-imprint is applied across the Runflow record, not inserted as a separate execution stage. It points to the origin, marks the evidence and lesson, and makes the history recognizable. It does not claim ownership, confer authority, change authorship, or rewrite the source.

**Thumb-imprint the origin. Let the seed learn from the pitfall. Let the lesson rise without repeating the harm.**

## Stop and recovery rules

Stop the affected action when authorization is absent, scope is exceeded, evidence contradicts a critical assumption, an invariant is threatened, or harm may be propagating. Contain first; do not silently repair, overwrite, or erase the trace.

A correction requires authorization. A recovery claim requires an observed test or an explicit statement that testing remains outstanding. If recovery cannot be safely tested, leave the task in RECOVERY-REQUIRED or UNRESOLVED and state the limitation.

## Initialization record

Runflow is initialized here as an operating protocol for ERIA. This initialization creates no background process, scheduled job, GitHub Actions workflow, runtime service, or automatic authority. It does not start execution of any pending task.

**Initial state: READY FOR INPUT.** The next task must supply or establish its origin, Iintênt (intent), scope, and required authorization before execution.

## Governing principle

**No progress without provenance. No execution without authorization. No conclusion beyond evidence. No correction without permission. No completion without review. No claimed recovery without a tested path.**
