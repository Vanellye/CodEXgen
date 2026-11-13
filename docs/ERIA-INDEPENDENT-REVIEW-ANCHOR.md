# ERIA independent review anchor

## Immutable source baseline

- Repository: `Vanellye/CodEXgen`
- Baseline commit: `2cce68f258f46058f18c108c264db9cc85200590`
- Baseline role: source snapshot against which the ERIA observation-engine work is compared.
- Baseline branch: `main` at the time this work was split.
- The SHA above is a fixed provenance anchor. It is not a moving branch name and must not be replaced by a later feature-branch head.

## Review lineage

| Stage | Branch / pull request | Relationship |
|---|---|---|
| Source baseline | `main` at `2cce68f258f46058f18c108c264db9cc85200590` | Immutable comparison anchor |
| Observation engine | `eria/elixir-observation-engine`, PR #48 | Draft proposal based on the source baseline |
| Format adapters | `eria/multiomics-format-adapters`, PR #49 | Draft child proposal based on PR #48 |
| BAM/CRAM execution | Separate next gate | Must be independently implemented and reviewed; not implied by PR #49 |

PR #49 is based on PR #48, not directly on `main`. Its changes do not alter PR #48 or `main` unless separately adopted through reviewed merges.

## Current adapter boundary

The format-adapter stage provides bounded FASTQ, VCF, and SAM structural readers. The SAM module can describe a BAM/CRAM conversion command as an argv list, but the current adapter stage does not execute that command. A plan is not evidence that conversion occurred.

The next conversion gate is to add an explicit file-ingestion operation that:
- invokes an installed `samtools` executable using argument-vector execution, never a shell command string;
- requires an explicit reference path for CRAM;
- validates input and output paths and bounds the conversion output;
- records tool identity/version, arguments, exit status, output digest, and source digest;
- rejects failed, empty, oversized, or malformed output and cleans up temporary files;
- is tested with deterministic fixtures and an integration test against a declared `samtools` version.

Automatic conversion means that an explicitly invoked BAM/CRAM ingestion operation performs the conversion as part of that operation. It does not mean a background watcher, hidden process, or conversion triggered merely by file presence.

## Independent workstreams

Instrument connectivity, vendor SDK integration, calibration registries, calibration verification, and device acquisition remain separate workstreams. Neither parser acceptance nor a conversion success certifies an instrument or its calibration.

Pantheon Integration Core (IC) contracts and transmission integration also remain separately reviewable. A green CI job for a source branch does not establish end-to-end transmission or physical-device behavior.

## Review and adoption requirements

1. Verify the immutable baseline SHA and compare every proposal against it.
2. Review source-format parsing, resource bounds, error handling, and provenance independently.
3. Review BAM/CRAM process execution as a separate security and reliability boundary.
4. Verify tests and CI on the exact proposed head SHA.
5. Keep research observations distinct from inferences; no clinical diagnosis or biological intervention authorization is produced.
6. Require human review and explicit approval before adopting any PR into its base branch.
7. Preserve branch identities, commit history, source digests, and reversible adoption paths.

## Current status at anchor creation

- PR #48: open, draft, not merged.
- PR #49: open, draft, not merged.
- `main`: no changes made by this review-anchor task.
- The CI run previously associated with PR #49 head `4c186a85e5c4e51f21ad2faf09e74bc6ec192006` failed at Elixir compilation due to a malformed duplicate fallback clause in `sam.ex`. The correction is isolated on the PR #49 branch and requires a fresh CI result.
