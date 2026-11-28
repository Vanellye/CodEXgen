package com.vanellye.eria.orchid

import android.content.Context
import org.json.JSONObject
import java.util.Locale

/**
 * Read-only loader for the bundled ORCHID symbol database.
 * The JSON asset is data only; it is never interpreted as executable code.
 */
data class OrchidDatabaseRecord(
    val id: String,
    val kind: String,
    val name: String,
    val glyph: String,
    val meaning: String,
    val status: String,
    val aliases: List<String>,
    val keywords: List<String>
)

class OrchidSymbolDatabase(context: Context) {
    private val records: List<OrchidDatabaseRecord>

    init {
        val source = context.applicationContext.assets
            .open("orchid/orchid-symbol-database.v1.json")
            .bufferedReader(Charsets.UTF_8)
            .use { it.readText() }
        val root = JSONObject(source)
        require(root.optString("format") == "ORCHID_SYMBOL_DATABASE") {
            "Unsupported ORCHID database format."
        }
        require(root.optString("schemaVersion").startsWith("1.")) {
            "Unsupported ORCHID database schema version."
        }
        val loaded = mutableListOf<OrchidDatabaseRecord>()
        listOf("records", "keywordRecords").forEach { collection ->
            val array = root.getJSONArray(collection)
            for (index in 0 until array.length()) {
                val item = array.getJSONObject(index)
                loaded += OrchidDatabaseRecord(
                    id = item.getString("id"),
                    kind = item.getString("kind"),
                    name = item.getString("name"),
                    glyph = item.getString("glyph"),
                    meaning = item.optString("meaning"),
                    status = item.optString("status", "unspecified"),
                    aliases = item.optStringArray("aliases"),
                    keywords = item.optStringArray("keywords")
                )
            }
        }
        require(loaded.map { it.id }.toSet().size == loaded.size) {
            "ORCHID database contains duplicate record IDs."
        }
        require(loaded.all { it.id.isNotBlank() && it.glyph.isNotBlank() }) {
            "ORCHID records require stable IDs and non-empty glyphs."
        }
        records = loaded.toList()
    }

    fun all(): List<OrchidDatabaseRecord> = records

    fun findById(id: String): OrchidDatabaseRecord? =
        records.firstOrNull { it.id == id }

    fun search(query: String, kind: String? = null): List<OrchidDatabaseRecord> {
        val needle = query.trim().lowercase(Locale.ROOT)
        if (needle.isEmpty()) return emptyList()
        return records.filter { record ->
            (kind == null || record.kind == kind) &&
                sequenceOf(record.name, record.meaning, record.glyph)
                    .plus(record.aliases.asSequence())
                    .plus(record.keywords.asSequence())
                    .any { it.lowercase(Locale.ROOT).contains(needle) }
        }
    }

    fun insertText(id: String): String =
        findById(id)?.glyph ?: error("Unknown ORCHID symbol ID: $id")

    private fun JSONObject.optStringArray(key: String): List<String> {
        val array = optJSONArray(key) ?: return emptyList()
        return (0 until array.length()).mapNotNull { index ->
            array.optString(index).takeIf { it.isNotBlank() }
        }
    }
}
