package com.vanellye.codexgen.gitbridge

data class PromptDimension(
    val name: String,
    val score: Int,
    val finding: String,
    val recommendation: String
)

data class PromptOptimizationReport(
    val overallScore: Int,
    val dimensions: List<PromptDimension>,
    val optimizedDraft: String,
    val caveat: String
)

/**
 * Deterministic prompt-quality review. It evaluates the supplied prompt text only.
 * It does not inspect private reasoning, change model weights, or self-modify code.
 */
object PromptReportEngine {
    fun analyze(prompt: String): PromptOptimizationReport {
        val p = prompt.trim()
        require(p.isNotBlank()) { "Enter a prompt to analyze." }

        val lower = p.lowercase()
        val hasGoal = listOf("goal", "objective", "want", "build", "create", "explain", "analyze")
            .any { lower.contains(it) }
        val hasContext = p.length >= 180 || listOf("context:", "background:", "for:", "project:")
            .any { lower.contains(it) }
        val hasConstraints = listOf("must", "don't", "do not", "constraint", "limit", "avoid", "only")
            .any { lower.contains(it) }
        val hasOutput = listOf("format", "table", "json", "steps", "deliverable", "output")
            .any { lower.contains(it) }
        val hasValidation = listOf("test", "verify", "validate", "acceptance", "success criteria")
            .any { lower.contains(it) }
        val hasSafety = listOf("safe", "risk", "privacy", "security", "evidence", "uncertainty")
            .any { lower.contains(it) }

        val dims = listOf(
            PromptDimension("Goal clarity", if (hasGoal) 90 else 45,
                if (hasGoal) "A goal/action is identifiable." else "The desired outcome is not explicit.",
                "State the exact outcome in the first sentence."),
            PromptDimension("Context", if (hasContext) 85 else 40,
                if (hasContext) "Some background or sufficient detail is present." else "Little project or audience context is supplied.",
                "Add relevant background, current state, and intended audience."),
            PromptDimension("Constraints", if (hasConstraints) 85 else 35,
                if (hasConstraints) "At least one constraint is stated." else "Boundaries and exclusions are unclear.",
                "List must-haves, must-not-haves, scope, and resource limits."),
            PromptDimension("Output specification", if (hasOutput) 90 else 35,
                if (hasOutput) "A desired output shape is suggested." else "The response format is unspecified.",
                "Specify the deliverable format, sections, and level of detail."),
            PromptDimension("Validation", if (hasValidation) 90 else 30,
                if (hasValidation) "Verification or testing is mentioned." else "No success criteria are stated.",
                "Define measurable acceptance criteria and how to verify them."),
            PromptDimension("Safety and uncertainty", if (hasSafety) 85 else 40,
                if (hasSafety) "Risk, evidence, or privacy is acknowledged." else "Risk and uncertainty handling could be clearer.",
                "Ask for evidence, assumptions, risks, and safe boundaries.")
        )
        val score = dims.map { it.score }.average().toInt()
        val improved = buildString {
            appendLine("Objective:")
            appendLine(p)
            appendLine()
            appendLine("Context: [Add the relevant project state, audience, and background.]")
            appendLine("Constraints: [List required boundaries, exclusions, and resources.]")
            appendLine("Deliverable: [Specify format, sections, and depth.]")
            appendLine("Validation: [Define tests and measurable acceptance criteria.]")
            appendLine("Evidence and safety: [Separate verified facts, assumptions, and uncertainty; identify risks.]")
        }
        return PromptOptimizationReport(
            score, dims, improved,
            "Heuristic text-only assessment. Scores are guidance, not a measure of intelligence or model quality. Review the suggested draft before use."
        )
    }
}
