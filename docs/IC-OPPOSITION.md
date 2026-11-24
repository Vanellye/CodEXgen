# I.C. Opposition

## Purpose

I.C. Opposition is the diagnostic validation discipline for Ɣơ adapter parity. It challenges an implementation claim by comparing independent language adapters against the same versioned test vectors and by running each adapter's own tests.

Opposition is not blind reversal, adversarial obstruction, or an autonomous repair authority.

## Operating rules

1. **Challenge, do not negate by default.** Every check identifies the behavior or invariant it tests.
2. **Preserve the baseline.** Keep the original CodEXgen implementation and its source revision identifiable.
3. **Use common evidence.** Python, JavaScript, and Kotlin consume the same versioned test-vector file.
4. **Make outcomes explicit.** Report PASS, FAIL, BLOCKED, or NOT_RUN. A workflow not executed is not a pass.
5. **Separate diagnosis from repair.** Findings may propose changes, but the workflow does not rewrite source or authorize merges.
6. **Keep human control.** Repository writes, merges, releases, and privileged actions require explicit human authorization.

## Workflow mapping

The GitHub Actions workflow named `I.C. Opposition — Ɣơ adapter parity` preserves the prior checks:
- Python codec execution and unit tests
- JavaScript adapter/parser test runner
- Kotlin adapter compilation and shared-vector execution

The workflow identity and job labels change the diagnostic framing, not the test semantics.
