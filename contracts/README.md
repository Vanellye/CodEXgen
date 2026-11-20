# Shared knowledge graph contract

The file contracts/knowledge-graph.schema.json is the platform-neutral source of truth
for ERIA graph event identity and serialization. Android and web clients consume the
same schema version and fixture; neither client owns a competing graph identity model.

## Invariants

- Graph, event, node, and edge IDs are stable identifiers.
- Event sequence numbers are contiguous and append ordered.
- Every node and edge carries a source reference and SHA-256 digest.
- Edges may reference only nodes already introduced in the event stream.
- Corrections are new superseded events. Existing records are never updated, re-keyed,
  or deleted to represent a correction.
- The visible graph is a deterministic projection of the event stream; clients do not
  invent identity or historical ordering independently.

## Verification

- Android: ./gradlew :app:testDebugUnitTest
- Web: cd contracts/web && npm install && npm test

The web validator uses the JSON Schema directly with Ajv. The Android model mirrors
its versioned fields and shared invariants. Schema changes require updating the fixture
and both platform test suites in the same reviewed change.
