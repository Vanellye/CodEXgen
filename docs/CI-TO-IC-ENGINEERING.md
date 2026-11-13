# CI-to-IC Engineering Plan — ERIA / Pantheon

**Scope:** repository-wide CI architecture and PR #42 implementation  
**CI source inspected:** `.github/workflows/independent-branch-ci.yml` on `main`  
**Software component:** Pantheon **IC — Integration Core**  
**Status:** Initial software contract implemented on PR #42; hardware design remains a separately specified engineering track.

## 1. What was reverse-engineered

The existing workflow is event-driven. It runs on `push`, `pull_request`, and explicit `workflow_dispatch`. It has read-only repository contents permission and does not cancel an in-progress run when another run starts for the same ref.

| Existing job | Current behavior | IC contract mapping |
|---|---|---|
| Source integrity and whitespace | Full checkout, Git object connectivity, whitespace check, read-only advisory scan | Source-integrity gate |
| Pantheon C99 contract integration tests | Compile and execute every listed C99 contract suite with warnings as errors | Component-contract gate |
| Python syntax and available unit tests | Preserve quarantined file by blob hash, compile non-quarantined Python, run unittest if present | Language-validation gate |
| Android debug APK build | Java 17/Android SDK setup, Android unit tests, debug APK build | Platform-build gate |

The current workflow is the observed baseline; this plan does not claim that hardware EDA stages already exist.

## 2. IC software component

In this repository, **IC means Integration Core**: a small Pantheon C99 state/gate contract that represents pipeline prerequisites, execution results, explicit approvals, and publication eligibility.

Implementation:
- `pantheon/IC/IC.h`
- `pantheon/IC/IC.c`
- `pantheon/IC/tests/test_IC.c`
- `pantheon/run-contract-tests.sh` invokes the new suite.

The component is deliberately non-executing. It cannot launch CI, execute shell commands, mutate Git, approve a PR, publish an artifact, or contact an external service. It is a deterministic policy primitive that later adapters may call only within their separately authorized boundaries.

## 3. Repository-wide and PR-wide behavior

The existing workflow already listens to repository `push` and `pull_request` events, so it is not a time-only or scheduled pipeline. The new IC contract suite is added to the existing Pantheon contract runner; consequently it participates in the same workflow for every branch/PR on which that workflow runs.

No cron schedule or time-triggered automation is introduced. `workflow_dispatch` remains a deliberate manual invocation. Concurrency remains non-cancelling so one ref's in-progress validation is not silently interrupted.

This PR adds the component and its test integration to the PR #42 branch. It does not rewrite every open PR branch or silently alter archived, dependency, or nested repositories. Once merged through the normal review process, the workflow definition and test runner on the default branch will apply to subsequent matching repository events. Existing open PRs may need a base update or a new commit to pick up the merged test suite; their heads are not rewritten here.

## 4. Hardware integrated-circuit track — what CI can and cannot establish

A CI pipeline can validate an IC design flow, but it cannot reveal a physical chip architecture from CI YAML alone. The inspected repository workflow contains no declared RTL source set, process design kit (PDK), EDA toolchain, timing constraints, package/pin plan, or fabrication target.

A real hardware track therefore needs a separately reviewed design brief and source artifacts before adding automated stages:

1. **Requirements:** use case, interfaces, power/thermal limits, operating range, safety constraints, and measurable acceptance criteria.
2. **RTL source:** HDL modules and versioned interface definitions.
3. **Static checks:** HDL lint, elaboration, clock/reset and CDC checks where applicable.
4. **Simulation:** unit and integration testbenches with deterministic vectors and coverage goals.
5. **Synthesis:** map RTL against a named, licensed PDK/library and record tool/version/configuration.
6. **Physical implementation:** floorplan, placement, clock-tree synthesis, routing, extraction.
7. **Signoff:** static timing analysis, DRC, LVS, antenna/ERC and power-integrity checks as required by the target process.
8. **Release package:** immutable source snapshot, constraints, tool versions, reports, hashes, and human signoff.
9. **Fabrication handoff:** separate explicit authorization by the design owner; CI success is not tapeout approval.

Until the design brief, RTL, PDK, and EDA tools are supplied and verified, these are planned gates only. No chip, netlist, GDSII, or fabrication-ready artifact is claimed.

## 5. Evidence and release gates

Every future stage should record:
- repository, branch, full commit SHA, and source paths;
- toolchain and schema versions;
- input and output digests;
- dependency results and test evidence;
- warnings, failures, and unresolved assumptions;
- independent approval where the action changes persistent state or crosses an external boundary.

A green test is evidence of the checks actually run, not a universal correctness claim or authorization to merge, deploy, dispatch, or fabricate.

## 6. Stop conditions

Hold the affected stage on missing prerequisites, unknown provenance, failed tests, tool/version drift, scope expansion, unavailable licenses/PDKs, or missing approval. Do not substitute a guessed design, unverified toolchain, alternate branch, or silent retry.

## 7. Next engineering sequence

1. Run the new IC C99 contract in the existing Pantheon test job.
2. Inspect CI results on the exact PR #42 head and fix only evidenced failures.
3. Review the complete PR diff and obtain human review.
4. Merge only after required checks and explicit merge approval.
5. Separately collect the IC hardware design brief, RTL, PDK/toolchain access, and acceptance criteria before implementing EDA jobs.

**Invariant:** CI verifies declared work; IC models the gates; neither creates authority. Hardware implementation and fabrication remain separate, evidence-based, human-approved stages.


## 8. Standalone perception and reasoning processor specification

The proposed physical architecture and staged requirements are recorded separately in [ERIA-PERCEPTION-REASONING-IC-SPEC.md](ERIA-PERCEPTION-REASONING-IC-SPEC.md). It defines a standalone sensory acquisition, DSP, perception, reasoning, context, and safety/actuation-boundary processor that interoperates with ERIA, Pantheon, Stride, PonsLucis, and Transmission through versioned contracts.

That document is a requirements baseline only. It does not add RTL, select a foundry/PDK, define a final bus/pinout or power budget, claim subjective consciousness, or produce a netlist/GDSII/fabrication package. The initial prototype is observe/propose mode; physical actuation remains separately inhibited and authorization-gated. Hardware design and signoff remain independent of the existing C99 Integration Core CI tests.
