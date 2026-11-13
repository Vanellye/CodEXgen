package com.vanellye.eria.contracts

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.nio.charset.StandardCharsets

class SkribedAndTransmissionTest {
    @Test
    fun originalWritingPreservesUnicodeAndPunctuationExactly() {
        val source = "Öôŕîɣîñäl·l  e\u0301 Ĉ̣ — Ɓûîľð"
        val document = SkribedDocument(source)

        assertEquals(source, document.originalText)
        assertArrayEquals(source.toByteArray(StandardCharsets.UTF_8), document.originalBytes())
        assertTrue(document.originalSha256.matches(Regex("^[0-9a-f]{64}$")))
    }

    @Test
    fun derivedWritingDoesNotReplaceOriginal() {
        val source = "Original: e\u0301 / Ĉ̣"
        val document = SkribedDocument(source)
        val corrected = document.derive(
            WritingVariantKind.CORRECTED,
            "Corrected: é / Ĉ̣",
            "editorial-correction",
            "1"
        )

        assertEquals(source, document.originalText)
        assertNotEquals(document.originalSha256, corrected.outputSha256)
        assertEquals(WritingVariantKind.CORRECTED, corrected.kind)
    }

    @Test(expected = IllegalArgumentException::class)
    fun originalCannotBeReplacedByDerivative() {
        SkribedDocument("source").derive(
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
