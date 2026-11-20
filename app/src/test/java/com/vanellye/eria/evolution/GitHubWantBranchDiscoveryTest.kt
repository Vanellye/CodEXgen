package com.vanellye.eria.evolution

import org.junit.Assert.*
import org.junit.Test

class GitHubWantBranchDiscoveryTest {
    private class FakeApi : GitHubReadOnlyApi {
        val requestedHeads = mutableListOf<String>()

        override fun listBranches(repository: String, page: Int, perPage: Int) =
            if (page == 1) listOf(
                GitHubBranchRef("knowledge-recycle-foundation", "a".repeat(40)),
                GitHubBranchRef("fiction-body", "b".repeat(40))
            ) else emptyList()

        override fun treeForCommit(repository: String, commitSha: String): GitHubTreeSnapshot {
            requestedHeads += commitSha
            return if (commitSha.first() == 'a') {
                GitHubTreeSnapshot(
                    listOf(
                        GitHubTreeEntry("docs/knowledge-provenance.md", "c".repeat(40), "blob"),
                        GitHubTreeEntry("src/engine.kt", "d".repeat(40), "blob"),
                        GitHubTreeEntry("build", "e".repeat(40), "tree")
                    ),
                    truncated = false
                )
            } else {
                GitHubTreeSnapshot(
                    listOf(GitHubTreeEntry("story.md", "f".repeat(40), "blob")),
                    truncated = true
                )
            }
        }
    }

    @Test fun discoveryPinsHeadsAndCreatesUnknownSourceRecords() {
        val api = FakeApi()
        val result = GitHubWantBranchDiscovery(api).discover("Vanellye/CodEXgen", "knowledge provenance")

        assertEquals(2, result.candidates.size)
        assertEquals(setOf("a".repeat(40), "b".repeat(40)), api.requestedHeads.toSet())
        assertEquals("a".repeat(40), result.matches.first().headRevision)
        assertTrue(result.sourceRecords.isNotEmpty())
        assertTrue(result.sourceRecords.all { it.evidence.single().evidenceStatus == EvidenceStatus.UNKNOWN })
        assertTrue(result.sourceRecords.all { it.evidence.single().sourceRef.contains("a".repeat(40)) })
        assertEquals(setOf("fiction-body"), result.truncatedBranches)
        assertEquals("knowledge-recycle-foundation", result.matches.first().branch)
    }

    @Test fun invalidRepositoryAndEmptyWantAreRejected() {
        val discovery = GitHubWantBranchDiscovery(FakeApi())
        assertThrows(IllegalArgumentException::class.java) { discovery.discover("../bad", "knowledge") }
        assertThrows(IllegalArgumentException::class.java) { discovery.discover("Vanellye/CodEXgen", " ") }
    }
}
