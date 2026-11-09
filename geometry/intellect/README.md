# Geometrical Intellect

This area is the mathematical reasoning layer behind the Geometry & Design library. It records the language, logical foundations, derivations, dimensional models, unresolved questions, and design decisions used to reason about geometric structures.

It is deliberately separate from the shape gallery, visual design collection, and empirical observation records.

## Knowledge areas

| Area | What belongs here |
|---|---|
| [Mathematical definitions and notation](DEFINITIONS-NOTATION.md) | Precise terms, symbols, sets, mappings, units, conventions, and notation keys |
| [Axioms, theorems, lemmas, and proofs](AXIOMS-THEOREMS-PROOFS.md) | Assumptions, formal statements, dependencies, proof strategies, and complete proofs |
| [Geometric reasoning and derivations](GEOMETRIC-REASONING.md) | Step-by-step arguments, constructions, transformations, and formula derivations |
| [Dimensions and coordinate systems](DIMENSIONS-COORDINATES.md) | Dimension, bases, coordinate frames, metrics, projections, and coordinate changes |
| [Conjectures and open questions](CONJECTURES-OPEN-QUESTIONS.md) | Clearly marked unproved claims, questions, counterexamples sought, and proof status |
| [Construction and design rationale](CONSTRUCTION-RATIONALE.md) | Why a particular geometry, constraint, transformation, or construction is selected |

## Evidence and proof-status labels

Use a label on every substantial claim:

- **Established:** accepted definition, axiom within a named system, or proved result.
- **Derived:** follows from stated assumptions through a shown argument.
- **Conjectural:** proposed but not proved.
- **Open:** unresolved question with a clearly stated scope.
- **Interpretive:** conceptual or philosophical framing, not a mathematical theorem.
- **Illustrative:** example or diagram used to communicate an idea, not evidence.

Do not call a conjecture a theorem. Do not present an illustration, simulation, analogy, or numerical example as a proof.

## Recommended record format

~~~text
# Title
## Purpose and scope
## Status label
## Definitions and notation
## Assumptions / axioms
## Statement or question
## Reasoning / derivation / proof
## Coordinate and dimensional conventions
## Diagram references
## Limitations and counterexamples
## Design implications (if applicable)
## Sources and revision notes
~~~

## Separation rules

- Mathematical claims and proofs belong here.
- Shape-specific visual references belong in [Shapes](../shapes/README.md).
- Compositions and visual systems belong in [Designs](../designs/README.md).
- Scalable explanatory illustrations belong in [Visuals](../visuals/README.md).
- Raw measurements, sensor output, time-series records, statistical plots, and empirical dashboards belong in the relevant observation or experiment area. Link to them; do not relocate or duplicate their role here.

## Quality standard

A reader should be able to identify the mathematical system being used, understand every symbol, trace each inference, distinguish assumptions from conclusions, and reproduce the argument without relying on an unstated intuition.
