package com.vanellye.eria.contracts

import java.io.File
import java.io.FileOutputStream
import java.nio.charset.StandardCharsets
import java.util.Base64

/** Append-only persistence boundary for correction tiers. */
interface CorrectionLineageJournal {
    fun append(tier: CorrectionTierLine)
    fun readAll(): List<CorrectionTierLine>
}

/** Process-local journal for callers that have not supplied durable storage. */
class InMemoryCorrectionLineageJournal : CorrectionLineageJournal {
    private val entries = mutableListOf<CorrectionTierLine>()

    @Synchronized
    override fun append(tier: CorrectionTierLine) {
        require(entries.none { it.correctionId == tier.correctionId }) {
            "Duplicate correction tier ID"
        }
        entries.add(tier)
    }

    @Synchronized
    override fun readAll(): List<CorrectionTierLine> = entries.toList()
}

/**
 * Durable append-only journal backed by a private application file.
 * Versioned tab-separated records use URL-safe Base64 fields; "~" represents empty.
 */
class FileCorrectionLineageJournal(private val file: File) : CorrectionLineageJournal {
    @Synchronized
    override fun append(tier: CorrectionTierLine) {
        require(readAll().none { it.correctionId == tier.correctionId }) {
            "Duplicate correction tier ID"
        }
        file.parentFile?.mkdirs()
        FileOutputStream(file, true).use { output ->
            output.write((encode(tier) + "\n").toByteArray(StandardCharsets.UTF_8))
            output.fd.sync()
        }
    }

    @Synchronized
    override fun readAll(): List<CorrectionTierLine> {
        if (!file.exists()) return emptyList()
        return file.readLines(StandardCharsets.UTF_8)
            .filter { it.isNotBlank() }
            .map(::decode)
    }

    private fun encode(tier: CorrectionTierLine): String {
        val fields = listOf(
            "v1",
            tier.correctionId,
            tier.originalSourceTierRef,
            tier.originalSourceTierCommit,
            tier.sourceContentSha256,
            tier.sourceCorrectionId.orEmpty(),
            tier.correctionPoint,
            tier.changeKind.name,
            tier.fromSha256,
            tier.toSha256,
            tier.operation,
            tier.operationVersion,
            tier.lineageCorrectionIds.joinToString(","),
            tier.resultingCommitSha.orEmpty()
        )
        return fields.joinToString("\t") { encodeField(it) }
    }

    private fun decode(line: String): CorrectionTierLine {
        val fields = line.split('\t').map(::decodeField)
        require(fields.size == 14 && fields[0] == "v1") {
            "Unsupported or malformed correction journal record"
        }
        return CorrectionTierLine(
            correctionId = fields[1],
            originalSourceTierRef = fields[2],
            originalSourceTierCommit = fields[3],
            sourceContentSha256 = fields[4],
            sourceCorrectionId = fields[5].ifEmpty { null },
            correctionPoint = fields[6],
            changeKind = CorrectionChangeKind.valueOf(fields[7]),
            fromSha256 = fields[8],
            toSha256 = fields[9],
            operation = fields[10],
            operationVersion = fields[11],
            lineageCorrectionIds = fields[12].split(',').filter { it.isNotEmpty() },
            resultingCommitSha = fields[13].ifEmpty { null }
        )
    }

    private fun encodeField(value: String): String {
        if (value.isEmpty()) return "~"
        return Base64.getUrlEncoder().withoutPadding()
            .encodeToString(value.toByteArray(StandardCharsets.UTF_8))
    }

    private fun decodeField(value: String): String {
        if (value == "~") return ""
        return String(Base64.getUrlDecoder().decode(value), StandardCharsets.UTF_8)
    }
}
