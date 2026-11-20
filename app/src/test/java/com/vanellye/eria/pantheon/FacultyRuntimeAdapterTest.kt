package com.vanellye.eria.pantheon

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class FacultyRuntimeAdapterTest {
    private val events = mutableListOf<FacultyAuditEvent>()
    private var auditAvailable = true
    private var signatureValid = true
    private val adapter = FacultyRuntimeAdapter(
        grantVerifier = FacultyGrantVerifier { signatureValid },
        auditSink = FacultyAuditSink { event ->
            if (auditAvailable) events.add(event)
            auditAvailable
        },
        clockEpochSeconds = { 1_000L }
    )

    private val request = FacultyRuntimeRequest(
        requestId = "req-17",
        requesterId = "operator-A",
        capability = FacultyCapability.AUTHENTICATED_ALLOWLISTED_DISPATCH,
        scope = "dispatch:partner-status",
        resourceRef = "provider://approved/status-hook",
        purpose = "Send an explicitly approved status update",
        consentConfirmed = true,
        controls = setOf(
            FacultyControl.AUTHENTICATED_CHANNEL,
            FacultyControl.DESTINATION_ALLOWLISTED,
            FacultyControl.CONSENT_CONFIRMED,
            FacultyControl.REPLAY_PROTECTION
        )
    )

    private fun grant(
        approver: String = "reviewer-B",
        expiry: Long = 2_000L,
        revoked: Boolean = false
    ) = FacultyApprovalGrant(
        requestId = request.requestId,
        requesterId = request.requesterId,
        approverId = approver,
        approvalRef = "approval-17",
        capability = request.capability,
        scope = request.scope,
        resourceRef = request.resourceRef,
        expiresAtEpochSeconds = expiry,
        humanApproved = true,
        revoked = revoked,
        signature = "opaque-signed-grant"
    )

    @Test fun validGrantAuthorizesPreflightOnlyAndAudits() {
        val result = adapter.authorizePreflight(request, grant())
        assertEquals(FacultyDecisionStatus.AUTHORIZED_PREFLIGHT_ONLY, result.status)
        assertFalse(result.actionTaken)
        assertEquals(1, events.size)
    }

    @Test fun missingGrantIsDenied() {
        val result = adapter.authorizePreflight(request, null)
        assertEquals(FacultyDecisionStatus.DENIED_MISSING_GRANT, result.status)
        assertFalse(result.actionTaken)
    }

    @Test fun scopeOrResourceMismatchIsDenied() {
        val mismatched = grant().copy(resourceRef = "provider://other")
        val result = adapter.authorizePreflight(request, mismatched)
        assertEquals(FacultyDecisionStatus.DENIED_GRANT_MISMATCH, result.status)
    }

    @Test fun requesterCannotApproveOwnRequest() {
        val result = adapter.authorizePreflight(request, grant(approver = request.requesterId))
        assertEquals(FacultyDecisionStatus.DENIED_SELF_APPROVAL, result.status)
    }

    @Test fun expiredAndRevokedGrantsAreDenied() {
        assertEquals(
            FacultyDecisionStatus.DENIED_EXPIRED,
            adapter.authorizePreflight(request, grant(expiry = 1_000L)).status
        )
        assertEquals(
            FacultyDecisionStatus.DENIED_REVOKED,
            adapter.authorizePreflight(request, grant(revoked = true)).status
        )
    }

    @Test fun invalidSignatureIsDenied() {
        signatureValid = false
        val result = adapter.authorizePreflight(request, grant())
        assertEquals(FacultyDecisionStatus.DENIED_SIGNATURE, result.status)
    }

    @Test fun missingSafetyControlsAreDenied() {
        val incomplete = request.copy(controls = setOf(FacultyControl.AUTHENTICATED_CHANNEL))
        val result = adapter.authorizePreflight(incomplete, grant())
        assertEquals(FacultyDecisionStatus.DENIED_REQUIRED_CONTROLS, result.status)
        assertTrue(result.missingControls.contains(FacultyControl.DESTINATION_ALLOWLISTED))
    }

    @Test fun unavailableAuditSinkFailsClosed() {
        auditAvailable = false
        val result = adapter.authorizePreflight(request, grant())
        assertEquals(FacultyDecisionStatus.DENIED_AUDIT_UNAVAILABLE, result.status)
        assertFalse(result.actionTaken)
    }

    @Test fun verifierExceptionFailsClosed() {
        signatureValid = false
        val result = adapter.authorizePreflight(request, grant())
        assertEquals(FacultyDecisionStatus.DENIED_SIGNATURE, result.status)
    }
}
