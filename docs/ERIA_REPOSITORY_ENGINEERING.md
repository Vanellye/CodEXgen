# ERIA Repository Engineering Orchestrator

## Scope

The `repository.review` command and `python -m tools.eria_pantheon.repository_engine <repo>` run a bounded repository-wide pass over the checked-out Git worktree:

1. **Acquire:** enumerate eligible files, calculate SHA-256, capture exact branch/commit/dirty state, identify manifests and test candidates, and omit sensitive paths and oversized files.
2. **Quality analysis:** report test/workflow coverage and evidence gaps. Findings are classified as facts or unknowns; the inventory is not a security verdict.
3. **Execution planning:** discover candidate test/build commands from repository metadata.
4. **Synthesis:** combine the revision, inventory, findings, and proposed next steps without changing source authority.

## Execution boundary

The orchestrator deliberately does not execute discovered project code. Pytest tests, Gradle build logic, Make targets, package hooks, and build scripts can execute arbitrary code. Candidate commands are returned with execution_state=HOLD until a separate isolated runner is provisioned and the exact command set is explicitly approved.

A future runner must use an ephemeral workspace, no inherited secrets, no source-checkout write access, network disabled by default, resource/time limits, captured output, exact commit pinning, and an auditable approval record. A passing test suite does not authorize source writes, deployment, publication, or transmission.

## Limits

- Inventory caps: 20,000 files and 5 MiB per file; common generated/vendor/cache directories are excluded.
- Credential-like paths are skipped; source text is not copied into the inventory.
- Credential-like literal detection records only a review flag, never the matched value.
- Dependency discovery is manifest-level; no package installation or network acquisition occurs.
- This pass does not replace Æị format translation, Âï source analysis, ÆĀÄÂ review, language-specific tests, or human security review.
- Results are NON_AUTHORITATIVE; original bytes and Git history remain unchanged.

## Termux

From the repository root:

    python -m tools.eria_pantheon.repository_engine . > eria-repository-review.json

The JSON report is a derived artifact. Review it before sharing or committing; do not place it in the source database as if it were original evidence.
