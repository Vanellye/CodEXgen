# BaseSpace Historical Canonical Index v0.1

Canonical host proposal: `Vanellye/CodEXgen`. Read-only consumers: `Vanellye/Ash` and `Vanellye/CodEXgen-2`.

## Files
- `schema/historical-record.schema.json` — JSON Schema Draft 2020-12.
- `registry/seed-records.json` — initial catalogue records covering Magna Carta reissues, Vatican archival institutions and Codex Vaticanus, ancient legal inscriptions, Galileo, and Babylonian astronomical records.
- `governance/access-policy.yaml` — ethical acquisition and access classification.
- `integration/vanellye-repository-contract.md` — read-only consumer contract.

## Integrity status
All seed entries are metadata-only. Their source-document SHA-256 fields remain null until exact source bytes are lawfully acquired. Never hash a URL as though it were the manuscript.

## Governance
Public catalogue discovery and metadata registration are automatic. Licensed or restricted contents require the appropriate terms or permission. Sealed contents remain unacquired until lawfully released or explicitly authorized. Original bytes are immutable; corrections and derivatives are append-only.

This branch is a review proposal. No changes are made to `main` and no pull request is merged automatically.
