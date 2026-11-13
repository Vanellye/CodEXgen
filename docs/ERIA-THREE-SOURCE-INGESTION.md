# ERIA Three-Source Ingestion and QC Pipeline

Status: implemented initial in-memory FASTA/FASTQ intake and quality-gated composition analysis. No remote public-data downloader, persistent file store, or clinical interpretation is enabled.

## Source adapters

- Existing sequence adapter accepts file content supplied by the host file picker. It does not access device storage itself.
- Public reference adapter delegates to an injected resolver and verifies that the exact requested accession is returned. Network retrieval, TLS, rate limits, license acceptance, and version pinning belong in a separately reviewed resolver.
- Synthetic adapter emits deterministic, clearly labeled test sequences with no public accession.

## Pipeline

1. Validate dataset identifier, source metadata, retrieval timestamp, accession rules, and license/terms.
2. Compute SHA-256 over the exact input text.
3. Parse FASTA (multi-line records) or strict four-line FASTQ (Phred+33).
4. Reject unsupported nucleotide symbols, malformed records, incomplete FASTQ records, and quality-length mismatches.
5. Enforce configurable input-character and read-count ceilings before accepting the in-memory payload.\n6. Compute read count, total bases, mean read length, GC fraction, ambiguous-base fraction, and mean Phred where available.
7. Apply explicit configurable minimum read/base counts, maximum ambiguous fraction, and optional mean Phred threshold.
8. Build an EvolutionaryDataset with source origin, digest, quality state, parameter fingerprint, input digest, output digest, and evidence class.
9. Run the existing dataset validator. Only then create QualifiedSequenceDataset.
10. Pass the qualified object to EvolutionaryAnalysisEngine for a descriptive composition summary.

## Evidence semantics

Existing sequence input is labeled observed input; public reference sequence is labeled reference evidence; synthetic data remains synthetic and its dataset evidence state is UNKNOWN. The engine's outputs are summaries, not diagnoses, predictions of individual health, or proof of evolutionary fitness.

## Limitations

- In-memory parser only; large files require streaming and resource limits before production use.
- FASTQ currently supports strict four-line records, not wrapped sequence/quality lines.
- FASTA does not carry per-base quality scores.
- GC and ambiguity metrics are basic sequence QC, not a complete sequencing QC suite.
- No alignment, variant calling, annotation, telomere estimation, repair-capacity inference, or clinical interpretation is performed.
- Public reference retrieval is an injected interface, not an implemented network client.
- Host must protect source files and avoid logging raw genomic content.

## Tests

Tests cover all three source paths, exact public accession matching, synthetic evidence labeling, FASTA parsing, FASTQ quality scores, malformed input, and threshold rejection.


## Explicit research intake questionnaire

Every intake call now requires a completed `ResearchIntakeQuestionnaire`. It records project identifier, purpose, organism (or "unknown"), source origin, format, authority/terms basis, data sensitivity, optional accession and assembly, requested analysis scopes, direct-identifier declaration, and completion timestamp.

Validation binds questionnaire origin and format to the adapter and payload. Existing sequence input requires recorded authority and restricted-genomic classification; public references require recorded terms review and an exact accession match; synthetic data must be explicitly marked synthetic. Direct personal identifiers and unsupported analysis scopes are rejected.

The questionnaire is not consent collection, proof of legal authority, ethics approval, or human authorization to modify biological material. It is a declared intake record. Dataset-specific human approval remains a separate digest-bound review contract. The questionnaire's relevant fields are included in the pipeline-parameter fingerprint; the raw questionnaire text is not persisted by this pipeline.
