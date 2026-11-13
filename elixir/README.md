# ERIA Observation Engine (Elixir)

A small, dependency-free Elixir application for source-linked biological and
ecological measurements. It supports five observation domains:

- `plant`: photosynthesis, growth, water exchange, nutrient uptake, gene expression
- `animal`: physiology, behavior, development, genetics, population, ecological relationships
- `cellular_molecular`: molecular abundance, sequence variation, cellular signaling, metabolism, repair
- `ecosystem`: energy flow, biomass, biodiversity, environmental change, resilience
- `earth`: land, water, air, life, and climate measurements (see `Eria.Earth` for subdomain mapping)

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

## Multi-omics research evidence extension

The normalized ingestion API accepts records for genomics, transcriptomics,
epigenomics, proteomics, metabolomics, lipidomics, microbiomics, and phenomics
across all four supported organism domains. Each record retains its source,
instrument identifier when supplied, timestamp, assay, method version,
reference version, QC claims/metadata, and SHA-256 fingerprint of the raw
payload. Rejections are returned with their input positions; they are not
silently discarded.

Example:

```elixir
ingestion = Eria.MultiOmics.Ingest.ingest([
  %{
    domain: "cellular_molecular",
    subject_id: "sample-001",
    modality: "transcriptomics",
    assay: "RNA-seq",
    feature: "GENE-A",
    value: 4.2,
    unit: "normalized_count",
    source: "lab-export-01",
    observed_at: "2026-11-13T10:00:00Z",
    raw_payload: "raw-read-count-payload",
    reference_version: "reference-build-1",
    method_version: "pipeline-1.0"
  }
])

{:ok, report} = Eria.Diagnostic.Support.build(ingestion)
```

The input contract is normalized maps, not direct FASTQ/BAM/CRAM/VCF or
vendor-specific instrument decoding. Raw hashes establish byte identity only;
they do not authenticate a source. QC metadata is retained as a supplied claim,
not independently verified. Findings must cite known record IDs and include a
method and uncertainty statement.

All outputs are **research-only**. The support report contains no diagnosis or
clinical recommendation, does not authorize intervention, and requires
independent review. Any downstream action remains disabled unless a separate,
scoped authorization process explicitly approves it. No instrument acquisition
or physical actuation is implemented by this extension.

## Independent review and authorization records

`Eria.Governance.record_review/1` requires a reviewer distinct from the
submitter and records the decision, scope, evidence IDs, and review time.
`Eria.Governance.record_authorization/1` requires an approved review, a
separate authorizer, a matching scope, an explicit action/target, expiry, and
an approval reference. These records do not authenticate identities or verify
the external approval reference cryptographically; that requires a trusted
identity/approval provider. The function deliberately returns
`execution_enabled: false`. No action executor is connected.

The diagnostic-support output always remains research-only and marks
intervention as unauthorized. A review or authorization record does not
convert research output into a diagnosis or enable biological intervention.

## Code interpretation and transmission trace

### Source documents used

This section records the repository-cloud documentation consulted on `main`
at commit `2cce68f258f46058f18c108c264db9cc85200590`. These documents are
references for interpretation and governance; they are not evidence that every
described capability exists in this Elixir application.

| Source | Exact source revision | Contract carried into this application |
|---|---|---|
| `docs/TRUE-NORTH-DATA-ARCHITECTURE.md` | blob `0db1b3ff1799bd425b83fea7fdeb5a51b5413e19` | Preserve raw and derived records; record transformations, versions, units, provenance, validation and authorization; fail closed when evidence is missing. |
| `docs/SKRIBED-TRANSMISSION-CONTRACT.md` | blob `b976ea94c2433c8ad256f640f00f49b94c3368bd` | Keep exact source text separate from interpretations and corrections; identify derivatives by operation/version/digest; internal receipt is not external dispatch authority. |
| `docs/TWO-SNAPSHOT-SYNTHESIS.md` | blob `c2f361a5022e0d326be5caf9fb39d7d2b7a4fbfa` | Preserve independent branch identity; compare provenance and interfaces before integration; distinguish observed content from proposed interpretation. |
| `pantheon/NEW/THOUGHT_TOTT/RETROSPECTIVE.md` | blob `0d10e846e3876ddb3eaa3618437ae8969b16a3ef` | Treat commit subjects as discovery clues, not proof; test negative paths; retain corrections and reversals as traceable history. |

The exact cloud source was the repository's `main` branch at the commit above.
No branch or file literally named `võîð` was returned by the repository
branch/file search; therefore this documentation does not claim to have pulled
from a separately named `võîð` object. If that is a distinct cloud location,
its exact repository/path/ref must be supplied before it can be imported.

### Interpretation pipeline

The Elixir implementation follows this explicit separation:

```text
SOURCE / INSTRUMENT
  -> CAPTURED OBSERVATION
  -> STRUCTURAL QUALITY CHECK
  -> NORMALIZED MULTI-OMICS RECORD
  -> SOURCE-LINKED RESEARCH FINDING
  -> INDEPENDENT REVIEW RECORD
  -> EXPLICIT, SCOPED AUTHORIZATION RECORD
```

- **Source:** original instrument export, dataset, or supplied payload. The current
  API accepts normalized maps; it does not decode vendor-specific raw files.
- **Observation:** a source-linked measurement with subject, domain, metric,
  value, unit, method, time, source, and raw-payload SHA-256 fingerprint.
- **Quality result:** structural qualification or rejection. A pass does not
  establish calibration, assay validity, source authenticity, or biological truth.
- **Derived interpretation:** a separately identified research finding that
  cites existing record IDs and states its method and uncertainty. Orphan
  references are rejected.
- **Review:** a reviewer distinct from the submitter records a decision and scope.
- **Authorization:** a separate authorizer records an approved scope, action,
  target, expiry, and approval reference. The record does not authenticate the
  identity provider or cryptographically verify that external approval.

### Transmission and lineage rules

1. Preserve the source payload and its digest; do not replace it with an interpretation.
2. Give each derived finding its own identity and retain the IDs of every source record.
3. Preserve units, timestamps, assay, method version, reference version, and supplied QC metadata.
4. Treat source-provided QC as an unverified claim until independently checked.
5. Record rejected input with its input position and reason; never silently discard it.
6. Corrections are additive records linked to prior identities, not in-place historical rewrites.
7. A hash proves byte identity relative to the hashed input; it does not prove who supplied it.
8. A review or authorization record is not an execution command. This engine has no connected action executor.

### Interpretation boundary

This is a **research-only** evidence interpretation system for plant, animal,
cellular/molecular, and ecosystem records. Multi-omics modalities include
genomics, transcriptomics, epigenomics, proteomics, metabolomics, lipidomics,
microbiomics, and phenomics.

The application does not generate clinical diagnoses, clinical recommendations,
causal conclusions by default, or permissions to modify biological material.
It does not verify instrument calibration, reference genome correctness, assay
performance, signer identity, or clinical validity. Any future clinical use
would require separately validated methods, qualified independent review, and
the appropriate clinical governance. Any consequential downstream action
requires a separate, trusted authorization system; this repository module
keeps execution disabled.

### Reproducibility record

For each analysis, retain at minimum:

- repository, branch, exact commit SHA, and source document blob SHAs;
- dataset/source identifiers and raw-payload digests;
- organism domain, subject/sample identifier, modality, assay, feature and units;
- observed timestamp, method version, reference/database version, and instrument identifier where supplied;
- quality checks, rejected records, and unresolved limitations;
- finding IDs, source-record IDs, method, uncertainty, and reviewer decision;
- Elixir/OTP versions, exact Mix commands, CI run URL, and test result for that commit.

The workflow is reproducible only to the extent that the original inputs,
toolchain, parameters, and referenced resources are available. Missing inputs
or unavailable checks must be marked **not verified**, never silently treated
as passing.

## Earth domain and Sacral-Lift

The `earth` observation domain organizes environmental measurements into five
subdomains: `land`, `water`, `air`, `life`, and `climate`. Earth metrics are
validated against their subdomain map by `Eria.Earth`.

`Eria.Earth.SacralLift` is a separate, consent-gated descriptive cue-pattern
engine. The requested "subliminal" label is constrained to analysis of
user-submitted or otherwise explicitly consented patterns. It requires an
explicit consent flag, stated purpose, and source-observation IDs. It produces
a reviewable metadata record only; it does not generate hidden messages,
deliver covert stimuli, infer subconscious states, or influence behavior.
Interpretation, execution, and external dispatch remain disabled. A qualified
human reviewer must assess any proposed interpretation independently.

Run the Earth/Sacral-Lift tests with `mix test` from this directory.