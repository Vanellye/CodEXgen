# Python Services — Root Access Tablet

**Status:** policy contract; per-service enforcement must be verified independently.  
**Applies to:** Stride services, JOB stores, semantic memory, telemetry, generators, and scripts.

- Caller-supplied input is readable only within the operation's declared context.
- Persistent JOB/history writes require explicit, scoped authorization.
- Semantic memory retrieval and mutation are separate rights.
- Telemetry read, append, export, and deletion are distinct operations.
- Code generation may write only to an explicitly selected output root; overwrite is denied unless separately authorized.
- Imported modules and scripts do not inherit caller privileges merely by being imported.
- No service may mint, broaden, or persist authorization for another service.
- Missing or ambiguous rights fail closed.

This tablet does not assert that all Python modules currently implement these controls.
