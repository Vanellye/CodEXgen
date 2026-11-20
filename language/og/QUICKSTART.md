# Ɣơ Local Quickstart

This guide assumes a checkout of `Vanellye/CodEXgen` on `feature/og-glyphic-language-spec`.

## 1. Checkout

```bash
git clone https://github.com/Vanellye/CodEXgen.git
cd CodEXgen
git fetch origin feature/og-glyphic-language-spec
git switch --track origin/feature/og-glyphic-language-spec
```

## 2. Inspect the language package

```bash
find language/og -maxdepth 3 -type f -print | sort
```

Start with:
- `README.md` for the package
- `GRAMMAR.md` for the current data envelope
- `GLYPH-ALPHABET.md` for the consonant-vowel map
- `ENCODING.md` for the reversible representation
- `../../docs/OG-LANGUAGE-SPEC.md` for the governing draft

## 3. Run tests

```bash
python3 -m unittest discover -s language/og/tests -v
```

The tests cover empty input, all 256 byte values, leading zero bytes, deterministic random round-trips, malformed input, unknown profiles, overflow, sample files and resource limits.

## 4. Encode a byte sequence

```bash
python3 language/og/reference/og_codec.py encode 0001ff
```

The output is an `OG/0` envelope. Every input byte is represented with four consonant-vowel syllables.

## 5. Decode an envelope

In Python:

```python
from pathlib import Path
from language.og.reference.og_codec import decode

source = Path("language/og/examples/zero-and-one.og")
original_bytes = decode(source.read_text(encoding="utf-8"))
print(original_bytes.hex())
```

Expected output for `zero-and-one.og` is `0001`.

## 6. Safety boundaries

The reference codec is deliberately pure: it does not write files, launch processes, access the network, or execute the bytes it encodes. It is not a compiler for arbitrary native source code.

Do not use it to replace Kotlin, C++, Python, or other repository sources. Such work needs a complete grammar/IR mapping, semantic-equivalence tests, independent review and its own scoped Runflow authorization.
