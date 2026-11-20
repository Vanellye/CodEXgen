# Ŷæṛö (formerly Ɣơ / Yoro)

Ŷæṛö is the canonical name for the symbolic language and its source-preserving analysis toolchain. Earlier Ɣơ and Yoro profiles remain historical format identifiers and compatibility aliases; they are not silently rewritten.

## Design commitments

1. **Preserve source:** C, C++, C+, C+++ (where that label refers to project-specific dialects or code) and JavaScript inputs remain immutable originals.
2. **Derive, don't overwrite:** parsers produce provenance-linked syntax trees and a typed intermediate representation (IR) in separate output locations.
3. **Atomic semantics:** an atom is the smallest typed, immutable semantic unit in the IR. An atomic transformation is a validated all-or-nothing change to a derived artifact, never an in-place rewrite of source.
4. **Cross-platform parity:** Kotlin/JVM, JavaScript, and Python adapters consume identical byte vectors and canonical IR fixtures.
5. **Evidence before claims:** no semantic equivalence, speedup, or quantum advantage is claimed without differential tests and measured benchmarks.

The word *atomic* describes software semantics and transaction boundaries. It does not claim matter-scale computation or atomic-scale hardware.

## Current status

The Ɣơ/2 reversible byte profile and experimental JavaScript parser are the compatibility foundation. Ŷæṛö adds the source-analysis, IR, and migration architecture without replacing them.

See [Atomic IR](ATOMIC-IR.md), [Legacy migration](LEGACY-MIGRATION.md), and [Quantum analysis](QUANTUM-ANALYSIS.md).
