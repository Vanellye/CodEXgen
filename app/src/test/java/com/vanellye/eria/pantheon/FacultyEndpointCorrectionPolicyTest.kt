package com.vanellye.eria.pantheon

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Test

class FacultyEndpointCorrectionPolicyTest {
    private val policy = FacultyEndpointCorrectionPolicy()
    private val corrections = setOf(
        EndpointCorrection.AUTHENTICATED_PROVIDER, EndpointCorrection.DESTINATION_ALLOWLIST,
        EndpointCorrection.PAYLOAD_PURPOSE_REVIEW, EndpointCorrection.CONSENT_CONFIRMATION,
        EndpointCorrection.REPLAY_PROTECTION, EndpointCorrection.ENDPOINT_HEALTH_AND_IDENTITY)
    private val input = EndpointValidation(
        requestId = "endpoint-req-1", requesterId = "requester",
        capability = EndpointCapability.EXTERNAL_DISPATCH, scope = "dispatch:one-endpoint",
        endpointRef = "provider://allowlisted/endpoint", manifestDigest = "sha256:abc123",
        passedCorrections = corrections, failedCorrections = emptySet())

    private fun grant() = FacultyApprovalGrant(
        requestId = input.requestId, requesterId = input.requesterId,
        approverId = "independent-reviewer", approvalRef = "faculty-approval-1",
        capability = FacultyCapability.AUTHENTICATED_ALLOWLISTED_DISPATCH,
        scope = input.scope, resourceRef = input.endpointRef, expiresAtEpochSeconds = 2_000L,
        humanApproved = true, revoked = false, signature = "signed-grant")

    @Test fun validationAndEligibilityAreSeparateFromActivation() {
        val validation = policy.validate(input)
        assertEquals(EndpointStageStatus.VALIDATION_PASSED, validation.status)
        val eligibility = policy.evaluateEligibility(input, validation)
        assertEquals(EndpointStageStatus.ELIGIBLE, eligibility.status)
        assertFalse(eligibility.actionTaken)
    }
    @Test fun missingCorrectionBlocksEligibility() {
        val incomplete = input.copy(passedCorrections = corrections - EndpointCorrection.REPLAY_PROTECTION)
        val validation = policy.validate(incomplete)
        assertEquals(EndpointStageStatus.VALIDATION_FAILED, validation.status)
        assertEquals(EndpointStageStatus.NOT_ELIGIBLE, policy.evaluateEligibility(incomplete, validation).status)
    }
    @Test fun failedCorrectionBlocksEligibility() {
        val failed = input.copy(failedCorrections = setOf(EndpointCorrection.CONSENT_CONFIRMATION))
        assertEquals(EndpointStageStatus.VALIDATION_FAILED, policy.validate(failed).status)
    }
    @Test fun activationNeedsIndependentVerifiedGrantAndAudit() {
        val validation = policy.validate(input)
        val eligible = policy.evaluateEligibility(input, validation)
        assertEquals(EndpointStageStatus.ACTIVATION_AUTHORIZED,
            policy.authorizeActivation(input, eligible, grant(), 1_000L, true, true).status)
        assertEquals(EndpointStageStatus.ACTIVATION_DENIED,
            policy.authorizeActivation(input, eligible, grant(), 1_000L, false, true).status)
        assertEquals(EndpointStageStatus.ACTIVATION_DENIED,
            policy.authorizeActivation(input, eligible, grant(), 1_000L, true, false).status)
    }
    @Test fun expiredGrantCannotActivate() {
        val validation = policy.validate(input)
        val eligible = policy.evaluateEligibility(input, validation)
        assertEquals(EndpointStageStatus.ACTIVATION_DENIED, policy.authorizeActivation(
            input, eligible, grant().copy(expiresAtEpochSeconds = 1_000L), 1_000L, true, true).status)
    }
    @Test fun biologicalInterventionIsProhibited() {
        val intervention = input.copy(capability = EndpointCapability.BIOLOGICAL_INTERVENTION)
        assertEquals(EndpointStageStatus.PROHIBITED, policy.validate(intervention).status)
        assertEquals(EndpointStageStatus.PROHIBITED, policy.authorizeActivation(
            intervention, EndpointStageResult(EndpointStageStatus.ELIGIBLE, intervention.requestId),
            grant(), 1L, true, true).status)
    }
}
