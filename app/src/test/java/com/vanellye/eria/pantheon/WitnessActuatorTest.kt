package com.vanellye.eria.pantheon

import org.junit.Assert.*
import org.junit.Test
import java.util.concurrent.Executor

class WitnessActuatorTest {
    @Test fun opposingNoiseChallengesNeverMutateTheSourceRecord() {
        val record = WitnessRecord("record-1", "source://witness", mapOf("origin" to "known", "claim" to "evidence"))
        val before = record.fields.toMap()
        val result = WitnessActuator.run(
            record,
            listOf(
                WitnessNoiseAction.ALTER_COPY_VALUE,
                WitnessNoiseAction.DROP_COPY_FIELD,
                WitnessNoiseAction.INJECT_SYNTHETIC_NOISE,
                WitnessNoiseAction.REORDER_COPY_FIELDS
            ),
            listOf(DigestWitnessAgent())
        )
        assertEquals(before, record.fields)
        assertTrue(result.entries.all { it.sourceRecordUnchanged })
        assertEquals(4, result.entries.size)
        assertEquals(75, result.witnessStrengthPercent)
        assertEquals(64, result.sourceDigest.length)
        assertEquals(64, result.auditRecordHash.length)
    }

    @Test fun reorderedFieldsDoNotChangeCanonicalDigest() {
        val first = mapOf("a" to "1", "b" to "2")
        val second = linkedMapOf("b" to "2", "a" to "1")
        assertEquals(WitnessActuator.digestFields(first), WitnessActuator.digestFields(second))
    }

    @Test fun auditRecordLinksPriorHashWithoutReplacingOrigin() {
        val parentHash = "a".repeat(64)
        val record = WitnessRecord("record-2", "source://immutable", mapOf("k" to "v"), parentHash)
        val result = WitnessActuator.run(
            record, listOf(WitnessNoiseAction.ALTER_COPY_VALUE), listOf(DigestWitnessAgent())
        )
        assertEquals("source://immutable", record.sourceRef)
        assertEquals(parentHash, result.previousRecordHash)
        assertEquals(100, result.witnessStrengthPercent)
    }

    @Test fun asyncExecutionRequiresAnExplicitExecutorAndRemainsLocal() {
        var submitted = false
        val executor = Executor { command -> submitted = true; command.run() }
        val handle = WitnessActuator.executeAsync(
            executor,
            WitnessRecord("record-async", "source://local", mapOf("x" to "y")),
            listOf(WitnessNoiseAction.ALTER_COPY_VALUE),
            listOf(DigestWitnessAgent())
        )
        assertTrue(submitted)
        assertEquals(100, handle.result().witnessStrengthPercent)
        assertFalse(handle.isCancelled())
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsUnboundedChallengeCount() {
        WitnessActuator.run(
            WitnessRecord("record", "source://local", mapOf("x" to "y")),
            listOf(WitnessNoiseAction.ALTER_COPY_VALUE),
            listOf(DigestWitnessAgent()),
            65
        )
    }
}
