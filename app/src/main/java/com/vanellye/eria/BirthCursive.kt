package com.vanellye.eria

import androidx.compose.foundation.layout.Column
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Text as MaterialText
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import java.security.MessageDigest
import java.util.ArrayDeque
import java.util.Collections
import java.util.IdentityHashMap

data class BirthCursiveRecord(
    val schema: String,
    val fieldPath: String,
    val originText: String,
    val originSha256: String,
    val meaning: String?,
    val possibility: String?,
    val derivedText: String,
    val derivedSha256: String,
    val ruleId: String?,
    val status: String,
    val coSigners: List<String>,
    val coSignatureRef: String?,
    val coSignatureStatus: String,
    val signatureVerification: String = "NOT_PERFORMED_BY_THIS_MODULE"
)

data class BirthCursiveTree(
    val origin: Any?,
    val derived: Any?,
    val records: List<BirthCursiveRecord>
)

/**
 * Origin-linked, constructive UI text derivation.
 *
 * Exact reviewed rules only. Unknown text is preserved for review. The nested
 * tree walker uses an explicit work stack; it does not recursively descend.
 * Hashes identify bytes, not authorship, consent, truth, or signature validity.
 */
object BirthCursiveEngine {
    private data class Rule(
        val id: String,
        val origin: String,
        val meaning: String,
        val possibility: String,
        val blessing: String
    )

    private val rules = listOf(
        Rule(
            "oppositio.failure.v1",
            "May you fail",
            "A wish for an unsuccessful outcome",
            "Learning, adaptation, and achievement remain possible",
            "May your efforts open paths to learning, growth, and success."
        ),
        Rule(
            "oppositio.suffering.v1",
            "May you suffer",
            "A wish for another person's suffering",
            "Relief, care, peace, and healing are constructive possibilities",
            "May you find relief, peace, care, and healing."
        ),
        Rule(
            "oppositio.worth.v1",
            "You are worthless",
            "A statement denying a person's worth",
            "Human dignity and belonging can be affirmed",
            "Your life has inherent worth and dignity."
        ),
        Rule(
            "oppositio.trapped.v1",
            "You are trapped",
            "A statement that presents a person as having no way forward",
            "Safe choices and paths toward freedom may be discovered",
            "May you discover a safe path toward freedom."
        ),
        Rule(
            "oppositio.darkness.v1",
            "Darkness surrounds you",
            "A statement expressing obscurity or disorientation",
            "Clarity, understanding, and guidance are possible",
            "May clarity and understanding illuminate your path."
        )
    )

    private val textFields = setOf(
        "text", "content", "label", "title", "description", "message",
        "tooltip", "placeholder", "accessibility_label", "accessibilityLabel",
        "aria_label", "ariaLabel", "alt", "notification", "dialog_text",
        "button_text", "helper_text", "caption", "summary"
    )

    private val neverTransformFields = setOf(
        "code", "command", "route", "url", "uri", "id", "key", "status",
        "error_code", "errorCode", "security_warning", "securityWarning",
        "warning_code", "warningCode", "shortcut", "hotkey", "escape_sequence"
    )

    private fun key(text: String): String =
        text.trim().lowercase()
            .trimEnd('.', '!', '?')
            .split(Regex("\\s+"))
            .filter { it.isNotEmpty() }
            .joinToString(" ")

    private fun digest(text: String): String =
        MessageDigest.getInstance("SHA-256")
            .digest(text.toByteArray(Charsets.UTF_8))
            .joinToString("") { byte -> "%02x".format(byte.toInt() and 0xff) }

    fun transformText(
        origin: String,
        fieldPath: String = "/ui/text",
        coSigners: List<String> = emptyList(),
        coSignatureRef: String? = null
    ): BirthCursiveRecord {
        val rule = rules.firstOrNull { key(it.origin) == key(origin) }
        val derived = rule?.blessing ?: origin
        val signers = coSigners.map { it.trim() }.filter { it.isNotEmpty() }.distinct()
        val reference = coSignatureRef?.trim()?.takeIf { it.isNotEmpty() }
        return BirthCursiveRecord(
            schema = "yaero.birth-cursive/1",
            fieldPath = fieldPath,
            originText = origin,
            originSha256 = digest(origin),
            meaning = rule?.meaning,
            possibility = rule?.possibility,
            derivedText = derived,
            derivedSha256 = digest(derived),
            ruleId = rule?.id,
            status = if (rule == null) "REVIEW_REQUIRED" else "DERIVED",
            coSigners = signers,
            coSignatureRef = reference,
            coSignatureStatus = if (reference != null && signers.isNotEmpty()) {
                "REFERENCE_ATTACHED_UNVERIFIED"
            } else {
                "PENDING"
            }
        )
    }

    private sealed class Work
    private data class Visit(
        val value: Any?,
        val path: String,
        val depth: Int,
        val textContext: Boolean,
        val blocked: Boolean,
        val assign: (Any?) -> Unit
    ) : Work()
    private data class Exit(val identity: Any) : Work()

    fun transformTree(
        origin: Any?,
        maxDepth: Int = 64,
        coSigners: List<String> = emptyList(),
        coSignatureRef: String? = null
    ): BirthCursiveTree {
        require(maxDepth >= 1) { "maxDepth must be at least 1" }
        val records = mutableListOf<BirthCursiveRecord>()
        val active = Collections.newSetFromMap(IdentityHashMap<Any, Boolean>())
        val root = arrayOfNulls<Any?>(1)
        val work = ArrayDeque<Work>()
        work.addLast(Visit(origin, "", 0, false, false) { root[0] = it })

        while (work.isNotEmpty()) {
            when (val item = work.removeLast()) {
                is Exit -> active.remove(item.identity)
                is Visit -> {
                    require(item.depth <= maxDepth) {
                        "maximum nested UI depth exceeded at " + item.path.ifBlank { "/" }
                    }
                    when (val value = item.value) {
                        is String -> {
                            if (item.blocked || !item.textContext) {
                                item.assign(value)
                            } else {
                                val record = transformText(
                                    value, item.path.ifBlank { "/" }, coSigners, coSignatureRef
                                )
                                records += record
                                item.assign(record.derivedText)
                            }
                        }
                        is Map<*, *> -> {
                            require(active.add(value)) {
                                "cycle detected at " + item.path.ifBlank { "/" }
                            }
                            val derived = LinkedHashMap<Any?, Any?>()
                            item.assign(derived)
                            work.addLast(Exit(value))
                            val entries = value.entries.toList()
                            for (index in entries.indices.reversed()) {
                                val entry = entries[index]
                                val field = entry.key as? String ?: entry.key.toString()
                                val childBlocked = item.blocked || field in neverTransformFields
                                val childText = !childBlocked && field in textFields
                                val childPath = item.path + "/" +
                                    field.replace("~", "~0").replace("/", "~1")
                                work.addLast(Visit(
                                    entry.value, childPath, item.depth + 1,
                                    childText, childBlocked
                                ) { result -> derived[entry.key] = result })
                            }
                        }
                        is List<*> -> {
                            require(active.add(value)) {
                                "cycle detected at " + item.path.ifBlank { "/" }
                            }
                            val derived = MutableList<Any?>(value.size) { null }
                            item.assign(derived)
                            work.addLast(Exit(value))
                            for (index in value.indices.reversed()) {
                                work.addLast(Visit(
                                    value[index], item.path + "/" + index,
                                    item.depth + 1, item.textContext, item.blocked
                                ) { result -> derived[index] = result })
                            }
                        }
                        else -> item.assign(value)
                    }
                }
            }
        }
        return BirthCursiveTree(origin, root[0], records.toList())
    }
}

/** Text presentation that keeps the exact origin and adds a separate possibility. */
@Composable
fun BirthCursiveText(
    text: String,
    modifier: Modifier = Modifier,
    color: Color = Color.Unspecified,
    style: TextStyle? = null,
    fontWeight: FontWeight? = null
) {
    val record = remember(text) { BirthCursiveEngine.transformText(text) }
    Column(modifier = modifier) {
        MaterialText(
            text = text,
            color = color,
            style = style ?: MaterialTheme.typography.body1,
            fontWeight = fontWeight
        )
        if (record.status == "DERIVED" && record.derivedText != record.originText) {
            MaterialText(
                text = "✧ Positive possibility: " + record.derivedText,
                color = Color(0xFF83D6C2),
                style = MaterialTheme.typography.caption
            )
        }
    }
}
