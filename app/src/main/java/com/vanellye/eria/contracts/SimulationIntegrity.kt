package com.vanellye.eria.contracts

import com.vanellye.eria.pons.PonsAnchorIdentity
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.charset.StandardCharsets
import java.security.MessageDigest

/**
 * Simulation output is evidence about a model execution, never evidence of hardware activity.
 * The runner executes the same declared inputs twice and compares exact output bytes.
 */
enum class SimulationIntegrityState { REPRODUCIBLE, NONDETERMINISTIC }

fun interface DeterministicSimulation {
    /** Implementations must be side-effect-free and deterministic for identical arguments. */
    fun execute(input: ByteArray, configuration: ByteArray, seed: Long): ByteArray
}

data class SimulationEvidence(
    val evidenceId: String,
    val runId: String,
    val scenarioId: String,
    val engineRef: String,
    val engineVersion: String,
    val seed: Long,
    val inputSha256: String,
    val configurationSha256: String,
    val firstOutputSha256: String,
    val secondOutputSha256: String,
    val state: SimulationIntegrityState,
    val anchor: PonsAnchorIdentity,
    val simulatedOnly: Boolean = true,
    val hardwareObserved: Boolean = false
)

/** Reproducibility check with explicit simulation-vs-hardware separation. */
object SimulationIntegrityRunner {
    fun run(
        runId: String,
        scenarioId: String,
        engineRef: String,
        engineVersion: String,
        seed: Long,
        input: ByteArray,
        configuration: ByteArray,
        simulator: DeterministicSimulation,
        anchor: PonsAnchorIdentity = PonsAnchorIdentity.CANONICAL
    ): SimulationEvidence {
        require(runId.isNotBlank()) { "runId must not be blank" }
        require(scenarioId.isNotBlank()) { "scenarioId must not be blank" }
        require(engineRef.isNotBlank()) { "engineRef must not be blank" }
        require(engineVersion.isNotBlank()) { "engineVersion must not be blank" }
        require(anchor == PonsAnchorIdentity.CANONICAL) { "Simulation anchor mismatch" }

        val stableInput = input.copyOf()
        val stableConfiguration = configuration.copyOf()
        val first = simulator.execute(stableInput.copyOf(), stableConfiguration.copyOf(), seed).copyOf()
        val second = simulator.execute(stableInput.copyOf(), stableConfiguration.copyOf(), seed).copyOf()
        val inputHash = sha256(stableInput)
        val configurationHash = sha256(stableConfiguration)
        val firstHash = sha256(first)
        val secondHash = sha256(second)
        val state = if (first.contentEquals(second)) {
            SimulationIntegrityState.REPRODUCIBLE
        } else {
            SimulationIntegrityState.NONDETERMINISTIC
        }
        val evidenceId = sha256(canonicalBytes(listOf(
            runId, scenarioId, engineRef, engineVersion, seed.toString(),
            inputHash, configurationHash, firstHash, secondHash,
            state.name, anchor.anchorId, anchor.branch, anchor.refSha,
            "simulated-only", "hardware-not-observed"
        )))
        return SimulationEvidence(
            evidenceId = evidenceId,
            runId = runId,
            scenarioId = scenarioId,
            engineRef = engineRef,
            engineVersion = engineVersion,
            seed = seed,
            inputSha256 = inputHash,
            configurationSha256 = configurationHash,
            firstOutputSha256 = firstHash,
            secondOutputSha256 = secondHash,
            state = state,
            anchor = anchor
        )
    }

    private fun sha256(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes)
            .joinToString("") { "%02x".format(it) }

    /** Length-prefixed UTF-8 fields avoid delimiter ambiguity in evidence identity. */
    private fun canonicalBytes(fields: List<String>): ByteArray {
        val encoded = fields.map { it.toByteArray(StandardCharsets.UTF_8) }
        val size = encoded.sumOf { 4 + it.size }
        val buffer = ByteBuffer.allocate(size).order(ByteOrder.BIG_ENDIAN)
        encoded.forEach { field ->
            buffer.putInt(field.size)
            buffer.put(field)
        }
        return buffer.array()
    }
}
