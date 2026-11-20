# ERIA Frequency Register — 556 / 772 / 420 Hz

**Status:** User-specified frequency metadata; documentation only  
**Scope:** This register is the canonical repository reference for the three supplied nominal values.

## Registered values

| Identifier | Frequency | Definition |
|---|---:|---|
| FREQ-556 | 556 Hz | User-specified nominal frequency; no effect or purpose asserted |
| FREQ-772 | 772 Hz | User-specified nominal frequency; no effect or purpose asserted |
| FREQ-420 | 420 Hz | User-specified nominal frequency; no effect or purpose asserted |

The order above preserves the order supplied by the user: **556, 772, 420**.

## Interpretation and provenance

These values are recorded as frequency metadata only. The repository does not currently provide a verified mapping from any value to a biological, medical, cognitive, spiritual, therapeutic, acoustic, or hardware effect. Do not infer one from the number alone.

A frequency value is not a complete signal specification. No waveform, amplitude, phase, modulation, duty cycle, duration, transducer, exposure level, or output device is specified by this register. Such parameters must not be invented or silently derived.

## Scope of application

This file is the canonical cross-reference for the values within this repository revision. Other documents and modules should reference the identifiers and values here rather than independently redefining them. A reference in documentation or source metadata does not imply that every branch, nested repository, generated artifact, or external repository has been updated.

Any future implementation must separately define:
- the intended use and evidence supporting it;
- the signal-generation and measurement specification;
- applicable safety limits and validation method;
- the exact module/device boundary and permitted output;
- tests, review state, and an attributable change receipt.

## Execution boundary

This register does **not** generate, play, transmit, modulate, or apply a signal. It does not activate a runtime, Android audio route, Bluetooth endpoint, webhook, remote service, or physical actuator. It grants no permission and is not an execution instruction.

**Invariant:** record the values exactly; preserve uncertainty; require separately reviewed implementation and explicit authorization before any signal output or external action.
