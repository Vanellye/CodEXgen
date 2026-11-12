# Temple Geometry — Sphere Directives

**Status:** Declarative C++11 model added on the ALEPH feature branch. It is a software architecture model, not a physical-body model, medical system, or actuator controller.

## The building blocks

- **Bass strings** represent named connections between two anchors. Tension is abstract metadata, not physical force.
- **Sways** represent bounded, periodic change associated with a string. Amplitude and period are descriptive simulation values; they do not emit vibration or command hardware.
- **Shapes** provide stable geometric anchors: points, lines, triangles, polygons, and spheres.
- **Bridges** connect two distinct shapes and label the relationship between them.
- **Sphere directives** gather purpose and required principles into a governing unit. A directive is rejected unless it preserves human dignity and requires human consent.

## Temple to the body

The temple is a stewardship metaphor: a person's body, boundaries, and agency must not be treated as system-owned resources. No geometry, directive, or automated process may infer consent, override a person's choices, or initiate physical action.

## Governing rule

**Do what you must, not merely what you will.**

In implementation terms: distinguish duty from impulse; validate purpose and evidence; require consent for actions affecting people; record provenance; and prefer reversible, bounded operations. A spiritual statement such as "God's will" may be retained as a user's declared value, but software cannot authenticate divine authority or use it to bypass consent, evidence, or human review.

## Integration

The `TempleModel` stores these relationships and validates references. ALEPH remains the execution failsafe: failure enters safe hold, and compensating actions require explicit authorized approval. Temple directives do not independently authorize execution.

## Verification

`pantheon_temple_geometry_test` checks valid connections, sway references, bridges, sphere directives, and rejection of directives that waive consent. Run CMake/CTest with the project's C++11 toolchain before treating the implementation as verified.
