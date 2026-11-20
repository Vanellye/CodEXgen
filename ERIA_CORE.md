# ERIA Core Branch

This branch is the proposed shared integration line for ERIA infrastructure.

## Repository roles

- `Vanellye/CodEXgen`: canonical ERIA application, Pantheon contracts, and Android runtime.
- `Vanellye/CodEXgen-2`: secondary integration and compatibility surface.
- `Vanellye/Ash`: governance and shared boundary integration.

## Continuous Forge

`.github/workflows/eria-continuous-forge.yml` runs on pushes, pull requests, manual dispatch, and an hourly schedule. It performs source-integrity checks, isolated storage-boundary tests, Pantheon contract tests where present, Android validation where present, and Python syntax validation.

The forge is read-only. It does not deploy, publish artifacts, merge pull requests, change repository settings, execute untrusted payloads, dispatch external actions, or activate hardware.

## Branch and governance rules

- Preserve `main` and all existing refs and commit history.
- `core` is created from the current `main` commit as a candidate canonical branch.
- Changing a repository's default branch is a separate repository-settings operation and must be confirmed in GitHub after the branch is reviewed.
- New infrastructure remains reviewable through a pull request; no automatic merge is enabled.
- Human authorization, provenance, and append-only audit records remain required at action boundaries.
