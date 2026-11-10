# Branch-by-Branch Knowledge Register

## Audit boundary

This register records a read-only inventory of the 27 branch refs returned by GitHub on 2026-11-10. Each row binds the branch name to the exact head SHA observed during this pass. The tree counts are Git tree entries at that SHA, not counts of meaningful source modules. No branch was fetched, merged, modified, promoted, or declared subordinate to another.

A branch name is a locator, not an ownership statement. The inventory is not a complete semantic audit. Where a distinct design document was not inspected, the row says so rather than inferring intent from the branch name.

## Inventory

| Branch | Observed head | Tree entries | Distinct evidence inspected in this pass |
|---|---|---:|---|
| `Vanellye-patch-1` | `cf732a008b5642243ab5e4133a5ce882f6513dca` | 65 | `EDIFY.md`, `HEROES.md`, `hypotheticals/BRIDGE.md` present; detailed review pending |
| `build-speed` | `fbec48cff29207732b6a8d17511a9af84b84434e` | 47 | No branch-specific design document inspected; commit/CI review pending |
| `cognitive-layer-2` | `68d83bf0c8e4b3d38cdf189123f27f66336e57de` | 79 | `docs/cognitive-layer-2.md`, `python/cognitive_layer.py`, focused tests |
| `edify` | `82e92324383bbcd02e2a3a938e8d7e4dbff4d837` | 59 | `EDIFY.md` inspected; branch-local transformation policy retained as a proposal |
| `fiction-body` | `71ab22da2f04c2b58171e1bafe889cc524a0ed61` | 53 | Shared fiction bridge/README inventory; branch-specific narrative review pending |
| `fiction-creation` | `63d398d8ecad5e686b5570023c065f89e2918790` | 53 | Shared fiction bridge/README inventory; branch-specific narrative review pending |
| `fiction-mind` | `ef62753230622ccbe755e560b0c49b268b882127` | 53 | Shared fiction bridge/README inventory; branch-specific narrative review pending |
| `heroes-raw` | `6dbb03dc9f2b79d8d791a34b5964d7fd031dfa0c` | 61 | `HEROES.md` inspected; load-bearing zero inventory |
| `history` | `362c7192692d5c48bec1e7374287fb32d3552c6a` | 61 | `HISTORY.md` inspected; historical branch/commit claims recorded as source claims, not independently reconciled here |
| `hypotheticals` | `860fc3e26e147da1aa4ee38659676830ad0ec099` | 53 | `hypotheticals/BRIDGE.md` present; narrative and source review pending |
| `integration/channel-router-main` | `52da4ddc4a1230b9215afb9044eeb0d40fba8b9e` | 72 | `docs/channel-router-integration.md`, router and focused test inventory |
| `integration/git-freedom-router` | `e3bd5bccc9d6180cc685b1a5340549a526ad99f8` | 72 | `docs/GIT-FREEDOM-ROUTER-REVIEW.md` inspected; open risks recorded |
| `knowledge-recycle-foundation` | `4227381c9ebfab486d7773f8fdc7a82b0a0993fa` |  — | This catalog work branch; two new knowledge artifacts |
| `leveled-consciousness` | `d73a606ec2a8b5d060abb06da77e92a9294d201c` | 234 | `docs/RESONANCE-STEWARDSHIP.md` inspected; faith, metaphor, digital data, and physical evidence kept distinct |
| `main` | `67ecdb5c5bd148b6fd7c9945fa648f3c89a93a95` |  — | Current baseline; PR #16 merge and legacy quarantine verified |
| `main-11-of-38` | `9ed3ca42e3e9b8862f019bc4069e36d6aafc1380` | 60 | No distinct design document inspected; snapshot/ancestry review pending |
| `mold` | `11736208aa6c8288a59601da4cce2b841989ff9e` | 51 | No distinct design document inspected; transformation and build-impact review pending |
| `olpirt/stride-next` | `a8c6a90efc09e27afbead0f07191e17bf4faa431` | 232 | Temporal reconciliation, Holified Inception, consent, Geometry, Android/API profile and Pantheon inventory; selected docs reviewed |
| `pantheon/branch-horizon` | `7b3de5ecf47a64bd3039b97c6a920f5d6b6f41c7` | 73 | Branch Horizon, Warden Principle and focused tests inspected |
| `pantheon/cpp-html-consent-engine` | `a02629956deda7db4416cdbb1bc9b3c5badf90a0` | 66 | No distinct design document inspected in this pass; historical snapshot relationship documented elsewhere |
| `pantheon/divergence-adoption` | `bdb4c8dae89140743ec06e6f4ce48774b2617d2c` | 77 | Divergence adoption proposal, Warden Principle, and adoption-gate tests inspected |
| `pantheon/signed-package-exchange` | `ae89abe4a44d90429fcf5316bdb196316a1de6cb` | 67 | Signed package exchange specification inspected; explicitly a design specification, not an implementation |
| `pantheon/source-digest-engine` | `0226d6c75e7745dabbd51c77c499651815431ffb` | 76 | Source Digest specification, engine and focused tests inventoried |
| `repair/quarantine-legacy-python-syntax` | `5a1cc0bca432f1294eb6e33a870e508f42068f74` | 70 | Quarantine and provenance docs inspected; PR #16 subsequently merged |
| `review/legacy-syntax-quarantine` | `2e3fd32c786aafc137de0a4cd79178fd14506bc2` | 68 | Review note inventoried; stale draft remains distinct from merged PR #16 |
| `review/two-snapshot-synthesis` | `82635ceb38990a7e1078fbeef78e59e809125b4e` | 69 | Snapshot synthesis and provenance documents inspected |
| `zero-dissipation-anchor` | `232238bd6d3f4a91db3a3c0ec6c459cc74e6fee0` | 69 | Zero-Dissipation protocol and read-only audit baseline inspected |

Tree-entry counts above are from the branch trees retrieved in this pass. Dashes indicate that a tree count was not separately retained for the current knowledge branch and main. No inference should be drawn from the count.

## Cross-branch lessons supported by inspected artifacts

### Warden boundary

The Warden Principle says the Warden governs boundaries between existence, absence, and adoption; it owns no branch, tag, source, identity, or unclaimed state. Observation is not permission; absence is not consent; tags identify objects but do not authorize adoption. Ambiguous checks fail closed. This is policy text on Pantheon branches, not evidence that every workflow has implemented it.

### Branch Horizon

Branch Horizon is documented as a bounded, read-only observer. It compares exact branch heads and emits reviewable signals about ancestry, lexical interfaces, dependencies, tests, and provenance. Similar declarations are not proof of runtime compatibility; differing dependency specs are not proof of incompatibility. The documented observer does not mutate refs or authorize adoption. Its test file includes explicit no-mutation and peer-comparison tests.

### Divergence adoption

The adoption document describes an opt-in proposal restricted to specially named branches and an allowlist. It requires exact-SHA binding, staged validation, pull requests, GitHub auto-merge and existing repository protections. The document explicitly says adoption is not active until the workflow is merged into the default branch. This register does not claim the workflow is active or that any branch has been adopted.

### Signed package exchange

The package exchange artifact is a draft design specification. It separates publisher signature verification, policy checks, receiver review, explicit approval, staging, validation, and installation. A valid signature proves signer authenticity/integrity only; it is not safety certification or installation permission. No implementation is claimed by this record.

### Cognitive Layer 2

The cognitive layer document describes append-only evidence, provenance, temporal reconciliation, visible conflicts, and human review. Its tests exercise duplicate rejection, lineage, overlapping/unknown time ranges, and database-level update/delete rejection. These are branch-local implementation and test claims; cross-branch integration remains unverified.

### Channel router

The channel-router integration document describes local SQLite channels with separate publish/read grants, idempotency, explicit recipient acceptance, revocation, and append-only event/decision rows. It explicitly excludes network transport and action execution. The SQLite owner can still alter the database file/schema; do not call it tamper-proof.

### Git Freedom router

The router review identifies useful controls—no force-push path, fast-forward-only pull, feature-branch push target, dirty-tree rejection—and unresolved risks around vault cryptography, passphrase policy, branch-guard coverage, workspace overwrite behavior, token lifecycle, and device TLS. A compile is not device/runtime proof.

### Pantheon Source Digest

The source-digest specification describes a local-first, non-executing analyzer that reads only explicitly approved relative Python paths, parses ASTs without importing/executing source, writes metadata catalogs and SHA-256 provenance manifests, and refuses silent output replacement. This is a source specification and test inventory, not a claim of broad production validation.

### Zero-Dissipation protocol

The protocol distinguishes zero, false, empty, null, unknown, and deleted states. It calls for read-only detection first, evidence-backed minimal repairs, focused tests, rollback, and authorized branch-by-branch propagation. Its audit baseline itself says it is not a full per-branch content audit.

### Resonance Stewardship

The stewardship document separates human/spiritual meaning, digital information operations, and measured physical phenomena. Faith is honored as purpose, not software-certified revelation; digital frequency labels or simulations are not biological evidence. Personal data transfer requires explicit authorization and minimum necessary data. These distinctions should remain attached to related future knowledge entries.

### History and load-bearing zeros

The History branch contains a commit/branch narrative and says its merge commit connects histories. That statement is preserved as a claim in the source document; this pass has not independently verified the entire ancestry graph. HEROES documents a count of 79 load-bearing zeros with file/line explanations. A zero's meaning depends on context; changing it because it looks empty or symbolic is not a safe general transformation.

## What remains open

- Read each fiction branch's unique narrative/source artifacts and preserve the fiction label.
- Inspect build-speed and mold changes with before/after build evidence.
- Compare all branch tips and ancestry with bounded Git comparisons; do not infer mergeability from tree similarity.
- Verify the current workflow state and test evidence for each implementation branch.
- Inspect full source/test implementations for Pantheon engines before describing runtime guarantees.
- Reconcile the History branch's ancestry claim against the actual graph.
- Expand branch-specific lessons only when a distinct artifact or reproducible test supports them.

## Preservation commitment

This register is an index, not a merger. Each row remains bound to its branch head SHA. Future refreshes must append a new snapshot or update the register through a reviewed change while retaining prior snapshot identities. No branch is forced to merge, adopt another branch's policy, or conform to a shared internal architecture.
