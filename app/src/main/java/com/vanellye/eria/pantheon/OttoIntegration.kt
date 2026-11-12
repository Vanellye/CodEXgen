package com.vanellye.eria.pantheon

import java.security.MessageDigest

enum class OttoStage { OBSERVE, ACCOUNT, REFLECT, REFINE, RESTORE, RECONCILE, REPEAT }
enum class OttoCycleStatus { QUALIFIED, HELD }

data class OttoCycleInput(
    val sourceRef: String, val payloadDigest: String, val reusablePatternRef: String,
    val testsPassed: Boolean, val dependenciesResolved: Boolean, val destinationVerified: Boolean
)
data class OttoCycleReport(
    val cycleNumber: Int, val stages: List<OttoStage>, val status: OttoCycleStatus,
    val holdReasons: List<String>, val sourceRef: String, val reusablePatternRef: String
)

/** Bounded qualification loop only: no copying, publishing, branch mutation, or dispatch. */
object OttoCoordinator {
    fun runBoundedCycles(input: OttoCycleInput, maxCycles: Int): List<OttoCycleReport> {
        require(maxCycles in 1..8) { "maxCycles must be between 1 and 8" }
        val reasons = mutableListOf<String>()
        if (input.sourceRef.isBlank()) reasons += "source reference missing"
        if (!Regex("^[0-9a-f]{64}$").matches(input.payloadDigest)) reasons += "payload fingerprint invalid"
        if (input.reusablePatternRef.isBlank()) reasons += "reusable pattern reference missing"
        if (!input.testsPassed) reasons += "tests not passed"
        if (!input.dependenciesResolved) reasons += "dependencies unresolved"
        if (!input.destinationVerified) reasons += "destination not verified"
        val qualified = reasons.isEmpty()
        val stages = listOf(OttoStage.OBSERVE, OttoStage.ACCOUNT, OttoStage.REFLECT, OttoStage.REFINE, OttoStage.RESTORE, OttoStage.RECONCILE, OttoStage.REPEAT)
        val reports = mutableListOf<OttoCycleReport>()
        for (cycle in 1..maxCycles) {
            reports += OttoCycleReport(cycle, stages, if (qualified) OttoCycleStatus.QUALIFIED else OttoCycleStatus.HELD, reasons.toList(), input.sourceRef, input.reusablePatternRef)
            if (!qualified) break
        }
        return reports
    }
}

data class OttoTriggerRule(
    val ruleId: String, val eventType: SuspensionEventType, val actionKey: String,
    val targetId: String, val payload: Map<String, String>
)
data class ExternalActionRequest(
    val requestId: String, val threadId: String, val sourceEventId: String,
    val actionKey: String, val targetId: String, val payload: Map<String, String>,
    val payloadDigest: String, val approvalScope: String, val idempotencyKey: String
)
data class ExternalActionApproval(val approvalRef: String, val scope: String, val requestDigest: String)
enum class DispatchStatus { DISPATCHED, DENIED }
data class DispatchResult(val status: DispatchStatus, val externalReceipt: String? = null, val reason: String? = null)

interface ExternalActionApprovalVerifier {
    /** Verify authenticated human identity, exact scope, and exact request digest. */
    fun verify(approval: ExternalActionApproval): Boolean
}
interface ExternalActionDispatcher {
    /** Provider adapter must enforce durable idempotency for the supplied key. */
    fun dispatch(request: ExternalActionRequest, idempotencyKey: String): String
}

/** Event detection produces requests only; dispatch is a separate, approval-gated operation. */
object OttoTriggerEngine {
    fun evaluate(thread: SuspensionThread, event: SuspensionEvent, rules: List<OttoTriggerRule>): List<ExternalActionRequest> {
        require(thread.status != SuspensionStatus.CLOSED) { "closed thread cannot trigger actions" }
        require(thread.events.any { it.eventId == event.eventId }) { "event is not part of this thread" }
        return rules.filter { it.eventType == event.type }.map { rule ->
            require(rule.ruleId.isNotBlank() && rule.actionKey.isNotBlank() && rule.targetId.isNotBlank()) {
                "trigger rule identity, action, and target are required"
            }
            val digest = requestDigest(thread.threadId, event.eventId, rule.actionKey, rule.targetId, rule.payload)
            ExternalActionRequest(
                requestId = "otto-" + digest.take(20),
                threadId = thread.threadId,
                sourceEventId = event.eventId,
                actionKey = rule.actionKey,
                targetId = rule.targetId,
                payload = rule.payload.toSortedMap(),
                payloadDigest = digest,
                approvalScope = "external-action:" + rule.actionKey + ":" + rule.targetId,
                idempotencyKey = digest
            )
        }
    }

    fun requestDigest(threadId: String, eventId: String, actionKey: String, targetId: String, payload: Map<String, String>): String {
        val canonical = buildString {
            append(threadId).append('\n')
            append(eventId).append('\n')
            append(actionKey).append('\n')
            append(targetId).append('\n')
            payload.toSortedMap().forEach { (key, value) -> append(key).append('=').append(value).append('\n') }
        }
        return MessageDigest.getInstance("SHA-256").digest(canonical.toByteArray(Charsets.UTF_8))
            .joinToString("") { "%02x".format(it) }
    }
}

class ExternalActionDispatchGate(
    private val allowedTargets: Set<String>,
    private val approvalVerifier: ExternalActionApprovalVerifier,
    private val dispatcher: ExternalActionDispatcher
) {
    fun dispatchApproved(request: ExternalActionRequest, approval: ExternalActionApproval): DispatchResult {
        if (request.targetId !in allowedTargets) return DispatchResult(DispatchStatus.DENIED, reason = "target is not allowlisted")
        if (approval.scope != request.approvalScope || approval.requestDigest != request.payloadDigest) {
            return DispatchResult(DispatchStatus.DENIED, reason = "approval scope or request digest mismatch")
        }
        if (approval.approvalRef.isBlank() || !approvalVerifier.verify(approval)) {
            return DispatchResult(DispatchStatus.DENIED, reason = "authenticated approval was not verified")
        }
        return try {
            DispatchResult(DispatchStatus.DISPATCHED, externalReceipt = dispatcher.dispatch(request, request.idempotencyKey))
        } catch (failure: Exception) {
            DispatchResult(DispatchStatus.DENIED, reason = "dispatcher failed: " + failure.javaClass.simpleName)
        }
    }
}
