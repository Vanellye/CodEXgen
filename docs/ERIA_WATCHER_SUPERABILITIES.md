# ERIA Watcher Superabilities — All-Remote-Refs Configuration

## Configuration state

The declarative configuration is stored at `config/eria_watcher.json`.

- Remote: `origin`
- Scope: all remote branches and tags
- Branch refspec: `+refs/heads/*:refs/remotes/origin/*`
- Tag refspec: `+refs/tags/*:refs/tags/*`
- Submodule recursion: disabled
- Pruning: disabled
- Polling interval target: 1,111 seconds
- Remote fetch: disabled
- Automatic acquisition: disabled
- PONS authorization: required for fetch, ref updates, and vault writes
- Default authorization decision: deny

This is a declarative configuration only. The current
`tools/eria_pantheon/data_vault.py watch` command still monitors local
`HEAD`; it does not implement remote fetch, all-ref enumeration, or ancestry
walking. Do not describe the expanded watcher as operational until those
capabilities are implemented and tested.

## Intended operating sequence

1. Verify the existing vault before any fetch or acquisition.
2. Obtain an explicit PONS grant scoped to remote `origin`, all branch and tag
   refspecs, the exact repository, and the permitted operation.
3. Fetch without pruning, merging, rebasing, pushing, deploying, or changing
   `main`. Fetch updates Git objects and remote-tracking refs; it is a Git
   metadata write and therefore requires the grant.
4. Enumerate fetched branch and tag targets, walk commit ancestry, and identify
   commits not already represented in the provenance manifest.
5. Capture each unseen commit from Git objects, retaining original bytes and
   separate commit/path lineage records.
6. Verify the manifest hash chain and every referenced object after each batch.
   On any error, stop in HOLD; do not silently advance the acquisition cursor.
7. Keep fetch and acquisition disabled if verification finds a missing
   manifest, a broken chain, a missing/mismatched object, or unexplained
   unreferenced objects.

## Preservation boundaries

- Never write, reset, force-update, merge into, or deploy `main`.
- Preserve all existing Git history and independent branch histories.
- Do not rewrite source bytes or overwrite original vault objects.
- Append provenance; derived indexes remain separate from source records.
- No uncommitted working-tree capture.
- No automatic network transmission beyond an explicitly PONS-authorized
  fetch from the configured remote.
- No submodule fetches, pruning, or tag deletion.
- Missing, expired, ambiguous, or mismatched PONS authorization means HOLD.

## Required implementation before activation

The current Data Vault writer has failed on Termux during temporary-object
creation/cleanup. The last device audit showed zero manifest records and
unreferenced object files. Its `VERIFIED` result only covered zero records and
is not evidence of a populated vault.

Before enabling any watcher:
- repair the Termux-compatible object writer and add tests for concurrent
  creation, interrupted writes, and cleanup;
- reconcile or quarantine unreferenced objects without deleting source data;
- capture the exact anchor and verify a non-empty manifest;
- implement the remote fetch/ancestry engine with PONS-gated Git writes;
- test all-ref discovery, tag/branch deduplication, retry behavior, and HOLD
  semantics in a disposable repository;
- prove `main` and source history remain unchanged.

## Current status

Configuration committed; execution disabled. The local watcher is not a
remote-fetch watcher. No fetch, automatic acquisition, merge, or deployment
was started by this configuration change.


## Preflight guardian and concurrent-creation protection

The watcher is intended to act as a visible guard before changes are made, not
merely report damage afterward.

Before any proposed creation, ref update, fetch-side ref mutation, or vault
write, the guardian should produce a preflight report showing:
- the exact target ref and whether it is protected;
- source and destination refs;
- expected old object ID and proposed new object ID;
- paths/objects to be created or changed;
- concurrent operations targeting the same ref, manifest, or object;
- conflicts, stale observations, and authorization scope.

### Main protection

Both `refs/heads/main` and `refs/remotes/origin/main` are protected targets.
The watcher must show a clear blocked-target warning before the operation and
deny the operation. There is no automatic fallback, retargeting, or retry
against `main`. Work belongs on feature branches or isolated review refs.

This is an application-level guard. It does not replace GitHub branch
protection or server-side rulesets, which must be independently configured.

### Concurrent creation

- Competing ref updates use expected-old-SHA compare-and-swap semantics. If
  the ref changes after preflight, abort and re-inspect; never force-update.
- Manifest appends are serialized under the vault lock and revalidate the
  chain head while holding the lock.
- Content-addressed object creation must be exclusive and idempotent. If two
  writers race for the same digest, verify the winner's bytes; mismatches
  enter HOLD.
- Duplicate commit/path records are idempotent. Conflicting provenance is
  retained as a conflict, not silently overwritten.
- Missing, stale, expired, or ambiguous PONS grants enter HOLD.

The configuration describes required behavior; it is not proof that runtime
interceptors or concurrency tests already exist. Remote fetching and automatic
acquisition remain disabled until the vault is repaired and the guardian is
implemented and tested.
