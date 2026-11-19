# Ɣơ / .og — ERIA Glyphic Language Specification (Draft)

**Status:** DRAFT — proposal only; no executable compiler or runtime is implied.
**Branch:** `feature/og-glyphic-language-spec`
**Authority:** Subordinate to `docs/ERIA-RUNFLOW-OPERATING-PROTOCOL.md` and `docs/CODE-ETHICS.md`.
**Purpose:** Define a reversible, testable intermediate language for representing program data and, in later stages, program semantics.

## 1. Design intent

Ɣơ (working name: Gamma-O) is a symbolic language layer with `.og` as its proposed source extension. It is not a replacement for machine code, an instruction set, or a native runtime. The first implementation target is a deterministic encoder/decoder for typed values and byte sequences. A later compiler may translate a restricted source-language subset into an intermediate representation (IR), then into verified target code.

The language must preserve meaning, provenance, and recoverability. A representation that loses information is not a valid compiler transformation.

## 2. Non-negotiable invariants

1. **Losslessness:** For every supported input, decoding an encoded value reproduces the original bytes or typed value exactly.
2. **Zero preservation:** Zero is data. No pass may delete, replace, or infer away zero without a formally specified reversible encoding.
3. **Semantic preservation:** Compiler optimizations must preserve observable behavior for the declared language subset.
4. **Provenance:** Every generated artifact records source identity, source digest, tool/version, options, and output digest.
5. **Fail closed:** Unknown syntax, unsupported types, overflow, malformed encodings, and failed checks are errors—not guessed values.
6. **Separation of concerns:** Parsing, normalization, encoding, optimization, verification, and code generation are separate passes.
7. **No implicit execution:** Parsing, compiling, validating, or generating code does not execute the result.
8. **Authorization:** Any repository write, privileged command, deployment, external dispatch, or runtime execution requires separate action-specific authorization under Runflow and Code Ethics.
9. **No self-approval:** The compiler, its tests, and an agent that proposes a transformation cannot approve its own adoption.

## 3. Conceptual pipeline

```text
source bytes
  -> source parser (language-specific)
  -> typed syntax / semantic IR
  -> canonical numeric and byte representation
  -> glyph encoder (.og)
  -> decoder round-trip verification
  -> optional semantics-preserving optimization
  -> target IR / backend
  -> target artifact + provenance manifest
```

For the initial milestone, only the byte/numeric representation and round-trip verification are in scope. Source-language parsing and native-code replacement are explicitly out of scope.

## 4. Typed values

The first version defines these distinct value kinds:

- `U8`, `U16`, `U32`, `U64`: unsigned fixed-width integers.
- `I8`, `I16`, `I32`, `I64`: signed fixed-width integers using a specified two's-complement byte representation.
- `F32`, `F64`: IEEE-754 bit-preserving floating-point payloads; NaN payloads and signed zero must survive round trips.
- `BYTES`: arbitrary byte sequence; no text assumption.
- `UTF8`: validated UTF-8 text, distinct from arbitrary bytes.
- `TEXT`: future Unicode text profile with normalization explicitly declared; not part of v0.
- `BOOL`: exactly one of false or true.
- `NULL`: explicit absence, distinct from numeric zero and empty values.

Values carry a type tag, length, and payload. Length is explicit. Empty payload and zero-valued payload are not interchangeable.

## 5. Numeric normalization

Numeric normalization is canonicalization, not a change in mathematical value or source semantics.

- Decimal text is parsed with an explicit numeric type and range.
- Fixed-width integers are range-checked; overflow is rejected.
- Integer zero remains zero.
- Leading zeroes in a textual literal are preserved in source metadata when lexical fidelity is required.
- Negative numbers retain sign and declared width.
- Floating-point values are handled by bit pattern when exact round-trip is required.
- No generic "positive number" substitution is permitted. Replacing a negative or zero value with a positive value changes program behavior.
- Algebraic rewrites require proof or exhaustive/property-based tests over the defined input domain.

## 6. Reversible base-5 glyph profile (proposal)

The initial alphabet uses the five lowercase vowels as base-5 digits:

| Digit | Glyph |
|---:|:---|
| 0 | `a` |
| 1 | `e` |
| 2 | `i` |
| 3 | `o` |
| 4 | `u` |

A canonical base-5 integer representation contains no leading `a`, except that numeric zero is represented by the single glyph `a`. This profile encodes unsigned integer values only; typed byte values include a length and preserve leading zero bytes.

A second, readable consonant-vowel syllable layer may map each base-5 digit to a pair (e.g. `ba`, `be`, `bi`, `bo`, `bu`). The mapping table is versioned and fixed per profile. This phonetic spelling is a display/serialization convention; it does not alter the underlying value.

Reserved markers for future grammar (not assigned executable semantics in v0): `ñ` namespace, `Ɣ` operator/profile marker, `r` run-length field, `z` explicit zero-run marker. Implementations must reject unknown markers unless an extension is declared.

### 6.1 Zero-run compression

Byte sequences may use a length-delimited run-length encoding. For example, an explicit token can mean "repeat byte 0 exactly N times." The run count is encoded independently and must be range-checked. The decoder expands the run exactly. This is lossless compression; it is not deletion or substitution of zero bits.

Compression is optional and must be retained only when the encoded output is smaller or offers a documented transport benefit.

## 7. Suggested textual envelope

Illustrative, non-executable syntax:

```text
OG/0
kind:U8
length:1
payload:ba
source-sha256:<64 lowercase hex digits>
encoder:og-reference/0.1
```

The exact grammar, escaping, canonical byte order, and checksum coverage must be fixed in a machine-readable schema before release.

## 8. Compiler stages and proof obligations

### Stage A — byte codec
- Encode arbitrary byte arrays to a canonical textual representation.
- Decode representation to the exact original bytes.
- Reject malformed lengths, unknown profile versions, invalid glyphs, and truncated input.
- Test empty arrays, all 256 byte values, zero-heavy arrays, random arrays, and large inputs.

### Stage B — typed numeric codec
- Implement the integer and floating-point profiles.
- Test min/max values, overflow, negative values, zero, signed zero, infinities, and NaN payload preservation.
- State whether equality is byte equality or numeric equality for each type.

### Stage C — parser and typed IR
- Begin with a deliberately small grammar.
- Keep identifiers, strings, numbers, operators, and comments distinct.
- Preserve source spans and original source digest.
- Do not parse-and-rewrite arbitrary Kotlin, C++, Python, or shell code in this stage.

### Stage D — verified optimization
- Each optimization has a named rule, preconditions, affected IR nodes, and a proof or test strategy.
- Differential tests compare baseline and optimized interpreters/backends on the supported domain.
- Undefined or implementation-dependent behavior blocks optimization.
- Keep the unoptimized IR and transformation log for audit and recovery.

### Stage E — backend
- Generate one target at a time.
- Compare output behavior against the source on test fixtures.
- Sign or hash build outputs and bind them to pinned inputs.
- Execution and deployment remain outside the compiler and separately authorized.

## 9. Canonical language example (illustrative only)

```text
Ɣơ/0
value count : U8 = ba
value enabled : BOOL = true
value payload : BYTES = [00, 00, 7F]
```

Here `be` is the base-5 digit pair for decimal one in the syllable layer. A complete byte value uses four syllables: decimal one is `ba-ba-ba-be`. The byte array explicitly retains its two leading zero bytes.

## 10. Rejected transformations

The following are invalid:
- dropping zero bits or bytes without a reversible length-delimited representation;
- replacing zero, negative, null, empty, or false with a positive value;
- changing integer width or signedness without a typed conversion;
- assuming a consonant/vowel spelling has the same semantics without a declared table;
- optimizing across side effects, exceptions, concurrency, I/O, or undefined behavior without a valid proof;
- compiling unsupported source constructs by guessing;
- executing generated output as part of validation.

## 11. Interoperability and migration

Existing Kotlin/Gradle Android sources remain the application source of truth. Ɣơ initially lives beside them as a specification and independent codec prototype. A future adapter may call the codec from Kotlin, but the codec must not rewrite application files. Generated artifacts are placed in a dedicated, reviewable output directory and never overwrite source files.

Migration is incremental:
1. Specify the encoding and test vectors.
2. Implement a standalone reference codec.
3. Add round-trip and property-based tests.
4. Review the implementation independently.
5. Integrate a read-only preview into ERIA.
6. Select one low-risk module for an opt-in translation experiment.
7. Compare behavior and performance; keep or reject the experiment based on evidence.
8. Consider additional modules only through separate Runflow tasks and approvals.

No "replace all native code" operation is defined by this specification.

## 12. Runflow record

For each implementation task, record:
- origin repository and exact source ref/SHA;
- stated intent, scope, and immutable paths;
- requested codec/profile version;
- explicit authorization for the exact write or execution action;
- generated artifacts and digests;
- tests run and observed results;
- independent review and recovery plan;
- final state: DRAFT, READY, AUTHORIZED, RUNNING, BLOCKED, UNRESOLVED, REVIEW, RECOVERY-REQUIRED, RECOVERED, COMPLETE, or LEARNED.

## 13. Current limitations

This document is a draft design. It does not provide a complete language grammar, parser, optimizer, compiler, runtime, cryptographic signing scheme, or verified backend. The proposed glyph choices and `.og` extension are provisional until implemented and tested. No performance or security benefit is claimed.
