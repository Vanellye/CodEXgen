# Higher Faculty Code Translation — First Implementation

## Purpose

Add a deterministic, read-only first pass that turns recognizable source constructs into candidate English explanations. It is an extension alongside the existing Faculty Engine, not a replacement for it.

## Faculty flow

1. **Discovery:** scan source text line by line and recognize a bounded set of declarations and statements.
2. **Antithesis:** attach review flags for ambiguity and unsupported semantic assumptions. The first pass does not claim to resolve all contradictions.
3. **Verification:** retain source path, source revision, caller-supplied digest, exact line number, and source text for every finding. The implementation verifies input completeness and bounded size, not runtime behavior.
4. **Creation:** emit a candidate English explanation for each recognized construct. Each explanation is explicitly classified as INTERPRETATION.

## Contract

- Input is source text plus path, language, revision, and digest of the exact source bytes.
- Output is a list of line-anchored findings and review flags.
- Original bytes are never modified; the engine has no filesystem, process, network, Git, or database access.
- The engine does not compile or execute source.
- Unsupported constructs produce no invented explanation.
- A caller must compute and verify the digest against the original bytes before treating provenance as verified.
- Human review is required before any generated explanation is promoted into the code-to-English index.
- PONS remains HOLD by default. Translation does not authorize code changes or execution.

## Initial lexical coverage

Headers/imports, class/struct/interface declarations, likely function/method declarations, return statements, conditionals, loops, and recognizable SQL verbs.

## Known limitations

This is not a parser, compiler, control-flow analyzer, type checker, security scanner, or full natural-language semantic translator. Matching is intentionally conservative and may miss language-specific syntax. The confidence value is a heuristic ranking aid, not a calibrated probability.

## Next implementation stage

Add language-specific parsers or AST adapters one at a time, beginning with C++ and Kotlin. Keep the same provenance envelope and test each adapter against source fixtures. Then add antithesis checks for conflicting declarations and verification against compiler/test evidence.
