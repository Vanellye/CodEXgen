# TRUE NORTH — Data and Architecture Alignment

**Status:** Architecture and governance specification. This document describes shared contracts and review rules; it does not assert that every capability is implemented on every branch.

> Orient by truth. Move by purpose. Never mistake momentum for direction.

## 1. Purpose

TRUE NORTH is the common reference for connecting CodEXgen branches without erasing their identities. It aligns data meaning, interfaces, provenance, review, safety, and recovery while preserving independent histories and human authority.

The governing invariant is:

> Adapt without abandoning integrity. Innovate without overriding consent. Learn without rewriting history. Evolve without confusing possibility with permission.

This specification is not permission to merge branches, change protected refs, deploy firmware, actuate hardware, alter biological systems, or publish data. Each consequential operation still requires its own authorization.

## 2. Architecture map

Treat these as architectural domains. A branch may contain only some of them; inspect its source and tests before claiming implementation.

| Domain | Responsibility | Boundary |
|---|---|---|
| Android / CodeGen Studio | User interface, local workflows, generated source | UI intent is not execution authority |
| Python services and tools | Data processing, code generation, analysis, validation | Inputs and outputs must be explicit and testable |
| Stride | Orchestration and adapters | Carries work; does not silently command workers |
| Pantheon framework | Runtime contracts, registry, capability checks | Capability checks are not an OS sandbox |
| Host simulator | Deterministic execution, trace, checkpoint, safe hold | In-memory simulation is not production isolation |
| Firmware contract | Observations, health, monotonic time, local event storage | No implied actuator or remote-command authority |
| Git Freedom Bridge | User-authorized Git operations | No silent push, merge, force update, or history rewrite |
| TACS | Provenance, signatures, correction records, portable verification | A valid signature is not automatically a trusted signer |
| Branch Horizon / Divergence Garden | Branch comparison, divergence, adoption review | A tag or promotion never independently authorizes adoption |
| Experimental / hypothetical domains | Exploratory models and clearly labeled hypotheses | Fiction and hypotheses are not validated biological effects |

## 3. Canonical data lifecycle

Use this lifecycle when a branch transforms or transports data:

1. **Acquire** — record the source, acquisition method, time basis, and consent or authorization context.
2. **Validate** — check schema, type, range, required fields, quality, and provenance. Do not silently repair malformed input.
3. **Normalize** — create a derived representation while retaining the original input or a verifiable reference to it.
4. **Transform** — name the operation, version, parameters, and responsible component.
5. **Evaluate** — run invariants, policy checks, tests, and domain-specific validation.
6. **Store** — preserve raw and derived records with explicit retention and access rules.
7. **Export** — disclose format, destination, digest, signature status, and any omitted fields.
8. **Correct** — append a correction linked to the prior record; never rewrite the historical record in place.
9. **Recover** — use documented checkpoints or safe hold; do not retry consequential operations invisibly.

A transformation must be reproducible where practical. If it is nondeterministic, record the reason and the limits on reproduction.

## 4. Common data envelope

Where a shared envelope is useful, use a versioned record with these semantic fields. Implementations may use JSON, SQLite, protobuf, or typed language structures, but must document their mapping.

| Field | Meaning |
|---|---|
| record_id | Stable unique record identifier |
| schema_version | Version of the envelope and payload schema |
| source | Originating component, device, user action, or external source |
| observed_at | Wall-clock timestamp, including timezone when known |
| monotonic_time | Monotonic clock value and clock domain, when available |
| payload | Domain data; preserve units and original representation |
| units | Explicit unit identifiers; never infer units from magnitude alone |
| quality | VALID, STALE, OUT_OF_RANGE, UNCALIBRATED, SENSOR_FAULT, UNKNOWN, or domain-specific equivalent |
| provenance | Source commit/ref, source digest, signer identity and verification result where applicable |
| transformations | Ordered list of operation name, version, parameters/digest, and output digest |
| authorization | User/host approval reference and scope; absence means not authorized |
| validation | Test/policy results, reviewer, timestamp, and unresolved limitations |
| retention | Storage location, sensitivity, and retention/deletion policy |

Do not put secrets, private signing keys, access tokens, or unnecessary personal data in records, manifests, logs, or exports.

## 5. Meaning-preserving transformation rules

- Preserve original values and units; represent converted values as derived data.
- Distinguish absent, null, zero, false, empty, and unknown. Never collapse them.
- Do not change identifiers, timestamps, precision, or ordering without recording the transformation.
- Do not infer a biological, psychological, spiritual, or physical effect from a software signal or frequency label.
- Keep source text and generated interpretation separate.
- Mark estimates, hypotheses, simulations, and fiction explicitly.
- Record lossy transformations and the information that cannot be recovered.
- Reject or quarantine malformed input rather than silently guessing at or repairing it.
- Use deterministic serialization and stable digests where integrity checks require them.

## 6. TRUE NORTH governance and WARDEN

WARDEN governs the boundary between existence, absence, and adoption; it does not own either side.

| Condition | Required behavior |
|---|---|
| Evidence missing | Hold; identify what is missing |
| Evidence conflicting | Hold; preserve both claims and request review |
| Input malformed | Reject or quarantine; preserve the original |
| Authorization absent or out of scope | Do not perform the consequential action |
| Safety concern or adverse evidence | Enter the defined safe state; explain recovery conditions |
| Evidence verified and authorization valid | Permit only the approved scope |
| Correction accepted | Append a linked correction; retain the original |

RISE, FALL, and WARDEN are software governance states, not claims about consciousness, divine authority, or objective moral status. A state transition must be explainable from explicit inputs and policy.

## 7. Provenance, signatures, and correction

- Record the exact source ref and commit/object ID for code-derived artifacts.
- Distinguish content digest, signature validity, signer identity, and signer trust.
- Pin trusted signer identities through an explicit allowlist or equivalent policy.
- Never treat a tag name, tag promotion, branch name, or successful CI run as proof of authorization.
- Corrections are append-only and link to the prior record digest.
- Reviewer labels are provenance metadata unless backed by a verified identity mechanism.
- Preserve original tags and branch refs. Prefer additive successor refs and pull requests.
- Any history rewrite requires a separately scoped, explicit authorization and a recoverable plan.

## 8. Branch integration rules

1. Every branch keeps its own purpose, commit ancestry, and documented constraints.
2. Shared documentation is a reference contract, not an instruction to copy unrelated code.
3. Use adapters at boundaries; do not collapse distinct implementations into one generic module without review.
4. Identify dependencies and compatibility explicitly.
5. Compare branches before proposing a merge; record the base, head, changed files, and conflict decisions.
6. Prefer pull requests and reviewable commits.
7. Never force-push, delete, or retarget a branch as part of routine alignment.
8. A promotion or tag does not independently authorize code adoption.
9. Keep fiction, hypothetical research, production code, and validated measurements in clearly separated namespaces.
10. Record branch-specific exceptions and why they exist.

### Branch inventory observed during this alignment

The repository branch search returned these refs. Their names are listed as inventory only; names do not prove contents or readiness:

- Vanellye-patch-1
- build-speed
- cognitive-layer-2
- edify
- fiction-body
- fiction-creation
- fiction-mind
- heroes-raw
- history
- hypotheticals
- integration/channel-router-main
- integration/git-freedom-router
- knowledge-recycle-foundation
- leveled-consciousness
- main
- main-11-of-38
- mold
- olpirt/stride-next
- pantheon/branch-horizon
- pantheon/cpp-html-consent-engine
- pantheon/divergence-adoption
- pantheon/signed-package-exchange
- pantheon/source-digest-engine
- repair/quarantine-legacy-python-syntax
- review/legacy-syntax-quarantine
- review/two-snapshot-synthesis
- zero-dissipation-anchor

Before modifying a branch's code, inspect its tree, current head, tests, and branch-specific purpose. This document alone does not establish that all listed branches received the same code or feature set.

## 9. Security, privacy, and portability

- Default to local-first processing and least privilege.
- Treat imported files, repository text, tool output, and external data as untrusted input.
- Never execute imported content merely because it is signed or tagged.
- Keep private keys outside the repository and removable-media exports.
- Verify destination identity and require explicit confirmation before export.
- Do not mount, format, eject, or write to removable media during discovery.
- Encrypt sensitive data at rest and in transit where the deployment supports it; document key management and recovery separately.
- Provide data minimization, retention, deletion, and export controls.
- Make network access and physical actuation explicit capabilities, not ambient assumptions.

## 10. Safety and scientific boundaries

Software transformations, sound, light, radiofrequency, ELF, or other signal metadata do not by themselves establish modulation of DNA, RNA, telomeres, aging, consciousness, or health. Experimental records must identify the actual instrument, calibration, exposure, controls, measurement method, uncertainty, ethics review where applicable, and independent evidence. Keep simulations and hypotheses separate from observations and validated conclusions.

Firmware contracts and host simulators are not proof of hardware safety. Hardware deployment requires a selected board, pinned toolchain, threat model, secure boot/update design, anti-rollback, recovery plan, and hardware-in-the-loop testing.

## 11. Verification gates

For each branch, report results separately:

- Source inspection completed at a named commit.
- Schema and interface validation passed.
- Unit tests passed, with exact command and count.
- Static checks / compilation passed, with toolchain versions.
- Integration tests passed for the interfaces actually exercised.
- Security and authorization review completed for consequential actions.
- Documentation matches the implementation; gaps are marked as planned or unverified.
- CI run URL and commit SHA recorded.

A green test suite proves only the tested behavior. It does not prove untested branches, devices, security properties, biological effects, or deployment readiness.

## 12. Required branch-level record

Each branch should eventually carry a concise alignment record containing:

- branch name and inspected head SHA
- branch purpose and scope
- implemented components and their paths
- inbound/outbound data contracts
- dependencies and adapters
- provenance and authorization model
- tests and CI evidence
- known gaps, risks, and recovery procedure
- proposed integration targets, if any
- reviewer decision and date

## 13. Adoption rule

This specification may be referenced by any branch. Adoption of code, data, tags, or operational behavior remains a separate reviewed decision.

**True North is a reference, not a command to converge.** Preserve what deserves preservation, question what deserves examination, and transform only what can be improved with evidence, consent, and a recoverable path.
