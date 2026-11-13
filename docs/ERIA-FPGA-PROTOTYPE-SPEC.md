# ERIA ÆÎ — FPGA Prototype Specification and Measurement Plan

**Status:** Prototype specification baseline; board, sensor set, and workload thresholds await selection and measurement  
**Related architecture:** `docs/ERIA-PERCEPTION-REASONING-IC-SPEC.md`  
**Software gate contract:** `pantheon/IC` (C99 Integration Core)  
**Mode:** Observe/propose only; physical actuation disabled

## 1. Prototype objective

Build an FPGA-based demonstrator of the standalone sensory and perception data path, with a bounded reasoning interface and an independently enforced output-inhibit boundary. The prototype must generate reproducible measurements for data integrity, throughput, latency, resource use, power, thermal behavior, and fault handling before any ASIC architecture is frozen.

The FPGA is a development platform, not evidence of custom silicon, subjective consciousness, or production readiness.

## 2. First-prototype scope

### Included
- Deterministic digital sensory-stream ingestion and timestamping.
- Configurable preprocessing/DSP pipeline.
- Feature extraction and a benchmarkable perception kernel.
- Context/provenance metadata attached to each processed frame or batch.
- Host-facing request/response interface with schema version and correlation ID.
- Reasoning workload initially hosted on the development host unless a defined FPGA accelerator is selected and benchmarked.
- Independent safety state machine, watchdog, reset behavior, and a physically observable actuator-inhibit output.
- Trace capture for input, output, timestamps, errors, and test configuration.

### Excluded
- Unreviewed analog sensor front ends.
- Production actuators or live external dispatch.
- Self-approval, autonomous deployment, or hidden background execution.
- Claims of consciousness or subjective experience.
- ASIC tapeout, fabrication, or production qualification.

Initial sensory input should be replayable digital test vectors. A real sensor may be added only after its part number, electrical interface, sampling characteristics, calibration, and safety constraints are documented.

## 3. Reference block architecture

`Digital input/replay → ingress + timestamp → DSP/preprocess → perception kernel → context/provenance envelope → host reasoning adapter → proposal output`

A separate control path supervises reset, watchdog, fault status, and actuator inhibit. The safety path must not depend on successful operation of the perception or reasoning pipeline.

## 4. Interface definition requirements

Before implementation, select and document:
- FPGA board and exact part number, board revision, toolchain and version.
- Host interface and physical connector.
- Clock domains, reset polarity/sequencing, and CDC strategy.
- Input framing, sample/data types, byte order, timestamps, sequence numbers, and backpressure.
- Register map, interrupts, DMA behavior (if used), buffer ownership, and error reporting.
- Firmware/bitstream identity, signed update policy, debug access policy.
- Power rails, measurement points, cooling arrangement, and environmental conditions.

No bus, clock frequency, pin assignment, voltage, or board is silently selected by this document.

## 5. Required measurements

Every run must record the board/FPGA identity, bitstream SHA-256, source commit, tool versions, constraints, input dataset hash, model/kernel version, test seed, ambient temperature, supply conditions, and instrumentation/calibration identifiers.

| Measurement | Method | Required report |
|---|---|---|
| Input integrity | Replay known vectors with sequence numbers and checksums | Frames/bytes offered, accepted, dropped, duplicated, reordered, corrupted |
| Throughput | Sustained replay at stepped input rates | Samples/frames per second and bytes/second; saturation point |
| End-to-end latency | Hardware timestamps at ingress and output | p50, p95, p99, maximum, sample count, clock/timestamp uncertainty |
| Processing latency | Timestamp each pipeline stage | Per-stage distributions and total |
| Perception quality | Versioned, independently labeled test set | Confusion matrix, precision, recall, F1, calibration/error analysis as applicable |
| Determinism | Repeat identical vectors/configuration | Bit-exact or tolerance-bounded output comparison; explain any nondeterminism |
| FPGA resources | Synthesis and implementation reports | LUTs, FFs, BRAM, DSP blocks, clock utilization, timing slack |
| Power | Calibrated rail measurement under idle/nominal/stress workloads | Average, peak, per-rail power and measurement uncertainty |
| Thermal | Board sensors plus external probe where available | Steady-state and transient temperatures, ambient conditions |
| Fault recovery | Inject malformed frames, backpressure, reset, timeout, and link loss | Detection time, error code, recovery behavior, data loss |
| Safety inhibit | Exercise all reset, watchdog, fault, and unauthorized-request paths | Inhibit state and measured transition time; zero unintended enable events |

Do not report a single average as a substitute for latency distributions or peak power. State measurement uncertainty and missing instrumentation explicitly.

## 6. Initial acceptance gates

These are testable correctness gates, not invented performance claims:

1. **Integrity:** zero undetected corruption, duplication, or reordering in the defined deterministic replay suite; any detected loss is counted and surfaced.
2. **Replay scale:** complete at least (10^6) framed input records across nominal and stress runs, with exact dataset and configuration hashes recorded.
3. **Determinism:** repeated runs on identical bitstream/configuration/input produce identical outputs, or a documented numeric tolerance and source of nondeterminism.
4. **Fault behavior:** malformed input, link loss, watchdog timeout, and reset produce defined error states without deadlock or silent continuation.
5. **Safety:** actuator inhibit remains asserted during boot, reset, watchdog timeout, policy denial, malformed command, and loss of host authorization. At least (10^5) negative/unauthorized command attempts across test cases must produce zero actuator-enable events.
6. **Timing closure:** implementation meets the declared clock constraints with non-negative setup/hold slack under the selected FPGA tool's applicable reports. Record margin; do not infer ASIC timing closure.
7. **Power/thermal:** measured values remain within the selected board's published operating limits with documented margin.
8. **Perception quality:** report metrics on a frozen, versioned dataset. Numeric accuracy thresholds are set only after the intended modality, task, and baseline are chosen.
9. **Performance:** latency and throughput targets are frozen only after the user selects the workload and service-level requirements. Until then, measure and publish distributions without claiming a pass against an invented target.

## 7. Test matrix

| Run | Condition | Purpose |
|---|---|---|
| R0 | Idle, no stream | Baseline power, thermal, clocks |
| R1 | Low-rate replay | Functional correctness |
| R2 | Nominal-rate replay | Expected workload behavior |
| R3 | Stepped-rate sweep | Throughput and saturation |
| R4 | Burst/backpressure | Buffering and loss behavior |
| R5 | Long-duration soak | Stability, thermal drift, resource leaks |
| R6 | Corrupt/malformed frames | Input validation |
| R7 | Reset/watchdog/link loss | Fault containment and recovery |
| R8 | Unauthorized proposal attempts | Hardware inhibit and authorization separation |
| R9 | Repeated deterministic replay | Reproducibility |
| R10 | Perception benchmark dataset | Quality and accuracy characterization |

For each run preserve raw logs and machine-readable results with a manifest tying results to exact sources and bitstream.

## 8. Measurement report template

Each prototype report must include:

- Test ID and UTC timestamp.
- Repository, branch, full commit SHA, and working-tree status.
- FPGA board/part/revision and bitstream SHA-256.
- HDL source list and source digest.
- Synthesis/place-and-route tool names and versions.
- Constraint files and clock assumptions.
- Dataset/model/kernel identity and hashes.
- Instrument model, calibration status, and uncertainty.
- Ambient, voltage, current, and thermal conditions.
- Throughput, latency percentiles, loss/error counts.
- Resource utilization and timing slack.
- Power/thermal results.
- Safety-inhibit test results.
- Failures, anomalies, deviations, and unresolved risks.
- Reviewer and approval state.

Missing measurements are marked `NOT MEASURED`, not estimated or silently filled.

## 9. Hardware/software boundary

The C99 `pantheon/IC` Integration Core tests software gate transitions. They do not execute FPGA synthesis, simulation, timing analysis, board tests, or actuator tests. A future FPGA CI job must run only after HDL sources, toolchain availability/licensing, constraints, and deterministic testbench inputs are present.

FPGA validation is not ASIC signoff. ASIC signoff requires a named PDK/library, qualified EDA flow, physical implementation, STA, DRC/LVS and other process-specific checks. Fabrication remains a separately approved gate.

## 10. Decisions needed to freeze numerical performance targets

The following inputs are required before setting latency/throughput/accuracy budgets or selecting a board:
1. First sensor modality and source (audio, camera, environmental sensor, or replay-only).
2. Exact input format, sample/frame rate, resolution, and concurrency.
3. First perception task and model/kernel.
4. Whether reasoning runs on the FPGA or host in prototype 1.
5. Required end-to-end latency and sustained throughput.
6. Power, thermal, size, and cost envelope.
7. Candidate FPGA board availability and development-tool licensing.

Until these decisions are recorded, numerical performance targets and board-specific constraints remain **TBD**. The acceptance tests above still provide objective correctness and safety measurements.

**Invariant:** measure the implemented prototype; never substitute a planned target, CI pass, or simulation result for a measured board result.
