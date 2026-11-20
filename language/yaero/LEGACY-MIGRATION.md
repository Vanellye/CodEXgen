# Ŷæṛö legacy-code migration pipeline

## Scope

The inventory covers C, C++, C+, and C+++ labels used by this repository, plus JavaScript. C+ and C+++ are not assumed to be standardized languages; each occurrence must be classified by its actual compiler, dialect, and build configuration.

## Staged pipeline

1. **Inventory:** identify files, build targets, compiler flags, generated files, vendored code, licenses, and ownership.
2. **Freeze source snapshot:** record commit, path, byte length, and SHA-256. Never overwrite the original.
3. **Parse:** use the correct frontend (for example, Clang tooling for supported C/C++ dialects and a JavaScript parser for the supported ECMAScript version).
4. **Normalize:** map syntax into Ŷæṛö atoms and typed IR while retaining source spans and unsupported-node diagnostics.
5. **Analyze:** build call, data-flow, dependency, and control-flow graphs on isolated copies.
6. **Generate candidate:** emit a patch or target-language module in a separate branch/artifact directory.
7. **Differential validation:** compile/run the original and candidate against the same fixtures, compare observable behavior, and test error paths.
8. **Review and promote:** independent review, provenance verification, and PONS authorization precede any repository write to protected branches.

## Reuse and recycling policy

Prefer semantic reuse of algorithms and interfaces over copying source text. Reimplement a component only when its behavior, license, dependencies, and test coverage are understood. Preserve attribution and license obligations. Do not delete or replace a native implementation merely because an IR representation exists.

## Acceptance gates

- No unexplained source hash changes.
- No missing or dropped syntax nodes without an explicit unsupported-feature diagnostic.
- Build and regression tests pass on all supported targets.
- Performance claims include reproducible baselines and hardware/runtime metadata.
- Equivalence claims are limited to tested behavior and defined preconditions.
