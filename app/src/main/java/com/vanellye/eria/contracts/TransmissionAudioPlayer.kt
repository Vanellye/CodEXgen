package com.vanellye.eria.contracts

import android.media.MediaPlayer
import java.io.File
import com.vanellye.eria.pons.PonsComponentStatus
import com.vanellye.eria.pons.PonsEffectiveState
import com.vanellye.eria.pons.PonsAnchorIdentity

/**
 * Explicit local playback for a WAV file created from a transmission.
 * Calling play() is the playback authorization point; receiving data never starts audio.
 */
object TransmissionAudioPlayer {
    fun play(wavFile: File, ponsStatus: PonsComponentStatus, onCompletion: (() -> Unit)? = null) {
        ponsStatus.requireReady("audio.player")
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
