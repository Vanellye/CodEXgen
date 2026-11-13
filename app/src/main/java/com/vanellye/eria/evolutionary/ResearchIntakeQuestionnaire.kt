package com.vanellye.eria.evolutionary

import java.time.Instant

enum class QuestionnaireAuthority {
    USER_AUTHORITY_RECORDED,
    PUBLIC_TERMS_RECORDED,
    SYNTHETIC_FIXTURE,
    NOT_CONFIRMED
}

enum class DataSensitivity { PUBLIC, RESTRICTED_GENOMIC, SYNTHETIC_ONLY }

data class ResearchIntakeQuestionnaire(
    val projectId: String,
    val researchPurpose: String,
    val organism: String,
    val sourceOrigin: IntakeOrigin,
    val sequenceFormat: SequenceFormat,
    val authority: QuestionnaireAuthority,
    val dataSensitivity: DataSensitivity,
    val declaredAccession: String? = null,
    val referenceAssembly: String? = null,
    val requestedAnalysisScopes: Set<String> = setOf("sequence_qc", "evolutionary_summary"),
    val containsDirectIdentifiers: Boolean = false,
    val completedAt: String = Instant.now().toString()
)

object ResearchIntakeQuestionnaireValidator {
    private val idPattern = Regex("^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
    private val allowedScopes = setOf("sequence_qc", "evolutionary_summary")

    fun validate(form: ResearchIntakeQuestionnaire, adapter: SequenceSourceAdapter, payload: SequencePayload): List<String> {
        val errors = mutableListOf<String>()
        if (!idPattern.matches(form.projectId)) errors += "projectId must be a stable identifier"
        if (form.researchPurpose.isBlank()) errors += "research purpose is required"
        if (form.organism.isBlank()) errors += "organism is required; use 'unknown' when not established"
        if (form.sourceOrigin != adapter.origin) errors += "questionnaire source origin does not match adapter"
        if (form.sequenceFormat != payload.format) errors += "questionnaire sequence format does not match payload"
        if (form.completedAt.let { try { Instant.parse(it); false } catch (_: Exception) { true } })
            errors += "completedAt must be ISO-8601"
        if (form.containsDirectIdentifiers) errors += "direct personal identifiers must be removed before intake"
        if (form.requestedAnalysisScopes.isEmpty()) errors += "at least one analysis scope is required"
        if (form.requestedAnalysisScopes.any { it !in allowedScopes }) errors += "questionnaire requests an unsupported analysis scope"
        when (form.sourceOrigin) {
            IntakeOrigin.EXISTING_SEQUENCE -> {
                if (form.authority != QuestionnaireAuthority.USER_AUTHORITY_RECORDED)
                    errors += "existing sequence requires recorded authority to use the data"
                if (form.dataSensitivity != DataSensitivity.RESTRICTED_GENOMIC)
                    errors += "existing sequence must be classified as restricted genomic data"
            }
            IntakeOrigin.PUBLIC_REFERENCE -> {
                if (form.authority != QuestionnaireAuthority.PUBLIC_TERMS_RECORDED)
                    errors += "public reference requires recorded license/terms review"
                if (form.dataSensitivity != DataSensitivity.PUBLIC)
                    errors += "public reference must be classified as public"
                if (form.declaredAccession.isNullOrBlank() || form.declaredAccession != payload.metadata.accession)
                    errors += "declared public accession must exactly match the resolved payload"
            }
            IntakeOrigin.SYNTHETIC -> {
                if (form.authority != QuestionnaireAuthority.SYNTHETIC_FIXTURE)
                    errors += "synthetic data must be identified as a synthetic fixture"
                if (form.dataSensitivity != DataSensitivity.SYNTHETIC_ONLY)
                    errors += "synthetic data must be classified as synthetic only"
                if (form.declaredAccession != null) errors += "synthetic data cannot declare a public accession"
            }
        }
        if (form.referenceAssembly != null && payload.metadata.referenceAssembly != null &&
            form.referenceAssembly != payload.metadata.referenceAssembly)
            errors += "declared reference assembly does not match payload metadata"
        return errors
    }
}
