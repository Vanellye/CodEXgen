package com.vanellye.eria.source

import com.vanellye.eria.contracts.AuthorizationStatus
import com.vanellye.eria.contracts.DataAuthorization
import com.vanellye.eria.contracts.DataEnvelope
import com.vanellye.eria.contracts.DataEnvelopeValidator
import com.vanellye.eria.contracts.DataProvenance
import com.vanellye.eria.contracts.DataQuality
import java.io.BufferedInputStream
import java.io.BufferedOutputStream
import java.io.DataInputStream
import java.io.DataOutputStream
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.nio.charset.StandardCharsets
import java.security.MessageDigest

/**
 * Atomic, app-private local persistence for collected source records.
 *
 * The caller must supply an app-private directory (normally Context.filesDir).
 * This class performs no network access, export, source execution, or repository
 * mutation. Stored bytes are not encrypted by this implementation.
 */
data class StoredSourceCode(
    val envelope: DataEnvelope,
    val content: String
)

class SourceIntegrityRejected(message: String) : IllegalArgumentException(message)

class LocalSourceCodeStore(private val root: File) {
    fun store(
        collected: CollectedSourceCode,
        authorization: DataAuthorization
    ): StoredSourceCode {
        requireStorageApproval(collected, authorization)
        val bytes = collected.content.toByteArray(StandardCharsets.UTF_8)
        verifyDigest(collected.envelope, bytes)
        validateEnvelope(collected.envelope)

        if (!root.exists() && !root.mkdirs()) {
            throw SourceIntegrityRejected("unable to create app-private storage directory")
        }
        if (!root.isDirectory) throw SourceIntegrityRejected("storage root is not a directory")
        val canonicalRoot = root.canonicalFile
        val id = collected.envelope.recordId.removePrefix("source-code:")
        if (!id.matches(Regex("^[0-9a-fA-F-]{36}$"))) {
            throw SourceIntegrityRejected("recordId is not a supported source-code record identifier")
        }
        val target = File(canonicalRoot, "$id.eria-source")
        val temp = File.createTempFile("eria-source-", ".tmp", canonicalRoot)
        try {
            FileOutputStream(temp).use { file ->
                DataOutputStream(BufferedOutputStream(file)).use { out ->
                    writeRecord(out, collected, authorization)
                    out.flush()
                    file.fd.sync()
                }
            }
            if (target.exists()) throw SourceIntegrityRejected("record already exists; overwrite is prohibited")
            if (!temp.renameTo(target)) throw SourceIntegrityRejected("atomic local commit failed")
            val verified = load(collected.envelope.recordId, authorization)
            if (verified.content != collected.content ||
                verified.envelope.provenance.sourceDigest != collected.envelope.provenance.sourceDigest
            ) {
                target.delete()
                throw SourceIntegrityRejected("read-back verification failed; stored record was rolled back")
            }
            return verified
        } finally {
            if (temp.exists()) temp.delete()
        }
    }

    fun load(recordId: String, authorization: DataAuthorization): StoredSourceCode {
        if (authorization.status != AuthorizationStatus.AUTHORIZED ||
            "source.read" !in authorization.scope ||
            authorization.approvalRef.isNullOrBlank()
        ) {
            throw SourceIntegrityRejected("local read requires explicit source.read authorization")
        }
        val id = recordId.removePrefix("source-code:")
        if (!id.matches(Regex("^[0-9a-fA-F-]{36}$"))) {
            throw SourceIntegrityRejected("invalid source-code record identifier")
        }
        val file = File(root.canonicalFile, "$id.eria-source")
        if (!file.isFile || file.canonicalFile.parentFile != root.canonicalFile) {
            throw SourceIntegrityRejected("stored source record does not exist in the approved local store")
        }
        val stored = DataInputStream(BufferedInputStream(FileInputStream(file))).use { readRecord(it) }
        verifyDigest(stored.envelope, stored.content.toByteArray(StandardCharsets.UTF_8))
        validateEnvelope(stored.envelope)
        return stored
    }

    private fun requireStorageApproval(
        collected: CollectedSourceCode,
        authorization: DataAuthorization
    ) {
        if (authorization.status != AuthorizationStatus.AUTHORIZED ||
            !authorization.scope.containsAll(listOf("source.collect", "source.store")) ||
            authorization.approvalRef.isNullOrBlank() ||
            authorization.approvalRef != collected.envelope.authorization.approvalRef
        ) {
            throw SourceIntegrityRejected(
                "local storage requires matching approvalRef and source.collect + source.store scopes"
            )
        }
    }

    private fun writeRecord(
        out: DataOutputStream,
        collected: CollectedSourceCode,
        authorization: DataAuthorization
    ) {
        val e = collected.envelope
        out.writeInt(MAGIC)
        out.writeInt(FORMAT_VERSION)
        out.writeUTF(e.recordId)
        out.writeInt(e.schemaVersion)
        out.writeUTF(e.source)
        out.writeUTF(e.observedAt)
        out.writeUTF(e.payload["repository"] as String)
        out.writeUTF(e.payload["sourceRef"] as String)
        out.writeUTF(e.payload["commitSha"] as String)
        out.writeUTF(e.payload["relativePath"] as String)
        out.writeUTF(e.payload["language"] as String)
        out.writeInt(collected.content.toByteArray(StandardCharsets.UTF_8).size)
        out.write(collected.content.toByteArray(StandardCharsets.UTF_8))
        out.writeUTF(e.provenance.sourceDigest ?: "")
        out.writeUTF(authorization.approvalRef!!)
        out.writeInt(authorization.scope.size)
        authorization.scope.sorted().forEach(out::writeUTF)
    }

    private fun readRecord(input: DataInputStream): StoredSourceCode {
        if (input.readInt() != MAGIC || input.readInt() != FORMAT_VERSION) {
            throw SourceIntegrityRejected("unknown or corrupt local record format")
        }
        val recordId = input.readUTF()
        val schemaVersion = input.readInt()
        val source = input.readUTF()
        val observedAt = input.readUTF()
        val repository = input.readUTF()
        val sourceRef = input.readUTF()
        val commitSha = input.readUTF()
        val relativePath = input.readUTF()
        val language = input.readUTF()
        val length = input.readInt()
        if (length !in 1..MAX_SOURCE_BYTES) throw SourceIntegrityRejected("stored source length is invalid")
        val bytes = ByteArray(length)
        input.readFully(bytes)
        if (input.read() != -1) throw SourceIntegrityRejected("stored record contains unexpected trailing data")
        val digest = input.readUTF()
        val approvalRef = input.readUTF()
        val count = input.readInt()
        if (count !in 1..16) throw SourceIntegrityRejected("stored authorization scope is invalid")
        val scopes = (0 until count).map { input.readUTF() }
        val content = String(bytes, StandardCharsets.UTF_8)
        val authorization = DataAuthorization(AuthorizationStatus.AUTHORIZED, scopes, approvalRef)
        val envelope = DataEnvelope(
            recordId = recordId,
            schemaVersion = schemaVersion,
            source = source,
            observedAt = observedAt,
            payload = mapOf(
                "repository" to repository,
                "sourceRef" to sourceRef,
                "commitSha" to commitSha,
                "relativePath" to relativePath,
                "language" to language,
                "content" to content,
                "byteCount" to length
            ),
            units = mapOf("byteCount" to "byte"),
            quality = DataQuality.VALID,
            provenance = DataProvenance(
                sourceRef = sourceRef,
                sourceCommit = commitSha,
                sourceDigest = digest,
                signatureStatus = "not_present"
            ),
            authorization = authorization,
            validation = mapOf(
                "content_digest" to "sha256",
                "source_execution" to "not_performed",
                "source_mutation" to "not_performed",
                "network_access" to "not_performed",
                "persistence" to "local_app_private"
            ),
            retention = mapOf(
                "handling" to "local_app_private_storage",
                "sensitivity" to "source_code",
                "durable_storage" to "approved_local_only"
            )
        )
        return StoredSourceCode(envelope, content)
    }

    private fun verifyDigest(envelope: DataEnvelope, bytes: ByteArray) {
        val actual = MessageDigest.getInstance("SHA-256").digest(bytes)
            .joinToString("") { "%02x".format(it) }
        if (actual != envelope.provenance.sourceDigest) {
            throw SourceIntegrityRejected("source SHA-256 does not match provenance envelope")
        }
    }

    private fun validateEnvelope(envelope: DataEnvelope) {
        val errors = DataEnvelopeValidator.validate(envelope)
        if (errors.isNotEmpty()) {
            throw SourceIntegrityRejected("provenance envelope is invalid: ${errors.joinToString("; ")}")
        }
    }

    companion object {
        private const val MAGIC = 0x45524941
        private const val FORMAT_VERSION = 1
        private const val MAX_SOURCE_BYTES = 1_048_576
    }
}
