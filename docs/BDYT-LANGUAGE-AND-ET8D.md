# bđyt — Byte-Oriented Learning and Adaptation Language

**Method identifier:** `ÆŤ8Ð`  
**Executable reference:** Bash interpreter, `scripts/bdyt.sh`  
**Status:** Experimental; local text interpreter and read-only reviewer

## Purpose

bđyt is a small operator language for receiving source text, preserving its origin fingerprint, constructing named derivatives, comparing values, and routing reports. Its operators are executable statements interpreted by `scripts/bdyt.sh`; they are no longer merely descriptive notation.

**Design rule:** Adopt verified inputs; adapt into new values; preserve the origin; report every decision.

## Executable grammar (v0.1)

One statement per line. Identifiers match `[A-Za-z_][A-Za-z0-9_]*`. Quoted strings cannot contain a quote or escape sequence in v0.1. Blank lines and full-line comments beginning with `#` are ignored.

| Operator | Statement form | Executable behavior |
|---|---|---|
| `ºŌº` | `ºŌº ID "path/to/file"` | Load a readable regular text file, reject symlinks/NULs and inputs over 1 MiB, retain its path and SHA-256 origin fingerprint |
| `*` | `* ID` | Adopt an existing value as the active source |
| `+` | `+ NEW_ID ACTIVE_ID "suffix"` | Create a new derived value by appending literal text; source must have been adopted; never overwrite an existing value |
| `×` | `× NEW_ID LEFT_ID RIGHT_ID` | Compose two existing values, in order, into a new value |
| `÷` | `÷ LEFT_ID RIGHT_ID SOURCE_ID "delimiter"` | Partition a value at the first occurrence of a non-empty delimiter into two new values |
| `=` | `= LEFT_ID RIGHT_ID` | Compare two existing values and emit `VERIFY=TRUE` or `VERIFY=FALSE` |
| `<>` | `<> LEFT_ID RIGHT_ID` | Review two values and emit an identical/different finding |
| `/` | `/ ID` | Route a value to the local report stream (stdout only) |
| `----` | `----` | End the program and emit a completion receipt; later statements are rejected |

### Complete example

```text
ºŌº origin "examples/origin.txt"
* origin
+ adapted origin " — reviewed"
× combined origin adapted
÷ first second combined " — "
= origin origin
<> origin adapted
/ adapted
----
```

Run it from the repository root:

```bash
bash scripts/bdyt.sh examples/demo.bdyt
```

The interpreter requires Bash 4+ (associative arrays) and standard utilities `wc`, `tr`, `cat`, `sha256sum`, and `awk`. It does not use `eval`, execute source/candidate content, expand variables from the language, or invoke a shell command named by a program.

## Operator semantics and limits

- `ºŌº` fingerprints the original file before loading its text value. Original files are never written.
- Text values are held in Bash variables. Consequently, trailing newline bytes are stripped on load and NUL/binary data is rejected. SHA-256 and byte count still describe the original file, not the normalized in-memory value.
- `*` sets the active source. `+` requires that exact source to be active and always creates a new identifier.
- `×` concatenates without an implicit separator. Supply a separator as part of one input value if needed.
- `÷` splits only at the first delimiter occurrence; both result identifiers must be unused.
- `=` and `<>` report results; a false equality is a finding, not an interpreter crash.
- `/` writes only to the process's stdout. It is not a network route, webhook, device action, or external dispatch.
- `----` is mandatory and is the terminal statement.

## Smoke tests

Run:

```bash
bash scripts/test-bdyt.sh
```

The test exercises every operator, checks that the source file's SHA-256 remains unchanged, and confirms that an unknown identifier is rejected.

## ÆŤ8Ð reviewer and coiless report protocol

The separate byte reviewer remains available:

```bash
bash scripts/bdyt-reviewer.sh SOURCE_FILE CANDIDATE_FILE
```

It fingerprints both files, compares exact bytes, and emits a unified diff for differing inputs. The coiless report markers remain report metadata:

- `@§` — begin a structured report
- `*(§)*` — noteworthy marker, not permission
- `^&&&^` — coalesce findings while retaining their individual evidence
- `coiless` — one bounded invocation; no persistent loop, hidden worker, or recursive trigger

Proposed method identity: `ÆŤ8Ð-COILLESS-REPORT`.

## Authority and provenance boundaries

- Parsing and interpreting this v0.1 language is local and bounded.
- No source file is modified, no candidate is executed, and no commit is created by the interpreter.
- A route is a local report stream only. A trigger or parsed statement is never authorization for external dispatch.
- Persistent repository changes, deletion, permission changes, merges, network calls, and device/physical actuation require separate action-specific authorization and implementations.
- Digests prove byte identity only; they do not prove truth, quality, authorship, or permission.
- Original source evidence remains distinct from derived values. Future transformations must preserve source digests, method version, and receipts.

This is an executable v0.1 text DSL, not a general-purpose programming language, binary-safe data processor, security sandbox, compiler, or autonomous agent.
