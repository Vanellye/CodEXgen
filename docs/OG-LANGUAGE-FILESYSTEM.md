# Ɣơ Language — Repository Filesystem Map

**Status:** Draft package map for `feature/og-glyphic-language-spec`.
**Authority:** This is a navigation and storage contract. It does not grant write or execution authority.

## Package root

The canonical package root is `language/og/`, relative to the repository root.

```text
CodEXgen/
├── docs/
│   ├── ERIA-RUNFLOW-OPERATING-PROTOCOL.md
│   ├── CODE-ETHICS.md
│   ├── AEAA-CODE-REHABILITATION.md
│   ├── OG-LANGUAGE-SPEC.md
│   └── OG-LANGUAGE-FILESYSTEM.md
└── language/
    └── og/
        ├── README.md
        ├── GRAMMAR.md
        ├── GLYPH-ALPHABET.md
        ├── ENCODING.md
        ├── FILESYSTEM.md
        ├── COMPILER-ROADMAP.md
        ├── reference/
        │   └── og_codec.py
        ├── tests/
        │   └── test_og_codec.py
        ├── examples/
        │   ├── empty.og
        │   ├── zero-and-one.og
        │   └── sample-bytes.og
        └── fixtures/
            └── byte-vectors.json
```

## Relative support links

From `language/og/README.md`:
- Formal design: `../../docs/OG-LANGUAGE-SPEC.md`
- Runflow: `../../docs/ERIA-RUNFLOW-OPERATING-PROTOCOL.md`
- Ethics: `../../docs/CODE-ETHICS.md`
- Rehabilitation: `../../docs/AEAA-CODE-REHABILITATION.md`

From this document:
- Package implementation: `../language/og/`
- Main language draft: `OG-LANGUAGE-SPEC.md`

## Local path-resolution policy

1. Treat the repository root as the anchor for project-relative commands.
2. Resolve package resources from the source file's own location where possible.
3. Do not assume the process current working directory is the repository root.
4. Generated artifacts, when introduced, belong under `build/og/` or another explicitly configured output root.
5. Never let a generated output path overlap a source, test, fixture, or governance path.
6. Do not follow symlinks outside the package root by default.
7. A tool must not overwrite existing files unless an action-specific authorization explicitly permits replacement.
8. Keep source, generated output, tests, fixtures, and provenance records in separate directories.

## Local test commands

From the repository root:

```bash
python3 -m unittest discover -s language/og/tests -v
python3 language/og/reference/og_codec.py encode 0001ff
```

The standalone decoder accepts full `.og` envelope text through its Python API. The CLI's `OG/0:<hex>` shorthand is only a convenience for displaying a known byte sequence in hexadecimal; it is not a binary-to-source compiler.

## What is not created yet

No `build/` directory, virtual machine, parser for native languages, native-source migration, generated Android source, or automatic repository mutation is included in this package.
