# THOUGHT TOTT — Initial Repository Correction Retrospective

**Scope:** 91 commit records returned for `eria/new-pantheon-staging` and its reachable ancestry at review time.
**State:** Candidate inventory only; no lesson below is automatically accepted.
**Method:** Commit subjects were screened for correction, fix, revert, test, provenance, evidence, merge, and preservation signals. A commit subject is a discovery clue, not proof that the underlying change was correct.

## Candidate correction and learning records

| Commit | Recorded subject | Initial classification |
|---|---|---|
| `d245783d26db` | fix: correct FaCADE C string escaping | Defect correction; compiler/test validation required |
| `a332be7e59bc` | test: cover FaCADE correction and restoration gates | Regression coverage |
| `f87c41471726` | implement additive FaCADE correction proposals | New correction workflow |
| `2f70f9bc6c7f` | define FaCADE correction contract | Contract definition |
| `e9b31db9a282` | require evidence classification and proof traceability | Evidence-governance refinement |
| `90f5b5582b07` | define evidence, proof, and provenance standards | Terminology and governance |
| `78f56617091e` | cover output truncation fail-closed behavior | Boundary-test correction |
| `5fa48aa5ea11` | verify evidence labels, privacy gate, and provenance separation | Regression coverage |
| `d3ed900624dc` | add claim evidence references without replacing provenance | Additive schema refinement |
| `e38dd5365451` | model evidence status separately from narrative | Classification refinement |
| `ecf0925e621d` | add NEW authorization and provenance tests | Regression coverage |
| `bf52be71464c` | implement fail-closed NEW proposal gate | Authorization control |
| `6cae59a111a9` | restore canonical seed-pitfall rise sequence | Historical/documentation restoration |
| `46bd003247e9` | merge latest main into ERIA identity migration | Integration event; inspect diff before lesson |
| `917803c53cc9` | run unit tests before APK build | CI sequencing improvement |
| `351cfff5fbb0` | add JUnit for TRUE NORTH contract | Regression coverage |
| `8062c37ed5ee` | correct ERIA token vault comment formatting | Documentation correction |
| `f1a90e2a2fc7` | fix ERIA token vault compatibility comment | Documentation/compatibility correction |
| `b76f107ce29a` | merge PR #10: preserve PR #1 implementation and provenance | Preservation/integration decision |
| `82635ceb3899` | document PR1 preservation and PR10 integration provenance | Provenance record |
| `99f7dd228f7b` | define provenance interface and reproducibility review gates | Reproducibility governance |
| `c89f1ff2623a` | record evidence-based synthesis of Main and Stride snapshots | Cross-branch synthesis |
| `7c5fc66df6cf` | revert “Birth resonance-1111 noise (hypotheticals)” | Reversal; inspect paired change and reason |
| `ff09b9a11513` | add friction-to-airways noise fiction on main (revertible) | Reverted experimental/fictional content; preserve distinction |

## Reusable candidate lessons — not yet accepted

1. **Fix the exact defect:** a syntax or escaping correction must be compiled with strict warnings and exercised by a regression test.
2. **Preserve semantic boundaries:** provenance, evidence, proof, interpretation, and authorization are separate fields and claims.
3. **Fail closed at consequential boundaries:** missing authorization, required evidence references, or output capacity must return a clear hold/error status.
4. **Test negative paths:** missing permission, unsupported classification, absent lineage, truncated output, and unverified links need explicit tests.
5. **Preserve before integrating:** branch/PR merges should retain origin, prior implementation, and a reviewable diff.
6. **Reversals teach context, not automatic prohibition:** inspect both the introduced change and its revert; distinguish intentional experiments, fictional content, and defects.
7. **Documentation changes are corrections too:** compatibility notes and operating contracts need traceable updates and consistency checks.
8. **Do not infer correctness from commit labels:** validate code, tests, runtime behavior, and intended scope independently.

## Remaining work

- Fetch each candidate commit's full patch and relevant test results.
- Pair reversions with the original change and document why it was reversed.
- Mark each lesson proposed, accepted, challenged, or superseded with reviewer and scope.
- Add regression tests for accepted lessons where feasible.
- Review the remainder of the repository's history and any corrections that exist only in conversations, issues, or external records.
- Never claim this inventory covers all of the user's lifetime history or every correction in all branches; it covers the 91 reachable commit records screened for this branch.

No source commit, old notice, or branch history was rewritten by this retrospective.
