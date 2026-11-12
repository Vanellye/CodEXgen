package com.vanellye.eria.pantheon

import org.junit.Assert.*
import org.junit.Test

class SleepEngineTest {
    private val quality = TriggerQualityEvidence(true, true, true, true, true, true)
    private val origin = TransmissionOrigin("tx-sleep", "gateway.transmission", "2026-11-12T10:00:00Z", "a".repeat(64))
    private fun event(type: SuspensionEventType, id: String) =
        SuspensionEvent(id, type, "2026-11-12T10:01:00Z", "operator", "test event")
    private fun thread() = SuspensionThread.fromTransmission("thread-sleep", origin, event(SuspensionEventType.THREAD_CREATED, "event-created"))
    private fun checkpoint(thread: SuspensionThread = thread()) =
        SleepEngine.createCheckpoint(thread, "checkpoint-1", "2026-11-12T10:02:00Z", "b".repeat(64), "recovery://checkpoint-1")
    private fun trigger(thread: SuspensionThread, evidence: TriggerQualityEvidence = quality) =
        ProtectedTransmissionTrigger("trigger-1", thread.threadId, thread.origin.transmissionId,
            thread.origin.sourceRef, thread.origin.payloadDigest, thread.events.first().eventId, evidence)
    private val verifier = object : SleepWakeApprovalVerifier {
        override fun verify(approval: SleepWakeApproval) = approval.approvalRef == "approved-by-human"
    }
    private fun approval(checkpoint: SleepCheckpoint) =
        SleepWakeApproval("approved-by-human", "sleep.resume:${checkpoint.checkpointId}", true)
    private val completeEvidence = SleepRecoveryEvidence(true, true, true, true)

    @Test fun checkpointRetainsExactTransmissionOriginAndVerifiesDigest() {
        val thread = thread()
        val checkpoint = checkpoint(thread)
        assertEquals(thread.origin.transmissionId, checkpoint.transmissionId)
        assertEquals(thread.origin.sourceRef, checkpoint.sourceRef)
        assertEquals(thread.origin.receivedAt, checkpoint.transmissionReceivedAt)
        assertEquals(thread.origin.payloadDigest, checkpoint.payloadDigest)
        assertTrue(SleepEngine.verifyCheckpoint(checkpoint))
    }

    @Test fun modifiedCheckpointIsRejectedByIntegrityCheck() {
        val original = checkpoint()
        val modified = original.copy(permissionSnapshotDigest = "c".repeat(64))
        assertFalse(SleepEngine.verifyCheckpoint(modified))
    }

    @Test fun wakeRequiresAllRecoveryEvidenceAndAuthenticatedScopedApproval() {
        val thread = thread()
        val asleep = checkpoint(thread)
        val incomplete = SleepEngine.resume(
            asleep, thread, SleepRecoveryEvidence(true, false, true, true), approval(asleep), verifier
        )
        assertFalse(incomplete.resumed)
        assertEquals(SleepState.ASLEEP, incomplete.checkpoint.state)
        assertTrue(incomplete.holdReasons.contains("checkpoint integrity not verified"))

        val wrongScope = SleepEngine.resume(
            asleep, thread, completeEvidence,
            SleepWakeApproval("approved-by-human", "sleep.resume:other", true), verifier
        )
        assertFalse(wrongScope.resumed)

        val resumed = SleepEngine.resume(asleep, thread, completeEvidence, approval(asleep), verifier)
        assertTrue(resumed.resumed)
        assertEquals(SleepState.AWAKE, resumed.checkpoint.state)
    }

    @Test fun unauthenticatedApprovalCannotWakeCheckpoint() {
        val thread = thread()
        val asleep = checkpoint(thread)
        val deniedVerifier = object : SleepWakeApprovalVerifier { override fun verify(approval: SleepWakeApproval) = false }
        val result = SleepEngine.resume(asleep, thread, completeEvidence, approval(asleep), deniedVerifier)
        assertFalse(result.resumed)
        assertEquals(SleepState.ASLEEP, result.checkpoint.state)
        assertTrue(result.holdReasons.contains("authenticated human approval was not verified"))
    }

    @Test fun protectedTriggerRemainsHeldDuringSleep() {
        val thread = thread()
        val result = SleepEngine.evaluateProtectedTrigger(checkpoint(thread), thread, trigger(thread))
        assertEquals(ProtectedTriggerDisposition.HELD_SLEEP, result.disposition)
    }

    @Test fun matchingTriggerAfterVerifiedWakeOnlyBecomesReadyForOttoReview() {
        val thread = thread()
        val asleep = checkpoint(thread)
        val awake = SleepEngine.resume(asleep, thread, completeEvidence, approval(asleep), verifier).checkpoint
        val result = SleepEngine.evaluateProtectedTrigger(awake, thread, trigger(thread))
        assertEquals(ProtectedTriggerDisposition.READY_FOR_OTTO_REVIEW, result.disposition)
        assertTrue(result.holdReasons.isEmpty())
    }

    @Test fun triggerFromDifferentTransmissionIsHeld() {
        val thread = thread()
        val asleep = checkpoint(thread)
        val awake = SleepEngine.resume(asleep, thread, completeEvidence, approval(asleep), verifier).checkpoint
        val foreign = SuspensionThread.fromTransmission(
            "thread-foreign",
            TransmissionOrigin("tx-foreign", "gateway.other", "2026-11-12T10:00:00Z", "d".repeat(64)),
            event(SuspensionEventType.THREAD_CREATED, "event-foreign")
        )
        val result = SleepEngine.evaluateProtectedTrigger(awake, foreign, trigger(foreign))
        assertEquals(ProtectedTriggerDisposition.HELD_TRANSMISSION_MISMATCH, result.disposition)
    }

    @Test fun suspendedThreadAndFailedQualityRemainHeldAfterWake() {
        val thread = thread()
        val asleep = checkpoint(thread)
        val awake = SleepEngine.resume(asleep, thread, completeEvidence, approval(asleep), verifier).checkpoint
        val suspended = thread.placeOnHold(event(SuspensionEventType.SUSPENDED, "event-suspended"))
        val suspendedResult = SleepEngine.evaluateProtectedTrigger(awake, suspended, trigger(suspended))
        assertEquals(ProtectedTriggerDisposition.HELD_THREAD_SUSPENDED, suspendedResult.disposition)

        val weak = trigger(thread, quality.copy(policyChecksPassed = false))
        val qualityResult = SleepEngine.evaluateProtectedTrigger(awake, thread, weak)
        assertEquals(ProtectedTriggerDisposition.HELD_QUALITY, qualityResult.disposition)
    }
}
