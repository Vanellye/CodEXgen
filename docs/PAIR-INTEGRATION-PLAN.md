# Pair Content Integration Plan

**Repository:** `Vanellye/CodEXgen`  
**Prepared:** 2026-11-09  
**Plan branch:** `olpirt/stride-next`  
**Mode:** content-level integration design only; no source branch merges

## Preservation contract

This plan preserves every source repository, branch ref, commit, and history. It does not authorize a merge, ref update, force push, branch deletion, or protection-setting change. Future content reconciliation must happen on a new, reviewable integration branch and must retain provenance to the exact source commit SHAs.

The two logical strands are:
1. `fiction-mind` + `fiction-body`
2. `fiction-creation` + `hypotheticals`

## Source snapshot

| Source | Audited head |
|---|---|
| `fiction-mind` | `c501b3fe2ae3a75960885d4919e2be86a5708484` |
| `fiction-body` | `6341d35bcc01a1ca8975555fb67ca989229c049c` |
| `fiction-creation` | `35dca4f01efffaf09f12f4123aeeda90c943bc47` |
| `hypotheticals` | `dbd55dfd66ce2d03b81f9ec030ba0c1c93556e6e` |

Re-fetch and verify these refs before any future integration because branch heads can move.

## Pair 1 — fiction-mind → fiction-body

### Observed file-level changes

The pair comparison reports two paths:

| Path | `fiction-mind` | `fiction-body` | Proposed treatment |
|---|---|---|---|
| `hypotheticals/body_fiction.py` | absent | added | Preserve as an additive body-strand module; do not overwrite another source |
| `hypotheticals/resonance_noise_fiction.py` | present | present, different blob | Reconcile as a shared module with explicit strand identity |

The body-only module is a small, standalone, text-printing fiction function. The shared resonance file has the same public function shape and fixed resonance constant, but branch-specific documentation and deterministic random seed strings: `fiction-mind` versus `fiction-body`. Those seed strings produce different deterministic sequences and are meaningful branch identity, not disposable noise.

### Proposed content resolution

- Retain the body-only `body_fiction.py` file.
- Replace the ambiguous single-branch seed with an explicit strand selector or two named deterministic entry points, preserving both `fiction-mind` and `fiction-body` output identities.
- Keep a backwards-compatible default only if the call-site review confirms which branch's behavior existing consumers expect; otherwise require an explicit strand argument.
- Preserve the current `RESONANCE = 1111`, output length default, and deterministic behavior unless tests prove a deliberate change is needed.
- Do not treat the fictional “resonance” value as a physical frequency or biological control.

### Required tests

- Same strand + same length yields byte-identical output across repeated runs.
- Mind and body strands produce their own expected deterministic outputs.
- Requested length is honored, including zero length and boundary inputs.
- Output alphabet remains the documented binary alphabet.
- Running the module as a script identifies the selected strand and does not silently change the data representation.

## Pair 2 — fiction-creation → hypotheticals

### Observed file-level changes

The pair comparison reports two paths:

| Path | `fiction-creation` | `hypotheticals` | Proposed treatment |
|---|---|---|---|
| `hypotheticals/BRIDGE.md` | absent | added | Preserve as the structural map; revise only after checking all four strand relationships |
| `hypotheticals/resonance_noise_fiction.py` | present | present, different blob | Reconcile raw binary generation and display formatting as separate operations |

The two resonance files have the same deterministic generator shape and constant, but use different seed labels. The `fiction-creation` script changes the displayed CLI output by replacing the character `0` with `ơ`; the generator itself still returns binary text. The `hypotheticals` version prints the raw binary text.

### Proposed content resolution

- Retain `BRIDGE.md` as documentation, but update its graph only after confirming the final four-strand relationships and explicitly mark all links as logical/content relationships, not Git merges.
- Preserve raw binary output as the canonical data representation.
- Add a separately named presentation formatter for the `ơ` marker. Apply it only at the display boundary; never alter numeric zero constants, program logic, file formats, or machine-readable binary data.
- Preserve both seed identities (`fiction-creation` and `hypotheticals`) through explicit named entry points or a required strand selector.
- Document that `ơ` is a visual convention, not an alternate numeric value or a cryptographic/data encoding.

### Required tests

- Deterministic output for each strand identity.
- Raw generator output contains only `0` and `1`.
- Marker formatter changes only display text and leaves the raw value unchanged.
- `ơ` appears only in the formatted output path.
- Bridge documentation references the intended four strands and does not imply that `main` was merged with fiction branches.

## Cross-pair collision — resolve before combining both strands

Both pairs touch the exact same path, `hypotheticals/resonance_noise_fiction.py`. The current variants have four distinct deterministic seed identities. Integrating pair 1 and pair 2 independently and then combining their results would create a second conflict at this path.

**Recommended resolution:** create one shared, small resonance module with explicit named strand variants for `fiction-mind`, `fiction-body`, `fiction-creation`, and `hypotheticals`; keep branch-specific wrapper/entry-point behavior where required; keep binary generation separate from marker formatting. Do not let one branch's seed or output formatting silently replace another's.

The shared module should not be added to any source branch until a separate integration branch is created and the user approves the content change.

## Suggested future integration sequence

1. Re-fetch and pin the four source head SHAs in an integration manifest.
2. Create a new integration branch from a chosen, explicitly approved base; do not repoint any source branch.
3. Import the additive `body_fiction.py` and `BRIDGE.md` files with source provenance.
4. Reconcile the shared resonance module using the four named deterministic identities.
5. Add unit tests for determinism, output length, raw binary invariants, and display-only marker formatting.
6. Run Python syntax checks and the targeted tests, then run applicable project builds.
7. Review the full diff and provenance map; record conflicts and decisions.
8. Stop for explicit approval before any merge or promotion to another branch.

## Current decision

**Plan complete; content integration not performed.** All four source branch refs remain unchanged by this plan. Pair compatibility is promising but not yet verified by tests, and the shared-path collision is a blocking design decision until the four identities are represented together.

## Legacy preservation gate

Apply the [Legacy Preservation & Independent Peering Protocol](LEGACY-PEERING-PROTOCOL.md) to every source file and component considered for this plan. Re-fetch and pin exact source SHAs; retain the original files and provenance; document consumers, interfaces, dependencies, and historical behavior; and place any extracted or reconciled implementation in a new, reviewable location. The proposed pair resolution is not approved peering until contract tests, compatibility checks, provenance review, and explicit human approval are recorded. Age, isolation, or unrelated ancestry is never permission to delete or overwrite a source branch.
