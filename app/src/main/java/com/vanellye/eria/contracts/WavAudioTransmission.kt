package com.vanellye.eria.contracts

import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import com.vanellye.eria.pons.PonsComponentStatus
import com.vanellye.eria.pons.PonsEffectiveState
import com.vanellye.eria.pons.PonsAnchorIdentity

/**
 * Converts a transmitted raw PCM16 payload into a standard RIFF/WAVE file.
 *
 * Input contract: signed 16-bit little-endian PCM, mono or stereo.
 * The endpoint only creates a local file when writeWavFile is explicitly called.
 */
class WavAudioTransmissionEndpoint(
    private val sampleRateHz: Int = 44_100,
    private val channels: Int = 1,
    private val ponsStatus: PonsComponentStatus
) : InternalTransmissionEndpoint {

    init {
        ponsStatus.requireReady("audio.wav-transmission")
        require(sampleRateHz in 8_000..192_000) { "Unsupported sample rate" }
        require(channels == 1 || channels == 2) { "Only mono or stereo PCM is supported" }
    }

    override fun receive(frame: TransmissionFrame): ByteArray {
        require(frame.hasValidIntegrity()) { "Audio transmission integrity check failed" }
        return encodePcm16(frame.payload(), sampleRateHz, channels)
    }

    /** Writes a received PCM transmission as a .wav file and returns the created file. */
    fun writeWavFile(frame: TransmissionFrame, destination: File): File {
        val wavBytes = receive(frame)
        destination.parentFile?.mkdirs()
        FileOutputStream(destination).use { it.write(wavBytes) }
        return destination
    }

    companion object {
        private const val HEADER_BYTES = 44

        fun encodePcm16(pcm: ByteArray, sampleRateHz: Int, channels: Int): ByteArray {
            require(sampleRateHz in 8_000..192_000) { "Unsupported sample rate" }
            require(channels == 1 || channels == 2) { "Only mono or stereo PCM is supported" }
            require(pcm.size % (2 * channels) == 0) {
                "PCM payload must contain complete 16-bit sample frames"
            }
            val byteRate = sampleRateHz * channels * 2
            val blockAlign = channels * 2
            val out = ByteArrayOutputStream(HEADER_BYTES + pcm.size)
            val header = ByteBuffer.allocate(HEADER_BYTES).order(ByteOrder.LITTLE_ENDIAN)
            header.put("RIFF".toByteArray(Charsets.US_ASCII))
            header.putInt(36 + pcm.size)
            header.put("WAVE".toByteArray(Charsets.US_ASCII))
            header.put("fmt ".toByteArray(Charsets.US_ASCII))
            header.putInt(16)
            header.putShort(1.toShort())
            header.putShort(channels.toShort())
            header.putInt(sampleRateHz)
            header.putInt(byteRate)
            header.putShort(blockAlign.toShort())
            header.putShort(16.toShort())
            header.put("data".toByteArray(Charsets.US_ASCII))
            header.putInt(pcm.size)
            out.write(header.array())
            out.write(pcm)
            return out.toByteArray()
        }
    }
}
