package com.vanellye.eria.pantheon

import com.vanellye.eria.contracts.*
import com.vanellye.eria.pons.*
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
    @Test fun ponsProvenanceIsRequiredBeforeReviewReady() {
        val source = "verified component".toByteArray()
        val digest = PonsProvenanceGate.sha256(source)
        val pin = PonsComponentPin(
            "pantheon.runtime", "main", "app/src/main/java/com/vanellye/eria/pantheon/PantheonRuntimeGate.kt", digest
        )
        val provenance = PonsProvenanceGate(mapOf(pin.componentId to pin))
            .verify(pin.componentId, source)
        val record = envelope().copy(provenance = DataProvenance(sourceDigest = digest))
        val result = gate.prepareReviewWithPons(record, "pantheon.review", true, provenance)
        assertEquals(PantheonGateStatus.REVIEW_READY, result.status)
        assertFalse(result.actionTaken)
    }

    @Test fun missingPonsEvidenceHolds() {
        val provenance = PonsProvenanceGate(emptyMap()).verify("pantheon.runtime", null)
        val result = gate.prepareReviewWithPons(envelope(), "pantheon.review", true, provenance)
        assertEquals(PantheonGateStatus.HOLD_PROVENANCE, result.status)
        assertFalse(result.actionTaken)
    }

}
