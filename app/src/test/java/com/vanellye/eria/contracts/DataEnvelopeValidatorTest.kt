package com.vanellye.eria.contracts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class DataEnvelopeValidatorTest {
    private fun validRecord() = DataEnvelope(
        recordId = "sensor.sample-001",
        source = "device.sensor-a",
        observedAt = "2026-11-09T19:00:00-06:00",
        payload = mapOf("reading" to 0, "enabled" to false, "note" to null, "values" to listOf(1, 2.5)),
        units = mapOf("reading" to "milli-unit"),
        quality = DataQuality.VALID,
        monotonicTime = MonotonicTime(123456L, "device.boot-7"),
        provenance = DataProvenance(sourceDigest = "a".repeat(64), signatureStatus = "unverified")
    )

    @Test fun acceptsValidRecordAndPreservesZeroFalseNull() {
        val record = validRecord()
        assertTrue(DataEnvelopeValidator.validate(record).isEmpty())
        assertEquals(0, record.payload["reading"])
        assertEquals(false, record.payload["enabled"])
        assertEquals(null, record.payload["note"])
    }

    @Test fun requiresTimezoneInTimestamp() {
        val errors = DataEnvelopeValidator.validate(validRecord().copy(observedAt = "2026-11-09T19:00:00"))
        assertTrue(errors.any { it.contains("timezone") })
    }

    @Test fun rejectsUnknownSchemaAndMalformedDigest() {
        val bad = validRecord().copy(
            schemaVersion = 2,
            provenance = DataProvenance(sourceDigest = "not-a-digest")
        )
        val errors = DataEnvelopeValidator.validate(bad)
        assertTrue(errors.any { it.contains("schemaVersion") })
        assertTrue(errors.any { it.contains("sourceDigest") })
    }

    @Test fun rejectsNonFinitePayloadValues() {
        val bad = validRecord().copy(payload = mapOf("reading" to Double.NaN))
        assertTrue(DataEnvelopeValidator.validate(bad).any { it.contains("non-finite") })
    }

    @Test fun requiresExplicitScopedAuthorization() {
        val unauthorized = validRecord().copy(
            authorization = DataAuthorization(AuthorizationStatus.NOT_AUTHORIZED, listOf("export"))
        )
        assertTrue(DataEnvelopeValidator.validate(unauthorized).any { it.contains("non-authorized") })

        val authorized = validRecord().copy(
            authorization = DataAuthorization(
                AuthorizationStatus.AUTHORIZED, listOf("export.bundle"), "approval-123"
            )
        )
        assertTrue(DataEnvelopeValidator.validate(authorized).isEmpty())
    }

    @Test fun rejectsNegativeMonotonicTimeAndInvalidQualityIsNotRepresentable() {
        val bad = validRecord().copy(monotonicTime = MonotonicTime(-1L, "device.boot-7"))
        assertTrue(DataEnvelopeValidator.validate(bad).any { it.contains("non-negative") })
    }
}
