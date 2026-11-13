package com.vanellye.eria.evolutionary

import java.time.Instant

enum class DatasetOrigin { EXISTING_SEQUENCE, PUBLIC_REFERENCE, SYNTHETIC }
enum class OmicsLayer { GENOME, EPIGENOME, TRANSCRIPTOME, PROTEOME, METABOLOME, DNA_REPAIR, TELOMERE, ENVIRONMENT }
enum class EvidenceState { OBSERVED, DERIVED, PREDICTED, UNKNOWN }
enum class ReviewStatus { NOT_REVIEWED, APPROVED, REJECTED }

data class DatasetProvenance(
    val origin: DatasetOrigin, val sourceName: String, val sourceAccession: String?,
    val sourceUri: String?, val sourceSha256: String, val retrievedAt: String,
    val referenceAssembly: String?, val licenseOrTerms: String
)
data class PipelineFingerprint(
    val pipelineName: String, val pipelineVersion: String, val toolchain: String,
    val parametersSha256: String, val inputSha256: String, val outputSha256: String
)
data class DatasetQuality(
    val qualityState: String, val coverageMean: Double?, val callRate: Double?,
    val contaminationEstimate: Double?, val warnings: List<String> = emptyList()
)
data class EvolutionaryDataset(
    val datasetId: String, val schemaVersion: Int = 1, val provenance: DatasetProvenance,
    val layers: Set<OmicsLayer>, val evidenceState: EvidenceState,
    val quality: DatasetQuality, val pipeline: PipelineFingerprint?,
    val createdAt: String, val notes: String = ""
)
data class HumanReview(
    val status: ReviewStatus = ReviewStatus.NOT_REVIEWED, val reviewerId: String? = null,
    val reviewedAt: String? = null, val approvedDatasetSha256: String? = null,
    val approvedScopes: Set<String> = emptySet(), val decisionReference: String? = null
)

object EvolutionaryDatasetValidator {
    private val idPattern = Regex("^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
    private val sha256Pattern = Regex("^[0-9a-f]{64}$")

    fun validate(dataset: EvolutionaryDataset): List<String> {
        val errors = mutableListOf<String>()
        if (!idPattern.matches(dataset.datasetId)) errors += "datasetId must be a stable identifier"
        if (dataset.schemaVersion != 1) errors += "unsupported schemaVersion"
        if (dataset.provenance.sourceName.isBlank()) errors += "sourceName is required"
        if (!sha256Pattern.matches(dataset.provenance.sourceSha256)) errors += "sourceSha256 must be lowercase SHA-256"
        if (dataset.provenance.licenseOrTerms.isBlank()) errors += "licenseOrTerms must be recorded"
        if (!isInstant(dataset.provenance.retrievedAt)) errors += "retrievedAt must be ISO-8601"
        if (!isInstant(dataset.createdAt)) errors += "createdAt must be ISO-8601"
        if (dataset.layers.isEmpty()) errors += "at least one omics layer is required"
        val q = dataset.quality
        if (q.qualityState.isBlank()) errors += "qualityState is required"
        q.coverageMean?.let { if (!it.isFinite() || it < 0.0) errors += "coverageMean must be finite and non-negative" }
        q.callRate?.let { if (!it.isFinite() || it !in 0.0..1.0) errors += "callRate must be between 0 and 1" }
        q.contaminationEstimate?.let { if (!it.isFinite() || it !in 0.0..1.0) errors += "contaminationEstimate must be between 0 and 1" }
        if (dataset.provenance.origin == DatasetOrigin.SYNTHETIC && dataset.provenance.sourceAccession != null)
            errors += "synthetic datasets must not claim a public accession"
        if (dataset.provenance.origin == DatasetOrigin.PUBLIC_REFERENCE && dataset.provenance.sourceAccession.isNullOrBlank())
            errors += "public reference datasets require a source accession"
        dataset.pipeline?.let { p ->
            if (p.pipelineName.isBlank() || p.pipelineVersion.isBlank() || p.toolchain.isBlank())
                errors += "pipeline name, version, and toolchain are required"
            listOf(p.parametersSha256, p.inputSha256, p.outputSha256).forEach {
                if (!sha256Pattern.matches(it)) errors += "pipeline fingerprints must be lowercase SHA-256"
            }
            if (p.inputSha256 != dataset.provenance.sourceSha256)
                errors += "pipeline input digest must match the recorded source digest"
        }
        return errors
    }

    fun validateReview(review: HumanReview, datasetSha256: String, requestedScope: String): List<String> {
        val errors = mutableListOf<String>()
        if (review.status != ReviewStatus.APPROVED) errors += "human approval is required"
        if (review.reviewerId.isNullOrBlank()) errors += "reviewerId is required"
        if (review.decisionReference.isNullOrBlank()) errors += "decisionReference is required"
        if (review.reviewedAt == null || !isInstant(review.reviewedAt)) errors += "reviewedAt must be ISO-8601"
        if (review.approvedDatasetSha256 != datasetSha256 || !sha256Pattern.matches(datasetSha256))
            errors += "approval must match the exact dataset digest"
        if (requestedScope !in review.approvedScopes) errors += "requested scope is not approved"
        return errors
    }

    private fun isInstant(value: String): Boolean = try { Instant.parse(value); true } catch (_: Exception) { false }
}

/** Synthetic fixture metadata only; it contains no human or clinical observations. */
object SyntheticEvolutionaryFixture {
    fun dataset() = EvolutionaryDataset(
        datasetId = "synthetic.demo-001",
        provenance = DatasetProvenance(
            origin = DatasetOrigin.SYNTHETIC, sourceName = "ERIA deterministic synthetic fixture",
            sourceAccession = null, sourceUri = null, sourceSha256 = "a".repeat(64),
            retrievedAt = "2026-11-13T00:00:00Z", referenceAssembly = "synthetic-no-reference",
            licenseOrTerms = "Generated test fixture; not biological data"
        ),
        layers = setOf(OmicsLayer.GENOME, OmicsLayer.DNA_REPAIR, OmicsLayer.TELOMERE),
        evidenceState = EvidenceState.UNKNOWN,
        quality = DatasetQuality("synthetic_test_only", 30.0, 0.99, 0.0),
        pipeline = PipelineFingerprint("eria-fixture", "1.0.0", "Kotlin/JVM",
            "b".repeat(64), "a".repeat(64), "c".repeat(64)),
        createdAt = "2026-11-13T00:00:00Z",
        notes = "Synthetic metadata only; no biological inference permitted."
    )
}
