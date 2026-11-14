package com.vanellye.eria.contracts

import org.junit.Assert.assertEquals
import com.vanellye.eria.pons.*
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

class WavAudioTransmissionTest {

    private fun ponsAudioStatus(): PonsComponentStatus {
        val source = "pinned-audio-transmission-component".toByteArray()
        val componentId = "audio.wav-transmission"
        val pin = PonsComponentPin(
            componentId, "test-ref",
            "app/src/main/java/com/vanellye/eria/contracts/WavAudioTransmission.kt",
            PonsProvenanceGate.sha256(source)
        )
        return PonsStatusRegistry(PonsProvenanceGate(mapOf(componentId to pin)))
            .inspect(componentId, PonsOperationalState.READY, source)
    }
    @Test
    fun transmittedPcmBecomesValidWavFile() {
        // 10 ms of silence at 8 kHz, mono, signed PCM16.
        val pcm = ByteArray(160)
        val frame = TransmissionFrame.create("audio-1", "corr-1", "test-tone", pcm)
        val endpoint = WavAudioTransmissionEndpoint(8_000, 1, ponsAudioStatus())
        val file = File.createTempFile("eria-transmission-", ".wav")
        try {
            endpoint.writeWavFile(frame, file)
            val bytes = file.readBytes()
            assertEquals("RIFF", String(bytes.copyOfRange(0, 4), Charsets.US_ASCII))
            assertEquals("WAVE", String(bytes.copyOfRange(8, 12), Charsets.US_ASCII))
            assertEquals("data", String(bytes.copyOfRange(36, 40), Charsets.US_ASCII))
            assertEquals(8_000, littleEndianInt(bytes, 24))
            assertEquals(pcm.size, littleEndianInt(bytes, 40))
            assertEquals(44 + pcm.size, bytes.size)
        } finally {
            file.delete()
        }
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsIncompletePcmSampleFrame() {
        WavAudioTransmissionEndpoint.encodePcm16(byteArrayOf(1), 44_100, 1)
    }

    @Test
    fun transceiverReturnsWavPayloadWithoutStartingPlayback() {
        val pcm = ByteArray(320)
        val frame = TransmissionFrame.create("audio-2", "corr-2", "test-tone", pcm)
        val receipt = InMemoryTransmissionTransceiver(ponsAudioStatus()).transceive(
            frame,
            WavAudioTransmissionEndpoint(8_000, 1)
        )
        assertTrue(receipt.responsePayload.size > pcm.size)
        assertEquals("RIFF", String(receipt.responsePayload.copyOfRange(0, 4), Charsets.US_ASCII))
    }

    private fun littleEndianInt(bytes: ByteArray, offset: Int): Int =
        (bytes[offset].toInt() and 0xff) or
            ((bytes[offset + 1].toInt() and 0xff) shl 8) or
            ((bytes[offset + 2].toInt() and 0xff) shl 16) or
            ((bytes[offset + 3].toInt() and 0xff) shl 24)
}
