# bđyt — Byte-Oriented Learning and Adaptation Language

**Method identifier:** `ÆŤ8Ð`
**Initial implementation:** Bash reference reviewer  
**Baseline:** `2cce68f258f46058f18c108c264db9cc85200590`
**Status:** Experimental; review-only reference implementation

## Purpose

bđyt is a proposed language for receiving source data, preserving its origin, constructing derivatives, and evaluating changes. Its first implementation is deliberately small: a deterministic byte-integrity and diff reviewer. It does not claim autonomous general intelligence, and it does not silently alter repository contents.

**Design rule:** Adopt verified inputs; adapt only in a bounded workspace; preserve the source; report every difference.

## Invented operator grammar

| Token | Meaning | Initial behavior |
|---|---|---|
| `ºŌº` | Origin identity | Identify the immutable source input |
| `*` | Adopt | Select a source without modifying it |
| `+` | Adapt | Describe or stage a derivative; never overwrite origin |
| `×` | Compose | Combine explicitly named inputs in a later language version |
| `÷` | Partition | Split data into independently identified components |
| `=` | Verify | Compare exact bytes or declared invariants |
| `<>` | Review | Produce a difference report |
| `/` | Route | Name a local destination; does not dispatch |
| `----` | Boundary | End the operation and emit a receipt |

Example notation:

```text
ºŌº SOURCE("original.bin")
  * ADOPT(read_only)
  + ADAPT("candidate.bin")
  <> REVIEW(source, candidate)
  = VERIFY(sha256, byte_count)
  / PROPOSE(local_target)
  ---- RECEIPT(no_mutation)
```

This is a language design notation, not yet a parser or executable DSL. The Bash reviewer implements only source/candidate validation, byte counts, SHA-256, equality detection, and a unified diff.

## ÆŤ8Ð — execution method

1. **Receive:** accept two explicitly supplied regular files.
2. **Validate:** reject missing files, symlinks, identical paths, missing utilities, and inputs larger than 10 MiB.
3. **Fingerprint:** calculate SHA-256 and byte counts for both inputs.
4. **Compare:** if bytes match, return `NO_OP`.
5. **Review:** if bytes differ, print a unified diff and return `PROPOSE_ONLY`.
6. **Receipt:** report that no input was modified and no external dispatch occurred.

Run from the repository root:

```bash
bash scripts/bdyt-reviewer.sh path/to/source path/to/candidate
```

Dependencies: Bash, `sha256sum`, `wc`, `cmp`, `diff`, and `awk`.

## Cost of Nothing

When source and candidate are byte-identical:

- no write;
- no delete;
- no commit;
- no dispatch;
- no adaptation;
- return `DECISION=NO_OP`.

This is a deliberate successful result, not an error.

## Background reviewer behavior

The reviewer is deterministic and read-only. It can be invoked by a developer or a separately configured scheduler. This commit does not install a daemon, create a schedule, invoke an AI service, or run unattended.

A future intelligence adapter may classify diffs or recommend transformations, but it must identify its model/version, disclose uncertainty, preserve the raw evidence, and emit proposals rather than silently applying changes.

## Authority and interference boundaries

This design removes a manual approval step from passive observation and reporting. It does **not** remove authorization from consequential operations.

- Read-only inspection and digest generation may be automatic.
- Candidate generation may occur in an isolated, bounded workspace.
- Source deletion, persistent repository mutation, permission changes, merges, external dispatch, and device/physical actuation remain separately gated.
- A trigger is not authorization.
- A digest proves byte identity only, not truth, quality, authorship, or permission.
- “Deleting interference” means filtering or excluding explicitly identified noise from a derived view; it never means deleting source records or hiding audit evidence.

## Verification limits

The reference reviewer is not a malware scanner, semantic verifier, AI model, compiler, or authorization service. It does not execute candidate files. It does not prove that a candidate is safe or correct. Review results must be interpreted within those limits.

## Provenance invariant

Original source bytes remain distinct from adapted bytes. All future transformations must record source digest, candidate digest, method version, and a return receipt. Historical evidence is append-only; corrections are additive.
