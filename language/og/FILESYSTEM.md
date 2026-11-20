# Ɣơ Local Filesystem Contract

The package uses relative paths rooted at `language/og/`. Commands should be run from the repository root unless stated otherwise.

## Layout

```text
language/og/
├── README.md
├── GRAMMAR.md
├── GLYPH-ALPHABET.md
├── ENCODING.md
├── FILESYSTEM.md
├── COMPILER-ROADMAP.md
├── QUICKSTART.md
├── .gitignore
├── reference/
│   └── og_codec.py
├── tests/
│   └── test_og_codec.py
├── examples/
│   ├── README.md
│   ├── empty.og
│   ├── zero-and-one.og
│   └── sample-bytes.og
└── fixtures/
    ├── README.md
    └── byte-vectors.json
```

## Path rules

- Resolve package resources relative to the package directory, never the caller's current working directory.
- Do not write generated content into source directories.
- Keep generated artifacts under a dedicated build/output directory (future: `build/og/`).
- Treat `examples/` and `fixtures/` as immutable test inputs during ordinary codec runs.
- Do not follow symlinks outside the package root in any future build tool without explicit policy and validation.
- Preserve exact relative source paths in provenance records.
- Do not overwrite an existing file by default. Any future writer must be create-only unless a separate scoped authorization explicitly permits replacement.

## Local commands

From the repository root:

```bash
python3 -m unittest discover -s language/og/tests -v
python3 language/og/reference/og_codec.py encode 0001ff
python3 language/og/reference/og_codec.py decode OG/0:0001ff
```

## Relative document links

All support documents link relative to this directory. Repository-level governance documents are linked by relative paths from the spec file. Avoid machine-specific absolute paths in documentation and tests.
