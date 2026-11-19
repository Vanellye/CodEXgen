# Ɣơ (Yoro) — Safety and Limitations

**Version:** 0.1  
**Status:** Draft

## 1. Encoding is not execution

Ɣơ version 0.1 is a reversible byte notation. Encoding bytes does not validate, sanitize, compile, or make their contents safe. Decoding returns data; it MUST NOT execute that data.

## 2. Preserve originals

- Keep original source files unchanged.
- Write encoded output to a separate destination.
- Do not overwrite source files during experiments.
- Record the source hash, encoding version, and tool version when provenance matters.

## 3. Zero values and losslessness

Zero bytes are meaningful data. A conforming reversible encoding preserves zero bytes, leading zero bytes, length, and order.

Any experimental operation that drops zero bits or maps multiple input values to the same glyph is lossy and is NOT part of the version 0.1 reversible profile. Such an experiment must use a separately named and versioned profile and must never be presented as a recoverable backup.

## 4. Untrusted payloads

Treat decoded content as untrusted input. Do not pass it to a shell, interpreter, compiler, dynamic loader, or other execution facility merely because it has been decoded successfully.

## 5. Validation

Implementations should:
- Enforce documented size limits.
- Reject invalid glyphs, malformed lengths, duplicate fields, and unsupported versions.
- Avoid silently repairing malformed input.
- Test empty input, all 256 byte values, leading zeros, truncation, and extra tokens.

## 6. Scope boundary

This document does not authorize native-code replacement, repository-wide rewrites, privileged execution, or changes to protected branches. Those require separate design, testing, review, and authorization.
