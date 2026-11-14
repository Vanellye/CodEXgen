# ERIA Canonical Anchor

This manifest pins the ERIA component baseline to one immutable Git commit.
It is a reference record; it does not rewrite component source, Git history, or runtime configuration.

- Repository: `Vanellye/CodEXgen`
- Canonical commit: `b549dea5af2e51402cf41234f3e2b3cdfb064032`
- Anchor branch: `anchor/eria-unified-b549dea`
- Anchor commit URL: https://github.com/Vanellye/CodEXgen/commit/b549dea5af2e51402cf41234f3e2b3cdfb064032

## Component references

All paths below are resolved at the canonical commit above.

| Component | Repository path / source |
|---|---|
| Native Kotlin dashboard | `app/src/main/java/com/vanellye/eria/RepositoryDashboardScreen.kt` |
| Android app integration | `app/src/main/java/com/vanellye/eria/MainActivity.kt` |
| Termux conversation/repository engine | `tools/eria_repository_conversation.py` |
| Termux API server and dashboard endpoints | `tools/eria_conversation_server.py` |
| Browser dashboard | `tools/eria_repository.html` |
| PONS capability gate | `tools/eria_pantheon/pons.py` |
| PONS interface | `tools/eria_pantheon/interface.py` |
| Provenance, audit, and file-index APIs | `tools/eria_conversation_server.py` |
| PONS bridge tests | `tests/test_eria_pantheon_bridge.py` |
| Dashboard store tests | `tests/test_eria_dashboard_store.py` |

## Anchor and change policy

1. Treat the canonical commit SHA as the baseline for comparisons and provenance.
2. Do not move the anchor branch or rewrite the anchored commit.
3. Implement future work on a separate feature or integration branch.
4. Record the new commit SHA and the canonical anchor SHA in change notes.
5. Preserve source files, original Git history, and audit evidence.
6. An anchor reference is not proof that a component has been rebuilt, deployed, or hardware-tested.
7. Keep execution, transmission, and protected Git mutation subject to explicit human authorization and the existing PONS policy.

## Verification

To inspect the exact baseline locally:

```bash
git fetch origin
git show --no-patch --format=fuller b549dea5af2e51402cf41234f3e2b3cdfb064032
git diff --stat b549dea5af2e51402cf41234f3e2b3cdfb064032
```
