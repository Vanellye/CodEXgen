# CodEXgen Firmware Layer

## Mission

The firmware layer is the small, auditable device-side foundation for CodEXgen. It owns hardware-specific initialization, bounded observation, health reporting, watchdog servicing, and safe shutdown. It does not own project policy, user intent, identity decisions, or emergency command.

## Architecture

- **Board support package (BSP):** exact MCU/board, clock tree, pin map, memory map, boot configuration, and vendor SDK version. A BSP is added only after the target hardware is selected.
- **Hardware abstraction layer (HAL):** narrow interfaces for monotonic time, read-only sensor observations, health state, and bounded local event storage.
- **Device services:** sampling schedules, calibration metadata, fault reporting, and watchdog integration.
- **Transport adapter:** optional, disabled by default; sends minimized, authenticated records through a separately authorized host connection.
- **Boot/update boundary:** signed firmware images, version/rollback policy, integrity verification, and recovery image strategy are required before field deployment.

## Safety and security invariants

1. No device-specific pin, bus, radio, or actuator operation is enabled by a generic framework module.
2. No remote command execution, remote firmware update, or physical actuation is enabled by default.
3. Sensor readings carry units, timestamp, source identity, calibration status, and quality flags; unknown values remain unknown.
4. Hardware faults, watchdog expiry, invalid configuration, and integrity failures enter a documented safe state.
5. Firmware does not decide identity, authorization, rescue deployment, or whether a person is safe.
6. Secrets are not compiled into source, logs, test fixtures, or firmware defaults.
7. Secure boot, signed updates, anti-rollback, protected key storage, and recovery behavior are release gates, not assumed capabilities.
8. Debug interfaces are disabled or access-controlled in production builds.
9. Firmware updates require explicit operator authorization, image signature verification, power-loss-safe installation, and a tested recovery path.
10. Every supported board has a threat model, pin/peripheral inventory, reproducible build instructions, and hardware-in-loop test report.

## Repository layout

- `include/codexgen/firmware_contract.hpp` — portable C++11 observation and health contracts.
- `boards/` — future board-specific BSPs; none is selected yet.
- `tests/` — host contract tests and later hardware-in-loop tests.
- `toolchains/` — pinned cross-compilers and reproducible build configuration.

## Current status

The portable interface contract is provided; this repository does not yet contain a selected-board BSP, cross-compiler configuration, bootloader, signed updater, hardware driver, or flashable firmware image. Do not flash this repository to hardware. Select the MCU/board and define its safety and threat model before implementing board support.
