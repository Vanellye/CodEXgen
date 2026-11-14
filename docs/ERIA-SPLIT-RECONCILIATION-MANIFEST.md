# ERIA Split Reconciliation Manifest

**Status:** Proposed integration map; four review PRs opened as drafts  
**Source snapshot:** `2f9e83322bf782cdb3e7fc11bfe4e28fee605532`  
**Original PR:** [#42](https://github.com/Vanellye/CodEXgen/pull/42) — retained as the historical source record  
**Integration base:** `main` at `2cce68f258f46058f18c108c264db9cc85200590`

## Split workstreams

| Workstream | PR | Branch | Split-content commit |
|---|---:|---|---|
| Lineage and governance | [#43](https://github.com/Vanellye/CodEXgen/pull/43) | `reconcile/lineage-governance` | `654a20040546522616ee879003edce2d9072a27c` |
| Transmission metadata | [#44](https://github.com/Vanellye/CodEXgen/pull/44) | `reconcile/transmission-metadata` | `341d09f4809ddee003e9f9fae38755f6b6976054` |
| Pantheon Integration Core | [#45](https://github.com/Vanellye/CodEXgen/pull/45) | `reconcile/pantheon-integration-core` | `13dba05589f68297d3b1f5e2fd2fe3bff9bf765c` |
| ERIA hardware specifications | [#46](https://github.com/Vanellye/CodEXgen/pull/46) | `reconcile/eria-hardware` | `9245345444d0e6c796ad80bdfce8a1430a03ac93` |

The listed SHA for PR #43 is the lineage/governance content commit before this manifest was added. PR #43's live head also contains the subsequent manifest commit; use the live PR metadata for the current head. The other three SHAs identify their split-content commits and are the live heads at the time this manifest was written.\n\n## Reconciliation and dependency edges

- PR #43 is the provenance and branch-governance reference for the split.
- PR #44 is an independent metadata/documentation track; it does not configure a signal generator or audio output.
- PR #45 contains the C99 Integration Core and its test wiring. It is software-only and does not authorize merge, publication, CI dispatch, or physical output.
- PR #46 describes the ERIA perception/reasoning processor and FPGA validation plan. It is a specification track and does not contain verified RTL or board measurements.
- The hardware documentation may refer to the Integration Core conceptually, but physical hardware validation is independent of Pantheon software CI.
- The four PRs are siblings from the same `main` baseline; none is silently stacked on or merged into another. Reconcile dependencies in a later integration PR only after each workstream is reviewed and its checks pass.

## Preservation and status rules

- PR #42 remains open as the original historical source record.
- All four split PRs are draft and target `main` at the same recorded base SHA.
- No branch history is rewritten; no force-push or ref reset is used.
- No merge, deployment, external dispatch, runtime activation, or physical actuator enablement is performed by this manifest.
- Pinned heads are snapshots. If a branch advances, update this manifest with a new attributable commit and retain the prior SHA in review history.
- CI, review, and merge status must be checked independently for each PR. A passing run is not merge authorization.

**Reconnection invariant:** every workstream has a named source branch, exact head SHA, review destination, and explicit dependency boundary.