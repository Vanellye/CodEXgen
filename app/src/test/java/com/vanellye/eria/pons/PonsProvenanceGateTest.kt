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

    @Test fun trustPinMapIsSnapshotted() {
        val source = "stable-source".toByteArray()
        val id = "stable.component"
        val pin = PonsComponentPin(id, "ref-1", "src/Stable.kt", PonsProvenanceGate.sha256(source))
        val mutablePins = mutableMapOf(id to pin)
        val gate = PonsProvenanceGate(mutablePins)
        mutablePins[id] = pin.copy(sha256 = "0".repeat(64))
        assertEquals(PonsProvenanceState.VERIFIED, gate.verify(id, source).state)
    }


    @Test fun signedManifestFactoryRequiresTrustedVerifier() {
        val source = "manifest-backed".toByteArray()
        val id = "signed.component"
        val pin = PonsComponentPin(
            id, "reviewed-commit", "app/src/main/java/Signed.kt",
            PonsProvenanceGate.sha256(source)
        )
        val manifest = PonsSignedManifest(
            version = "manifest-v1",
            keyId = "review-key",
            signature = "signature",
            anchor = PonsAnchorIdentity.CANONICAL,
            pins = listOf(pin)
        )
        try {
            PonsProvenanceGate.fromSignedManifest(manifest) { _, _, _ -> false }
            throw AssertionError("rejected signature must not create a gate")
        } catch (_: IllegalArgumentException) {
            // expected fail-closed result
        }
        val gate = PonsProvenanceGate.fromSignedManifest(manifest) { payload, key, signature ->
            payload.isNotEmpty() && key == "review-key" && signature == "signature"
        }
        assertEquals(PonsProvenanceState.VERIFIED, gate.verify(id, source).state)
    }

}
