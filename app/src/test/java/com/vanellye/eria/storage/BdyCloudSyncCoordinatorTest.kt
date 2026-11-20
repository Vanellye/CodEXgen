package com.vanellye.eria.storage

import org.junit.Assert.*
import org.junit.Test

class BdyCloudSyncCoordinatorTest {
    private class Local(private val records: List<BdyCloudRecord>) : BdyLocalRecordStore {
        val marked = mutableListOf<String>()
        override fun pendingRecords() = records
        override fun markSynchronized(recordId: String, remoteVersion: String) {
            marked += recordId
        }
    }

    private class Cloud : BdyCloudObjectStore {
        val writes = mutableListOf<String>()
        override fun putIfAbsent(record: BdyCloudRecord): RemoteRecordReceipt {
            writes += record.recordId
            return RemoteRecordReceipt(record.recordId, record.sha256, "v1")
        }
    }

    private fun record() = BdyCloudRecord.create(
        recordId = "source-1",
        kind = BdyRecordKind.SOURCE,
        payload = "origin".toByteArray(),
        methodVersion = "bđyt/0.1",
        createdAtEpochMillis = 1L,
    )

    @Test fun uploadsAreDisabledWithoutGrant() {
        val local = Local(listOf(record()))
        val cloud = Cloud()
        val result = BdyCloudSyncCoordinator(local, cloud).uploadPending()
        assertEquals(BdySyncStatus.UPLOADS_DISABLED, result.status)
        assertTrue(cloud.writes.isEmpty())
        assertTrue(local.marked.isEmpty())
    }

    @Test fun explicitScopedGrantAllowsOnlySelectedKind() {
        val local = Local(listOf(record()))
        val cloud = Cloud()
        val grant = BdyUploadGrant.fromExplicitConsent(
            approved = true,
            allowedKinds = setOf(BdyRecordKind.SOURCE),
            expiresAtEpochMillis = 500L,
            consentReference = "consent-test-1",
        )
        val result = BdyCloudSyncCoordinator(local, cloud, grant) { 100L }.uploadPending()
        assertEquals(BdySyncStatus.UPLOADED, result.status)
        assertEquals(listOf("source-1"), cloud.writes)
        assertEquals(listOf("source-1"), local.marked)
    }

    @Test fun expiredGrantBlocksUpload() {
        val local = Local(listOf(record()))
        val cloud = Cloud()
        val grant = BdyUploadGrant.fromExplicitConsent(
            approved = true,
            allowedKinds = setOf(BdyRecordKind.SOURCE),
            expiresAtEpochMillis = 99L,
            consentReference = "consent-test-2",
        )
        val result = BdyCloudSyncCoordinator(local, cloud, grant) { 100L }.uploadPending()
        assertEquals(BdySyncStatus.BLOCKED_INVALID_RECORD, result.status)
        assertTrue(cloud.writes.isEmpty())
    }

    @Test fun declinedConsentCannotCreateGrant() {
        assertNull(
            BdyUploadGrant.fromExplicitConsent(
                approved = false,
                allowedKinds = BdyRecordKind.values().toSet(),
                expiresAtEpochMillis = 500L,
                consentReference = "declined",
            )
        )
    }
}
