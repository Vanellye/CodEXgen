package com.vanellye.eria.pantheon

import com.vanellye.eria.contracts.AuthorizationStatus
import com.vanellye.eria.contracts.DataEnvelope
import com.vanellye.eria.contracts.DataEnvelopeValidator
import com.vanellye.eria.pons.PonsProvenanceResult
import com.vanellye.eria.pons.PonsProvenanceState

/**
 * Android runtime boundary for Pantheon.
 *
 * This adapter can validate an envelope and prepare a human-review record only.
 * It has deliberately no executor, wallet/provider client, filesystem writer,
 * process launcher, network client, or Git mutation capability.
 */
enum class PantheonGateStatus {
    HOLD_INVALID_ENVELOPE,
    HOLD_NOT_AUTHORIZED,
    HOLD_SCOPE_MISMATCH,
    HOLD_REVIEW_NOT_CONFIRMED,
    HOLD_PROVENANCE,
    REVIEW_READY
}

data class PantheonReview(
    val status: PantheonGateStatus,
    val recordId: String,
    val requestedScope: String,
    val approvalReference: String?,
    val validationErrors: List<String>,
    val actionTaken: Boolean = false
)

class PantheonRuntimeGate {
    fun prepareReview(
        envelope: DataEnvelope,
        requestedScope: String,
        humanReviewConfirmed: Boolean
    ): PantheonReview {
        val errors = DataEnvelopeValidator.validate(envelope)
        if (errors.isNotEmpty()) {
            return result(PantheonGateStatus.HOLD_INVALID_ENVELOPE, envelope, requestedScope, errors)
        }
        if (envelope.authorization.status != AuthorizationStatus.AUTHORIZED) {
            return result(PantheonGateStatus.HOLD_NOT_AUTHORIZED, envelope, requestedScope)
        }
        if (requestedScope.isBlank() ||
            envelope.authorization.scope.isEmpty() ||
            envelope.authorization.scope.any { it != requestedScope }
        ) {
            return result(PantheonGateStatus.HOLD_SCOPE_MISMATCH, envelope, requestedScope)
        }
        if (!humanReviewConfirmed) {
            return result(PantheonGateStatus.HOLD_REVIEW_NOT_CONFIRMED, envelope, requestedScope)
        }
        // REVIEW_READY is not permission to execute. It only permits presentation
        // of the validated proposal to a person for a separate decision.
        return result(PantheonGateStatus.REVIEW_READY, envelope, requestedScope)
    }

    /** PONS must independently verify the component bytes before review can proceed. */
    fun prepareReviewWithPons(
        envelope: DataEnvelope,
        requestedScope: String,
        humanReviewConfirmed: Boolean,
        provenance: PonsProvenanceResult
    ): PantheonReview {
        if (provenance.state != PonsProvenanceState.VERIFIED ||
            provenance.actualSha256 == null ||
            envelope.provenance.sourceDigest != provenance.actualSha256
        ) {
            return result(PantheonGateStatus.HOLD_PROVENANCE, envelope, requestedScope)
        }
        return prepareReview(envelope, requestedScope, humanReviewConfirmed)
    }

    private fun result(
        status: PantheonGateStatus,
        envelope: DataEnvelope,
        scope: String,
        errors: List<String> = emptyList()
    ) = PantheonReview(
        status = status,
        recordId = envelope.recordId,
        requestedScope = scope,
        approvalReference = envelope.authorization.approvalRef,
        validationErrors = errors,
        actionTaken = false
    )
}
