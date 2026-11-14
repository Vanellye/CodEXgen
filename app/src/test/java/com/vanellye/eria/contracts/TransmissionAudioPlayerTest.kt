package com.vanellye.eria.contracts

import com.vanellye.eria.pons.PonsProvenanceGate
import com.vanellye.eria.pons.PonsStatusRegistry
import com.vanellye.eria.pons.PonsOperationalState
import org.junit.Test
import java.io.File

class TransmissionAudioPlayerTest {
    @Test(expected = IllegalArgumentException::class)
    fun playbackHoldsWhenPonsEvidenceIsUnknown() {
        val status = PonsStatusRegistry(PonsProvenanceGate(emptyMap()))
            .inspect("audio.player", PonsOperationalState.READY, null)
        TransmissionAudioPlayer.play(File("not-opened.wav"), status)
    }
}
