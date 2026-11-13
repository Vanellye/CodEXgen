# PANTHEON RAW — Controlled Sensor Integration

**Status:** proposal only; no sensor is enabled or activated by this change.  
**Scope:** microphone and accelerometer measurement interfaces only.

## Goals

- Add a governed integration boundary between Pantheon/ERIA and device sensors.
- Preserve repository source files and generated originals.
- Make sensor discovery, calibration, permission checks, approval, and measurement separately auditable.
- Fail closed whenever device identity, API support, permissions, calibration, limits, or approval are missing.

## Explicit exclusions

This integration does not enable speaker output, vibration motors, contact actuators, wireless transmission, or automatic background recording. It does not claim that Termux currently exposes every requested sensor.

## Activation sequence

1. **Repository inspection:** identify the actual application/runtime and source revision.
2. **Capability discovery:** enumerate available sensors using a verified platform API; record sensor name, vendor, identifier, resolution, range, and reporting mode where available.
3. **Permission verification:** request microphone permission through the supported Android application path. Do not bypass Android permissions.
4. **Calibration:** establish sensor-specific baseline, units, orientation, timestamp behavior, and noise characteristics.
5. **Safety configuration:** define maximum session duration and sampling rate from the actual device/API documentation. Do not guess these limits.
6. **Human authorization:** obtain explicit approval for the specific sensor, purpose, duration, and sampling configuration.
7. **Controlled measurement:** start one bounded session; show visible recording/measurement state; support immediate stop.
8. **Audit and close:** record start/stop, device/sensor identity, configuration hash, source revision, calibration reference, approval, and result status. Preserve raw originals and write derived data separately.

## Fail-closed conditions

No acquisition is allowed if any required check is missing or fails. A dashboard button may create an approval request, but must not imply that acquisition has started. No code in this proposal opens a microphone or reads accelerometer hardware.

## Termux / Android implementation note

Termux is not itself an Android sensor permission broker. The actual adapter must be selected only after checking the installed Android app, Termux:API companion compatibility, available commands, and device sensor capabilities. If a sensor is not exposed through a verified interface, use a small Android companion app with normal runtime permissions rather than root or permission bypasses.

## Proposed repository layout

- `config/pantheon-raw-sensor-policy.json` — default-deny policy.
- `tools/pantheon_sensor_gate.py` — offline policy inspection and approval-request audit writer.
- `.eria/pantheon-sensor-audit.jsonl` — runtime audit destination (generated locally; do not commit personal sensor recordings).
- `docs/PANTHEON-RAW-SENSOR-INTEGRATION.md` — integration and activation protocol.

## Acceptance criteria before physical activation

- [ ] Confirm Android device model and OS/API level from the device itself.
- [ ] Confirm exact microphone and accelerometer APIs and permissions.
- [ ] Confirm sensor metadata and units.
- [ ] Set documented session/sample limits.
- [ ] Verify calibration and stop behavior.
- [ ] Review data retention and privacy behavior.
- [ ] Human approval for a specific bounded test.
- [ ] Independent review of adapter and safety gate.

Until all criteria are satisfied, status remains `proposal_only`.
