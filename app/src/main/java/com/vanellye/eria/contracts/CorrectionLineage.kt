package com.vanellye.eria.contracts

enum class CorrectionChangeKind { ADD, REMOVE, REPLACE, CONSTRAIN }

/** Direction is explicit: reverse creates a new tier; it never erases the forward tier. */
enum class CorrectionDirection { FORWARD, REVERSE }

data class CorrectionTierLine(
    val correctionId: String,
    val originalSourceTierRef: String,
    val originalSourceTierCommit: String,
    val futureMarkerAnchorCommit: String,
    val sourceContentSha256: String,
    val sourceCorrectionId: String?,
    val correctionPoint: String,
    val changeKind: CorrectionChangeKind,
    val direction: CorrectionDirection,
    val fromSha256: String,
    val toSha256: String,
    val operation: String,
    val operationVersion: String,
    val lineageCorrectionIds: List<String>,
    val resultingCommitSha: String? = null
) {
    init {
        require(correctionId.isNotBlank())
        require(originalSourceTierRef.isNotBlank())
        require(originalSourceTierCommit == ORIGINAL_SOURCE_TIER_COMMIT) {
            "Correction lineage must retain the immutable @11 source commit"
        }
        require(futureMarkerAnchorCommit == FUTURE_MARKER_ANCHOR_COMMIT) {
            "Future markers must retain the designated 7129618 anchor"
        }
        require(sourceContentSha256.matches(SHA256_PATTERN))
        require(fromSha256.matches(SHA256_PATTERN))
        require(toSha256.matches(SHA256_PATTERN))
        require(correctionPoint.isNotBlank())
        require(operation.isNotBlank())
        require(operationVersion.isNotBlank())
        require(lineageCorrectionIds.distinct().size == lineageCorrectionIds.size)
        require(sourceCorrectionId == null || lineageCorrectionIds.lastOrNull() == sourceCorrectionId) {
            "The direct source correction must be the final tier in the lineage path"
        }
        require(resultingCommitSha == null || resultingCommitSha.matches(COMMIT_SHA_PATTERN))
    }

    companion object {
        const val ORIGINAL_SOURCE_TIER_REF = "archive/justly-11-merge"
        const val ORIGINAL_SOURCE_TIER_COMMIT =
            "b60fac42ba0573c251cf7f7fe139bfa0f9c078f8"
        const val FUTURE_MARKER_ANCHOR_REF = "main-at-pr-39-base"
        const val FUTURE_MARKER_ANCHOR_COMMIT =
            "712961866e615ff4db9e90cd40bece78a45afe39"

        private val SHA256_PATTERN = Regex("^[0-9a-f]{64}$")
        private val COMMIT_SHA_PATTERN = Regex("^[0-9a-f]{40}$")
    }
}
