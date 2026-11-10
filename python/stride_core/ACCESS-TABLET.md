# Stride 2 — Root Access Tablet

**Status:** access policy contract; Python service-level enforcement must be verified per function.  
**Applies to:** JOB lifecycle/history, integrations, reconciliation, perception, creative composition, and contextual reading.

| Capability | READ right | WRITE right | Boundary |
|---|---|---|---|
| JOB engine | Read explicitly selected JOB state | Create/update lifecycle records | No global enumeration or implicit mutation |
| JOB history | Read named JOB event history | Append correction/event | No in-place rewrite of history |
| JOB integrations | Read explicitly selected integration input | Write to named integration target | No implied network or cross-account authority |
| Reconciliation | Read the two explicitly supplied snapshots | Write a reconciliation proposal | No automatic source overwrite |
| Faculty engine | Read caller-supplied observations/concepts | No persistent write by default | Pure calculation is preferred |
| Holified Inception | Read caller-supplied context | No persistent write by default | No private-record retrieval or external action |
| Medium/signal engine | Read caller-supplied parameters | Write generated local result only when target is specified | Simulation values do not authorize physical emission |

## Rules

- A caller-supplied dataset is not permission to retrieve adjacent private data.
- Reading one JOB ID does not authorize reading all JOBs.
- Appending an event is distinct from rewriting a historical event.
- Memory search, memory mutation, telemetry export, and code generation output are separate operations.
- Scripts may not infer or mint authorization from a user's intention or from a successful validation.
- When rights are unknown, fail closed and explain which scope is missing.

## Implementation status

This tablet documents required behavior. It does not yet provide a shared Python authorization engine, and it does not claim that every service enforces these rules.
