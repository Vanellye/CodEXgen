package com.vanellye.eria.pons

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Test

class PonsProvenanceGateTest {
    private val bytes = "ERIA source".toByteArray()
    private val pin = PonsComponentPin(
        componentId = "android.pantheon-runtime-gate",
        sourceRef = "main",
        sourcePath = "app/src/main/java/com/vanellye/eria/pantheon/PantheonRuntimeGate.kt",
        sha256 = PonsProvenanceGate.sha256(bytes)
    )

    @Test fun matchingDigestVerifies() {
        val result = PonsProvenanceGate(mapOf(pin.componentId to pin))
            .verify(pin.componentId, bytes)
        assertEquals(PonsProvenanceState.VERIFIED, result.state)
    }

    @Test fun mismatchHolds() {
        val result = PonsProvenanceGate(mapOf(pin.componentId to pin))
            .verify(pin.componentId, "altered".toByteArray())
        assertEquals(PonsProvenanceState.HOLD, result.state)
        assertNotEquals(pin.sha256, result.actualSha256)
    }

    @Test fun missingPinOrSourceIsUnknown() {
        val gate = PonsProvenanceGate(emptyMap())
        assertEquals(PonsProvenanceState.UNKNOWN, gate.verify("unknown", bytes).state)
        val pinned = PonsProvenanceGate(mapOf(pin.componentId to pin))
        assertEquals(PonsProvenanceState.UNKNOWN, pinned.verify(pin.componentId, null).state)
    }

    @Test(expected = IllegalArgumentException::class)
    fun alteredCanonicalAnchorIsRejected() {
        PonsProvenanceGate(emptyMap(), PonsAnchorIdentity("x", "zero-dissipation-anchor", "0".repeat(40)))
    }
    @Test fun effectiveStatusCannotOverrideProvenanceHold() {
        val gate = PonsProvenanceGate(mapOf(pin.componentId to pin))
        val status = PonsStatusRegistry(gate).inspect(
            pin.componentId, PonsOperationalState.READY, "changed".toByteArray()
        )
        assertEquals(PonsEffectiveState.HOLD, status.effectiveState)
    }

    @Test fun unpinnedComponentRemainsUnknownEvenWhenReportedReady() {
        val status = PonsStatusRegistry(PonsProvenanceGate(emptyMap())).inspect(
            "music.engine", PonsOperationalState.READY, bytes
        )
        assertEquals(PonsEffectiveState.UNKNOWN, status.effectiveState)
    }

}
