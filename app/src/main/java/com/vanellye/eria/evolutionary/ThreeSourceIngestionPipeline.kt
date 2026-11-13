package com.vanellye.eria.evolutionary

import java.security.MessageDigest
import java.time.Instant
import java.util.Locale

enum class SequenceFormat { FASTA, FASTQ }
enum class IntakeOrigin { EXISTING_SEQUENCE, PUBLIC_REFERENCE, SYNTHETIC }
enum class IntakeState { ACCEPTED, REJECTED }
enum class SequenceEvidence { OBSERVED_INPUT, PUBLIC_REFERENCE, SYNTHETIC_TEST }

data class SequenceSourceMetadata(
    val sourceName: String,
    val accession: String? = null,
    val sourceUri: String? = null,
    val retrievedAt: String = Instant.now().toString(),
    val referenceAssembly: String? = null,
    val licenseOrTerms: String
)

data class SequencePayload(val metadata: SequenceSourceMetadata, val format: SequenceFormat, val content: String)

interface SequenceSourceAdapter {
    val origin: IntakeOrigin
    fun load(): SequencePayload
}

/** Adapter for a user-provided file already read by the host application's file picker. */
class ExistingSequenceAdapter(private val payload: SequencePayload) : SequenceSourceAdapter {
    override val origin = IntakeOrigin.EXISTING_SEQUENCE
    override fun load() = payload
}

fun interface PublicReferenceResolver {
    /** Implementations must return the exact accession/version requested, or throw. */
    fun resolve(accession: String): SequencePayload
}

/** Network access is deliberately injected; tests can use a pinned offline resolver. */
class PublicReferenceAdapter(
    private val accession: String,
    private val resolver: PublicReferenceResolver
) : SequenceSourceAdapter {
    override val origin = IntakeOrigin.PUBLIC_REFERENCE
    override fun load(): SequencePayload {
        require(accession.isNotBlank()) { "public accession is required" }
        val payload = resolver.resolve(accession)
        require(payload.metadata.accession == accession) { "resolver returned a different accession" }
        return payload
    }
}

/** Deterministic, explicitly non-biological fixture source. */
class SyntheticSequenceAdapter : SequenceSourceAdapter {
    override val origin = IntakeOrigin.SYNTHETIC
    override fun load() = SequencePayload(
        SequenceSourceMetadata(
            sourceName = "ERIA deterministic synthetic sequence",
            licenseOrTerms = "Synthetic test fixture; not biological data",
            referenceAssembly = "synthetic-no-reference",
            retrievedAt = "2026-11-13T00:00:00Z"
        ),
        SequenceFormat.FASTA,
        ">synthetic-read-1\nACGTACGTNN\n>synthetic-read-2\nGGCCATTA\n"
    )
}

data class QualityThresholds(
    val minimumReads: Int = 1,
    val minimumBases: Long = 1,
    val maximumAmbiguousFraction: Double = 0.05,
    val minimumMeanPhred: Double? = null,
    val maximumInputCharacters: Int = 20_000_000,
    val maximumReads: Int = 2_000_000
) {
    init {
        require(minimumReads >= 1)
        require(minimumBases >= 1)
        require(maximumInputCharacters >= 1)
        require(maximumReads >= 1)
        require(maximumAmbiguousFraction in 0.0..1.0)
        require(minimumMeanPhred == null || minimumMeanPhred in 0.0..93.0)
    }
}

data class SequenceQcMetrics(
    val readCount: Int,
    val totalBases: Long,
    val meanReadLength: Double,
    val gcFraction: Double,
    val ambiguousFraction: Double,
    val meanPhred: Double?,
    val format: SequenceFormat
)

data class IntakeReport(
    val state: IntakeState,
    val origin: IntakeOrigin,
    val sourceSha256: String?,
    val metrics: SequenceQcMetrics?,
    val errors: List<String>,
    val warnings: List<String>,
    val createdAt: String
)

data class EvolutionaryFinding(
    val datasetId: String,
    val sourceSha256: String,
    val evidence: SequenceEvidence,
    val readCount: Int,
    val totalBases: Long,
    val gcFraction: Double,
    val ambiguousFraction: Double,
    val meanPhred: Double?,
    val interpretation: String
)

/** Constructor is internal: only the intake gate creates a qualified dataset. */
class QualifiedSequenceDataset internal constructor(
    val dataset: EvolutionaryDataset,
    val metrics: SequenceQcMetrics,
    val evidence: SequenceEvidence
)

sealed class IngestionResult {
    data class Accepted(val qualified: QualifiedSequenceDataset, val report: IntakeReport) : IngestionResult()
    data class Rejected(val report: IntakeReport) : IngestionResult()
}

object SequenceQualityControl {
    private val allowedBases = setOf('A', 'C', 'G', 'T', 'N', 'R', 'Y', 'K', 'M', 'S', 'W', 'B', 'D', 'H', 'V')

    fun parse(payload: SequencePayload): Pair<List<String>, List<Int>?> {
        val lines = payload.content.lineSequence().map { it.trim() }.filter { it.isNotEmpty() }.toList()
        require(lines.isNotEmpty()) { "sequence file is empty" }
        return when (payload.format) {
            SequenceFormat.FASTA -> {
                require(lines.first().startsWith(">")) { "FASTA must begin with a header" }
                val reads = mutableListOf<String>()
                var current = StringBuilder()
                lines.forEach { line ->
                    if (line.startsWith(">")) {
                        if (current.isNotEmpty()) reads += current.toString()
                        current = StringBuilder()
                    } else {
                        require(!line.startsWith("@") && !line.startsWith("+")) { "invalid FASTA record" }
                        current.append(line.uppercase(Locale.ROOT))
                    }
                }
                if (current.isNotEmpty()) reads += current.toString()
                require(reads.isNotEmpty()) { "FASTA contains no sequence records" }
                reads.forEach(::validateSequence)
                reads to null
            }
            SequenceFormat.FASTQ -> {
                require(lines.size % 4 == 0) { "FASTQ must contain complete four-line records" }
                val reads = mutableListOf<String>()
                val scores = mutableListOf<Int>()
                lines.chunked(4).forEachIndexed { index, record ->
                    require(record[0].startsWith("@") && record[2].startsWith("+")) {
                        "malformed FASTQ record at index $index"
                    }
                    val sequence = record[1].uppercase(Locale.ROOT)
                    validateSequence(sequence)
                    require(record[3].length == sequence.length) { "FASTQ quality length mismatch at index $index" }
                    reads += sequence
                    record[3].forEach { ch ->
                        val score = ch.code - 33
                        require(score in 0..93) { "FASTQ quality character outside Phred+33 range" }
                        scores += score
                    }
                }
                reads to scores
            }
        }
    }

    fun measure(payload: SequencePayload): SequenceQcMetrics {
        val (reads, scores) = parse(payload)
        val bases = reads.sumOf { it.length.toLong() }
        val sequence = reads.joinToString("")
        val canonical = sequence.count { it in setOf('A', 'C', 'G', 'T') }
        val gc = sequence.count { it == 'G' || it == 'C' }
        val ambiguous = sequence.count { it !in setOf('A', 'C', 'G', 'T') }
        return SequenceQcMetrics(
            readCount = reads.size,
            totalBases = bases,
            meanReadLength = bases.toDouble() / reads.size,
            gcFraction = if (canonical == 0) 0.0 else gc.toDouble() / canonical,
            ambiguousFraction = ambiguous.toDouble() / bases,
            meanPhred = scores?.takeIf { it.isNotEmpty() }?.average(),
            format = payload.format
        )
    }

    private fun validateSequence(sequence: String) {
        require(sequence.isNotEmpty()) { "sequence record is empty" }
        require(sequence.all { it in allowedBases }) { "sequence contains unsupported nucleotide symbols" }
    }
}

class ThreeSourceIngestionPipeline(
    private val thresholds: QualityThresholds = QualityThresholds()
) {
    fun ingest(adapter: SequenceSourceAdapter, datasetId: String, questionnaire: ResearchIntakeQuestionnaire): IngestionResult {
        val now = Instant.now().toString()
        var digest: String? = null
        try {
            require(datasetId.matches(Regex("^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"))) { "invalid datasetId" }
            val payload = adapter.load()
            val questionnaireErrors = ResearchIntakeQuestionnaireValidator.validate(questionnaire, adapter, payload)
            require(questionnaireErrors.isEmpty()) { questionnaireErrors.joinToString("; ") }
            require(payload.metadata.sourceName.isNotBlank()) { "source name is required" }
            require(payload.metadata.licenseOrTerms.isNotBlank()) { "source license/terms are required" }
            Instant.parse(payload.metadata.retrievedAt)
            when (adapter.origin) {
                IntakeOrigin.PUBLIC_REFERENCE -> require(!payload.metadata.accession.isNullOrBlank()) {
                    "public reference accession is required"
                }
                IntakeOrigin.SYNTHETIC -> require(payload.metadata.accession == null) {
                    "synthetic data cannot claim a public accession"
                }
                IntakeOrigin.EXISTING_SEQUENCE -> Unit
            }
            digest = sha256(payload.content)
            require(payload.content.length <= thresholds.maximumInputCharacters) { "input exceeds configured character limit" }
            val metrics = SequenceQualityControl.measure(payload)
            require(metrics.readCount <= thresholds.maximumReads) { "read count exceeds configured maximum" }
            val failures = mutableListOf<String>()
            val warnings = mutableListOf<String>()
            if (metrics.readCount < thresholds.minimumReads) failures += "read count below configured minimum"
            if (metrics.totalBases < thresholds.minimumBases) failures += "base count below configured minimum"
            if (metrics.ambiguousFraction > thresholds.maximumAmbiguousFraction) failures += "ambiguous-base fraction exceeds configured maximum"
            if (thresholds.minimumMeanPhred != null) {
                val observed = metrics.meanPhred
                if (observed == null) failures += "mean Phred threshold configured but source has no FASTQ qualities"
                else if (observed < thresholds.minimumMeanPhred) failures += "mean Phred score below configured minimum"
            }
            if (metrics.format == SequenceFormat.FASTA) warnings += "FASTA has no per-base quality scores"
            if (adapter.origin == IntakeOrigin.SYNTHETIC) warnings += "synthetic fixture: results are software tests, not biological observations"
            if (failures.isNotEmpty()) return IngestionResult.Rejected(
                IntakeReport(IntakeState.REJECTED, adapter.origin, digest, metrics, failures, warnings, now)
            )

            val origin = when (adapter.origin) {
                IntakeOrigin.EXISTING_SEQUENCE -> DatasetOrigin.EXISTING_SEQUENCE
                IntakeOrigin.PUBLIC_REFERENCE -> DatasetOrigin.PUBLIC_REFERENCE
                IntakeOrigin.SYNTHETIC -> DatasetOrigin.SYNTHETIC
            }
            val parametersDigest = sha256(
                "${thresholds.minimumReads}|${thresholds.minimumBases}|${thresholds.maximumAmbiguousFraction}|${thresholds.minimumMeanPhred}|${thresholds.maximumInputCharacters}|${thresholds.maximumReads}|${questionnaire.projectId}|${questionnaire.researchPurpose}|${questionnaire.organism}|${questionnaire.authority}|${questionnaire.dataSensitivity}|${questionnaire.requestedAnalysisScopes.sorted()}|${questionnaire.sourceOrigin}|${questionnaire.sequenceFormat}|${questionnaire.declaredAccession}|${questionnaire.referenceAssembly}|${questionnaire.containsDirectIdentifiers}|${questionnaire.clinicalAuthorizationDeclared}|${questionnaire.clinicalAuthorizationReference}|${questionnaire.completedAt}"
            )
            val summary = listOf(metrics.readCount, metrics.totalBases, metrics.gcFraction, metrics.ambiguousFraction, metrics.meanPhred).joinToString("|")
            val dataset = EvolutionaryDataset(
                datasetId = datasetId,
                provenance = DatasetProvenance(
                    origin = origin,
                    sourceName = payload.metadata.sourceName,
                    sourceAccession = payload.metadata.accession,
                    sourceUri = payload.metadata.sourceUri,
                    sourceSha256 = digest,
                    retrievedAt = payload.metadata.retrievedAt,
                    referenceAssembly = payload.metadata.referenceAssembly,
                    licenseOrTerms = payload.metadata.licenseOrTerms
                ),
                layers = setOf(OmicsLayer.GENOME),
                evidenceState = if (origin == DatasetOrigin.SYNTHETIC) EvidenceState.UNKNOWN else EvidenceState.OBSERVED,
                quality = DatasetQuality("passed", null, null, null, warnings),
                pipeline = PipelineFingerprint(
                    "eria-three-source-intake", "1.0.0", "Kotlin/JVM",
                    parametersDigest, digest, sha256(summary)
                ),
                createdAt = now,
                notes = "Sequence QC only; no clinical or intervention interpretation."
            )
            val validationErrors = EvolutionaryDatasetValidator.validate(dataset)
            if (validationErrors.isNotEmpty()) return IngestionResult.Rejected(
                IntakeReport(IntakeState.REJECTED, adapter.origin, digest, metrics, validationErrors, warnings, now)
            )
            val evidence = when (adapter.origin) {
                IntakeOrigin.EXISTING_SEQUENCE -> SequenceEvidence.OBSERVED_INPUT
                IntakeOrigin.PUBLIC_REFERENCE -> SequenceEvidence.PUBLIC_REFERENCE
                IntakeOrigin.SYNTHETIC -> SequenceEvidence.SYNTHETIC_TEST
            }
            return IngestionResult.Accepted(
                QualifiedSequenceDataset(dataset, metrics, evidence),
                IntakeReport(IntakeState.ACCEPTED, adapter.origin, digest, metrics, emptyList(), warnings, now)
            )
        } catch (e: Exception) {
            return IngestionResult.Rejected(
                IntakeReport(IntakeState.REJECTED, adapter.origin, digest, null,
                    listOf(e.message ?: "unknown ingestion failure"), emptyList(), now)
            )
        }
    }
}

/** Accepts only datasets emitted by the quality gate; output is descriptive, not diagnostic. */
object EvolutionaryAnalysisEngine {
    fun analyze(input: QualifiedSequenceDataset): EvolutionaryFinding {
        val m = input.metrics
        return EvolutionaryFinding(
            datasetId = input.dataset.datasetId,
            sourceSha256 = input.dataset.provenance.sourceSha256,
            evidence = input.evidence,
            readCount = m.readCount,
            totalBases = m.totalBases,
            gcFraction = m.gcFraction,
            ambiguousFraction = m.ambiguousFraction,
            meanPhred = m.meanPhred,
            interpretation = when (input.evidence) {
                SequenceEvidence.SYNTHETIC_TEST -> "Synthetic QC demonstration only; no biological inference."
                SequenceEvidence.PUBLIC_REFERENCE -> "Reference sequence composition summary; not a sample-level clinical finding."
                SequenceEvidence.OBSERVED_INPUT -> "Input sequence composition summary; biological significance is not established."
            }
        )
    }
}

private fun sha256(value: String): String = MessageDigest.getInstance("SHA-256")
    .digest(value.toByteArray(Charsets.UTF_8))
    .joinToString("") { "%02x".format(it) }
