# THANKs — Motion Influence

**Status:** proposed motion-control contract; no actuator is enabled.

## Intent

Preserve the exact name **THANKs** for the proposed mechanism by which an approved signal may influence motion speed and create a measurable movement (“mobmint,” retained as the user's term). The meaning of “mobmint” remains open pending a precise operational definition.

This specification does not assume whether the target is a software animation, simulated agent, motor, vehicle, or other physical system. Those targets have materially different safety requirements and must be declared before implementation.

## Control contract

A motion request must specify:

- target and operating mode;
- measured current state and units;
- requested speed or velocity change;
- maximum speed, acceleration, and rate-of-change bounds;
- allowed operating envelope and environmental constraints;
- start condition, stop condition, timeout, and emergency-stop behavior;
- authorization identity and scope;
- telemetry and verification method.

The controller must reject requests outside configured limits, on stale or missing measurements, or without valid authorization. It must support a human stop/override and must fail to a defined safe state.

## Separation of concerns

1. **Signal detection** identifies a possible trigger.
2. **Evidence qualification** evaluates source integrity and reliability.
3. **Authorization** determines whether the requested target and operation are permitted.
4. **Motion planning** calculates a bounded trajectory.
5. **Actuation** occurs only after all gates pass.
6. **Telemetry and review** record requested, commanded, and measured motion separately.

A trigger, anomaly, rarity score, or “THANKs” event alone must never cause movement. No hidden actuation or external dispatch is implied.

## Speed and motion measures

Use target-appropriate SI units where applicable. Distinguish commanded speed from measured speed, and velocity from acceleration. Apply explicit ceilings, acceleration limits, rate limits, dead-man/stop behavior where appropriate, and independent safety interlocks for physical systems.

Do not invent universal safe values. Limits must come from the target's validated specification and risk assessment.

## Acceptance tests

- Missing or stale telemetry prevents actuation.
- Out-of-range speed or acceleration requests are rejected.
- Trigger detection without authorization produces no motion.
- Emergency stop overrides all ordinary motion requests.
- Logs distinguish requested, commanded, and measured movement.
- A failed controller or lost communication reaches the defined safe state.
- Simulated tests pass before any physical deployment is considered.
