package com.vanellye.codexgen.dataresonance

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

data class ResonanceObservation(
    val id: Long,
    val channel: String,
    val timestampMs: Long,
    val value: Double,
    val unit: String,
    val biomarker: String?,
    val referenceFrequencyHz: Double?,
    val notes: String?
)

/** Local app-private SQLite store. Frequency values are annotations, not treatment controls. */
class DataResonanceStore(context: Context) :
    SQLiteOpenHelper(context.applicationContext, "data_resonance.db", null, 1) {

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL(
            """CREATE TABLE observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel TEXT NOT NULL,
                timestamp_ms INTEGER NOT NULL,
                sample_value REAL NOT NULL,
                unit TEXT NOT NULL DEFAULT '',
                biomarker TEXT,
                reference_frequency_hz REAL,
                notes TEXT
            )""".trimIndent()
        )
        db.execSQL("CREATE INDEX observations_channel_time ON observations(channel, timestamp_ms)")
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) = Unit

    fun add(
        channel: String,
        value: Double,
        unit: String,
        biomarker: String?,
        frequencyHz: Double?,
        notes: String?
    ): Long {
        require(channel.isNotBlank()) { "Channel is required." }
        require(value.isFinite()) { "Sample value must be finite." }
        require(frequencyHz == null || (frequencyHz.isFinite() && frequencyHz > 0.0)) {
            "Reference frequency must be a positive finite number in Hz."
        }
        val values = ContentValues().apply {
            put("channel", channel.trim())
            put("timestamp_ms", System.currentTimeMillis())
            put("sample_value", value)
            put("unit", unit.trim())
            put("biomarker", biomarker?.trim()?.takeIf { it.isNotEmpty() })
            if (frequencyHz == null) putNull("reference_frequency_hz")
            else put("reference_frequency_hz", frequencyHz)
            put("notes", notes?.trim()?.takeIf { it.isNotEmpty() })
        }
        return writableDatabase.insertOrThrow("observations", null, values)
    }

    fun recent(limit: Int = 100): List<ResonanceObservation> {
        val rows = mutableListOf<ResonanceObservation>()
        readableDatabase.query(
            "observations",
            arrayOf("id", "channel", "timestamp_ms", "sample_value", "unit", "biomarker", "reference_frequency_hz", "notes"),
            null, null, null, null, "timestamp_ms DESC", limit.coerceIn(1, 500).toString()
        ).use { cursor ->
            while (cursor.moveToNext()) {
                rows += ResonanceObservation(
                    id = cursor.getLong(0),
                    channel = cursor.getString(1),
                    timestampMs = cursor.getLong(2),
                    value = cursor.getDouble(3),
                    unit = cursor.getString(4),
                    biomarker = if (cursor.isNull(5)) null else cursor.getString(5),
                    referenceFrequencyHz = if (cursor.isNull(6)) null else cursor.getDouble(6),
                    notes = if (cursor.isNull(7)) null else cursor.getString(7)
                )
            }
        }
        return rows
    }

    /** Exploratory Pearson r over chronological sample order; not a causal or clinical result. */
    fun correlation(channelA: String, channelB: String): Pair<Int, Double?> {
        val a = valuesFor(channelA)
        val b = valuesFor(channelB)
        val n = minOf(a.size, b.size)
        if (n < 2) return n to null
        val x = a.takeLast(n)
        val y = b.takeLast(n)
        val meanX = x.average()
        val meanY = y.average()
        val numerator = x.indices.sumOf { (x[it] - meanX) * (y[it] - meanY) }
        val sumX = x.sumOf { (it - meanX) * (it - meanX) }
        val sumY = y.sumOf { (it - meanY) * (it - meanY) }
        val denominator = kotlin.math.sqrt(sumX * sumY)
        return n to if (denominator == 0.0) null else numerator / denominator
    }

    private fun valuesFor(channel: String): List<Double> {
        val values = mutableListOf<Double>()
        readableDatabase.query(
            "observations",
            arrayOf("sample_value"),
            "channel = ?",
            arrayOf(channel.trim()),
            null, null, "timestamp_ms ASC"
        ).use { cursor ->
            while (cursor.moveToNext()) values += cursor.getDouble(0)
        }
        return values
    }
}
