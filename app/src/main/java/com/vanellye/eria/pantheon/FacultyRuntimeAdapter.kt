package com.vanellye.eria.pantheon

/**
 * Fail-closed Faculty authorization adapter.
 *
 * This component authorizes a narrowly scoped request for a separately
 * implemented adapter. It never invokes that adapter and never performs I/O.
 * A successful result is a preflight decision, not evidence that an operation
 * was executed.
 */
enum class FacultyCapability {
    SECRET_MANAGER_HANDLE,
    VISIBLE_USER_AUTHORIZED_PROCESS,
    AUTHENTICATED_ALLOWLISTED_DISPATCH,
    OPERATOR_CONFIRMED_HARDWARE_COMMAND,
    NON_INTERVENTIONAL_BIOLOGICAL_SIMULATION
}

enum class FacultyControl {
    APPROVED_SECRET_MANAGER,
    LEAST_PRIVILEGE,
    VISIBLE_PROCESS,
    USER_CONFIRMATION,
    RESOURCE_BOUNDS,
    AUTHENTICATED_CHANNEL,
    DESTINATION_ALLOWLISTED,
    CONSENT_CONFIRMED,
    REPLAY_PROTECTION,
    DOCUMENTED_DEVICE_API,
    OPERATOR_CONFIRMATION,
    SAFETY_INTERLOCK,
    EMERGENCY_STOP,
    LITERATURE_GROUNDED,
    SYNTHETIC_OR_APPROVED_DATA,
    NON_INTERVENTIONAL
}

enum class FacultyDecisionStatus {
    AUTHORIZED_PREFLIGHT_ONLY,
    DENIED_INVALID_REQUEST,
    DENIED_MISSING_GRANT,
    DENIED_GRANT_MISMATCH,
    DENIED_SELF_APPROVAL,
    DENIED_EXPIRED,
    DENIED_REVOKED,
    DENIED_SIGNATURE,
    DENIED_CONSENT,
    DENIED_REQUIRED_CONTROLS,
    DENIED_AUDIT_UNAVAILABLE
}

data class FacultyRuntimeRequest(
    val requestId: String,
    val requesterId: String,
    val capability: FacultyCapability,
    val scope: String,
    val resourceRef: String,
    val purpose: String,
    val consentConfirmed: Boolean,
    val controls: Set<FacultyControl>
)

/**
 * Claims must be populated by a trusted approval source. The adapter does not
 * mint grants or infer that a UI checkbox is an authenticated approval.
 */
data class FacultyApprovalGrant(
    val requestId: String,
    val requesterId: String,
    val approverId: String,
    val approvalRef: String,
    val capability: FacultyCapability,
    val scope: String,
    val resourceRef: String,
    val expiresAtEpochSeconds: Long,
    val humanApproved: Boolean,
    val revoked: Boolean,
    val signature: String
)

data class FacultyAuditEvent(
    val requestId: String,
    val capability: FacultyCapability,
    val decision: FacultyDecisionStatus,
    val approvalRef: String?,
    val reason: String
)

data class FacultyRuntimeDecision(
    val status: FacultyDecisionStatus,
    val requestId: String,
    val approvalRef: String?,
    val missingControls: Set<FacultyControl>,
    /** Always false: this adapter is authorization-only. */
    val actionTaken: Boolean = false
)

fun interface FacultyGrantVerifier {
    /** Must authenticate the grant and check its authoritative revocation state. */
    fun verify(grant: FacultyApprovalGrant): Boolean
}

fun interface FacultyAuditSink {
    /** Must durably append a redacted decision event; false means unavailable. */
    fun append(event: FacultyAuditEvent): Boolean
}

class FacultyRuntimeAdapter(
    private val grantVerifier: FacultyGrantVerifier,
    private val auditSink: FacultyAuditSink,
    private val clockEpochSeconds: () -> Long
) {
    fun authorizePreflight(
        request: FacultyRuntimeRequest,
        grant: FacultyApprovalGrant?
    ): FacultyRuntimeDecision {
        val missingControls = requiredControls(request.capability) - request.controls
        val invalid = request.requestId.isBlank() ||
            request.requesterId.isBlank() ||
            request.scope.isBlank() ||
            request.resourceRef.isBlank() ||
            request.purpose.isBlank()

        val decision = when {
            invalid -> result(request, FacultyDecisionStatus.DENIED_INVALID_REQUEST)
            grant == null -> result(request, FacultyDecisionStatus.DENIED_MISSING_GRANT)
            !matches(request, grant) -> result(request, FacultyDecisionStatus.DENIED_GRANT_MISMATCH, grant)
            grant.approverId.isBlank() || grant.approverId == request.requesterId ->
                result(request, FacultyDecisionStatus.DENIED_SELF_APPROVAL, grant)
            !request.consentConfirmed || !grant.humanApproved ->
                result(request, FacultyDecisionStatus.DENIED_CONSENT, grant)
            grant.revoked -> result(request, FacultyDecisionStatus.DENIED_REVOKED, grant)
            grant.expiresAtEpochSeconds <= clockEpochSeconds() ->
                result(request, FacultyDecisionStatus.DENIED_EXPIRED, grant)
            grant.approvalRef.isBlank() || grant.signature.isBlank() || !safeVerify(grant) ->
                result(request, FacultyDecisionStatus.DENIED_SIGNATURE, grant)
            missingControls.isNotEmpty() ->
                FacultyRuntimeDecision(
                    status = FacultyDecisionStatus.DENIED_REQUIRED_CONTROLS,
                    requestId = request.requestId,
                    approvalRef = grant.approvalRef,
                    missingControls = missingControls
                )
            else -> result(request, FacultyDecisionStatus.AUTHORIZED_PREFLIGHT_ONLY, grant)
        }

        val event = FacultyAuditEvent(
            requestId = request.requestId,
            capability = request.capability,
            decision = decision.status,
            approvalRef = decision.approvalRef,
            reason = decision.status.name
        )
        val recorded = try {
            auditSink.append(event)
        } catch (_: Exception) {
            false
        }
        return if (recorded) decision else FacultyRuntimeDecision(
            status = FacultyDecisionStatus.DENIED_AUDIT_UNAVAILABLE,
            requestId = request.requestId,
            approvalRef = decision.approvalRef,
            missingControls = decision.missingControls
        )
    }

    private fun safeVerify(grant: FacultyApprovalGrant): Boolean = try {
        grantVerifier.verify(grant)
    } catch (_: Exception) {
        false
    }

    private fun matches(request: FacultyRuntimeRequest, grant: FacultyApprovalGrant): Boolean =
        grant.requestId == request.requestId &&
            grant.requesterId == request.requesterId &&
            grant.capability == request.capability &&
            grant.scope == request.scope &&
            grant.resourceRef == request.resourceRef

    private fun result(
        request: FacultyRuntimeRequest,
        status: FacultyDecisionStatus,
        grant: FacultyApprovalGrant? = null
    ) = FacultyRuntimeDecision(
        status = status,
        requestId = request.requestId,
        approvalRef = grant?.approvalRef,
        missingControls = emptySet()
    )

    private fun requiredControls(capability: FacultyCapability): Set<FacultyControl> =
        when (capability) {
            FacultyCapability.SECRET_MANAGER_HANDLE -> setOf(
                FacultyControl.APPROVED_SECRET_MANAGER,
                FacultyControl.LEAST_PRIVILEGE
            )
            FacultyCapability.VISIBLE_USER_AUTHORIZED_PROCESS -> setOf(
                FacultyControl.VISIBLE_PROCESS,
                FacultyControl.USER_CONFIRMATION,
                FacultyControl.RESOURCE_BOUNDS
            )
            FacultyCapability.AUTHENTICATED_ALLOWLISTED_DISPATCH -> setOf(
                FacultyControl.AUTHENTICATED_CHANNEL,
                FacultyControl.DESTINATION_ALLOWLISTED,
                FacultyControl.CONSENT_CONFIRMED,
                FacultyControl.REPLAY_PROTECTION
            )
            FacultyCapability.OPERATOR_CONFIRMED_HARDWARE_COMMAND -> setOf(
                FacultyControl.DOCUMENTED_DEVICE_API,
                FacultyControl.OPERATOR_CONFIRMATION,
                FacultyControl.SAFETY_INTERLOCK,
                FacultyControl.EMERGENCY_STOP
            )
            FacultyCapability.NON_INTERVENTIONAL_BIOLOGICAL_SIMULATION -> setOf(
                FacultyControl.LITERATURE_GROUNDED,
                FacultyControl.SYNTHETIC_OR_APPROVED_DATA,
                FacultyControl.NON_INTERVENTIONAL
            )
        }
}
