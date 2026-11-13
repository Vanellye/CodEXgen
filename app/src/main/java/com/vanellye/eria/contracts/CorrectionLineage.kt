package com.vanellye.eria.contracts

/**
 * Runtime correction-lineage contract.
 *
 * Every correction tier is anchored to the immutable @11 source commit. A new
 * correction points to the exact content hash and, when applicable, the prior
 * correction tier from which it was derived.
 */
enum class CorrectionChangeKind {
    ADD,
    REMOVE,
    REPLACE,
    CONSTRAIN
}

data class CorrectionTierLine(
    val correctionId: String,
    val originalSourceTierRef: String,
    val originalSourceTierCommit: String,
    val sourceContentSha256: String,
    val sourceCorrectionId: String?,
    val correctionPoint: String,
    val changeKind: CorrectionChangeKind,
    val fromSha256: String,
    val toSha256: String,
    val operation: String,
    val operationVersion: String,
    val lineageCorrectionIds: List<String>,
    /**
     * Null until the correction is committed to Git. Runtime code must not
     * fabricate a repository commit SHA.
     */
    val resultingCommitSha: String? = null
) {
    init {
        require(correctionId.isNotBlank())
        require(originalSourceTierRef.isNotBlank())
        require(originalSourceTierCommit == ORIGINAL_SOURCE_TIER_COMMIT) {
            "Correction lineage must retain the immutable @11 source commit"
        }
        require(sourceContentSha256.matches(SHA256_PATTERN))
        require(fromSha256.matches(SHA256_PATTERN))
        require(toSha256.matches(SHA256_PATTERN))
        require(correctionPoint.isNotBlank())
        require(operation.isNotBlank())
        require(operationVersion.isNotBlank())
        require(lineageCorrectionIds.distinct().size == lineageCorrectionIds.size) {
            "Correction lineage cannot contain duplicate tier IDs"
        }
        require(sourceCorrectionId == null || lineageCorrectionIds.lastOrNull() == sourceCorrectionId) {
            "The direct source correction must be the final tier in the lineage path"
        }
        require(resultingCommitSha == null || resultingCommitSha.matches(COMMIT_SHA_PATTERN)) {
            "A resulting Git commit must be a full hexadecimal SHA"
        }
    }

    companion object {
        const val ORIGINAL_SOURCE_TIER_REF = "archive/justly-11-merge"
        const val ORIGINAL_SOURCE_TIER_COMMIT =
            "b60fac42ba0573c251cf7f7fe139bfa0f9c078f8"

        private val SHA256_PATTERN = Regex("^[0-9a-f]{64}$")
        private val COMMIT_SHA_PATTERN = Regex("^[0-9a-f]{40}$")
    }
}
