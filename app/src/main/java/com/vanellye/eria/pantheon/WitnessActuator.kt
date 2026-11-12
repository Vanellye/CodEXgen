package com.vanellye.eria.pantheon

import java.security.MessageDigest
import java.util.concurrent.Executor
import java.util.concurrent.FutureTask
import java.util.concurrent.atomic.AtomicBoolean

/**
 * Local-only adversarial witness test harness.
 *
 * Background execution is explicit: a host must call executeAsync and supply an Executor.
 * Every challenge operates on a copy. This class has no provider, network, process-launch,
 * device-control, persistence, or external-dispatch capability.
 */
data class WitnessRecord(
    val recordId: String,
    val sourceRef: String,
    val fields: Map<String, String>,
    val previousRecordHash: String? = null
)

enum class WitnessNoiseAction {
    ALTER_COPY_VALUE,
    DROP_COPY_FIELD,
    INJECT_SYNTHETIC_NOISE,
    REORDER_COPY_FIELDS
}

data class WitnessChallenge(
    val challengeId: String,
    val action: WitnessNoiseAction,
    val challengedFields: Map<String, String>,
    val syntheticNoise: Boolean
)

data class WitnessAssessment(
    val witnessId: String,
    val detectedAlteration: Boolean,
    val observedDigest: String,
    val note: String
)

interface WitnessAgent {
    val witnessId: String
    fun assess(originalDigest: String, challenge: WitnessChallenge): WitnessAssessment
}

/** A baseline witness that detects changes to the canonical field map. */
class DigestWitnessAgent(override val witnessId: String = "digest-witness") : WitnessAgent {
    override fun assess(originalDigest: String, challenge: WitnessChallenge): WitnessAssessment {
        val observed = WitnessActuator.digestFields(challenge.challengedFields)
        return WitnessAssessment(
            witnessId = witnessId,
            detectedAlteration = observed != originalDigest,
            observedDigest = observed,
            note = if (observed != originalDigest) "challenge differs from source digest" else "no digest difference observed"
        )
    }
}

data class WitnessRunEntry(
    val challengeId: String,
    val action: WitnessNoiseAction,
    val assessment: WitnessAssessment,
    val sourceRecordUnchanged: Boolean
)

data class WitnessRunResult(
    val recordId: String,
    val sourceDigest: String,
    val previousRecordHash: String?,
    val entries: List<WitnessRunEntry>,
    val witnessStrengthPercent: Int,
    val auditRecordHash: String
)

class WitnessRunHandle internal constructor(
    private val cancelled: AtomicBoolean,
    private val task: FutureTask<WitnessRunResult>
) {
    fun cancel(): Boolean {
        cancelled.set(true)
        return task.cancel(true)
    }
    fun isCancelled(): Boolean = cancelled.get() || task.isCancelled
    fun result(): WitnessRunResult = task.get()
}

object WitnessActuator {
    private val sha256Pattern = Regex("^[0-9a-f]{64}$")

    /**
     * Runs a finite set of synthetic opposing challenges. Each challenge is applied only to
     * a copied map; the original record is never modified. No challenge is dispatched.
     */
    fun run(
        record: WitnessRecord,
        actions: List<WitnessNoiseAction>,
        witnesses: List<WitnessAgent>,
        maxChallenges: Int = 16
    ): WitnessRunResult {
        require(record.recordId.isNotBlank() && record.sourceRef.isNotBlank()) { "record identity and source are required" }
        require(record.previousRecordHash == null || sha256Pattern.matches(record.previousRecordHash)) {
            "previous record hash must be lowercase SHA-256"
        }
        require(actions.isNotEmpty()) { "at least one opposing action is required" }
        require(witnesses.isNotEmpty()) { "at least one witness agent is required" }
        require(maxChallenges in 1..64) { "maxChallenges must be between 1 and 64" }

        val original = record.fields.toSortedMap()
        val originalDigest = digestFields(original)
        val entries = mutableListOf<WitnessRunEntry>()
        val selected = actions.take(maxChallenges)
        selected.forEachIndexed { index, action ->
            val challenged = challengeCopy(original, action, index)
            val challenge = WitnessChallenge(
                challengeId = "${record.recordId}-challenge-${index + 1}",
                action = action,
                challengedFields = challenged.toMap(),
                syntheticNoise = action == WitnessNoiseAction.INJECT_SYNTHETIC_NOISE
            )
            witnesses.forEach { witness ->
                val assessment = witness.assess(originalDigest, challenge)
                entries += WitnessRunEntry(
                    challengeId = challenge.challengeId,
                    action = action,
                    assessment = assessment,
                    sourceRecordUnchanged = digestFields(record.fields) == originalDigest
                )
            }
        }
        val unchanged = digestFields(record.fields) == originalDigest
        val scored = entries.count { it.assessment.detectedAlteration && it.sourceRecordUnchanged }
        val strength = if (entries.isEmpty()) 0 else scored * 100 / entries.size
        val auditCanonical = buildString {
            append(record.recordId).append('\n')
            append(record.sourceRef).append('\n')
            append(originalDigest).append('\n')
            append(record.previousRecordHash.orEmpty()).append('\n')
            entries.forEach {
                append(it.challengeId).append('|').append(it.action.name).append('|')
                append(it.assessment.witnessId).append('|')
                append(it.assessment.detectedAlteration).append('|')
                append(it.assessment.observedDigest).append('|')
                append(it.sourceRecordUnchanged).append('\n')
            }
            append("source-unchanged=").append(unchanged)
        }
        return WitnessRunResult(
            recordId = record.recordId,
            sourceDigest = originalDigest,
            previousRecordHash = record.previousRecordHash,
            entries = entries.toList(),
            witnessStrengthPercent = strength,
            auditRecordHash = sha256(auditCanonical)
        )
    }

    /** Explicitly submits a bounded local run to a host-provided executor. */
    fun executeAsync(
        executor: Executor,
        record: WitnessRecord,
        actions: List<WitnessNoiseAction>,
        witnesses: List<WitnessAgent>,
        maxChallenges: Int = 16
    ): WitnessRunHandle {
        val cancelled = AtomicBoolean(false)
        val task = FutureTask {
            if (cancelled.get() || Thread.currentThread().isInterrupted) {
                throw InterruptedException("witness run cancelled before execution")
            }
            run(record, actions, witnesses, maxChallenges)
        }
        val handle = WitnessRunHandle(cancelled, task)
        executor.execute(task)
        return handle
    }

    internal fun digestFields(fields: Map<String, String>): String {
        val canonical = buildString {
            fields.toSortedMap().forEach { (key, value) ->
                append(key.length).append(':').append(key)
                append(value.length).append(':').append(value)
            }
        }
        return sha256(canonical)
    }

    private fun challengeCopy(
        source: Map<String, String>,
        action: WitnessNoiseAction,
        index: Int
    ): Map<String, String> {
        val copy = source.toMutableMap()
        when (action) {
            WitnessNoiseAction.ALTER_COPY_VALUE -> {
                val key = copy.keys.sorted().firstOrNull()
                if (key != null) copy[key] = copy.getValue(key) + "#opposed-$index"
                else copy["synthetic"] = "opposed-$index"
            }
            WitnessNoiseAction.DROP_COPY_FIELD -> copy.keys.sorted().firstOrNull()?.let { copy.remove(it) }
            WitnessNoiseAction.INJECT_SYNTHETIC_NOISE -> copy["__eria_synthetic_noise_$index"] = "noise-only-test-data"
            WitnessNoiseAction.REORDER_COPY_FIELDS -> return copy.entries.sortedByDescending { it.key }
                .associate { it.key to it.value }
        }
        return copy.toMap()
    }

    private fun sha256(value: String): String =
        MessageDigest.getInstance("SHA-256")
            .digest(value.toByteArray(Charsets.UTF_8))
            .joinToString("") { "%02x".format(it) }
}
