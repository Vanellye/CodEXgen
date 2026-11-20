# ERIA Water Flow — Independent Workstreams

## Scope

This proposal models a complete water-management lifecycle as five independent
planning contracts plus a narrow integration contract:

1. **Collection** — source identity, source-linked flow observations, and a
   proposed intake rate bounded by observed availability.
2. **Purification** — configured treatment stages and linked sample records.
   Configuration is not proof of treatment efficacy or potability.
3. **Storage** — vessel capacity, observed current volume, proposed inflow,
   and a calculated overflow remainder.
4. **Distribution** — demand allocation by explicit numeric priority, with
   unmet demand visible rather than hidden.
5. **Recycling** — wastewater stream accounting and constrained non-potable
   reuse classes, with suitability left unverified.
6. **Integration** — validates the declared stage order and emits a logical
   route record only.

## Data and provenance

Each stage has its own module under `elixir/lib/eria/water/`. Source and sample
observation IDs are explicit inputs where applicable. The contracts do not
invent sensor measurements, treatment results, flow availability, or recovery
efficiency. Water measurements can also be represented by the existing
`Eria.Observation` plant `water_exchange` metric or ecosystem
`environmental_change` metric when the measurement domain supports it.

## Safety and non-claims

- All outputs are proposals or logical records; execution is disabled.
- No pump, valve, sensor, dosing system, filter, UV unit, or treatment plant is
  connected or actuated by this software.
- No potability, pathogen removal, contaminant clearance, or regulatory
  compliance claim is inferred from a configured treatment train.
- Recycled-water suitability is not established by selecting a reuse class.
  Applicable local standards and independent sample testing must be supplied
  and reviewed.
- Distribution priorities are a deterministic allocation rule, not a claim
  about legal water rights, emergency priorities, or operational safety.
- Calibration, sensor integration, field commissioning, and control-system
  authorization remain separate workstreams.

## Validation

The ExUnit tests exercise source-linked collection limits, treatment-stage
representation, tank overflow arithmetic, priority allocation, recycling
volume bounds, and stage-order validation. They do not simulate real fluid
dynamics, certify equipment, or replace hydraulic and water-quality engineering.
