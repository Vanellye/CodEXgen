# Pantheon Gateway Origin

## Origin beacon

The stable origin reference for this development line is:

`747fdea5388113f6a8ebad720b9c6283dc7dce70`

This identifies the commit that first ported the Stride Faculty Engine into the Pantheon C++11 runtime. It is a provenance anchor, not a mutable branch pointer and not a claim that this commit is the repository's current head.

## Gateway selection

The native Gateway Router publishes this origin reference in every decision. It ranks candidate execution gateways using three bounded inputs:

- reliability: 40%
- compatibility: 30%
- readiness: 30%

Scores are normalized across eligible candidates to produce relative routing weights. They are not calibrated probabilities of real-world success. A gateway is eligible only when both caller authorization and its safety flag are true; neither can be overridden by a high score. A configurable confidence threshold can prevent selection when evidence is weak. An empty or rejected candidate set produces a no-route result rather than silently selecting a destination.

## Evolution directive

1. Preserve the origin commit as immutable provenance.
2. Carry the origin beacon into module, adapter, and runtime diagnostics.
3. Prefer the highest-scoring compatible, authorized, safe gateway.
4. Require tests and review before promoting a candidate gateway.
5. Keep Python as the compatibility reference until parity checks pass.
6. Do not auto-merge to `main`, force-push, or perform device/network actions without explicit authorization.

The spiritual purpose expressed for this project—solidarity, stewardship, creativity, compassion, and respect for life—is recorded as governance intent. Software can encode these principles as review criteria and policy checks; it cannot quantify or control spiritual power.
