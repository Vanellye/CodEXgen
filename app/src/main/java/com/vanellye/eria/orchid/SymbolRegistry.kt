package com.vanellye.eria.orchid

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.util.UUID

data class OrchidSymbol(val id: String, val name: String, val glyph: String, val meaning: String, val origin: String = "ORCHID_CHRONOGLYPH_02")

data class OrchidWordKey(
    val id: String,
    val name: String,
    val glyph: String,
    val silhouette: String,
    val meaning: String
)

class SymbolRegistry(context: Context) {
    private val wordKeys = listOf(
        OrchidWordKey("ORC-300-001","SWERVE","↗","🌪️","Change direction sharply"),
        OrchidWordKey("ORC-300-002","VEER","➚","🧭","Turn gradually from a course"),
        OrchidWordKey("ORC-300-003","PIVOT","⦿","🔄","Turn around a fixed point"),
        OrchidWordKey("ORC-300-004","CONVERGE","⇢⇠","🧲","Move toward a shared point"),
        OrchidWordKey("ORC-300-005","DIVERGE","↗↖","✴️","Separate into distinct directions"),
        OrchidWordKey("ORC-300-006","WEAVE","⌘","🧵","Interlace connected paths"),
        OrchidWordKey("ORC-300-007","FOLD","⌒","📜","Bend one layer over another"),
        OrchidWordKey("ORC-300-008","UNFOLD","⋀","🦋","Open or extend folded layers"),
        OrchidWordKey("ORC-300-009","FLOW","≈","🌊","Move continuously"),
        OrchidWordKey("ORC-300-010","SURGE","≫","🌊","Advance in a strong wave"),
        OrchidWordKey("ORC-300-011","DRIFT","⋯","🍃","Move gradually without fixed course"),
        OrchidWordKey("ORC-300-012","OSCILLATE","∿","📳","Move repeatedly between positions"),
        OrchidWordKey("ORC-300-013","ORBIT","◎","🪐","Travel around an origin"),
        OrchidWordKey("ORC-300-014","REVOLVE","⟳","🌀","Rotate around an axis"),
        OrchidWordKey("ORC-300-015","ASCEND","⇡","🚀","Move upward"),
        OrchidWordKey("ORC-300-016","DESCEND","⇣","🪂","Move downward"),
        OrchidWordKey("ORC-300-017","RETURN","↶","🪃","Come back toward origin"),
        OrchidWordKey("ORC-300-018","RETRACE","〰↶","👣","Follow a recorded path backward"),
        OrchidWordKey("ORC-300-019","REVERSE","↔","🔁","Invert direction or order"),
        OrchidWordKey("ORC-300-020","EVOLVE","◉∿","🧬","Develop through successive states"),
        OrchidWordKey("ORC-300-021","TRANSFORM","✥","🦋","Change form while retaining lineage"),
        OrchidWordKey("ORC-300-022","MERGE","⊗","🤝","Join while preserving provenance"),
        OrchidWordKey("ORC-300-023","SPLIT","⋔","⚡","Divide into distinct paths"),
        OrchidWordKey("ORC-300-024","RESOLVE","✓","🎯","Reach a defined outcome")
    )
    fun wordKeys(): List<OrchidWordKey> = wordKeys

    private val prefs = context.getSharedPreferences("orchid_private_symbols", Context.MODE_PRIVATE)
    private val keyboardPrefs = context.getSharedPreferences(KEYBOARD_PREFS, Context.MODE_PRIVATE)
    private val canonical = listOf(
        OrchidSymbol("ORC-TRYNITI-001","TRYNITI","4♧","TRINITY_SOURCE_3_STRANDS_OVER_INFINITY", "ORCHID_TRYNITI_01"),
        OrchidSymbol("ORC-CG01-0001","VORA","⧖","TEMPORAL_FLEXIBILITY"),
        OrchidSymbol("ORC-CG01-0002","ELUN","⫶","OBSERVATION_INSTANT"),
        OrchidSymbol("ORC-CG01-0003","THERA","⤙","HISTORICAL_DIRECTION"),
        OrchidSymbol("ORC-CG01-0004","AVER","⤚","FUTURE_DIRECTION"),
        OrchidSymbol("ORC-CG01-0005","NOVEX","⧓","TEMPORAL_BRANCHING"),
        OrchidSymbol("ORC-CG01-0006","SELVA","⫰","DURATION"),
        OrchidSymbol("ORC-CG01-0007","RUVEN","⧔","RECURRENCE"),
        OrchidSymbol("ORC-CG01-0008","KERIN","⫷","SYNCHRONIZATION"),
        OrchidSymbol("ORC-CG01-0009","MORIN","⧉","SIMULTANEITY"),
        OrchidSymbol("ORC-CG01-0010","DEXEN","⤺","REVERSIBLE_TRACE"),
        OrchidSymbol("ORC-CG01-0011","ORIEL","⧗","TEMPORAL_UNCERTAINTY"),
        OrchidSymbol("ORC-CG01-0012","ZEPHIR","⫯","INTERVAL_COMPLETION")
    )

    fun all(): List<OrchidSymbol> = canonical + readPrivate()

    fun addPrivate(name: String, glyph: String, meaning: String): OrchidSymbol {
        require(name.isNotBlank() && name.length <= 80) { "Name must contain 1–80 characters." }
        require(glyph.isNotBlank() && glyph.codePointCount(0, glyph.length) <= 8) { "Glyph is limited to eight Unicode code points." }
        require(meaning.length <= 500) { "Meaning is limited to 500 characters." }
        val symbol = OrchidSymbol("ORC-LOCAL-" + UUID.randomUUID().toString(), name.trim(), glyph, meaning.trim(), "LOCAL_PRIVATE")
        savePrivate(readPrivate().filterNot { it.id == symbol.id } + symbol)
        return symbol
    }

    fun importPrivate(json: String): Int {
        require(json.length <= MAX_PACK_CHARS) { "Symbol pack exceeds the 256 KB import limit." }
        val root = JSONObject(json)
        require(root.optString("format") == "ORCHID_SYMBOL_PACK_V1") { "Unsupported symbol pack." }
        val array = root.getJSONArray("symbols")
        require(array.length() <= MAX_PACK_SYMBOLS) { "Symbol pack exceeds the 500-symbol limit." }
        val values = readPrivate().associateBy { it.id }.toMutableMap()
        val canonicalIds = canonical.map { it.id }.toSet()
        var count = 0
        for (i in 0 until array.length()) {
            val item = array.getJSONObject(i)
            val glyph = item.getString("glyph")
            val name = item.getString("name")
            val meaning = item.optString("meaning")
            require(name.isNotBlank() && name.length <= 80) { "Imported symbol name must contain 1–80 characters." }
            require(glyph.isNotBlank() && glyph.codePointCount(0, glyph.length) <= 8) { "Imported glyph is limited to eight Unicode code points." }
            require(meaning.length <= 500) { "Imported meaning is limited to 500 characters." }
            val suppliedId = item.optString("id")
            val id = if (suppliedId.startsWith("ORC-LOCAL-") && suppliedId !in canonicalIds) suppliedId
                     else "ORC-LOCAL-" + UUID.randomUUID().toString()
            values[id] = OrchidSymbol(id, name.trim(), glyph, meaning, "IMPORTED_PRIVATE")
            count++
        }
        savePrivate(values.values.toList())
        return count
    }

    fun exportPrivatePack(): String = JSONObject().apply {
        put("format", "ORCHID_SYMBOL_PACK_V1")
        put("visibility", "USER_SHARED_PRIVATE_PACK")
        put("symbols", JSONArray().apply { readPrivate().forEach { put(it.toJson()) } })
    }.toString(2)

    fun isFavorite(id: String): Boolean = favorites().contains(id)

    fun toggleFavorite(id: String): Boolean {
        val values = favorites().toMutableSet()
        val nowFavorite = if (values.contains(id)) { values.remove(id); false } else { values.add(id); true }
        keyboardPrefs.edit().putStringSet(KEY_FAVORITES, values).apply()
        return nowFavorite
    }

    fun favorites(): Set<String> = keyboardPrefs.getStringSet(KEY_FAVORITES, null)?.toSet() ?: DEFAULT_FAVORITES

    fun recordRecent(id: String) {
        val old = recent().filterNot { it == id }
        val next = (listOf(id) + old).take(MAX_RECENT)
        keyboardPrefs.edit().putString(KEY_RECENTS, JSONArray(next).toString()).apply()
    }

    fun recent(): List<String> = runCatching {
        val array = JSONArray(keyboardPrefs.getString(KEY_RECENTS, "[]"))
        (0 until array.length()).map { array.getString(it) }
    }.getOrDefault(emptyList())

    fun setting(key: String, default: String): String = keyboardPrefs.getString(key, default) ?: default
    fun setSetting(key: String, value: String) { keyboardPrefs.edit().putString(key, value).apply() }
    fun booleanSetting(key: String, default: Boolean): Boolean = keyboardPrefs.getBoolean(key, default)
    fun setBooleanSetting(key: String, value: Boolean) { keyboardPrefs.edit().putBoolean(key, value).apply() }

    private fun savePrivate(values: List<OrchidSymbol>) {
        prefs.edit().putString(KEY_PRIVATE, JSONArray().apply { values.forEach { put(it.toJson()) } }.toString()).apply()
    }

    private fun readPrivate(): List<OrchidSymbol> = runCatching {
        val array = JSONArray(prefs.getString(KEY_PRIVATE, "[]"))
        (0 until array.length()).map { array.getJSONObject(it).toSymbol() }
    }.getOrDefault(emptyList())

    private fun OrchidSymbol.toJson() = JSONObject().apply {
        put("id",id); put("name",name); put("glyph",glyph); put("meaning",meaning)
    }
    private fun JSONObject.toSymbol() = OrchidSymbol(getString("id"),getString("name"),getString("glyph"),optString("meaning"),optString("origin","IMPORTED_PRIVATE"))

    companion object {
        const val KEYBOARD_PREFS = "orchid_keyboard_preferences"
        const val KEY_HEIGHT = "key_height"
        const val KEY_THEME = "keyboard_theme"
        const val KEY_VIBRATION = "key_vibration"
        const val KEY_NUMBER_ROW = "number_row"
        private const val KEY_PRIVATE = "private_symbols_v1"
        private const val KEY_FAVORITES = "favorites_v1"
        private const val KEY_RECENTS = "recents_v1"
        private val DEFAULT_FAVORITES = setOf(
            "ORC-LAYER-STAR-001", "ORC-LAYER-STAR-002", "ORC-LAYER-STAR-003",
            "ORC-LAYER-STAR-004", "ORC-LAYER-STAR-005", "ORC-LAYER-STAR-006",
            "ORC-LAYER-STAR-007", "ORC-LAYER-STAR-008"
        )
        private const val MAX_RECENT = 24
        private const val MAX_PACK_CHARS = 256 * 1024
        private const val MAX_PACK_SYMBOLS = 500
    }
}
