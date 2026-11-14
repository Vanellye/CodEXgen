# AÐð Fïl·lĕŕ — Rightous Companioxn Protocol

**Status:** governance contract for the FILLER structure-completion utility  
**Scope:** repository-local planning and explicitly mapped scaffolding  
**Initial implementation branch:** `feature/ashes-to-angels-pheonix`

## Purpose

FILLER identifies missing repository structures and helps complete them from reviewed
templates. The **Rightous Companioxn** principle means that completion serves the
existing source and its maintainers; it does not claim ownership of the source, infer
consent, or elevate its own authority.

## Companion commitments

1. **Source remains distinct.** Original files, authorship, commit history, and branch
   identity remain intact. Generated files are derivatives, never retroactive originals.
2. **Evidence before assertion.** A missing path is a verifiable observation. Its
   intended contents are not known unless a reviewed template or specification supplies
   them. Unknown requirements remain explicitly unknown.
3. **Proposal before mutation.** Planning is the default. A mapping must name both the
   exact destination and the exact source template.
4. **No overwrite.** Existing files and symlinks are preserved. FILLER creates only
   destinations that do not exist at the time of the write.
5. **Human authorization.** Apply requires an explicit approval token bound to the
   configured feature branch. Approval does not authorize a merge, push, deployment,
   permission change, or external transmission.
6. **Least authority.** FILLER has no self-granting privileges, no credentials
   management, no hidden execution, and no automatic external dispatch.
7. **Traceable derivatives.** Each created file records its source template, SHA-256
   digest, destination, and branch in an append-only local ledger.
8. **Validation before connection.** Generated structures remain inert scaffolding
   until reviewed, tested, and separately connected to a runtime by an authorized
   maintainer.
9. **Recoverability.** Changes must be reviewable through version control and reversible
   by ordinary, human-directed repository operations. FILLER itself never deletes.
10. **Honest reporting.** Planned, created, preserved, and blocked paths are reported
    separately. A successful scaffold operation is not represented as a successful
    application build or runtime integration.

## Up / Down module contract

- **UP:** inspect parent declarations and identify required child structures. UP may
  propose mappings; it cannot silently propagate content or widen permissions.
- **DOWN:** return child-module findings, missing dependencies, and validation outcomes
  to the parent as evidence. DOWN cannot rewrite parent source automatically.
- **L·L bridge:** carries structured proposals and results between UP and DOWN. It is
  provider-neutral and does not itself authorize writes.
- **Reconciliation:** conflicts are surfaced for human resolution. The original source
  and the generated derivative remain separately identifiable.

## Execution contract

From the repository root:

```bash
# Read-only plan; no repository files are created.
bash tools/filler/filler.sh --plan

# Explicitly approved creation on the named feature branch only.
bash tools/filler/filler.sh --apply --approve feature/ashes-to-angels-pheonix
```

The manifest at `tools/filler/filler.manifest` is intentionally empty until individual
mappings have been reviewed. Each mapping is tab-separated:

```text
destination/path<TAB>reviewed/template/path
```

The utility rejects path traversal, missing or symlink templates, existing targets,
unknown arguments, and apply attempts from another branch. It does not infer application
logic or fabricate missing module behavior.

## Non-goals

FILLER is not an autonomous agent, authorization bypass, hidden actuator, code
obfuscator, deployment system, branch promoter, or substitute for tests and review.
Detection of a trigger, missing file, or structural difference is never permission to
perform an unrelated action.

## Current implementation boundary

The first implementation provides a read-only planner and an explicitly gated,
template-only file creator. It does not yet implement recursive architecture discovery,
automatic dependency resolution, UP/DOWN runtime messaging, or build/test execution.
Those capabilities require separate specifications, tests, and review.
