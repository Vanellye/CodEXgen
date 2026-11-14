package com.vanellye.eria.oprozal

/**
 * Oprozal's hybrid contract: an independent advisory mindframe that can also
 * receive deficiency events from Æị, Âï, and Ēx.
 *
 * This module emits advice and inert code-faculty proposals only. It has no
 * shell, process, filesystem-write, network, Git, or dynamic-classloading API.
 */
enum class OprozalSource {
    AEI_EVIDENCE,
    AI_CONVERSATION,
    EX_CRITICAL_REVIEW,
    ERIA_RUNTIME,
    HUMAN
}

enum class OprozalSeverity { INFO, LOW, MEDIUM, HIGH, CRITICAL }

enum class OprozalGap {
    MISSING_EVIDENCE,
    MISSING_CAPABILITY,
    RUNTIME_LATENCY,
    BUILD_FAILURE,
    DEPENDENCY_RISK,
    TEST_COVERAGE_GAP,
    SECURITY_CONCERN,
    STORAGE_PRESSURE,
    CONTRADICTION,
    UNKNOWN
}

enum class OprozalFaculty {
    EVIDENCE_GAP_ANALYSIS,
    CONVERSATION_EXPLANATION,
    INDEPENDENT_CRITIQUE,
    TEST_GENERATION,
    BUILD_DIAGNOSTICS,
    DEPENDENCY_COMPATIBILITY,
    PERFORMANCE_PROFILING,
    SECURITY_REVIEW,
    PROVENANCE_AUDIT,
    SYNTHESIS_PLANNING
}

data class OprozalSignal(
    val signalId: String,
    val source: OprozalSource,
    val gap: OprozalGap,
    val severity: OprozalSeverity,
    val summary: String,
    val evidenceRefs: List<String> = emptyList(),
    val observedAt: String,
    val metrics: Map<String, String> = emptyMap()
)

data class OprozalAdvice(
    val adviceId: String,
    val signalId: String,
    val diagnosis: String,
    val recommendation: String,
    val facultyCandidates: List<OprozalFaculty>,
    val verificationSteps: List<String>,
    val evidenceRefs: List<String>,
    val confidence: String,
    val requiresHumanReview: Boolean = true
)

data class OprozalFacultyProposal(
    val proposalId: String,
    val faculty: OprozalFaculty,
    val purpose: String,
    val proposedInputs: List<String>,
    val proposedOutputs: List<String>,
    val acceptanceChecks: List<String>,
    val sourceSignalIds: List<String>,
    val status: ProposalStatus = ProposalStatus.REVIEW_REQUIRED,
    val ponsScope: String = "eria.faculty.propose",
    val actionTaken: Boolean = false
)

enum class ProposalStatus {
    REVIEW_REQUIRED,
    APPROVED_FOR_IMPLEMENTATION,
    REJECTED,
    SUPERSEDED
}

/** Pluggable boundary for a separately hosted Oprozal model, if configured. */
fun interface OprozalMindframe {
    fun assess(signal: OprozalSignal): OprozalAdvice
}
