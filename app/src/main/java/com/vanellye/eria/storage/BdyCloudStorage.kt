package com.vanellye.eria.storage

import java.security.MessageDigest

/**
 * Provider-neutral bđyt cloud record envelope.
 *
 * Payload bytes are immutable by contract; callers must not mutate the array after
 * constructing this value. The SHA-256 and byte count are verified before transfer.
 */
enum class BdyRecordKind { SOURCE, DERIVED, EXECUTION_RECEIPT }

class BdyCloudRecord private constructor(
    val recordId: String,
    val kind: BdyRecordKind,
    private val content: ByteArray,
    val sha256: String,
    val parentRecordIds: List<String>,
    val methodVersion: String,
    val createdAtEpochMillis: Long,
) {
    val byteCount: Long get() = content.size.toLong()

    /** Return a defensive copy so providers cannot mutate the retained source bytes. */
    fun payloadCopy(): ByteArray = content.copyOf()

    fun verifyIntegrity(): Boolean =
        sha256.equals(sha256(content), ignoreCase = true)

    companion object {
        fun create(
            recordId: String,
            kind: BdyRecordKind,
            payload: ByteArray,
            parentRecordIds: List<String> = emptyList(),
            methodVersion: String,
            createdAtEpochMillis: Long,
        ) = BdyCloudRecord(
            recordId = recordId,
            kind = kind,
            content = payload.copyOf(),
            sha256 = sha256(payload),
            parentRecordIds = parentRecordIds.toList(),
            methodVersion = methodVersion,
            createdAtEpochMillis = createdAtEpochMillis,
        )

        private fun sha256(bytes: ByteArray): String =
            MessageDigest.getInstance("SHA-256").digest(bytes)
                .joinToString("") { "%02x".format(it.toInt() and 0xff) }
    }
}

data class RemoteRecordReceipt(
    val recordId: String,
    val sha256: String,
    val remoteVersion: String,
)

/** Local append-only source for records waiting to be synchronized. */
interface BdyLocalRecordStore {
    fun pendingRecords(): List<BdyCloudRecord>
    fun markSynchronized(recordId: String, remoteVersion: String)
}

/**
 * Implement this interface for a selected cloud provider.
 * No provider implementation or credentials are bundled in this change.
 */
interface BdyCloudObjectStore {
    /** Must be idempotent for an existing recordId with the same digest. */
    fun putIfAbsent(record: BdyCloudRecord): RemoteRecordReceipt
}

/**
 * A short-lived, user-approved capability. It is deliberately not persisted.
 * The app must create one only in response to an explicit upload confirmation UI.
 */
class BdyUploadGrant private constructor(
    internal val allowedKinds: Set<BdyRecordKind>,
    internal val expiresAtEpochMillis: Long,
    val consentReference: String,
) {
    companion object {
        fun fromExplicitConsent(
            approved: Boolean,
            allowedKinds: Set<BdyRecordKind>,
            expiresAtEpochMillis: Long,
            consentReference: String,
        ): BdyUploadGrant? {
            if (!approved || allowedKinds.isEmpty() || consentReference.isBlank()) return null
            return BdyUploadGrant(allowedKinds.toSet(), expiresAtEpochMillis, consentReference)
        }
    }

    internal fun permits(record: BdyCloudRecord, nowEpochMillis: Long): Boolean =
        nowEpochMillis < expiresAtEpochMillis && record.kind in allowedKinds
}

enum class BdySyncStatus { UPLOADS_DISABLED, NOTHING_TO_SYNC, UPLOADED, BLOCKED_INVALID_RECORD }

data class BdySyncReport(
    val status: BdySyncStatus,
    val uploadedRecordIds: List<String> = emptyList(),
    val detail: String,
)

/**
 * Uploads remain disabled unless a live, scoped BdyUploadGrant is explicitly supplied.
 * This class does not schedule itself or initiate background work.
 */
class BdyCloudSyncCoordinator(
    private val localStore: BdyLocalRecordStore,
    private val cloudStore: BdyCloudObjectStore,
    private val uploadGrant: BdyUploadGrant? = null,
    private val clock: () -> Long = System::currentTimeMillis,
) {
    fun uploadPending(): BdySyncReport {
        val grant = uploadGrant
            ?: return BdySyncReport(BdySyncStatus.UPLOADS_DISABLED, detail = "No explicit upload grant")
        val pending = localStore.pendingRecords()
        if (pending.isEmpty()) {
            return BdySyncReport(BdySyncStatus.NOTHING_TO_SYNC, detail = "No pending records")
        }

        val uploaded = mutableListOf<String>()
        for (record in pending) {
            if (!record.verifyIntegrity() || !grant.permits(record, clock())) {
                return BdySyncReport(
                    status = BdySyncStatus.BLOCKED_INVALID_RECORD,
                    uploadedRecordIds = uploaded,
                    detail = "Integrity, scope, or grant-expiry check failed for ${record.recordId}",
                )
            }
            val receipt = cloudStore.putIfAbsent(record)
            require(receipt.recordId == record.recordId && receipt.sha256.equals(record.sha256, true)) {
                "Cloud provider returned a mismatched receipt"
            }
            localStore.markSynchronized(record.recordId, receipt.remoteVersion)
            uploaded += record.recordId
        }
        return BdySyncReport(BdySyncStatus.UPLOADED, uploaded, "Explicitly authorized records synchronized")
    }
}
