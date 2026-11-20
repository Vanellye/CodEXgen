package com.vanellye.eria.evolution

/**
 * Read-only WANT branch discovery and knowledge-lineage primitives.
 *
 * This module ranks supplied branch/knowledge candidates. It does not query
 * GitHub, checkout branches, write files, merge, or authorize execution.
 * A host adapter must supply repository observations and preserve their refs.
 */

enum class KnowledgeKind {
    FACT,
    KNOW_HOW,
    KNOW_WHY,
    HYPOTHESIS,
    OPEN_QUESTION
}

enum class EvidenceStatus {
    VERIFIED,
    SUPPORTED,
    UNVERIFIED,
    CONFLICTED,
    UNKNOWN
}

enum class NexusRelation {
    SUPPORTS,
    CONTRADICTS,
    DERIVED_FROM,
    IMPLEMENTS,
    TESTS,
    DEPENDS_ON,
    RELATED_TO
}

data class KnowledgeEvidence(
    val sourceRef: String,
    val sourceRevision: String?,
    val contentDigest: String?,
    val method: String,
    val observedAt: String?,
    val evidenceStatus: EvidenceStatus
) {
    init {
        require(sourceRef.isNotBlank()) { "Evidence sourceRef is required." }
        require(method.isNotBlank()) { "Record how the knowledge was obtained." }
    }
}

data class KnowledgeNode(
    val id: String,
    val title: String,
    val claim: String,
    val kind: KnowledgeKind,
    val evidence: List<KnowledgeEvidence>,
    val limitations: List<String> = emptyList(),
    val tags: Set<String> = emptySet()
) {
    init {
        require(id.isNotBlank())
        require(title.isNotBlank())
        require(claim.isNotBlank())
        require(evidence.isNotEmpty()) {
            "A knowledge node needs at least one evidence record or an explicit UNKNOWN record."
        }
    }

    val evidenceStatus: EvidenceStatus
        get() = when {
            evidence.any { it.evidenceStatus == EvidenceStatus.CONFLICTED } ->
                EvidenceStatus.CONFLICTED
            evidence.any { it.evidenceStatus == EvidenceStatus.VERIFIED } ->
                EvidenceStatus.VERIFIED
            evidence.any { it.evidenceStatus == EvidenceStatus.SUPPORTED } ->
                EvidenceStatus.SUPPORTED
            evidence.all { it.evidenceStatus == EvidenceStatus.UNKNOWN } ->
                EvidenceStatus.UNKNOWN
            else -> EvidenceStatus.UNVERIFIED
        }
}

data class WantBranchCandidate(
    val branch: String,
    val repository: String,
    val headRevision: String,
    val summary: String,
    val topics: Set<String>,
    val knowledge: List<KnowledgeNode>,
    val changedPaths: Set<String> = emptySet()
) {
    init {
        require(branch.isNotBlank())
        require(repository.isNotBlank())
        require(headRevision.isNotBlank())
    }
}

data class NexusLink(
    val fromId: String,
    val relation: NexusRelation,
    val toId: String,
    val sourceRef: String,
    val rationale: String
) {
    init {
        require(fromId.isNotBlank() && toId.isNotBlank())
        require(sourceRef.isNotBlank())
        require(rationale.isNotBlank())
    }
}

data class WantBranchMatch(
    val branch: String,
    val repository: String,
    val headRevision: String,
    val score: Int,
    val matchedTerms: Set<String>,
    val evidenceSummary: Map<EvidenceStatus, Int>,
    val reasons: List<String>,
    val reviewRequired: Boolean = true
)

class WantBranchDetector {
    /**
     * Deterministic lexical ranking with explicit evidence signals.
     * The score is a triage aid, not a truth/confidence score or adoption decision.
     */
    fun detect(
        wantStatement: String,
        candidates: List<WantBranchCandidate>
    ): List<WantBranchMatch> {
        val terms = tokens(wantStatement)
        if (terms.isEmpty()) return emptyList()

        return candidates.map { candidate ->
            val candidateTerms = tokens(
                candidate.branch + " " + candidate.summary + " " +
                    candidate.topics.joinToString(" ") + " " +
                    candidate.knowledge.joinToString(" ") { "${it.title} ${it.claim} ${it.tags.joinToString(" ")}" }
            )
            val matched = terms.intersect(candidateTerms)
            val statuses = candidate.knowledge
                .flatMap { it.evidence }
                .groupingBy { it.evidenceStatus }
                .eachCount()

            val score = (matched.size * 10) +
                (statuses[EvidenceStatus.VERIFIED] ?: 0) * 4 +
                (statuses[EvidenceStatus.SUPPORTED] ?: 0) * 2 -
                (statuses[EvidenceStatus.CONFLICTED] ?: 0) * 3

            val reasons = buildList {
                if (matched.isNotEmpty()) add("WANT terms match: ${matched.sorted().joinToString(", ")}.")
                if ((statuses[EvidenceStatus.VERIFIED] ?: 0) > 0) add("Contains verified evidence records.")
                if ((statuses[EvidenceStatus.SUPPORTED] ?: 0) > 0) add("Contains supported, not necessarily conclusive, evidence.")
                if ((statuses[EvidenceStatus.CONFLICTED] ?: 0) > 0) add("Conflicting evidence requires human examination.")
                if (candidate.knowledge.any { it.kind == KnowledgeKind.KNOW_HOW }) add("Contains procedural know-how records.")
                if (candidate.knowledge.any { it.kind == KnowledgeKind.KNOW_WHY }) add("Contains rationale/how-it-is-known records.")
                if (candidate.knowledge.isEmpty()) add("No structured knowledge records supplied.")
                add("Candidate head must be re-fetched before review: ${candidate.headRevision}.")
            }

            WantBranchMatch(
                branch = candidate.branch,
                repository = candidate.repository,
                headRevision = candidate.headRevision,
                score = score,
                matchedTerms = matched,
                evidenceSummary = statuses,
                reasons = reasons
            )
        }.sortedWith(compareByDescending<WantBranchMatch> { it.score }.thenBy { it.branch })
    }

    private fun tokens(value: String): Set<String> =
        Regex("[A-Za-z0-9][A-Za-z0-9._-]{1,}")
            .findAll(value.lowercase())
            .map { it.value.trim('.', '-', '_') }
            .filter { it.length >= 2 }
            .toSet()
}

/** Read-only nexus validation; links never imply equivalence or permission. */
class NexusIndex(
    nodes: List<KnowledgeNode>,
    links: List<NexusLink>
) {
    val nodes: List<KnowledgeNode> = nodes.toList()
    val links: List<NexusLink> = links.toList()

    fun validate(): List<String> {
        val problems = mutableListOf<String>()
        val ids = nodes.map { it.id }.toSet()
        if (ids.size != nodes.size) problems += "Duplicate knowledge node IDs."
        links.forEach { link ->
            if (link.fromId !in ids) problems += "Missing nexus source node: ${link.fromId}"
            if (link.toId !in ids) problems += "Missing nexus target node: ${link.toId}"
        }
        return problems
    }

    fun relatedTo(nodeId: String): List<NexusLink> =
        links.filter { it.fromId == nodeId || it.toId == nodeId }
}
