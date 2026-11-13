package com.vanellye.eria.contracts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ResonantPaintingDataAdapterTest {
    private fun sample() = ResonantPaintingExport(
        recordId = "paint-test-001",
        observedAt = "2026-11-13T15:00:00Z",
        artworkSourceRef = "paintings/paint-test-001.png",
        artworkSha256 = "a".repeat(64),
        artworkBytes = 2048L,
        audioFeatures = mapOf("rms" to 0.12, "dominant_hz" to 440.0),
        paintingFeatures = mapOf("brightness" to 0.5, "stroke_count" to 3),
        style = "geometric",
        operation = "rotate",
        parametersSha256 = "b".repeat(64)
    )

    @Test fun mapsMeasurementsToStructurallyValidEnvelope() {
        val envelope = ResonantPaintingDataAdapter.toEnvelope(sample())
        assertTrue(DataEnvelopeValidator.validate(envelope).isEmpty())
        assertEquals(DataQuality.UNCALIBRATED, envelope.quality)
        assertEquals(AuthorizationStatus.NOT_AUTHORIZED, envelope.authorization.status)
        assertEquals(false, envelope.payload["microphoneAudioStored"])
        assertEquals(1, envelope.transformations.size)
    }

    @Test fun reviewGateKeepsEnvelopeOnHoldWithoutAuthorization() {
        val review = PantheonRuntimeGate().prepareReview(
            ResonantPaintingDataAdapter.toEnvelope(sample()),
            requestedScope = "eria.painting.export",
            humanReviewConfirmed = true
        )
        assertEquals(PantheonGateStatus.HOLD_NOT_AUTHORIZED, review.status)
        assertFalse(review.actionTaken)
    }
}
