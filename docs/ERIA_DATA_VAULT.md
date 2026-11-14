# ERIA Data Vault — Commit-Anchored Acquisition

## Anchor

Initial provenance anchor requested for this vault:

`bf492e085efbf8c0bb7e594af8027817fa4a99a0`

The anchor is a full Git commit SHA. Acquisition reads Git tree/blob objects from
that exact commit, not the mutable working directory. A different commit creates
a separate set of provenance records. The original commit remains the authority
for what was acquired.

## Storage model

The default vault is outside the checkout:

`~/.eria/vault/`

- `objects/ab/cdef...`: original file bytes, addressed by SHA-256.
- `manifest.jsonl`: append-only acquisition records with commit SHA, Git blob
  SHA, repository-relative path, file mode, byte count, SHA-256, and a
  previous-record hash link.
- `wordplay/<commit>.json`: derived lexical index, separate from source bytes.
- `.manifest.lock`: local process lock for concurrent captures.

The manifest is tamper-evident through a hash chain, not a hardware-backed
immutable/WORM store. Back it up to independently controlled storage if stronger
retention guarantees are required. Never treat the wordplay index as source.

## Automatic acquisition habits

One-time capture of the requested anchor:

```sh
python -m tools.eria_pantheon.data_vault capture . \
  --anchor bf492e085efbf8c0bb7e594af8027817fa4a99a0
```

Continuously watch the currently checked-out repository's HEAD and capture each
newly observed commit (default interval 300 seconds; minimum 30 seconds):

```sh
python -m tools.eria_pantheon.data_vault watch . --interval 300
```

Stop the watcher with Ctrl-C. It is an explicit foreground process, not a hidden
daemon or scheduled task. Android may suspend or terminate background processes;
use Termux:Boot or an OS-level scheduler only after the operator chooses that
lifecycle. The watcher reads local Git objects and does not push, fetch, deploy,
or transmit data.

Verify stored objects and manifest links:

```sh
python -m tools.eria_pantheon.data_vault verify
```

Repeated captures of the same commit/path are idempotent. The watcher notices
new HEAD values; it does not silently capture uncommitted working-tree edits.

## Wordplay indexing

For eligible UTF-8 text files, ERIA derives:
- frequency-ranked terms;
- alliteration candidates grouped by initial character;
- repeated three-character word endings as rhyme-like candidates.

These are mechanical language patterns, not semantic interpretation, phonetic
rhyme verification, or authorship evidence. Binary files are stored as bytes but
not wordplay-indexed.

## Safety and limits

- Source checkout, Git refs, commits, and existing SQLite records are not edited.
- Secret-like paths, credentials, private keys, symlinks, submodules, and
  non-regular Git tree entries are skipped.
- Files larger than 5 MiB are skipped; acquisition is capped at 50,000 entries.
- Original file bytes are never normalized or rewritten.
- A repeated commit/path is not overwritten; conflicting object bytes cause
  HOLD.
- The vault is local-only. No remote storage provider or external account is
  configured by this module.
- The first capture and watcher must be run by the operator; no process is
  started automatically by importing the module or opening the ERIA UI.

## Provenance interpretation

A vault record establishes that a byte sequence was acquired from a specific
path and Git blob at a specific commit. It does not prove who authored the file,
whether the code is safe, or whether the content is true. Conflicting claims and
independent histories remain separate.
