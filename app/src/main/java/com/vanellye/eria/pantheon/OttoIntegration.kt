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

/** Provider-neutral integration families. These are contracts, not live connections. */
enum class ExternalActionChannel { WEBHOOK, HTTP_CALLBACK, NOTIFICATION, MESSAGE_QUEUE, GENERIC_API }

data class TriggerQualityEvidence(
    val sourceIntegrityVerified: Boolean,
    val eventOrderVerified: Boolean,
    val payloadSchemaVerified: Boolean,
    val destinationIdentityVerified: Boolean,
    val replayCheckPassed: Boolean,
    val policyChecksPassed: Boolean
) {
    fun report(): TriggerQualityReport {
        val checks = listOf(
            "source integrity not verified" to sourceIntegrityVerified,
            "event order not verified" to eventOrderVerified,
            "payload schema not verified" to payloadSchemaVerified,
            "destination identity not verified" to destinationIdentityVerified,
            "replay check failed or missing" to replayCheckPassed,
            "policy checks failed or missing" to policyChecksPassed
        )
        val passed = checks.count { it.second }
        return TriggerQualityReport(passed * 100 / checks.size, passed == checks.size,
            checks.filterNot { it.second }.map { it.first })
    }
}
data class TriggerQualityReport(val scorePercent: Int, val qualified: Boolean, val holdReasons: List<String>)

data class OttoTriggerRule(
    val ruleId: String,
    val eventType: SuspensionEventType,
    val channel: ExternalActionChannel,
    val actionKey: String,
    val targetId: String,
    val payload: Map<String, String>,
    val quality: TriggerQualityEvidence
)
data class ExternalActionTarget(val channel: ExternalActionChannel, val targetId: String)
data class ExternalActionRequest(
    val requestId: String, val threadId: String, val sourceEventId: String,
    val channel: ExternalActionChannel, val actionKey: String, val targetId: String,
    val payload: Map<String, String>, val payloadDigest: String,
    val approvalScope: String, val idempotencyKey: String
)
data class HeldTriggerRule(val ruleId: String, val quality: TriggerQualityReport)
data class TriggerEvaluationResult(
    val requests: List<ExternalActionRequest>,
    val heldRules: List<HeldTriggerRule>
)
data class ExternalActionApproval(val approvalRef: String, val scope: String, val requestDigest: String)
enum class DispatchStatus { DISPATCHED, DENIED }
data class DispatchResult(val status: DispatchStatus, val externalReceipt: String? = null, val reason: String? = null)

interface ExternalActionApprovalVerifier {
    /** Verify authenticated human identity, exact scope, and exact request digest. */
    fun verify(approval: ExternalActionApproval): Boolean
}
interface ExternalActionDispatcher {
    /** One host-configured provider adapter; it must enforce durable idempotency. */
    fun dispatch(request: ExternalActionRequest, idempotencyKey: String): String
}

/** Event detection creates qualified requests only; it never calls a provider. */
object OttoTriggerEngine {
    fun evaluate(thread: SuspensionThread, event: SuspensionEvent, rules: List<OttoTriggerRule>): TriggerEvaluationResult {
        require(thread.status != SuspensionStatus.CLOSED) { "closed thread cannot trigger actions" }
        require(thread.events.any { it == event }) { "event is not part of this thread" }
        val requests = mutableListOf<ExternalActionRequest>()
        val held = mutableListOf<HeldTriggerRule>()
        rules.filter { it.eventType == event.type }.forEach { rule ->
            require(rule.ruleId.isNotBlank() && rule.actionKey.isNotBlank() && rule.targetId.isNotBlank()) {
                "trigger rule identity, action, and target are required"
            }
            val quality = rule.quality.report()
            if (!quality.qualified) {
                held += HeldTriggerRule(rule.ruleId, quality)
            } else {
                val digest = requestDigest(thread.threadId, event.eventId, rule.channel, rule.actionKey, rule.targetId, rule.payload)
                requests += ExternalActionRequest(
                    requestId = "otto-" + digest.take(20),
                    threadId = thread.threadId,
                    sourceEventId = event.eventId,
                    channel = rule.channel,
                    actionKey = rule.actionKey,
                    targetId = rule.targetId,
                    payload = rule.payload.toSortedMap(),
                    payloadDigest = digest,
                    approvalScope = approvalScope(rule.channel, rule.actionKey, rule.targetId),
                    idempotencyKey = digest
                )
            }
        }
        return TriggerEvaluationResult(requests, held)
    }

    fun approvalScope(channel: ExternalActionChannel, actionKey: String, targetId: String) =
        "external-action:" + channel.name.lowercase() + ":" + actionKey + ":" + targetId

    fun requestDigest(
        threadId: String, eventId: String, channel: ExternalActionChannel,
        actionKey: String, targetId: String, payload: Map<String, String>
    ): String {
        val canonical = buildString {
            append(threadId).append('\n')
            append(eventId).append('\n')
            append(channel.name).append('\n')
            append(actionKey).append('\n')
            append(targetId).append('\n')
            payload.toSortedMap().forEach { (key, value) -> append(key).append('=').append(value).append('\n') }
        }
        return MessageDigest.getInstance("SHA-256").digest(canonical.toByteArray(Charsets.UTF_8))
            .joinToString("") { "%02x".format(it) }
    }
}

/** Dispatch requires a channel+target allowlist and separately authenticated, digest-bound approval. */
class ExternalActionDispatchGate(
    private val allowedTargets: Set<ExternalActionTarget>,
    private val approvalVerifier: ExternalActionApprovalVerifier,
    private val dispatcher: ExternalActionDispatcher
) {
    fun dispatchApproved(request: ExternalActionRequest, approval: ExternalActionApproval): DispatchResult {
        if (ExternalActionTarget(request.channel, request.targetId) !in allowedTargets) {
            return DispatchResult(DispatchStatus.DENIED, reason = "channel/target pair is not allowlisted")
        }
        val expectedScope = OttoTriggerEngine.approvalScope(request.channel, request.actionKey, request.targetId)
        if (request.actionKey.isBlank() || request.approvalScope != expectedScope) {
            return DispatchResult(DispatchStatus.DENIED, reason = "request approval scope is invalid")
        }
        val recomputedDigest = OttoTriggerEngine.requestDigest(
            request.threadId, request.sourceEventId, request.channel, request.actionKey, request.targetId, request.payload
        )
        if (recomputedDigest != request.payloadDigest || request.idempotencyKey != recomputedDigest ||
            request.requestId != "otto-" + recomputedDigest.take(20)) {
            return DispatchResult(DispatchStatus.DENIED, reason = "request integrity check failed")
        }
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
