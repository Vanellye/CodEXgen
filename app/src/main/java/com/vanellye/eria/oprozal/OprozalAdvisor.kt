package com.vanellye.eria.oprozal

/**
 * Deterministic baseline advisor. A model-backed OprozalMindframe can be
 * injected later without changing the signal, advice, or provenance contracts.
 */
class RuleBasedOprozalMindframe : OprozalMindframe {
    override fun assess(signal: OprozalSignal): OprozalAdvice {
        val (diagnosis, recommendation, faculties, checks) = when (signal.gap) {
            OprozalGap.MISSING_EVIDENCE -> Quad(
                "The reported conclusion lacks sufficient linked source evidence.",
                "Request the missing source material and keep the conclusion marked unverified.",
                listOf(OprozalFaculty.EVIDENCE_GAP_ANALYSIS, OprozalFaculty.PROVENANCE_AUDIT),
                listOf("Resolve every evidence reference.", "Record source revision and digest.", "Reassess the conclusion after evidence is available.")
            )
            OprozalGap.MISSING_CAPABILITY -> Quad(
                "A required capability is not represented in the current faculty inventory.",
                "Draft a bounded faculty specification with explicit inputs, outputs, and acceptance checks.",
                listOf(OprozalFaculty.SYNTHESIS_PLANNING, OprozalFaculty.TEST_GENERATION),
                listOf("Define a narrow capability contract.", "Identify data and permission boundaries.", "Add unit and integration acceptance tests.")
            )
            OprozalGap.RUNTIME_LATENCY -> Quad(
                "A runtime delay has been reported; its cause is not established by the signal alone.",
                "Collect stage-level timings and profile before proposing optimization.",
                listOf(OprozalFaculty.PERFORMANCE_PROFILING, OprozalFaculty.TEST_GENERATION),
                listOf("Capture baseline latency and workload.", "Profile CPU, I/O, memory, and queue wait separately.", "Compare the candidate against the same workload.")
            )
            OprozalGap.BUILD_FAILURE -> Quad(
                "The build pipeline reports a failure that needs a reproducible diagnostic.",
                "Preserve the complete build log and isolate the first causal error before changing code.",
                listOf(OprozalFaculty.BUILD_DIAGNOSTICS, OprozalFaculty.TEST_GENERATION),
                listOf("Record commit and toolchain versions.", "Identify the earliest causal compiler or task error.", "Run the smallest relevant test before the full suite.")
            )
            OprozalGap.DEPENDENCY_RISK -> Quad(
                "A dependency may be incompatible, unsupported, or exposed to supply-chain risk.",
                "Prepare a compatibility matrix and review provenance before changing dependency versions.",
                listOf(OprozalFaculty.DEPENDENCY_COMPATIBILITY, OprozalFaculty.SECURITY_REVIEW),
                listOf("Record current and proposed versions.", "Check platform and API compatibility.", "Run lockfile, license, and vulnerability review.")
            )
            OprozalGap.TEST_COVERAGE_GAP -> Quad(
                "The reported behavior does not have sufficient test coverage.",
                "Propose focused tests for expected behavior, failure modes, and regression boundaries.",
                listOf(OprozalFaculty.TEST_GENERATION, OprozalFaculty.INDEPENDENT_CRITIQUE),
                listOf("Define observable expected behavior.", "Cover success, invalid input, and failure paths.", "Run tests against the unchanged baseline and candidate.")
            )
            OprozalGap.SECURITY_CONCERN -> Quad(
                "A security concern has been reported and must be treated as unverified until assessed.",
                "Prioritize a read-only security review; do not execute generated code or touch secrets.",
                listOf(OprozalFaculty.SECURITY_REVIEW, OprozalFaculty.PROVENANCE_AUDIT),
                listOf("Describe the threat model and affected boundary.", "Use synthetic fixtures and read-only inspection.", "Record evidence, limitations, and remediation options.")
            )
            OprozalGap.STORAGE_PRESSURE -> Quad(
                "Storage pressure has been reported, but capacity and retention requirements are unknown.",
                "Measure usage and growth, then propose a storage or retention design without deleting records.",
                listOf(OprozalFaculty.PERFORMANCE_PROFILING, OprozalFaculty.PROVENANCE_AUDIT),
                listOf("Measure current usage and growth rate.", "Identify retention and backup requirements.", "Validate capacity estimates without modifying existing records.")
            )
            OprozalGap.CONTRADICTION -> Quad(
                "Two or more findings appear inconsistent.",
                "Preserve both claims and request independent evidence-based reconciliation.",
                listOf(OprozalFaculty.INDEPENDENT_CRITIQUE, OprozalFaculty.EVIDENCE_GAP_ANALYSIS),
                listOf("Link each conflicting claim to its source.", "Compare timestamps, scope, and test conditions.", "Record unresolved disagreement if evidence is inconclusive.")
            )
            OprozalGap.UNKNOWN -> Quad(
                "The signal does not map to a known deficiency category.",
                "Request a more specific description and retain the event without inferring a cause.",
                listOf(OprozalFaculty.CONVERSATION_EXPLANATION, OprozalFaculty.EVIDENCE_GAP_ANALYSIS),
                listOf("Clarify the observed symptom.", "Attach reproducible evidence.", "Classify only after review.")
            )
        }

        return OprozalAdvice(
            adviceId = "oprozal-advice-${signal.signalId}",
            signalId = signal.signalId,
            diagnosis = diagnosis,
            recommendation = recommendation,
            facultyCandidates = faculties,
            verificationSteps = checks,
            evidenceRefs = signal.evidenceRefs,
            confidence = if (signal.gap == OprozalGap.UNKNOWN) "LOW" else "PROVISIONAL",
            requiresHumanReview = true
        )
    }

    private data class Quad(
        val diagnosis: String,
        val recommendation: String,
        val faculties: List<OprozalFaculty>,
        val checks: List<String>
    )
}

/**
 * Hybrid coordinator: accepts signals from all existing mindframes and
 * independently assesses each signal through the OprozalMindframe contract.
 */
class OprozalCoordinator(
    private val mindframe: OprozalMindframe = RuleBasedOprozalMindframe()
) {
    fun advise(signal: OprozalSignal): OprozalAdvice {
        require(signal.signalId.isNotBlank()) { "signalId must not be blank" }
        require(signal.summary.isNotBlank()) { "summary must not be blank" }
        return mindframe.assess(signal)
    }

    fun proposeFaculty(signal: OprozalSignal, advice: OprozalAdvice): List<OprozalFacultyProposal> {
        require(advice.signalId == signal.signalId) { "Advice must refer to the supplied signal" }
        return advice.facultyCandidates.map { faculty ->
            OprozalFacultyProposal(
                proposalId = "${advice.adviceId}-${faculty.name.lowercase()}",
                faculty = faculty,
                purpose = advice.recommendation,
                proposedInputs = listOf("OprozalSignal", "linked evidence references"),
                proposedOutputs = listOf("reviewable faculty result", "provenance record"),
                acceptanceChecks = advice.verificationSteps,
                sourceSignalIds = listOf(signal.signalId)
            )
        }
    }
}
