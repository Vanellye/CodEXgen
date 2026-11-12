package com.vanellye.eria.source

import com.vanellye.eria.contracts.AuthorizationStatus
import com.vanellye.eria.contracts.DataAuthorization
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.nio.file.Files

class LocalSourceCodeStoreTest {
    private val collectApproval = DataAuthorization(
        AuthorizationStatus.AUTHORIZED,
        listOf("source.collect"),
        "approval-local-001"
    )
    private val storeApproval = DataAuthorization(
        AuthorizationStatus.AUTHORIZED,
        listOf("source.collect", "source.store", "source.read"),
        "approval-local-001"
    )

    private fun collected(content: String = "fun main() = Unit") =
        SourceCodeCollector().collect(
            SourceCodeInput(
                repository = "Vanellye/CodEXgen",
                sourceRef = "refs/heads/transmission",
                commitSha = "b".repeat(40),
                relativePath = "src/Sample.kt",
                language = "kotlin",
                content = content
            ),
            collectApproval
        )

    @Test fun storesOnlyWithSeparateMatchingStorageApprovalAndReadsBackVerifiedBytes() {
        val dir = Files.createTempDirectory("eria-store-test").toFile()
        try {
            val store = LocalSourceCodeStore(dir)
            val record = collected()
            val saved = store.store(record, storeApproval)
            assertEquals(record.content, saved.content)
            assertEquals(record.envelope.provenance.sourceDigest, saved.envelope.provenance.sourceDigest)
            val loaded = store.load(record.envelope.recordId, storeApproval)
            assertEquals(record.content, loaded.content)
        } finally {
            dir.deleteRecursively()
        }
    }

    @Test fun rejectsCollectionOnlyApprovalAndMismatchedApprovalReference() {
        val dir = Files.createTempDirectory("eria-store-deny").toFile()
        try {
            val store = LocalSourceCodeStore(dir)
            try {
                store.store(collected(), collectApproval)
                throw AssertionError("storage must require source.store")
            } catch (expected: SourceIntegrityRejected) {
                assertTrue(expected.message!!.contains("source.store"))
            }
            try {
                store.store(collected(), storeApproval.copy(approvalRef = "different-approval"))
                throw AssertionError("storage must require matching approval reference")
            } catch (expected: SourceIntegrityRejected) {
                assertTrue(expected.message!!.contains("approvalRef"))
            }
            assertTrue(dir.listFiles().orEmpty().isEmpty())
        } finally {
            dir.deleteRecursively()
        }
    }

    @Test fun rejectsTamperedInMemoryContentBeforeWriting() {
        val dir = Files.createTempDirectory("eria-store-tamper").toFile()
        try {
            val record = collected()
            try {
                LocalSourceCodeStore(dir).store(record.copy(content = "tampered"), storeApproval)
                throw AssertionError("digest mismatch must fail closed")
            } catch (expected: SourceIntegrityRejected) {
                assertTrue(expected.message!!.contains("SHA-256"))
            }
            assertTrue(dir.listFiles().orEmpty().isEmpty())
        } finally {
            dir.deleteRecursively()
        }
    }
}
