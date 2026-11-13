package com.vanellye.eria.contracts

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.nio.charset.StandardCharsets

class SkribedAndTransmissionTest {
    @Test
    fun originalWritingPreservesUnicodeAndPunctuationExactly() {
        val source = "Öôŕîɣîñäl·l  e\u0301 Ĉ̣ — Ɓûîľð"
        val document = document(source)

        assertEquals(source, document.originalText)
        assertArrayEquals(source.toByteArray(StandardCharsets.UTF_8), document.originalBytes())
        assertTrue(document.originalSha256.matches(Regex("^[0-9a-f]{64}$")))
    }

    @Test
    fun derivedWritingDoesNotReplaceOriginalAndCreatesAnchoredCorrectionTier() {
        val source = "Original: e\u0301 / Ĉ̣"
        val document = document(source)
        val corrected = document.derive(
            WritingVariantKind.CORRECTED,
            "Corrected: é / Ĉ̣",
            "editorial-correction",
            "1"
        )

        assertEquals(source, document.originalText)
        assertNotEquals(document.originalSha256, corrected.outputSha256)
        assertEquals(WritingVariantKind.CORRECTED, corrected.kind)
        assertEquals(
            CorrectionTierLine.ORIGINAL_SOURCE_TIER_COMMIT,
            corrected.correctionTier.originalSourceTierCommit
        )
        assertEquals(document.originalSha256, corrected.correctionTier.fromSha256)
        assertEquals(corrected.outputSha256, corrected.correctionTier.toSha256)
        assertEquals(CorrectionChangeKind.REPLACE, corrected.correctionTier.changeKind)
        assertEquals(1, document.correctionTiers().size)
    }

    @Test
    fun chainedCorrectionsRetainTheFullTierLineage() {
        val document = document("source")
        val first = document.derive(
            WritingVariantKind.CORRECTED,
            "first correction",
            "correction-one",
            "1"
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
        assertEquals(
            listOf(first.correctionTier.correctionId),
            second.correctionTier.lineageCorrectionIds
        )
        assertEquals(
            CorrectionTierLine.ORIGINAL_SOURCE_TIER_COMMIT,
            second.correctionTier.originalSourceTierCommit
        )
        assertEquals(2, document.correctionTiers().size)
        assertEquals("source", document.originalText)
    }

    @Test
    fun fileJournalPersistsCorrectionTiersAcrossJournalInstances() {
        val file = File.createTempFile("eria-corrections-", ".log")
        try {
            val firstJournal = FileCorrectionLineageJournal(file)
            val document = SkribedDocument(
                originalText = "source",
                correctionJournal = firstJournal
            )
            val correction = document.derive(
                WritingVariantKind.CORRECTED,
                "corrected",
                "persisted-correction",
                "1",
                correctionPoint = "test.persisted-correction"
            )

            val restored = FileCorrectionLineageJournal(file).readAll()
            assertEquals(1, restored.size)
            assertEquals(correction.correctionTier.correctionId, restored.single().correctionId)
            assertEquals(
                CorrectionTierLine.ORIGINAL_SOURCE_TIER_COMMIT,
                restored.single().originalSourceTierCommit
            )
            assertEquals(correction.correctionTier.fromSha256, restored.single().fromSha256)
            assertEquals(correction.correctionTier.toSha256, restored.single().toSha256)
        } finally {
            file.delete()
        }
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsCorrectionBasedOnDetachedVariant() {
        val document = document("source")
        val foreignDocument = document("other source")
        val detached = foreignDocument.derive(
            WritingVariantKind.CORRECTED,
            "foreign correction",
            "foreign-operation",
            "1"
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
            WritingVariantKind.CORRECTED,
            "corrected",
            "editorial-correction",
            "1"
        )

        val snapshot = document.correctionTiers()
        assertEquals(1, snapshot.size)
        assertTrue(snapshot.single().resultingCommitSha == null)
    }

    @Test(expected = IllegalArgumentException::class)
    fun originalCannotBeReplacedByDerivative() {
        document("source").derive(
            WritingVariantKind.ORIGINAL,
            "replacement",
            "rewrite",
            "1"
        )
    }

    @Test
    fun transceiverReturnsCorrelatedInternalResponse() {
        val request = "sound-data".toByteArray(StandardCharsets.UTF_8)
        val frame = TransmissionFrame.create("tx-1", "corr-1", "audio.capture", request)
        val transceiver = InMemoryTransmissionTransceiver()

        val receipt = transceiver.transceive(frame) { incoming ->
            incoming.payload() + "-returned".toByteArray(StandardCharsets.UTF_8)
        }

        assertEquals("tx-1", receipt.transmissionId)
        assertEquals("corr-1", receipt.correlationId)
        assertEquals("audio.capture", receipt.sourceRef)
        assertEquals(
            "sound-data-returned",
            String(receipt.responsePayload, StandardCharsets.UTF_8)
        )
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
