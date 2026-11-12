package com.vanellye.eria.pantheon
import org.junit.Assert.*
import org.junit.Test
class SuspensionThreadTest {
    private val origin = TransmissionOrigin("tx-001", "gateway.source-a", "2026-11-12T10:00:00Z", "a".repeat(64))
    private fun event(type: SuspensionEventType, id: String, approval: String? = null) =
        SuspensionEvent(id, type, "2026-11-12T10:01:00Z", "operator.local", "test event", approval)
    private fun thread() = SuspensionThread.fromTransmission("thread-001", origin, event(SuspensionEventType.THREAD_CREATED, "event-0"))
    @Test fun createsThreadWithoutLosingTransmissionOrigin() {
        val thread = thread()
        assertEquals(SuspensionStatus.ACTIVE, thread.status)
        assertEquals(origin, thread.origin)
        assertEquals(SuspensionEventType.THREAD_CREATED, thread.events.single().type)
    }
    @Test fun suspendsAndResumesOnlyWithMatchingHumanApprovalScope() {
        val held = thread().placeOnHold(event(SuspensionEventType.SUSPENDED, "event-1"))
        assertEquals(SuspensionStatus.SUSPENDED, held.status)
        assertThrows(IllegalArgumentException::class.java) {
            held.resume(event(SuspensionEventType.RESUMED, "event-2", "approval-1"), ResumeApproval("approval-1", "suspension.resume:other-thread", true))
        }
        val resumed = held.resume(event(SuspensionEventType.RESUMED, "event-2", "approval-1"), ResumeApproval("approval-1", "suspension.resume:thread-001", true))
        assertEquals(SuspensionStatus.ACTIVE, resumed.status)
        assertEquals(3, resumed.events.size)
    }
    @Test fun rejectsResumeWithoutHumanConfirmation() {
        val held = thread().placeOnHold(event(SuspensionEventType.SUSPENDED, "event-1"))
        assertThrows(IllegalArgumentException::class.java) {
            held.resume(event(SuspensionEventType.RESUMED, "event-2", "approval-1"), ResumeApproval("approval-1", "suspension.resume:thread-001", false))
        }
    }
    @Test fun preservesEvidenceStateAndRejectsDuplicateCrossReference() {
        val ref = ThreadCrossReference("xref-1", "record://related/7", "related-to", CrossReferenceEvidence.INFERRED)
        val withRef = thread().addCrossReference(ref, event(SuspensionEventType.CROSS_REFERENCE_ADDED, "event-1"))
        assertEquals(CrossReferenceEvidence.INFERRED, withRef.crossReferences.single().evidence)
        assertThrows(IllegalArgumentException::class.java) { withRef.addCrossReference(ref, event(SuspensionEventType.CROSS_REFERENCE_ADDED, "event-2")) }
    }
    @Test fun verifiedCrossReferenceRequiresEvidenceReference() {
        val ref = ThreadCrossReference("xref-verified", "record://related/8", "supports", CrossReferenceEvidence.VERIFIED)
        assertFalse(ref.validate().isEmpty())
        assertTrue(ref.copy(evidenceRef = "evidence://audit/8").validate().isEmpty())
    }
}
