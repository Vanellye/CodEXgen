package com.vanellye.codexgen.consent;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

/** Local audit trail; avoid sensitive details in the short purpose summary. */
public final class ConsentReviewStore extends SQLiteOpenHelper {
    public ConsentReviewStore(Context context) {
        super(context.getApplicationContext(), "stride_consent_review.db", null, 1);
    }
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE consent_reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at INTEGER NOT NULL, outcome TEXT NOT NULL, layer_flags TEXT NOT NULL, reviewer TEXT NOT NULL, purpose_summary TEXT NOT NULL)");
    }
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) { }
    public long record(String outcome, boolean[] layers, String reviewer, String purpose) {
        if (!"ASSENTED".equals(outcome) && !"DECLINED".equals(outcome) && !"PAUSED".equals(outcome))
            throw new IllegalArgumentException("Invalid review outcome.");
        if (layers == null || layers.length != 7) throw new IllegalArgumentException("Exactly seven layer flags are required.");
        String safeReviewer = reviewer == null ? "" : reviewer.trim();
        String safePurpose = purpose == null ? "" : purpose.trim();
        if (safeReviewer.length() > 120) throw new IllegalArgumentException("Reviewer field is limited to 120 characters.");
        if (safePurpose.length() > 500) throw new IllegalArgumentException("Purpose summary is limited to 500 characters.");
        ContentValues values = new ContentValues();
        values.put("created_at", Long.valueOf(System.currentTimeMillis()));
        values.put("outcome", outcome);
        StringBuilder flags = new StringBuilder();
        for (int i = 0; i < layers.length; i++) flags.append(layers[i] ? '1' : '0');
        values.put("layer_flags", flags.toString());
        values.put("reviewer", reviewer == null ? "" : reviewer.trim());
        values.put("purpose_summary", purpose == null ? "" : purpose.trim());
        return getWritableDatabase().insertOrThrow("consent_reviews", null, values);
    }
    public String recent(int limit) {
        StringBuilder out = new StringBuilder("Local review history (newest first)\n");
        Cursor c = getReadableDatabase().query("consent_reviews",
            new String[]{"id","created_at","outcome","layer_flags","reviewer","purpose_summary"},
            null,null,null,null,"created_at DESC",String.valueOf(Math.max(1,Math.min(100,limit))));
        try {
            while (c.moveToNext()) {
                out.append("#").append(c.getLong(0)).append(" • ").append(c.getString(2))
                    .append(" • ").append(c.getLong(1)).append("\nLayers: ").append(c.getString(3))
                    .append("\nHuman reviewer: ").append(c.getString(4))
                    .append("\nPurpose: ").append(c.getString(5)).append("\n\n");
            }
        } finally { c.close(); }
        return out.toString();
    }
}
