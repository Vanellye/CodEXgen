package com.vanellye.eria.pantheon
enum class SuspensionStatus { ACTIVE, SUSPENDED, CLOSED }
enum class CrossReferenceEvidence { VERIFIED, INFERRED, UNKNOWN }
enum class SuspensionEventType { THREAD_CREATED, SUSPENDED, CROSS_REFERENCE_ADDED, RESUMED, CLOSED }

data class TransmissionOrigin(val transmissionId: String, val sourceRef: String, val receivedAt: String, val payloadDigest: String) {
    fun validate(): List<String> = buildList {
        if (transmissionId.isBlank()) add("transmissionId is required")
        if (sourceRef.isBlank()) add("sourceRef is required")
        if (receivedAt.isBlank()) add("receivedAt is required")
        if (!Regex("^[0-9a-f]{64}$").matches(payloadDigest)) add("payloadDigest must be lowercase SHA-256")
    }
}
data class ThreadCrossReference(
    val referenceId: String, val targetRef: String, val relation: String,
    val evidence: CrossReferenceEvidence, val evidenceRef: String? = null
) {
    fun validate(): List<String> = buildList {
        if (referenceId.isBlank()) add("referenceId is required")
        if (targetRef.isBlank()) add("targetRef is required")
        if (relation.isBlank()) add("relation is required")
        if (evidence == CrossReferenceEvidence.VERIFIED && evidenceRef.isNullOrBlank()) add("verified cross-references require evidenceRef")
    }
}
data class SuspensionEvent(
    val eventId: String, val type: SuspensionEventType, val occurredAt: String,
    val actorRef: String, val detail: String, val approvalRef: String? = null
)
data class ResumeApproval(val approvalRef: String, val scope: String, val humanConfirmed: Boolean)

/** Approval fields are host-supplied assertions, not cryptographic proof. */
data class SuspensionThread(
    val threadId: String, val origin: TransmissionOrigin, val status: SuspensionStatus,
    val events: List<SuspensionEvent>, val crossReferences: List<ThreadCrossReference>
) {
    fun placeOnHold(event: SuspensionEvent): SuspensionThread {
        require(status == SuspensionStatus.ACTIVE) { "only active threads can be suspended" }
        require(event.type == SuspensionEventType.SUSPENDED) { "expected SUSPENDED event" }
        require(event.actorRef.isNotBlank() && event.detail.isNotBlank()) { "actor and reason are required" }
        return copy(status = SuspensionStatus.SUSPENDED, events = events + event)
    }
    fun addCrossReference(reference: ThreadCrossReference, event: SuspensionEvent): SuspensionThread {
        require(status != SuspensionStatus.CLOSED) { "closed threads cannot be changed" }
        require(reference.validate().isEmpty()) { reference.validate().joinToString() }
        require(crossReferences.none { it.referenceId == reference.referenceId }) { "duplicate referenceId" }
        require(event.type == SuspensionEventType.CROSS_REFERENCE_ADDED) { "expected CROSS_REFERENCE_ADDED event" }
        return copy(crossReferences = crossReferences + reference, events = events + event)
    }
    fun resume(event: SuspensionEvent, approval: ResumeApproval): SuspensionThread {
        require(status == SuspensionStatus.SUSPENDED) { "thread is not suspended" }
        require(approval.humanConfirmed) { "human confirmation is required" }
        require(approval.approvalRef.isNotBlank()) { "approval reference is required" }
        require(approval.scope == "suspension.resume:$threadId") { "approval scope mismatch" }
        require(event.type == SuspensionEventType.RESUMED) { "expected RESUMED event" }
        require(event.approvalRef == approval.approvalRef) { "event approval reference mismatch" }
        return copy(status = SuspensionStatus.ACTIVE, events = events + event)
    }
    fun close(event: SuspensionEvent): SuspensionThread {
        require(status != SuspensionStatus.CLOSED) { "thread is already closed" }
        require(event.type == SuspensionEventType.CLOSED) { "expected CLOSED event" }
        return copy(status = SuspensionStatus.CLOSED, events = events + event)
    }
    companion object {
        fun fromTransmission(threadId: String, origin: TransmissionOrigin, createdEvent: SuspensionEvent): SuspensionThread {
            require(threadId.isNotBlank()) { "threadId is required" }
            require(origin.validate().isEmpty()) { origin.validate().joinToString() }
            require(createdEvent.type == SuspensionEventType.THREAD_CREATED) { "expected THREAD_CREATED event" }
            return SuspensionThread(threadId, origin, SuspensionStatus.ACTIVE, listOf(createdEvent), emptyList())
        }
    }
}
