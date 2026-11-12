package com.vanellye.eria.pantheon
import org.junit.Assert.*
import org.junit.Test

class OttoIntegrationTest {
    private fun threadAndEvent(): Pair<SuspensionThread, SuspensionEvent> {
        val created = SuspensionEvent("event-create", SuspensionEventType.THREAD_CREATED, "2026-11-12T10:00:00Z", "operator", "created")
        val thread = SuspensionThread.fromTransmission(
            "thread-otto", TransmissionOrigin("tx-otto", "gateway.otto", "2026-11-12T10:00:00Z", "c".repeat(64)), created
        )
        return thread to created
    }

    @Test fun boundedRinseRepeatHoldsWhenQualificationFails() {
        val reports = OttoCoordinator.runBoundedCycles(OttoCycleInput("source://module", "d".repeat(64), "pattern://one", false, true, true), 4)
        assertEquals(1, reports.size)
        assertEquals(OttoCycleStatus.HELD, reports.single().status)
        assertTrue(reports.single().holdReasons.contains("tests not passed"))
    }

    @Test fun qualifiedRinseRepeatIsBoundedAndPreservesLineage() {
        val reports = OttoCoordinator.runBoundedCycles(OttoCycleInput("source://module", "d".repeat(64), "pattern://one", true, true, true), 3)
        assertEquals(3, reports.size)
        assertTrue(reports.all { it.status == OttoCycleStatus.QUALIFIED })
        assertTrue(reports.all { it.sourceRef == "source://module" })
        assertEquals(OttoStage.REPEAT, reports.last().stages.last())
    }

    @Test fun triggerCreatesRequestButDoesNotDispatch() {
        val (thread, event) = threadAndEvent()
        val request = OttoTriggerEngine.evaluate(
            thread, event, listOf(OttoTriggerRule("rule-1", SuspensionEventType.THREAD_CREATED, "notify", "local-notifier", mapOf("kind" to "thread-created")))
        ).single()
        assertEquals("external-action:notify:local-notifier", request.approvalScope)
        assertEquals(64, request.payloadDigest.length)
    }

    @Test fun dispatchRequiresAllowlistedTargetAndMatchingVerifiedApproval() {
        val (thread, event) = threadAndEvent()
        val request = OttoTriggerEngine.evaluate(thread, event, listOf(OttoTriggerRule("rule-1", SuspensionEventType.THREAD_CREATED, "notify", "local-notifier", emptyMap()))).single()
        var dispatched = 0
        val verifier = object : ExternalActionApprovalVerifier {
            override fun verify(approval: ExternalActionApproval) = approval.approvalRef == "human-approval"
        }
        val dispatcher = object : ExternalActionDispatcher {
            override fun dispatch(request: ExternalActionRequest, idempotencyKey: String): String {
                dispatched += 1
                assertEquals(request.payloadDigest, idempotencyKey)
                return "receipt-1"
            }
        }
        val gate = ExternalActionDispatchGate(setOf("local-notifier"), verifier, dispatcher)
        val denied = gate.dispatchApproved(request, ExternalActionApproval("human-approval", "external-action:other:target", request.payloadDigest))
        assertEquals(DispatchStatus.DENIED, denied.status)
        assertEquals(0, dispatched)
        val approved = gate.dispatchApproved(request, ExternalActionApproval("human-approval", request.approvalScope, request.payloadDigest))
        assertEquals(DispatchStatus.DISPATCHED, approved.status)
        assertEquals(1, dispatched)
    }

    @Test fun rejectsUnapprovedOrUnlistedExternalTarget() {
        val (thread, event) = threadAndEvent()
        val request = OttoTriggerEngine.evaluate(thread, event, listOf(OttoTriggerRule("rule-2", SuspensionEventType.THREAD_CREATED, "publish", "unknown-target", emptyMap()))).single()
        var dispatched = false
        val gate = ExternalActionDispatchGate(
            emptySet(),
            object : ExternalActionApprovalVerifier { override fun verify(approval: ExternalActionApproval) = true },
            object : ExternalActionDispatcher {
                override fun dispatch(request: ExternalActionRequest, idempotencyKey: String): String {
                    dispatched = true
                    return "should-not-run"
                }
            }
        )
        val result = gate.dispatchApproved(request, ExternalActionApproval("approval", request.approvalScope, request.payloadDigest))
        assertEquals(DispatchStatus.DENIED, result.status)
        assertFalse(dispatched)
    }
}
