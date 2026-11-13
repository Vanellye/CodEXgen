package com.vanellye.eria.contracts

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.nio.charset.StandardCharsets

class SkribedAndTransmissionTest {
    private fun document(source: String): SkribedDocument =
        SkribedDocument(source, InMemoryCorrectionLineageJournal())

    @Test
    fun originalWritingPreservesUnicodeAndPunctuationExactly() {
        val source = "Öôŕîɣîñäl·l  e\u0301 Ĉ̣ — Ɓûîľð"
        val document = document(source)
        assertEquals(source, document.originalText)
        assertArrayEquals(source.toByteArray(StandardCharsets.UTF_8), document.originalBytes())
        assertTrue(document.originalSha256.matches(Regex("^[0-9a-f]{64}$")))
    }

    @Test
    fun correctionTiersRetainBothHistoricalAndFutureMarkerAnchors() {
        val document = document("source")
        val corrected = document.derive(
            WritingVariantKind.CORRECTED, "corrected", "editorial-correction", "1"
        )
        assertEquals(
            CorrectionTierLine.ORIGINAL_SOURCE_TIER_COMMIT,
            corrected.correctionTier.originalSourceTierCommit
        )
        assertEquals(
            "712961866e615ff4db9e90cd40bece78a45afe39",
            corrected.correctionTier.futureMarkerAnchorCommit
        )
        assertEquals(
            CorrectionDirection.FORWARD,
            corrected.correctionTier.direction
        )
    }

    @Test
    fun reverseAlternatorCreatesNewToFromTierWithoutErasingForwardTier() {
        val source = "source"
        val document = document(source)
        val forward = document.derive(
            WritingVariantKind.CORRECTED,
            "corrected",
            "editorial-correction",
            "1"
        )
        val reverse = document.reverseTo(
            prior = forward,
            targetText = source,
            operationVersion = "1"
        )

        assertEquals(forward.outputSha256, reverse.correctionTier.fromSha256)
        assertEquals(document.originalSha256, reverse.correctionTier.toSha256)
        assertEquals(CorrectionDirection.REVERSE, reverse.correctionTier.direction)
        assertEquals(forward.correctionTier.correctionId, reverse.correctionTier.sourceCorrectionId)
        assertEquals(
            listOf(forward.correctionTier.correctionId),
            reverse.correctionTier.lineageCorrectionIds
        )
        assertEquals(2, document.correctionTiers().size)
        assertEquals(CorrectionDirection.FORWARD, document.correctionTiers()[0].direction)
        assertEquals(CorrectionDirection.REVERSE, document.correctionTiers()[1].direction)
        assertEquals(source, document.originalText)
    }

    @Test(expected = IllegalArgumentException::class)
    fun reverseAlternatorRejectsTargetThatDoesNotMatchPriorFromHash() {
        val document = document("source")
        val forward = document.derive(
            WritingVariantKind.CORRECTED, "corrected", "editorial-correction", "1"
        )
        document.reverseTo(forward, "not-the-original", "1")
    }

    @Test
    fun chainedCorrectionsRetainFullTierLineage() {
        val document = document("source")
        val first = document.derive(
            WritingVariantKind.CORRECTED, "first correction", "correction-one", "1"
        )
        val second = document.derive(
            WritingVariantKind.CORRECTED,
            "second correction",
            "correction-two",
            "1",
            basedOn = first
        )
        assertEquals(first.outputSha256, second.correctionTier.fromSha256)
        assertEquals(first.correctionTier.correctionId, second.correctionTier.sourceCorrectionId)
        assertEquals(listOf(first.correctionTier.correctionId), second.correctionTier.lineageCorrectionIds)
        assertEquals(2, document.correctionTiers().size)
        assertEquals("source", document.originalText)
    }

    @Test
    fun fileJournalPersistsDirectionAndMarkerAnchorAcrossJournalInstances() {
        val file = File.createTempFile("eria-corrections-", ".log")
        try {
            val document = SkribedDocument("source", FileCorrectionLineageJournal(file))
            val forward = document.derive(
                WritingVariantKind.CORRECTED, "corrected", "persisted-correction", "1"
            )
            document.reverseTo(forward, "source", "1")
            val restored = FileCorrectionLineageJournal(file).readAll()

            assertEquals(2, restored.size)
            assertEquals(CorrectionDirection.FORWARD, restored[0].direction)
            assertEquals(CorrectionDirection.REVERSE, restored[1].direction)
            assertEquals(
                CorrectionTierLine.FUTURE_MARKER_ANCHOR_COMMIT,
                restored[1].futureMarkerAnchorCommit
            )
        } finally {
            file.delete()
        }
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsCorrectionBasedOnDetachedVariant() {
        val document = document("source")
        val foreignDocument = document("other source")
        val detached = foreignDocument.derive(
            WritingVariantKind.CORRECTED, "foreign correction", "foreign-operation", "1"
        )
        document.derive(
            WritingVariantKind.CORRECTED,
            "attempted detached correction",
            "local-operation",
            "1",
            basedOn = detached
        )
    }

    @Test
    fun correctionHistoryIsReturnedAsASnapshot() {
        val document = document("source")
        document.derive(
            WritingVariantKind.CORRECTED, "corrected", "editorial-correction", "1"
        )
        val snapshot = document.correctionTiers()
        assertEquals(1, snapshot.size)
        assertTrue(snapshot.single().resultingCommitSha == null)
    }

    @Test(expected = IllegalArgumentException::class)
    fun originalCannotBeReplacedByDerivative() {
        document("source").derive(
            WritingVariantKind.ORIGINAL, "replacement", "rewrite", "1"
        )
    }

    @Test
    fun transceiverReturnsCorrelatedInternalResponse() {
        val request = "sound-data".toByteArray(StandardCharsets.UTF_8)
        val frame = TransmissionFrame.create("tx-1", "corr-1", "audio.capture", request)
        val receipt = InMemoryTransmissionTransceiver().transceive(frame) { incoming ->
            incoming.payload() + "-returned".toByteArray(StandardCharsets.UTF_8)
        }
        assertEquals("tx-1", receipt.transmissionId)
        assertEquals("corr-1", receipt.correlationId)
        assertEquals("audio.capture", receipt.sourceRef)
        assertEquals("sound-data-returned", String(receipt.responsePayload, StandardCharsets.UTF_8))
        assertTrue(receipt.responseSha256.matches(Regex("^[0-9a-f]{64}$")))
    }

    @Test
    fun frameOwnsDefensiveCopyOfInputPayload() {
        val input = byteArrayOf(1, 2, 3)
        val frame = TransmissionFrame.create("tx-2", "corr-2", "test.source", input)
        input[0] = 99
        assertArrayEquals(byteArrayOf(1, 2, 3), frame.payload())
    }
}
