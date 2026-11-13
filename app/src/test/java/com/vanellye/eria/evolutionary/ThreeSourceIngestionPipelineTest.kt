package com.vanellye.eria.evolutionary

import org.junit.Assert.*
import org.junit.Test

class ThreeSourceIngestionPipelineTest {
    private val pipeline = ThreeSourceIngestionPipeline()

    private fun payload(accession: String? = null, format: SequenceFormat = SequenceFormat.FASTA, content: String = ">r1\nACGTACGT\n") =
        SequencePayload(SequenceSourceMetadata("test-source", accession, retrievedAt = "2026-11-13T00:00:00Z", licenseOrTerms = "test terms"), format, content)

    @Test fun ingestsExistingSequenceAndHandsOnlyQualifiedOutputToEngine() {
        val result = pipeline.ingest(ExistingSequenceAdapter(payload()), "existing.test-1")
        assertTrue(result is IngestionResult.Accepted)
        val accepted = result as IngestionResult.Accepted
        assertEquals(IntakeOrigin.EXISTING_SEQUENCE, accepted.report.origin)
        val finding = EvolutionaryAnalysisEngine.analyze(accepted.qualified)
        assertEquals(8L, finding.totalBases)
        assertEquals(0.5, finding.gcFraction, 0.0001)
        assertEquals(SequenceEvidence.OBSERVED_INPUT, finding.evidence)
    }

    @Test fun resolvesExactPublicAccessionAndRejectsMismatch() {
        val resolver = PublicReferenceResolver { accession -> payload(accession) }
        val ok = pipeline.ingest(PublicReferenceAdapter("REF-001", resolver), "public.test-1")
        assertTrue(ok is IngestionResult.Accepted)
        val mismatch = pipeline.ingest(PublicReferenceAdapter("REF-002", PublicReferenceResolver { payload("REF-001") }), "public.test-2")
        assertTrue(mismatch is IngestionResult.Rejected)
    }

    @Test fun syntheticOriginRemainsExplicitAndUnknown() {
        val result = pipeline.ingest(SyntheticSequenceAdapter(), "synthetic.test-1")
        assertTrue(result is IngestionResult.Accepted)
        val accepted = result as IngestionResult.Accepted
        assertEquals(DatasetOrigin.SYNTHETIC, accepted.qualified.dataset.provenance.origin)
        assertEquals(EvidenceState.UNKNOWN, accepted.qualified.dataset.evidenceState)
        assertEquals(SequenceEvidence.SYNTHETIC_TEST, EvolutionaryAnalysisEngine.analyze(accepted.qualified).evidence)
    }

    @Test fun rejectsBadFastaAndQualityThresholdFailure() {
        val malformed = pipeline.ingest(ExistingSequenceAdapter(payload(content = ">r1\nACGT!\n")), "bad.fasta")
        assertTrue(malformed is IngestionResult.Rejected)
        val strict = ThreeSourceIngestionPipeline(QualityThresholds(maximumAmbiguousFraction = 0.0))
        val ambiguous = strict.ingest(ExistingSequenceAdapter(payload(content = ">r1\nACGTNN\n")), "ambiguous")
        assertTrue(ambiguous is IngestionResult.Rejected)
    }

    @Test fun rejectsFastaWithoutHeaderAndInputOverLimit() {
        val noHeader = pipeline.ingest(
            ExistingSequenceAdapter(payload(content = "ACGTACGT\\n")), "no-header")
        assertTrue(noHeader is IngestionResult.Rejected)
        val bounded = ThreeSourceIngestionPipeline(QualityThresholds(maximumInputCharacters = 5))
        val oversized = bounded.ingest(ExistingSequenceAdapter(payload()), "oversized")
        assertTrue(oversized is IngestionResult.Rejected)
    }

    @Test fun parsesFastqAndComputesMeanPhred() {
        val fastq = payload(format = SequenceFormat.FASTQ, content = "@r1\nACGT\n+\nIIII\n")
        val result = pipeline.ingest(ExistingSequenceAdapter(fastq), "fastq.test-1")
        assertTrue(result is IngestionResult.Accepted)
        assertEquals(40.0, (result as IngestionResult.Accepted).qualified.metrics.meanPhred!!, 0.0001)
    }

    @Test fun enforcesConfiguredPhredThreshold() {
        val strict = ThreeSourceIngestionPipeline(QualityThresholds(minimumMeanPhred = 41.0))
        val fastq = payload(format = SequenceFormat.FASTQ, content = "@r1\nACGT\n+\nIIII\n")
        assertTrue(strict.ingest(ExistingSequenceAdapter(fastq), "low-quality").let { it is IngestionResult.Rejected })
    }
}
