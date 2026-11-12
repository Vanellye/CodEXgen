package com.vanellye.eria.source

import com.vanellye.eria.contracts.AuthorizationStatus
import com.vanellye.eria.contracts.DataAuthorization
import com.vanellye.eria.contracts.DataEnvelope
import com.vanellye.eria.contracts.DataEnvelopeValidator
import com.vanellye.eria.contracts.DataProvenance
import com.vanellye.eria.contracts.DataQuality
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.time.Clock
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.util.UUID

/**
 * Explicit, in-memory intake for source-code records.
 *
 * This adapter does not read paths, access Git/network services, persist data,
 * execute imported code, or modify the supplied source. The caller supplies
 * the source text and a separately obtained, narrowly scoped authorization.
 */
data class SourceCodeInput(
    val repository: String,
    val sourceRef: String,
    val commitSha: String,
    val relativePath: String,
    val language: String,
    val content: String
)

data class CollectedSourceCode(
    val envelope: DataEnvelope,
    /** Exact caller-supplied source text; retained in memory only by this result. */
    val content: String
)

class SourceCollectionRejected(message: String) : IllegalArgumentException(message)

class SourceCodeCollector(
    private val clock: Clock = Clock.systemUTC(),
    private val maxBytes: Int = DEFAULT_MAX_BYTES
) {
    init {
        require(maxBytes in 1..DEFAULT_MAX_BYTES) {
            "maxBytes must be between 1 and $DEFAULT_MAX_BYTES"
        }
    }

    fun collect(
        input: SourceCodeInput,
        authorization: DataAuthorization
    ): CollectedSourceCode {
        requireText(input.repository, "repository")
        requireText(input.sourceRef, "sourceRef")
        requireText(input.language, "language")
        validateRelativePath(input.relativePath)
        if (!FULL_COMMIT.matches(input.commitSha)) {
            throw SourceCollectionRejected("commitSha must be a full 40- or 64-character hexadecimal object id")
        }

        if (authorization.status != AuthorizationStatus.AUTHORIZED ||
            "source.collect" !in authorization.scope ||
            authorization.approvalRef.isNullOrBlank()
        ) {
            throw SourceCollectionRejected("source collection requires explicit source.collect authorization")
        }

        val bytes = input.content.toByteArray(StandardCharsets.UTF_8)
        if (bytes.isEmpty()) throw SourceCollectionRejected("empty source content is not collectable")
        if (bytes.size > maxBytes) {
            throw SourceCollectionRejected("source content exceeds the $maxBytes-byte collection limit")
        }

        val digest = sha256(bytes)
        val observedAt = OFFSET_TIMESTAMP.format(clock.instant().atZone(ZoneOffset.UTC))
        val envelope = DataEnvelope(
            recordId = "source-code:${UUID.randomUUID()}",
            source = "source-code.collection",
            observedAt = observedAt,
            payload = mapOf(
                "repository" to input.repository,
                "sourceRef" to input.sourceRef,
                "commitSha" to input.commitSha.lowercase(),
                "relativePath" to input.relativePath,
                "language" to input.language,
                "content" to input.content,
                "byteCount" to bytes.size
            ),
            units = mapOf("byteCount" to "byte"),
            quality = DataQuality.VALID,
            provenance = DataProvenance(
                sourceRef = input.sourceRef,
                sourceCommit = input.commitSha.lowercase(),
                sourceDigest = digest,
                signatureStatus = "not_present"
            ),
            authorization = authorization,
            validation = mapOf(
                "content_digest" to "sha256",
                "source_execution" to "not_performed",
                "source_mutation" to "not_performed",
                "network_access" to "not_performed",
                "persistence" to "not_performed"
            ),
            retention = mapOf(
                "handling" to "in_memory_result_only",
                "sensitivity" to "source_code",
                "durable_storage" to "not_configured"
            )
        )

        val errors = DataEnvelopeValidator.validate(envelope)
        if (errors.isNotEmpty()) {
            throw SourceCollectionRejected("collected envelope failed validation: ${errors.joinToString("; ")}")
        }
        return CollectedSourceCode(envelope = envelope, content = input.content)
    }

    private fun requireText(value: String, field: String) {
        if (value.isBlank()) throw SourceCollectionRejected("$field must not be blank")
    }

    private fun validateRelativePath(path: String) {
        if (path.isBlank() || path.startsWith("/") || path.startsWith("\\") ||
            path.split('/', '\\').any { it == ".." } ||
            Regex("^[A-Za-z]:").containsMatchIn(path)
        ) {
            throw SourceCollectionRejected("relativePath must be a safe repository-relative path")
        }
    }

    private fun sha256(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }

    companion object {
        const val DEFAULT_MAX_BYTES = 1_048_576
        private val FULL_COMMIT = Regex("^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")
        private val OFFSET_TIMESTAMP = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ssXXX")
    }
}
