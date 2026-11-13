package com.vanellye.eria.contracts

import java.io.File
import java.io.FileOutputStream
import java.net.URLDecoder
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

interface CorrectionLineageJournal {
    fun append(tier: CorrectionTierLine)
    fun readAll(): List<CorrectionTierLine>
}

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
 * Durable append-only journal. V2 records include the future marker anchor and direction.
 * V1 records remain readable but keep a null marker anchor: their provenance is not
 * retroactively rewritten or falsely attributed to the later 7129618 marker.
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
            "v2",
            tier.correctionId,
            tier.originalSourceTierRef,
            tier.originalSourceTierCommit,
            tier.futureMarkerAnchorCommit.orEmpty(),
            tier.sourceContentSha256,
            tier.sourceCorrectionId.orEmpty(),
            tier.correctionPoint,
            tier.changeKind.name,
            tier.direction.name,
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
        return when (fields.firstOrNull()) {
            "v1" -> {
                require(fields.size == 14) { "Malformed v1 correction journal record" }
                CorrectionTierLine(
                    correctionId = fields[1],
                    originalSourceTierRef = fields[2],
                    originalSourceTierCommit = fields[3],
                    futureMarkerAnchorCommit = null,
                    sourceContentSha256 = fields[4],
                    sourceCorrectionId = fields[5].ifEmpty { null },
                    correctionPoint = fields[6],
                    changeKind = CorrectionChangeKind.valueOf(fields[7]),
                    direction = CorrectionDirection.FORWARD,
                    fromSha256 = fields[8],
                    toSha256 = fields[9],
                    operation = fields[10],
                    operationVersion = fields[11],
                    lineageCorrectionIds = fields[12].split(',').filter { it.isNotEmpty() },
                    resultingCommitSha = fields[13].ifEmpty { null }
                )
            }
            "v2" -> {
                require(fields.size == 16) { "Malformed v2 correction journal record" }
                CorrectionTierLine(
                    correctionId = fields[1],
                    originalSourceTierRef = fields[2],
                    originalSourceTierCommit = fields[3],
                    futureMarkerAnchorCommit = fields[4].ifEmpty { null },
                    sourceContentSha256 = fields[5],
                    sourceCorrectionId = fields[6].ifEmpty { null },
                    correctionPoint = fields[7],
                    changeKind = CorrectionChangeKind.valueOf(fields[8]),
                    direction = CorrectionDirection.valueOf(fields[9]),
                    fromSha256 = fields[10],
                    toSha256 = fields[11],
                    operation = fields[12],
                    operationVersion = fields[13],
                    lineageCorrectionIds = fields[14].split(',').filter { it.isNotEmpty() },
                    resultingCommitSha = fields[15].ifEmpty { null }
                )
            }
            else -> error("Unsupported correction journal record version")
        }
    }

    private fun encodeField(value: String): String =
        if (value.isEmpty()) "~" else URLEncoder.encode(value, "UTF-8")

    private fun decodeField(value: String): String =
        if (value == "~") "" else URLDecoder.decode(value, "UTF-8")
}
