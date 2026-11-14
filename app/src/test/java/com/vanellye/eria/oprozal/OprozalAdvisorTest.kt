package com.vanellye.eria.oprozal

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class OprozalAdvisorTest {
    private val coordinator = OprozalCoordinator()

    private fun signal(gap: OprozalGap) = OprozalSignal(
        signalId = "signal-1",
        source = OprozalSource.ERIA_RUNTIME,
        gap = gap,
        severity = OprozalSeverity.MEDIUM,
        summary = "Test deficiency",
        evidenceRefs = listOf("commit:abc123", "test:runtime"),
        observedAt = "2026-11-14T00:00:00Z"
    )

    @Test fun runtimeLatencyRecommendsProfilingBeforeOptimization() {
        val advice = coordinator.advise(signal(OprozalGap.RUNTIME_LATENCY))
        assertTrue(advice.facultyCandidates.contains(OprozalFaculty.PERFORMANCE_PROFILING))
        assertTrue(advice.verificationSteps.any { it.contains("baseline", ignoreCase = true) })
        assertTrue(advice.requiresHumanReview)
    }

    @Test fun allMindframesCanSubmitSignals() {
        OprozalSource.values().forEach { source ->
            val event = signal(OprozalGap.MISSING_EVIDENCE).copy(source = source)
            assertEquals(event.signalId, coordinator.advise(event).signalId)
        }
    }

    @Test fun proposalsRemainReviewOnlyAndDoNotExecute() {
        val event = signal(OprozalGap.MISSING_CAPABILITY)
        val advice = coordinator.advise(event)
        val proposals = coordinator.proposeFaculty(event, advice)
        assertTrue(proposals.isNotEmpty())
        assertTrue(proposals.all { it.status == ProposalStatus.REVIEW_REQUIRED })
        assertTrue(proposals.all { !it.actionTaken })
        assertTrue(proposals.all { it.ponsScope == "eria.faculty.propose" })
    }

    @Test(expected = IllegalArgumentException::class)
    fun mismatchedAdviceCannotGenerateFacultyProposals() {
        val event = signal(OprozalGap.MISSING_CAPABILITY)
        coordinator.proposeFaculty(event, coordinator.advise(event).copy(signalId = "other"))
    }

    @Test fun unknownSignalStaysLowConfidence() {
        val advice = coordinator.advise(signal(OprozalGap.UNKNOWN))
        assertEquals("LOW", advice.confidence)
        assertFalse(advice.facultyCandidates.isEmpty())
    }
}
