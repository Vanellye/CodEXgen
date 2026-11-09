# Python-to-Pantheon migration matrix

| Existing capability | Native destination | Port boundary | Completion gate | Status |
|---|---|---|---|---|
| `stride_core/faculty_engine.py` | `pantheon/modules/faculty` (public API in `faculty_engine.hpp`) | Numeric feature ranking, deterministic concept prompts + SHA-256 seed, bounded scalar adaptation, channel metadata, runtime module | Golden fixtures + invalid-input tests + host C++11 test | **Native first pass implemented; Python remains reference** |
| `stride_core/medium_signal_engine.py` | `pantheon/modules/medium` | Deterministic signal samples and illustrative attenuation/count models | Golden fixtures + numerical tolerance tests | Pending |
| `olpirt/rise_wisdom_bridge.py` | `pantheon/modules/wisdom` | Stable event hash, SQLite schema, idempotent insert/export | SQLite compatibility and duplicate-event tests | Pending |
| `adaptive_governance.py` | `pantheon/modules/governance` | Cosine distance, thresholds, correction-state transitions, telemetry | Python fixture parity; judge injected separately | Pending |
| `code_generator.py` | `pantheon/modules/codegen` | Validated identifiers, deterministic source rendering | Byte-for-byte output fixtures | Pending |
| `semantic_vector_memory.py` | `pantheon/adapters/semantic_memory` | Provider interface, persistence metadata, query result shape | Adapter contract tests; embedding provider stays replaceable | Pending |
| `generated_modules/*.py` | generated output, not runtime engine | Keep generation templates and output formats versioned | Regeneration diff is clean | Pending |
| `hypotheticals/*.py` | documentation/examples or isolated simulation module | Preserve fictional/theoretical labeling | No claims of biological efficacy | Isolated |

Status: Faculty Engine has a C++11 native implementation and a runtime registration entry point. Python remains authoritative until cross-language golden fixtures and Android build checks pass. Native channel plans are metadata only; no physical emitter or biological-modulation behavior is implemented.
