# DEALER Old-Antique Rewrite Ledger

Date: 2026-11-24
Repository: `Vanellye/CodEXgen`
Operation: replace remote `dealer` branch head with a rewritten prototype lineage based on `mold`.

## Source prototype

Source branch: `mold`
Source HEAD: `42a8228fcfc370aff8f5c707c1f60025ece2d2dc`
Source tree: `39d8a1537b52d364b571e397cf5c66aea16c2bca`

The source tree contains:
- `Cold.html` — deprecated concatenated dump note
- `cold` — identical deprecated dump note
- `PENDULUM.py`
- Kotlin Android app and tests
- Compose mirrors
- Python modules
- TRUE NORTH data architecture documentation

The dump note says the former mixed Kotlin/Python blob was split into tracked source files. The source branch itself is not modified by this operation.

## Source commit ancestry (oldest to newest)

| Order | Commit SHA | Message | Parent |
|---:|---|---|---|
| 1 | `307ececa62e59c6361b75cc69c72c491168c623a` | Initial commit | none |
| 2 | `0aded462217e35586be00cdc8e458e94a59b64a3` | Create cold — OLD | `307ececa62e59c6361b75cc69c72c491168c623a` |
| 3 | `bc9f251695c8c9bd49c1a2a5aca514dc2d024394` | Create Cold.html — OLD.APIK | `0aded462217e35586be00cdc8e458e94a59b64a3` |
| 4 | `21369682e996e1b26e47871d1fab83f1342e71d1` | Update .gitignore | `bc9f251695c8c9bd49c1a2a5aca514dc2d024394` |
| 5 | `a0a3de8fce2784c6b50e02f832caadfda0efda28` | Add TRUE NORTH data contract | `21369682e996e1b26e47871d1fab83f1342e71d1` |
| 6 | `15dc6bb1d62dfdb4e580489e530b5d598ca6f606` | Add TRUE NORTH data contract | `a0a3de8fce2784c6b50e02f832caadfda0efda28` |
| 7 | `5dc45a9d3670655d77bf91952a657ea9efca30fe` | Add JUnit for TRUE NORTH contract | `15dc6bb1d62dfdb4e580489e530b5d598ca6f606` |
| 8 | `42a8228fcfc370aff8f5c707c1f60025ece2d2dc` | Test TRUE NORTH contract before APK build | `5dc45a9d3670655d77bf91952a657ea9efca30fe` |

Parent SHAs are the authoritative graph edges.

## Prior DEALER ref

Before replacement, `dealer` pointed to:
- Old HEAD: `37b6aeac7b8da21a7d1df0c36047a6564b9eb068`
- Parent: `4412dc714bf35296a9e751e2b8c30e0cd6cadede`
- Message: `feat(dealer): define reversible wordspace binary encoding`

That prior ref is preserved by backup branch `dealer-pre-rewrite-20261124`.

## New DEALER ref

The rewritten branch is based on the old-antique `mold` prototype tree, with the v0.2 wordspace specification and this ledger added. `main` and `mold` are not targets of the ref update.

## Integrity and limits

- Original source commit SHAs are recorded above; source objects remain reachable from `mold`.
- The backup branch preserves the prior one-commit `dealer` history.
- The new history is a deliberate lineage reset at the DEALER branch ref; it does not claim to reproduce every original commit object or signature.
- Do not treat the custom Wordspace-26 bitstream as encryption or a security boundary.
