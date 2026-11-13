# ERIA Evolutionary Sustainability Gene-Data Engineering

Status: initial implementation contract. This is a computational research and data-governance subsystem, not a clinical diagnostic or biological intervention system.

## Goals

Unify three explicitly separated input classes:
1. Existing sequencing datasets supplied by an authorized user.
2. Public reference datasets with accession, source URI, license/terms, reference assembly, and retrieval timestamp.
3. Deterministic synthetic fixtures used only to test software behavior.

Never silently merge these source classes. Every dataset retains its origin classification and immutable source digest.

## Sequence

1. **Intake and provenance** — identify source, accession, assembly/build, format, source checksum, retrieval time, license/terms, and permitted use.
2. **Format and integrity checks** — validate readability, compression, reference compatibility, metadata completeness, and checksums before analysis.
3. **Quality qualification** — record applicable read quality, depth/coverage, mapping rate, duplicate rate, contamination, call rate, missingness, and batch effects. Non-applicable metrics must be marked not-applicable, not fabricated.
4. **Omics layers** — keep genome, epigenome, transcriptome, proteome, metabolome, DNA repair, telomere, and environmental observations distinct.
5. **Analysis** — produce source-linked observations and derived results. Predictions remain separately labeled.
6. **Reproducibility** — pin pipeline version, toolchain, parameters digest, input digest, output digest, reference resources, and exact command/configuration.
7. **Independent review** — validate scientific assumptions, limitations, dataset permissions, and result provenance.
8. **Human authorization** — require reviewer identity, timestamp, decision reference, exact dataset digest, and narrow approved scope before privileged export or downstream action.

## Data and evidence rules

- Original source files are read-only; derived outputs are separate artifacts.
- Use SHA-256 digests to bind manifests and pipeline inputs/outputs.
- Keep personal genomic data private; do not place raw sequences, direct identifiers, access tokens, or sensitive metadata in logs or public fixtures.
- Preserve genome assembly/build and annotation release. Coordinates without reference context are not interpretable.
- Report missing, stale, incompatible, or unverified evidence as unknown or review-required.
- Synthetic fixtures must be unmistakably labeled and never described as biological observations.
- Quality thresholds are assay- and platform-specific; do not apply one universal threshold.
- Passing software validation does not establish biological validity, clinical significance, or safety.

## Analysis domains

| Domain | Permitted computational scope | Important limitation |
|---|---|---|
| Genome | variant inventory, annotation, QC | variants are not diagnoses |
| Epigenome | methylation/chromatin summaries | tissue and assay context matter |
| Transcriptome | expression and differential-expression summaries | batch and normalization effects |
| Proteome | abundance/pathway summaries | assay coverage and detection limits |
| Metabolome | measured metabolite profiles | platform and specimen handling |
| DNA repair | literature-linked pathway and assay observations | expression does not prove repair capacity |
| Telomeres | measured length distributions and method metadata | assay-specific uncertainty; not a standalone aging clock |
| Environment | documented exposure variables | association does not prove causation |
| Evolution | population-level diversity and selection analyses | no individual future outcome prediction |

## Quality report minimum fields

Dataset ID, source class, accession/URI, source SHA-256; reference assembly and annotation versions; file format and parser/tool versions; applicable coverage/call/missingness metrics; contamination and batch-effect checks; exclusions, warnings, thresholds and reasons; pipeline name/version, toolchain and parameters digest; input/output digests; observed/derived/predicted classification; uncertainty, limitations and reviewer decision.

## Authorization boundary

Authorization is not implied by data availability, a valid checksum, passing QC, a signature, or a model score. Every privileged action must be explicitly scoped and bound to the exact reviewed dataset digest. Approval for report generation is not approval for clinical use, sample handling, or biological intervention. No automated pathway may authorize genetic modification, sample manipulation, treatment, or clinical diagnosis.

## Initial implementation

EvolutionaryDataset.kt supplies source classes, omics-layer labels, evidence states, provenance and pipeline fingerprints, QC fields, human-review binding, and a deterministic synthetic metadata fixture. It intentionally does not fetch public datasets, ingest raw sequence files, execute bioinformatics tools, or claim scientific validation. Those adapters must be added behind explicit source-specific contracts and tested against pinned fixtures before use.

## Acceptance criteria

- [ ] Existing, public-reference, and synthetic origins remain distinguishable.
- [ ] Every input is bound to a source digest and provenance record.
- [ ] Public references require an accession; synthetic fixtures cannot claim one.
- [ ] QC values are range-checked and missing values remain missing.
- [ ] Pipeline fingerprints bind parameters, input, and output.
- [ ] Human review binds exact digest, reviewer, timestamp, decision reference, and scope.
- [ ] Tests cover invalid provenance, quality metrics, and authorization bypass attempts.
- [ ] No write path modifies original source data.
- [ ] No clinical or biological action is executable through this module.
