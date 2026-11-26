package com.vanellye.eria.orchid

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.util.UUID

data class OrchidSymbol(val id: String, val name: String, val glyph: String, val meaning: String, val origin: String = "ORCHID_CHRONOGLYPH_02")

class SymbolRegistry(context: Context) {
    private val prefs = context.getSharedPreferences("orchid_private_symbols", Context.MODE_PRIVATE)
    private val canonical = listOf(
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
        val values = readPrivate().filterNot { it.id == symbol.id } + symbol
        savePrivate(values)
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
        private const val KEY_PRIVATE = "private_symbols_v1"
        private const val MAX_PACK_CHARS = 256 * 1024
        private const val MAX_PACK_SYMBOLS = 500
    }
}
