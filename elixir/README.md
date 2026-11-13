# ERIA Observation Engine (Elixir)

A small, dependency-free Elixir application for source-linked biological and
ecological measurements. It supports four domains:

- `plant`: photosynthesis, growth, water exchange, nutrient uptake, gene expression
- `animal`: physiology, behavior, development, genetics, population, ecological relationships
- `cellular_molecular`: molecular abundance, sequence variation, cellular signaling, metabolism, repair
- `ecosystem`: energy flow, biomass, biodiversity, environmental change, resilience

## Design contract

- **Observation** is an instrument/source record.
- **Measurement** is a numeric value with a unit, method, subject, timestamp and conditions.
- **Inference** is a separate derived record and is not created automatically.
- **Provenance** includes source identity and SHA-256 of the submitted raw payload.
- Corrections create new records; they do not overwrite historical observations.
- The parser accepts a narrow data grammar only. It does not execute code.
- Quality qualification checks record structure, not calibration, biological truth, or clinical validity.

## Code language

One record per line:

```text
OBSERVE|domain|subject_id|metric|value|unit|method|ISO8601_timestamp|source|raw_payload
```

Example:

```text
OBSERVE|plant|plot-7|photosynthesis_rate|12.5|umol_m-2_s-1|gas_exchange|2026-11-13T10:00:00Z|sensor-log-01|raw-sample-001
```

Fields cannot contain the pipe delimiter in this initial grammar. Use a future escaped/JSONL transport adapter for arbitrary raw payloads.

## Run

From this directory, with Elixir and Mix installed:

```sh
mix test
```

The library API:

```elixir
{:ok, observations} = Eria.CodeLanguage.parse(input)
report = Eria.Interpreter.interpret(observations)
```

## Explicit limits

The engine does not acquire sensor data, establish instrument calibration, infer causation,
make clinical diagnoses, authorize biological modification, or activate physical actuators.
Those require independent data sources, validated methods, qualified review, and separate
authorization systems.
