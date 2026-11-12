package com.vanellye.eria.pantheon

import com.vanellye.eria.contracts.*
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Test

class PantheonRuntimeGateTest {
    private val gate = PantheonRuntimeGate()

    private fun envelope(
        status: AuthorizationStatus = AuthorizationStatus.AUTHORIZED,
        scope: List<String> = listOf("pantheon.review"),
        approval: String? = "approval-1"
    ) = DataEnvelope(
        recordId = "record-1",
        source = "test-source",
        observedAt = "2026-11-11T12:00:00Z",
        payload = mapOf("claim" to "sample"),
        units = emptyMap(),
        quality = DataQuality.VALID,
        provenance = DataProvenance(sourceRef = "source-1", sourceDigest = "a".repeat(64)),
        authorization = DataAuthorization(status, scope, approval)
    )

    @Test fun missingAuthorizationHolds() {
        val result = gate.prepareReview(envelope(AuthorizationStatus.NOT_AUTHORIZED, emptyList(), null), "pantheon.review", true)
        assertEquals(PantheonGateStatus.HOLD_NOT_AUTHORIZED, result.status)
        assertFalse(result.actionTaken)
    }

    @Test fun scopeMismatchHolds() {
        val result = gate.prepareReview(envelope(scope = listOf("pantheon.read")), "pantheon.review", true)
        assertEquals(PantheonGateStatus.HOLD_SCOPE_MISMATCH, result.status)
        assertFalse(result.actionTaken)
    }

    @Test fun humanReviewIsRequired() {
        val result = gate.prepareReview(envelope(), "pantheon.review", false)
        assertEquals(PantheonGateStatus.HOLD_REVIEW_NOT_CONFIRMED, result.status)
        assertFalse(result.actionTaken)
    }

    @Test fun validRequestOnlyPreparesReview() {
        val result = gate.prepareReview(envelope(), "pantheon.review", true)
        assertEquals(PantheonGateStatus.REVIEW_READY, result.status)
        assertEquals("approval-1", result.approvalReference)
        assertFalse(result.actionTaken)
    }

    @Test fun invalidEnvelopeHolds() {
        val result = gate.prepareReview(envelope().copy(recordId = ""), "pantheon.review", true)
        assertEquals(PantheonGateStatus.HOLD_INVALID_ENVELOPE, result.status)
        assertFalse(result.actionTaken)
    }
}
