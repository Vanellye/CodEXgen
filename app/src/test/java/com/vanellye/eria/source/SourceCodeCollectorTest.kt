package com.vanellye.eria.source

import com.vanellye.eria.contracts.AuthorizationStatus
import com.vanellye.eria.contracts.DataAuthorization
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.time.Clock
import java.time.Instant
import java.time.ZoneOffset

class SourceCodeCollectorTest {
    private val approval = DataAuthorization(
        status = AuthorizationStatus.AUTHORIZED,
        scope = listOf("source.collect"),
        approvalRef = "approval-source-001"
    )

    private fun input(content: String = "fun main() = Unit") = SourceCodeInput(
        repository = "Vanellye/CodEXgen",
        sourceRef = "refs/heads/transmission",
        commitSha = "a".repeat(40),
        relativePath = "app/src/main/kotlin/Sample.kt",
        language = "kotlin",
        content = content
    )

    private fun collector() = SourceCodeCollector(
        clock = Clock.fixed(Instant.parse("2026-11-12T18:00:00Z"), ZoneOffset.UTC)
    )

    @Test fun collectsExactTextWithSha256AndOrigin() {
        val result = collector().collect(input(), approval)
        val expected = MessageDigest.getInstance("SHA-256")
            .digest("fun main() = Unit".toByteArray(StandardCharsets.UTF_8))
            .joinToString("") { "%02x".format(it) }

        assertEquals("fun main() = Unit", result.content)
        assertEquals(expected, result.envelope.provenance.sourceDigest)
        assertEquals("Vanellye/CodEXgen", result.envelope.payload["repository"])
        assertEquals("refs/heads/transmission", result.envelope.provenance.sourceRef)
        assertEquals("a".repeat(40), result.envelope.provenance.sourceCommit)
        assertEquals("not_performed", result.envelope.validation["source_execution"])
        assertEquals("not_performed", result.envelope.validation["network_access"])
    }

    @Test fun rejectsMissingOrInsufficientAuthorization() {
        val missing = DataAuthorization()
        val wrongScope = approval.copy(scope = listOf("source.inspect"))
        listOf(missing, wrongScope).forEach { authorization ->
            try {
                collector().collect(input(), authorization)
                throw AssertionError("collection should have been rejected")
            } catch (expected: SourceCollectionRejected) {
                assertTrue(expected.message!!.contains("authorization"))
            }
        }
    }

    @Test fun rejectsPathTraversalAndNonFullCommitIds() {
        try {
            collector().collect(input().copy(relativePath = "../secrets.txt"), approval)
            throw AssertionError("path traversal should have been rejected")
        } catch (expected: SourceCollectionRejected) {
            assertTrue(expected.message!!.contains("relative"))
        }

        try {
            collector().collect(input().copy(commitSha = "main"), approval)
            throw AssertionError("symbolic refs are not commit identities")
        } catch (expected: SourceCollectionRejected) {
            assertTrue(expected.message!!.contains("commitSha"))
        }
    }

    @Test fun rejectsEmptyAndOversizedContent() {
        try {
            collector().collect(input(content = ""), approval)
            throw AssertionError("empty content should have been rejected")
        } catch (expected: SourceCollectionRejected) {
            assertTrue(expected.message!!.contains("empty"))
        }

        try {
            collector().collect(input(content = "x".repeat(SourceCodeCollector.DEFAULT_MAX_BYTES + 1)), approval)
            throw AssertionError("oversized content should have been rejected")
        } catch (expected: SourceCollectionRejected) {
            assertTrue(expected.message!!.contains("exceeds"))
        }
    }
}
