package com.vanellye.eria.pantheon

import java.security.MessageDigest

enum class SleepState { ASLEEP, AWAKE }
enum class ProtectedTriggerDisposition {
    HELD_CHECKPOINT_INTEGRITY,
    HELD_TRANSMISSION_MISMATCH,
    HELD_SLEEP,
    HELD_THREAD_SUSPENDED,
    HELD_QUALITY,
    READY_FOR_OTTO_REVIEW
}

data class SleepCheckpoint(
    val checkpointId: String,
    val threadId: String,
    val transmissionId: String,
    val sourceRef: String,
    val transmissionReceivedAt: String,
    val payloadDigest: String,
    val capturedAt: String,
    val permissionSnapshotDigest: String,
    val recoveryRef: String,
    val previousCheckpointId: String?,
    val checkpointDigest: String,
    val state: SleepState
)

data class SleepWakeApproval(
    val approvalRef: String,
    val scope: String,
    val humanConfirmed: Boolean
)
data class SleepRecoveryEvidence(
    val sourceTransmissionVerified: Boolean,
    val checkpointIntegrityVerified: Boolean,
    val permissionsRestored: Boolean,
    val recoveryTestPassed: Boolean
) {
    fun holdReasons(): List<String> = buildList {
        if (!sourceTransmissionVerified) add("source transmission not verified")
        if (!checkpointIntegrityVerified) add("checkpoint integrity not verified")
        if (!permissionsRestored) add("permission snapshot not restored")
        if (!recoveryTestPassed) add("recovery test not passed")
    }
}
data class SleepWakeResult(
    val checkpoint: SleepCheckpoint,
    val resumed: Boolean,
    val holdReasons: List<String>
)

interface SleepWakeApprovalVerifier {
    /** Verify authenticated human identity and exact checkpoint-scoped approval. */
    fun verify(approval: SleepWakeApproval): Boolean
}

data class ProtectedTransmissionTrigger(
    val triggerId: String,
    val threadId: String,
    val transmissionId: String,
    val sourceRef: String,
    val payloadDigest: String,
    val sourceEventId: String,
    val quality: TriggerQualityEvidence
)
data class ProtectedTriggerEvaluation(
    val triggerId: String,
    val disposition: ProtectedTriggerDisposition,
    val quality: TriggerQualityReport,
    val holdReasons: List<String>
)

/**
 * Sleep is a checkpoint/suspension boundary, not a background actor.
 * It never wakes itself or dispatches a protected trigger.
 */
object SleepEngine {
    fun createCheckpoint(
        thread: SuspensionThread,
        checkpointId: String,
        capturedAt: String,
        permissionSnapshotDigest: String,
        recoveryRef: String,
        previousCheckpointId: String? = null
    ): SleepCheckpoint {
        require(thread.status != SuspensionStatus.CLOSED) { "closed threads cannot be checkpointed" }
        require(thread.origin.validate().isEmpty()) { thread.origin.validate().joinToString() }
        require(checkpointId.isNotBlank() && capturedAt.isNotBlank() && recoveryRef.isNotBlank()) {
            "checkpoint identity, capture time, and recovery reference are required"
        }
        require(Regex("^[0-9a-f]{64}$").matches(permissionSnapshotDigest)) {
            "permissionSnapshotDigest must be lowercase SHA-256"
        }
        require(previousCheckpointId != checkpointId) { "checkpoint cannot reference itself" }
        val digest = checkpointDigest(
            checkpointId, thread.threadId, thread.origin, capturedAt,
            permissionSnapshotDigest, recoveryRef, previousCheckpointId
        )
        return SleepCheckpoint(
            checkpointId, thread.threadId, thread.origin.transmissionId, thread.origin.sourceRef,
            thread.origin.receivedAt, thread.origin.payloadDigest, capturedAt, permissionSnapshotDigest, recoveryRef,
            previousCheckpointId, digest, SleepState.ASLEEP
        )
    }

    fun verifyCheckpoint(checkpoint: SleepCheckpoint): Boolean {
        val origin = TransmissionOrigin(
            checkpoint.transmissionId, checkpoint.sourceRef, checkpoint.transmissionReceivedAt, checkpoint.payloadDigest
        )
        if (origin.validate().isNotEmpty() || checkpoint.checkpointId.isBlank() || checkpoint.threadId.isBlank() ||
            checkpoint.capturedAt.isBlank() || checkpoint.recoveryRef.isBlank() || checkpoint.previousCheckpointId == checkpoint.checkpointId ||
            !Regex("^[0-9a-f]{64}$").matches(checkpoint.permissionSnapshotDigest)) return false
        val expected = checkpointDigest(
            checkpoint.checkpointId, checkpoint.threadId, origin, checkpoint.capturedAt,
            checkpoint.permissionSnapshotDigest, checkpoint.recoveryRef, checkpoint.previousCheckpointId
        )
        return expected == checkpoint.checkpointDigest
    }

    fun resume(
        checkpoint: SleepCheckpoint,
        thread: SuspensionThread,
        evidence: SleepRecoveryEvidence,
        approval: SleepWakeApproval,
        verifier: SleepWakeApprovalVerifier
    ): SleepWakeResult {
        val reasons = mutableListOf<String>()
        if (checkpoint.state != SleepState.ASLEEP) reasons += "checkpoint is not asleep"
        if (!verifyCheckpoint(checkpoint)) reasons += "checkpoint integrity verification failed"
        if (thread.status == SuspensionStatus.CLOSED) reasons += "transmission thread is closed"
        if (checkpoint.threadId != thread.threadId || !matchesOrigin(checkpoint, thread.origin)) {
            reasons += "checkpoint does not match the current transmission thread"
        }
        reasons += evidence.holdReasons()
        val expectedScope = "sleep.resume:${checkpoint.checkpointId}"
        if (!approval.humanConfirmed || approval.approvalRef.isBlank() || approval.scope != expectedScope) {
            reasons += "human approval or exact checkpoint scope is missing"
        } else if (!verifier.verify(approval)) {
            reasons += "authenticated human approval was not verified"
        }
        if (reasons.isNotEmpty()) return SleepWakeResult(checkpoint, false, reasons.distinct())
        return SleepWakeResult(checkpoint.copy(state = SleepState.AWAKE), true, emptyList())
    }

    fun evaluateProtectedTrigger(
        checkpoint: SleepCheckpoint,
        thread: SuspensionThread,
        trigger: ProtectedTransmissionTrigger
    ): ProtectedTriggerEvaluation {
        val quality = trigger.quality.report()
        fun held(disposition: ProtectedTriggerDisposition, reasons: List<String>) =
            ProtectedTriggerEvaluation(trigger.triggerId, disposition, quality, reasons)
        if (!verifyCheckpoint(checkpoint)) {
            return held(ProtectedTriggerDisposition.HELD_CHECKPOINT_INTEGRITY, listOf("checkpoint integrity verification failed"))
        }
        if (trigger.triggerId.isBlank() || trigger.sourceEventId.isBlank() ||
            checkpoint.threadId != thread.threadId || !matchesOrigin(checkpoint, thread.origin) ||
            trigger.threadId != thread.threadId || trigger.transmissionId != thread.origin.transmissionId ||
            trigger.sourceRef != thread.origin.sourceRef || trigger.payloadDigest != thread.origin.payloadDigest ||
            thread.events.none { it.eventId == trigger.sourceEventId }) {
            return held(ProtectedTriggerDisposition.HELD_TRANSMISSION_MISMATCH,
                listOf("trigger does not match the checkpointed transmission and thread event"))
        }
        if (checkpoint.state == SleepState.ASLEEP) {
            return held(ProtectedTriggerDisposition.HELD_SLEEP, listOf("protected trigger held while Sleep Engine is asleep"))
        }
        if (thread.status != SuspensionStatus.ACTIVE) {
            return held(ProtectedTriggerDisposition.HELD_THREAD_SUSPENDED, listOf("transmission thread is not active"))
        }
        if (!quality.qualified) {
            return held(ProtectedTriggerDisposition.HELD_QUALITY, quality.holdReasons)
        }
        return held(ProtectedTriggerDisposition.READY_FOR_OTTO_REVIEW, emptyList())
    }

    private fun matchesOrigin(checkpoint: SleepCheckpoint, origin: TransmissionOrigin): Boolean =
        checkpoint.transmissionId == origin.transmissionId &&
            checkpoint.sourceRef == origin.sourceRef &&
            checkpoint.payloadDigest == origin.payloadDigest

    private fun checkpointDigest(
        checkpointId: String, threadId: String, origin: TransmissionOrigin, capturedAt: String,
        permissionSnapshotDigest: String, recoveryRef: String, previousCheckpointId: String?
    ): String {
        val canonical = listOf(
            checkpointId, threadId, origin.transmissionId, origin.sourceRef, origin.receivedAt,
            origin.payloadDigest, capturedAt, permissionSnapshotDigest, recoveryRef, previousCheckpointId.orEmpty()
        ).joinToString("\n")
        return MessageDigest.getInstance("SHA-256").digest(canonical.toByteArray(Charsets.UTF_8))
            .joinToString("") { "%02x".format(it) }
    }
}
