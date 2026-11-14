package com.vanellye.eria.pantheon

/** Three distinct stages; no stage performs an external or physical action. */
enum class EndpointCapability { EXTERNAL_DISPATCH, HARDWARE_ACTIVATION, BIOLOGICAL_RESEARCH_SIMULATION, BIOLOGICAL_INTERVENTION }
enum class EndpointCorrection {
    AUTHENTICATED_PROVIDER, DESTINATION_ALLOWLIST, PAYLOAD_PURPOSE_REVIEW, CONSENT_CONFIRMATION,
    REPLAY_PROTECTION, ENDPOINT_HEALTH_AND_IDENTITY, DOCUMENTED_DEVICE_API, DEVICE_IDENTITY,
    BOUNDED_COMMAND_MANIFEST, OPERATOR_CONFIRMATION, SAFETY_INTERLOCK, EMERGENCY_STOP,
    LITERATURE_PROVENANCE_REVIEW, MODEL_ASSUMPTIONS_UNCERTAINTY, APPROVED_OR_SYNTHETIC_DATA,
    NON_INTERVENTIONAL_SCOPE, ENDPOINT_MODEL_VALIDATION
}
enum class EndpointStageStatus {
    VALIDATION_PASSED, VALIDATION_FAILED, ELIGIBLE, NOT_ELIGIBLE,
    ACTIVATION_AUTHORIZED, ACTIVATION_DENIED, PROHIBITED
}
data class EndpointValidation(
    val requestId: String,
    val requesterId: String,
    val capability: EndpointCapability,
    val scope: String,
    val endpointRef: String,
    val manifestDigest: String,
    val passedCorrections: Set<EndpointCorrection>,
    val failedCorrections: Set<EndpointCorrection>
)
data class EndpointStageResult(
    val status: EndpointStageStatus,
    val requestId: String,
    val missingCorrections: Set<EndpointCorrection> = emptySet(),
    val actionTaken: Boolean = false
)

class FacultyEndpointCorrectionPolicy {
    fun validate(input: EndpointValidation): EndpointStageResult {
        if (input.capability == EndpointCapability.BIOLOGICAL_INTERVENTION)
            return EndpointStageResult(EndpointStageStatus.PROHIBITED, input.requestId)
        if (input.requestId.isBlank() || input.requesterId.isBlank() || input.scope.isBlank() ||
            input.endpointRef.isBlank() || input.manifestDigest.isBlank() || input.failedCorrections.isNotEmpty())
            return EndpointStageResult(EndpointStageStatus.VALIDATION_FAILED, input.requestId,
                required(input.capability) - input.passedCorrections)
        val missing = required(input.capability) - input.passedCorrections
        return if (missing.isEmpty()) EndpointStageResult(EndpointStageStatus.VALIDATION_PASSED, input.requestId)
        else EndpointStageResult(EndpointStageStatus.VALIDATION_FAILED, input.requestId, missing)
    }

    fun evaluateEligibility(input: EndpointValidation, validation: EndpointStageResult): EndpointStageResult {
        if (input.capability == EndpointCapability.BIOLOGICAL_INTERVENTION)
            return EndpointStageResult(EndpointStageStatus.PROHIBITED, input.requestId)
        val complete = validation.status == EndpointStageStatus.VALIDATION_PASSED &&
            validation.requestId == input.requestId && input.failedCorrections.isEmpty() &&
            required(input.capability).all { it in input.passedCorrections }
        return if (complete) EndpointStageResult(EndpointStageStatus.ELIGIBLE, input.requestId)
        else EndpointStageResult(EndpointStageStatus.NOT_ELIGIBLE, input.requestId,
            required(input.capability) - input.passedCorrections)
    }

    /** Final authorization decision only; no runnable handle or side effect is returned. */
    fun authorizeActivation(
        input: EndpointValidation,
        eligibility: EndpointStageResult,
        grant: FacultyApprovalGrant?,
        nowEpochSeconds: Long,
        independentGrantVerified: Boolean,
        auditRecorded: Boolean
    ): EndpointStageResult {
        if (input.capability == EndpointCapability.BIOLOGICAL_INTERVENTION)
            return EndpointStageResult(EndpointStageStatus.PROHIBITED, input.requestId)
        val eligible = eligibility.status == EndpointStageStatus.ELIGIBLE &&
            eligibility.requestId == input.requestId
        val expectedCapability = when (input.capability) {
            EndpointCapability.EXTERNAL_DISPATCH -> FacultyCapability.AUTHENTICATED_ALLOWLISTED_DISPATCH
            EndpointCapability.HARDWARE_ACTIVATION -> FacultyCapability.OPERATOR_CONFIRMED_HARDWARE_COMMAND
            EndpointCapability.BIOLOGICAL_RESEARCH_SIMULATION -> FacultyCapability.NON_INTERVENTIONAL_BIOLOGICAL_SIMULATION
            EndpointCapability.BIOLOGICAL_INTERVENTION -> return EndpointStageResult(EndpointStageStatus.PROHIBITED, input.requestId)
        }
        val validGrant = grant != null &&
            grant.requestId == input.requestId && grant.requesterId == input.requesterId &&
            grant.capability == expectedCapability && grant.scope == input.scope &&
            grant.resourceRef == input.endpointRef && grant.humanApproved && !grant.revoked &&
            grant.approverId.isNotBlank() && grant.approverId != input.requesterId &&
            grant.expiresAtEpochSeconds > nowEpochSeconds && grant.approvalRef.isNotBlank() &&
            grant.signature.isNotBlank() && independentGrantVerified
        return if (eligible && validGrant && auditRecorded)
            EndpointStageResult(EndpointStageStatus.ACTIVATION_AUTHORIZED, input.requestId)
        else EndpointStageResult(EndpointStageStatus.ACTIVATION_DENIED, input.requestId,
            required(input.capability) - input.passedCorrections)
    }

    private fun required(capability: EndpointCapability): Set<EndpointCorrection> = when (capability) {
        EndpointCapability.EXTERNAL_DISPATCH -> setOf(
            EndpointCorrection.AUTHENTICATED_PROVIDER, EndpointCorrection.DESTINATION_ALLOWLIST,
            EndpointCorrection.PAYLOAD_PURPOSE_REVIEW, EndpointCorrection.CONSENT_CONFIRMATION,
            EndpointCorrection.REPLAY_PROTECTION, EndpointCorrection.ENDPOINT_HEALTH_AND_IDENTITY)
        EndpointCapability.HARDWARE_ACTIVATION -> setOf(
            EndpointCorrection.DOCUMENTED_DEVICE_API, EndpointCorrection.DEVICE_IDENTITY,
            EndpointCorrection.BOUNDED_COMMAND_MANIFEST, EndpointCorrection.OPERATOR_CONFIRMATION,
            EndpointCorrection.SAFETY_INTERLOCK, EndpointCorrection.EMERGENCY_STOP,
            EndpointCorrection.ENDPOINT_HEALTH_AND_IDENTITY)
        EndpointCapability.BIOLOGICAL_RESEARCH_SIMULATION -> setOf(
            EndpointCorrection.LITERATURE_PROVENANCE_REVIEW, EndpointCorrection.MODEL_ASSUMPTIONS_UNCERTAINTY,
            EndpointCorrection.APPROVED_OR_SYNTHETIC_DATA, EndpointCorrection.NON_INTERVENTIONAL_SCOPE,
            EndpointCorrection.ENDPOINT_MODEL_VALIDATION)
        EndpointCapability.BIOLOGICAL_INTERVENTION -> emptySet()
    }
}
