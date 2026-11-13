package com.vanellye.eria.evolutionary

import org.junit.Assert.assertTrue
import org.junit.Test

class EvolutionaryDatasetValidatorTest {
    @Test fun acceptsSyntheticFixture() {
        assertTrue(EvolutionaryDatasetValidator.validate(SyntheticEvolutionaryFixture.dataset()).isEmpty())
    }
    @Test fun rejectsMissingPublicAccessionAndBadDigest() {
        val fixture = SyntheticEvolutionaryFixture.dataset()
        val bad = fixture.copy(provenance = fixture.provenance.copy(
            origin = DatasetOrigin.PUBLIC_REFERENCE, sourceAccession = null, sourceSha256 = "bad"))
        val errors = EvolutionaryDatasetValidator.validate(bad)
        assertTrue(errors.any { it.contains("accession") })
        assertTrue(errors.any { it.contains("SHA-256") })
    }
    @Test fun rejectsInvalidQualityMetrics() {
        val bad = SyntheticEvolutionaryFixture.dataset().copy(
            quality = DatasetQuality("qc", -1.0, 1.5, Double.NaN))
        val errors = EvolutionaryDatasetValidator.validate(bad)
        assertTrue(errors.any { it.contains("coverageMean") })
        assertTrue(errors.any { it.contains("callRate") })
        assertTrue(errors.any { it.contains("contaminationEstimate") })
    }
    @Test fun requiresApprovalBoundToExactDigestAndScope() {
        val digest = "d".repeat(64)
        val review = HumanReview(ReviewStatus.APPROVED, "human.reviewer-1",
            "2026-11-13T00:00:00Z", digest, setOf("report.generate"), "approval-001")
        assertTrue(EvolutionaryDatasetValidator.validateReview(review, digest, "report.generate").isEmpty())
        assertTrue(EvolutionaryDatasetValidator.validateReview(review, "e".repeat(64), "report.generate").isNotEmpty())
        assertTrue(EvolutionaryDatasetValidator.validateReview(review, digest, "biological.intervention").isNotEmpty())
    }
    @Test fun syntheticFixtureCannotClaimPublicAccession() {
        val fixture = SyntheticEvolutionaryFixture.dataset()
        val bad = fixture.copy(provenance = fixture.provenance.copy(sourceAccession = "FAKE-ACCESSION"))
        assertTrue(EvolutionaryDatasetValidator.validate(bad).any { it.contains("synthetic datasets") })
    }
}
