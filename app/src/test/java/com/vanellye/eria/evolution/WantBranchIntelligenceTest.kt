package com.vanellye.eria.evolution

import org.junit.Assert.*
import org.junit.Test

class WantBranchIntelligenceTest {
    private fun evidence(status: EvidenceStatus, method: String = "unit test") =
        KnowledgeEvidence(
            sourceRef = "test://evidence/1",
            sourceRevision = "abc123",
            contentDigest = "sha256:abc",
            method = method,
            observedAt = "2026-11-13T00:00:00Z",
            evidenceStatus = status
        )

    @Test fun detectorRanksRelevantBranchesAndExplainsEvidence() {
        val relevant = WantBranchCandidate(
            branch = "knowledge-recycle-foundation",
            repository = "Vanellye/CodEXgen",
            headRevision = "head-1",
            summary = "Knowledge provenance and know how",
            topics = setOf("evidence", "learning"),
            knowledge = listOf(
                KnowledgeNode(
                    "k1", "How validation works", "Validation procedure",
                    KnowledgeKind.KNOW_HOW, listOf(evidence(EvidenceStatus.VERIFIED))
                ),
                KnowledgeNode(
                    "k2", "Why source pins matter", "Revision pinning rationale",
                    KnowledgeKind.KNOW_WHY, listOf(evidence(EvidenceStatus.SUPPORTED, "design review"))
                )
            )
        )
        val unrelated = WantBranchCandidate(
            branch = "fiction-body",
            repository = "Vanellye/CodEXgen",
            headRevision = "head-2",
            summary = "Narrative fiction archive",
            topics = setOf("story"),
            knowledge = emptyList()
        )

        val matches = WantBranchDetector().detect(
            "find knowledge provenance and know how",
            listOf(unrelated, relevant)
        )

        assertEquals("knowledge-recycle-foundation", matches.first().branch)
        assertEquals("head-1", matches.first().headRevision)
        assertTrue(matches.first().reasons.any { it.contains("verified evidence") })
        assertTrue(matches.first().reviewRequired)
    }

    @Test fun conflictingEvidenceIsVisibleAndPenalized() {
        val candidate = WantBranchCandidate(
            "branch-a", "Vanellye/CodEXgen", "head-a", "knowledge provenance",
            setOf("knowledge"),
            listOf(
                KnowledgeNode(
                    "k1", "Claim", "Claim under review", KnowledgeKind.FACT,
                    listOf(evidence(EvidenceStatus.CONFLICTED))
                )
            )
        )

        val result = WantBranchDetector().detect("knowledge provenance", listOf(candidate)).single()

        assertEquals(1, result.evidenceSummary[EvidenceStatus.CONFLICTED])
        assertTrue(result.reasons.any { it.contains("Conflicting evidence") })
    }

    @Test fun nexusIndexFindsDanglingLinksAndDuplicateIds() {
        val node = KnowledgeNode(
            "same", "Known item", "A documented item", KnowledgeKind.FACT,
            listOf(evidence(EvidenceStatus.UNKNOWN))
        )
        val index = NexusIndex(
            nodes = listOf(node, node),
            links = listOf(NexusLink("same", NexusRelation.SUPPORTS, "missing", "test://link", "test"))
        )

        val problems = index.validate()

        assertTrue(problems.any { it.contains("Duplicate") })
        assertTrue(problems.any { it.contains("missing") })
    }

    @Test fun emptyWantDoesNotProduceBranchMatches() {
        assertTrue(WantBranchDetector().detect("!!!", emptyList()).isEmpty())
    }
}
