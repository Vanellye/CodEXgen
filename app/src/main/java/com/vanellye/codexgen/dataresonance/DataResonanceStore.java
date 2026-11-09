package com.vanellye.codexgen.dataresonance;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

/** App-private SQLite notebook. Frequency and biomarker fields are annotations only. */
public final class DataResonanceStore extends SQLiteOpenHelper {
    public DataResonanceStore(Context context) {
        super(context.getApplicationContext(), "data_resonance.db", null, 1);
    }
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE observations (id INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT NOT NULL, timestamp_ms INTEGER NOT NULL, sample_value REAL NOT NULL, unit TEXT NOT NULL DEFAULT '', biomarker TEXT, reference_frequency_hz REAL, notes TEXT)");
        db.execSQL("CREATE INDEX observations_channel_time ON observations(channel, timestamp_ms)");
    }
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) { }
    public long add(String channel, double value, String unit, String biomarker, Double frequencyHz, String notes) {
        if (channel == null || channel.trim().length() == 0) throw new IllegalArgumentException("Channel is required.");
        if (Double.isNaN(value) || Double.isInfinite(value)) throw new IllegalArgumentException("Value must be finite.");
        if (frequencyHz != null && (Double.isNaN(frequencyHz.doubleValue()) || Double.isInfinite(frequencyHz.doubleValue()) || frequencyHz.doubleValue() <= 0))
            throw new IllegalArgumentException("Frequency must be positive and finite.");
        ContentValues v = new ContentValues();
        v.put("channel", channel.trim()); v.put("timestamp_ms", Long.valueOf(System.currentTimeMillis()));
        v.put("sample_value", Double.valueOf(value)); v.put("unit", unit == null ? "" : unit.trim());
        if (biomarker == null || biomarker.trim().length() == 0) v.putNull("biomarker"); else v.put("biomarker", biomarker.trim());
        if (frequencyHz == null) v.putNull("reference_frequency_hz"); else v.put("reference_frequency_hz", frequencyHz);
        if (notes == null || notes.trim().length() == 0) v.putNull("notes"); else v.put("notes", notes.trim());
        return getWritableDatabase().insertOrThrow("observations", null, v);
    }
    public String recent(int limit) {
        StringBuilder out = new StringBuilder();
        Cursor c = getReadableDatabase().query("observations",
            new String[]{"id","channel","timestamp_ms","sample_value","unit","biomarker","reference_frequency_hz","notes"},
            null,null,null,null,"timestamp_ms DESC",String.valueOf(Math.max(1,Math.min(500,limit))));
        try {
            while (c.moveToNext()) {
                out.append("#").append(c.getLong(0)).append("  ")
                    .append(c.getString(1)).append(" = ").append(c.getDouble(3))
                    .append(" ").append(c.getString(4)).append(" @ ").append(c.getLong(2));
                if (!c.isNull(5)) out.append(" • biomarker ").append(c.getString(5));
                if (!c.isNull(6)) out.append(" • reference ").append(c.getDouble(6)).append(" Hz");
                if (!c.isNull(7)) out.append(" • ").append(c.getString(7));
                out.append("\n");
            }
        } finally { c.close(); }
        return out.toString();
    }
    public int count() {
        Cursor c = getReadableDatabase().rawQuery("SELECT COUNT(*) FROM observations", null);
        try { return c.moveToFirst() ? c.getInt(0) : 0; }
        finally { c.close(); }
    }
}
