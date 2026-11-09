# Python-to-Pantheon migration matrix

| Existing capability | Native destination | Port boundary | Completion gate |
|---|---|---|---|
| `stride_core/faculty_engine.py` | `pantheon/modules/faculty` | Numeric maps, deterministic prompts, bounded adaptation, channel metadata | Golden fixtures + invalid-input tests |
| `stride_core/medium_signal_engine.py` | `pantheon/modules/medium` | Deterministic signal samples and illustrative attenuation/count models | Golden fixtures + numerical tolerance tests |
| `olpirt/rise_wisdom_bridge.py` | `pantheon/modules/wisdom` | Stable event hash, SQLite schema, idempotent insert/export | SQLite compatibility and duplicate-event tests |
| `adaptive_governance.py` | `pantheon/modules/governance` | Cosine distance, thresholds, correction-state transitions, telemetry | Python fixture parity; judge injected separately |
| `code_generator.py` | `pantheon/modules/codegen` | Validated identifiers, deterministic source rendering | Byte-for-byte output fixtures |
| `semantic_vector_memory.py` | `pantheon/adapters/semantic_memory` | Provider interface, persistence metadata, query result shape | Adapter contract tests; embedding provider stays replaceable |
| `generated_modules/*.py` | generated output, not runtime engine | Keep generation templates and output formats versioned | Regeneration diff is clean |
| `hypotheticals/*.py` | documentation/examples or isolated simulation module | Preserve fictional/theoretical labeling | No claims of biological efficacy |

Status: **foundation scaffolded; capability ports not yet complete**. Python remains authoritative until each row passes its completion gate.
