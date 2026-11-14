package com.vanellye.eria.contracts

import com.vanellye.eria.pons.PonsAnchorIdentity
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.nio.charset.StandardCharsets

class SimulationIntegrityTest {
    @Test
    fun identicalInputsAndSeedProduceReproducibleSimulationEvidence() {
        val input = "stimulus".toByteArray(StandardCharsets.UTF_8)
        val config = "configuration-v1".toByteArray(StandardCharsets.UTF_8)
        val evidence = SimulationIntegrityRunner.run(
            runId = "run-001",
            scenarioId = "audio-resonance-baseline",
            engineRef = "test-engine-ref",
            engineVersion = "0.1.0",
            seed = 1111L,
            input = input,
            configuration = config,
            simulator = DeterministicSimulation { source, settings, seed ->
                (source + settings + seed.toString().toByteArray()).reversedArray()
            }
        )

        assertEquals(SimulationIntegrityState.REPRODUCIBLE, evidence.state)
        assertEquals(PonsAnchorIdentity.CANONICAL, evidence.anchor)
        assertTrue(evidence.simulatedOnly)
        assertFalse(evidence.hardwareObserved)
        assertEquals(evidence.firstOutputSha256, evidence.secondOutputSha256)
        assertTrue(evidence.evidenceId.matches(Regex("^[0-9a-f]{64}$")))
        assertTrue(evidence.input().contentEquals(input))
        assertTrue(evidence.configuration().contentEquals(config))
        assertTrue(evidence.firstOutput().contentEquals(evidence.secondOutput()))
        val exposedCopy = evidence.firstOutput()
        exposedCopy[0] = (exposedCopy[0].toInt() xor 0xff).toByte()
        assertTrue(evidence.firstOutput().contentEquals(evidence.secondOutput()))
    }

    @Test
    fun nondeterministicOutputsAreExplicitlyMarkedAndNeverHardwareEvidence() {
        var invocation = 0
        val evidence = SimulationIntegrityRunner.run(
            runId = "run-002",
            scenarioId = "unstable-model",
            engineRef = "test-engine-ref",
            engineVersion = "0.1.0",
            seed = 7L,
            input = byteArrayOf(1),
            configuration = byteArrayOf(2),
            simulator = DeterministicSimulation { _, _, _ ->
                invocation++
                byteArrayOf(invocation.toByte())
            }
        )

        assertEquals(SimulationIntegrityState.NONDETERMINISTIC, evidence.state)
        assertNotEquals(evidence.firstOutputSha256, evidence.secondOutputSha256)
        assertTrue(evidence.simulatedOnly)
        assertFalse(evidence.hardwareObserved)
    }

    @Test(expected = IllegalArgumentException::class)
    fun alternateAnchorCannotCreateSimulationEvidence() {
        SimulationIntegrityRunner.run(
            runId = "run-003",
            scenarioId = "alternate-anchor",
            engineRef = "test-engine-ref",
            engineVersion = "0.1.0",
            seed = 1L,
            input = byteArrayOf(1),
            configuration = byteArrayOf(2),
            simulator = DeterministicSimulation { source, _, _ -> source },
            anchor = PonsAnchorIdentity("other", "other-branch", "0".repeat(40))
        )
    }
}
