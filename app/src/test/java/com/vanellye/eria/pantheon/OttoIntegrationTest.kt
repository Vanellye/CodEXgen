package com.vanellye.eria.pantheon
import org.junit.Assert.*
import org.junit.Test

class OttoIntegrationTest {
    private val quality = TriggerQualityEvidence(true, true, true, true, true, true)
    private fun rule(channel: ExternalActionChannel = ExternalActionChannel.WEBHOOK, target: String = "hook-1", evidence: TriggerQualityEvidence = quality) =
        OttoTriggerRule("rule-1", SuspensionEventType.THREAD_CREATED, channel, "notify", target, mapOf("kind" to "thread-created"), evidence)

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

    @Test fun triggerCreatesWebhookRequestOnlyAfterFullQualityQualification() {
        val (thread, event) = threadAndEvent()
        val result = OttoTriggerEngine.evaluate(thread, event, listOf(rule()))
        val request = result.requests.single()
        assertTrue(result.heldRules.isEmpty())
        assertEquals(ExternalActionChannel.WEBHOOK, request.channel)
        assertEquals("external-action:webhook:notify:hook-1", request.approvalScope)
        assertEquals(64, request.payloadDigest.length)
    }

    @Test fun incompleteQualityHoldsTriggerAndReportsReasons() {
        val (thread, event) = threadAndEvent()
        val weak = quality.copy(payloadSchemaVerified = false, replayCheckPassed = false)
        val result = OttoTriggerEngine.evaluate(thread, event, listOf(rule(evidence = weak)))
        assertTrue(result.requests.isEmpty())
        assertEquals(1, result.heldRules.size)
        assertEquals(66, result.heldRules.single().quality.scorePercent)
        assertTrue(result.heldRules.single().quality.holdReasons.contains("payload schema not verified"))
    }

    @Test fun relatedProviderChannelsShareOneTriggerContract() {
        val (thread, event) = threadAndEvent()
        val channels = listOf(ExternalActionChannel.WEBHOOK, ExternalActionChannel.HTTP_CALLBACK,
            ExternalActionChannel.NOTIFICATION, ExternalActionChannel.MESSAGE_QUEUE, ExternalActionChannel.GENERIC_API)
        val result = OttoTriggerEngine.evaluate(thread, event, channels.map { rule(channel = it, target = "target-${it.name}") })
        assertEquals(channels.toSet(), result.requests.map { it.channel }.toSet())
        assertEquals(channels.size, result.requests.size)
    }

    @Test fun dispatchRequiresChannelTargetAllowlistAndMatchingVerifiedApproval() {
        val (thread, event) = threadAndEvent()
        val request = OttoTriggerEngine.evaluate(thread, event, listOf(rule())).requests.single()
        var dispatched = 0
        val verifier = object : ExternalActionApprovalVerifier {
            override fun verify(approval: ExternalActionApproval) = approval.approvalRef == "human-approval"
        }
        val dispatcher = object : ExternalActionDispatcher {
            override fun dispatch(request: ExternalActionRequest, idempotencyKey: String): String {
                dispatched += 1
                assertEquals(request.payloadDigest, idempotencyKey)
                assertEquals(ExternalActionChannel.WEBHOOK, request.channel)
                return "receipt-1"
            }
        }
        val gate = ExternalActionDispatchGate(setOf(ExternalActionTarget(ExternalActionChannel.WEBHOOK, "hook-1")), verifier, dispatcher)
        val denied = gate.dispatchApproved(request, ExternalActionApproval("human-approval", "external-action:webhook:other:hook-1", request.payloadDigest))
        assertEquals(DispatchStatus.DENIED, denied.status)
        assertEquals(0, dispatched)
        val approved = gate.dispatchApproved(request, ExternalActionApproval("human-approval", request.approvalScope, request.payloadDigest))
        assertEquals(DispatchStatus.DISPATCHED, approved.status)
        assertEquals(1, dispatched)
    }

    @Test fun rejectsChannelConfusionAndUnlistedTargets() {
        val (thread, event) = threadAndEvent()
        val request = OttoTriggerEngine.evaluate(thread, event, listOf(rule())).requests.single()
        var dispatched = false
        val gate = ExternalActionDispatchGate(
            setOf(ExternalActionTarget(ExternalActionChannel.HTTP_CALLBACK, "hook-1")),
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

    @Test fun rejectsModifiedPayloadBeforeExternalDispatch() {
        val (thread, event) = threadAndEvent()
        val request = OttoTriggerEngine.evaluate(thread, event, listOf(rule())).requests.single()
        var dispatched = false
        val gate = ExternalActionDispatchGate(
            setOf(ExternalActionTarget(ExternalActionChannel.WEBHOOK, "hook-1")),
            object : ExternalActionApprovalVerifier { override fun verify(approval: ExternalActionApproval) = true },
            object : ExternalActionDispatcher {
                override fun dispatch(request: ExternalActionRequest, idempotencyKey: String): String {
                    dispatched = true
                    return "unexpected"
                }
            }
        )
        val tampered = request.copy(payload = mapOf("kind" to "changed"))
        val result = gate.dispatchApproved(tampered, ExternalActionApproval("approval", request.approvalScope, request.payloadDigest))
        assertEquals(DispatchStatus.DENIED, result.status)
        assertFalse(dispatched)
    }
}
