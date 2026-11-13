package com.vanellye.eria.contracts

import android.media.MediaPlayer
import java.io.File

/**
 * Explicit local playback for a WAV file created from a transmission.
 * Calling play() is the playback authorization point; receiving data never starts audio.
 */
object TransmissionAudioPlayer {
    fun play(wavFile: File, onCompletion: (() -> Unit)? = null) {
        require(wavFile.isFile && wavFile.canRead()) { "WAV file is not readable" }
        val player = MediaPlayer()
        try {
            player.setDataSource(wavFile.absolutePath)
            player.setOnCompletionListener {
                it.release()
                onCompletion?.invoke()
            }
            player.setOnErrorListener { mp, _, _ ->
                mp.release()
                true
            }
            player.setOnPreparedListener { it.start() }
            player.prepareAsync()
        } catch (failure: Exception) {
            player.release()
            throw failure
        }
    }
}
