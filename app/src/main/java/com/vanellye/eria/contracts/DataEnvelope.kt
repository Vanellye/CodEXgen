package com.vanellye.eria.contracts

import java.text.ParsePosition
import java.text.SimpleDateFormat
import java.util.Locale
import java.util.TimeZone

enum class DataQuality {
    VALID, STALE, OUT_OF_RANGE, UNCALIBRATED, SENSOR_FAULT, UNKNOWN
}

enum class AuthorizationStatus { NOT_AUTHORIZED, AUTHORIZED, DECLINED }

data class MonotonicTime(val value: Long, val clockDomain: String)

data class DataProvenance(
    val sourceRef: String? = null,
    val sourceCommit: String? = null,
    val sourceDigest: String? = null,
    val signer: String? = null,
    val signatureStatus: String = "not_present"
)

data class DataTransformation(
    val operation: String,
    val version: String,
    val parametersDigest: String? = null,
    val outputDigest: String? = null
)

data class DataAuthorization(
    val status: AuthorizationStatus = AuthorizationStatus.NOT_AUTHORIZED,
    val scope: List<String> = emptyList(),
    val approvalRef: String? = null
)

/**
 * Platform-native representation of the TRUE NORTH data envelope.
 *
 * Validation is deliberately separate from authorization: a valid record does
 * not grant permission to execute an operation.
 */
data class DataEnvelope(
    val recordId: String,
    val schemaVersion: Int = 1,
    val source: String,
    val observedAt: String,
    val payload: Map<String, Any?>,
    val units: Map<String, String>,
    val quality: DataQuality,
    val provenance: DataProvenance = DataProvenance(),
    val transformations: List<DataTransformation> = emptyList(),
    val authorization: DataAuthorization = DataAuthorization(),
    val validation: Map<String, String> = emptyMap(),
    val retention: Map<String, String> = emptyMap(),
    val monotonicTime: MonotonicTime? = null
)

object DataEnvelopeValidator {
    private val identifier = Regex("^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
    private val sha256 = Regex("^[0-9a-f]{64}$")
    private val signatureStates = setOf("not_present", "valid", "invalid", "unverified")

    /** Returns stable, human-readable validation errors; an empty list means valid. */
    fun validate(record: DataEnvelope): List<String> {
        val errors = mutableListOf<String>()
        requireIdentifier(record.recordId, "recordId", errors)
        requireIdentifier(record.source, "source", errors)
        if (record.schemaVersion != 1) errors += "schemaVersion must equal 1"
        if (!isOffsetTimestamp(record.observedAt)) {
            errors += "observedAt must be a valid ISO-8601 timestamp with timezone"
        }
        record.monotonicTime?.let {
            if (it.value < 0L) errors += "monotonicTime.value must be non-negative"
            requireIdentifier(it.clockDomain, "monotonicTime.clockDomain", errors)
        }
        record.units.forEach { (key, value) ->
            if (key.isBlank() || value.isBlank()) errors += "units keys and values must be non-blank"
        }
        record.payload.forEach { (key, value) ->
            if (key.isBlank()) errors += "payload keys must be non-blank"
            validateJsonValue(value, "payload.$key", 0, errors)
        }

        record.provenance.sourceDigest?.let {
            if (!sha256.matches(it)) errors += "provenance.sourceDigest must be lowercase SHA-256"
        }
        if (record.provenance.signatureStatus !in signatureStates) {
            errors += "provenance.signatureStatus is not recognized"
        }
        record.transformations.forEachIndexed { index, item ->
            requireIdentifier(item.operation, "transformations[$index].operation", errors)
            requireIdentifier(item.version, "transformations[$index].version", errors)
            item.parametersDigest?.let {
                if (!sha256.matches(it)) errors += "transformations[$index].parametersDigest is invalid"
            }
            item.outputDigest?.let {
                if (!sha256.matches(it)) errors += "transformations[$index].outputDigest is invalid"
            }
        }

        when (record.authorization.status) {
            AuthorizationStatus.AUTHORIZED -> {
                if (record.authorization.scope.isEmpty()) errors += "authorized records require a non-empty scope"
                record.authorization.scope.forEachIndexed { index, scope ->
                    requireIdentifier(scope, "authorization.scope[$index]", errors)
                }
                requireIdentifier(record.authorization.approvalRef, "authorization.approvalRef", errors)
            }
            AuthorizationStatus.NOT_AUTHORIZED, AuthorizationStatus.DECLINED -> {
                if (record.authorization.approvalRef != null) {
                    errors += "non-authorized records must not contain approvalRef"
                }
                if (record.authorization.scope.isNotEmpty()) {
                    errors += "non-authorized records must not declare an approved scope"
                }
            }
        }
        return errors
    }

    private fun requireIdentifier(value: String?, field: String, errors: MutableList<String>) {
        if (value == null || !identifier.matches(value)) errors += "$field must be a stable identifier"
    }

    private fun isOffsetTimestamp(value: String): Boolean {
        val format = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX", Locale.ROOT).apply {
            isLenient = false
            timeZone = TimeZone.getTimeZone("UTC")
        }
        val position = ParsePosition(0)
        val parsed = format.parse(value, position)
        return parsed != null && position.index == value.length
    }

    private fun validateJsonValue(
        value: Any?,
        path: String,
        depth: Int,
        errors: MutableList<String>
    ) {
        if (depth > 64) {
            errors += "$path exceeds maximum nesting depth"
            return
        }
        when (value) {
            null, is String, is Boolean, is Byte, is Short, is Int, is Long -> Unit
            is Float -> if (!value.isFinite()) errors += "$path contains a non-finite number"
            is Double -> if (!value.isFinite()) errors += "$path contains a non-finite number"
            is Number -> Unit
            is List<*> -> value.forEachIndexed { index, item ->
                validateJsonValue(item, "$path[$index]", depth + 1, errors)
            }
            is Map<*, *> -> value.forEach { (key, item) ->
                if (key !is String) {
                    errors += "$path object keys must be strings"
                } else {
                    validateJsonValue(item, "$path.$key", depth + 1, errors)
                }
            }
            else -> errors += "$path contains unsupported type ${value::class.java.simpleName}"
        }
    }
}
