package com.vanellye.eria

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class BirthCursiveEngineTest {
    @Test fun derivesConstructiveMeaningAndRetainsOrigin() {
        val record = BirthCursiveEngine.transformText("May you fail", "/dialog/title")
        assertEquals("May you fail", record.originText)
        assertEquals(
            "May your efforts open paths to learning, growth, and success.",
            record.derivedText
        )
        assertEquals("DERIVED", record.status)
        assertTrue(record.originSha256 != record.derivedSha256)
        assertEquals("oppositio.failure.v1", record.ruleId)
    }

    @Test fun unknownMessagesRemainUnchangedForReview() {
        val record = BirthCursiveEngine.transformText("An ambiguous expression")
        assertEquals(record.originText, record.derivedText)
        assertEquals("REVIEW_REQUIRED", record.status)
    }

    @Test fun nestedUiTreeUsesIterativeVisitorAndPreservesSource() {
        val source = mapOf(
            "dialog" to mapOf(
                "title" to "May you fail",
                "buttons" to listOf(
                    mapOf("label" to "You are worthless"),
                    mapOf("label" to "Continue")
                )
            ),
            "security_warning" to mapOf("message" to "May you fail"),
            "command" to mapOf("label" to "May you fail")
        )
        val result = BirthCursiveEngine.transformTree(source)
        val dialog = result.derived as Map<*, *>
        val dialogBody = dialog["dialog"] as Map<*, *>
        val buttons = dialogBody["buttons"] as List<*>
        assertEquals("May you fail", (source["dialog"] as Map<*, *>)["title"])
        assertEquals(
            "May your efforts open paths to learning, growth, and success.",
            dialogBody["title"]
        )
        assertEquals("Your life has inherent worth and dignity.", (buttons[0] as Map<*, *>)["label"])
        assertEquals("Continue", (buttons[1] as Map<*, *>)["label"])
        assertEquals("May you fail", ((dialog["security_warning"] as Map<*, *>)["message"]))
        assertEquals("May you fail", ((dialog["command"] as Map<*, *>)["label"]))
        assertEquals(3, result.records.size)
    }

    @Test fun coSignatureReferenceIsNeverClaimedAsVerified() {
        val record = BirthCursiveEngine.transformText(
            "May you fail",
            "/button/label",
            listOf("origin-owner", "reviewer"),
            "signature-ledger:event-42"
        )
        assertEquals("REFERENCE_ATTACHED_UNVERIFIED", record.coSignatureStatus)
        assertEquals("NOT_PERFORMED_BY_THIS_MODULE", record.signatureVerification)
    }

    @Test fun cycleIsRejectedByIterativeVisitor() {
        val cycle = mutableMapOf<String, Any?>()
        cycle["nested"] = cycle
        var rejected = false
        try {
            BirthCursiveEngine.transformTree(cycle)
        } catch (_: IllegalArgumentException) {
            rejected = true
        }
        assertTrue(rejected)
    }

    @Test fun veryDeepTreeUsesWorkStack() {
        var source: Any? = mapOf("label" to "May you fail")
        repeat(1100) { source = mapOf("nested" to source) }
        val result = BirthCursiveEngine.transformTree(source, maxDepth = 1200)
        assertEquals(1, result.records.size)
    }
}
