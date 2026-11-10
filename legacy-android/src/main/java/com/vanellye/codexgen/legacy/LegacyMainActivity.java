package com.vanellye.codexgen.legacy;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.content.Context;

/**
 * API 11-compatible native-Views shell. No Compose, AndroidX, Kotlin runtime,
 * coroutines, or Android Keystore dependency is used by this module.
 */
public final class LegacyMainActivity extends Activity {
    private TextView status;
    private EditText note;
    private LegacyStore store;

    static {
        try { System.loadLibrary("codexgen_legacy"); }
        catch (Throwable ignored) { }
    }

    private native String nativeStatus();

    @Override
    public void onCreate(Bundle state) {
        super.onCreate(state);
        store = new LegacyStore(this);
        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        int pad = dp(16);
        root.setPadding(pad, pad, pad, pad);
        scroll.addView(root);

        TextView heading = new TextView(this);
        heading.setText("CodEXgen • Legacy Android");
        heading.setTextSize(24);
        root.addView(heading);

        TextView compatibility = new TextView(this);
        compatibility.setText("API 11 baseline • Native Android Views • Local-first storage");
        root.addView(compatibility);

        status = new TextView(this);
        status.setText("Native bridge: " + nativeStatusSafe());
        root.addView(status);

        note = new EditText(this);
        note.setHint("Record a local Data Resonance observation");
        root.addView(note);

        Button save = new Button(this);
        save.setText("Save local observation");
        root.addView(save);
        save.setOnClickListener(new View.OnClickListener() {
            public void onClick(View view) {
                String value = note.getText().toString().trim();
                if (value.length() == 0) {
                    status.setText("Enter an observation first.");
                    return;
                }
                long id = store.add(value);
                note.setText("");
                status.setText("Saved locally. Observation #" + id);
            }
        });

        Button history = new Button(this);
        history.setText("Show recent observations");
        root.addView(history);
        history.setOnClickListener(new View.OnClickListener() {
            public void onClick(View view) {
                status.setText(store.recent());
            }
        });

        TextView limitations = new TextView(this);
        limitations.setText("\nLegacy profile intentionally avoids modern AndroidX APIs. Git operations requiring JGit and secure token storage are not enabled in this API 11 profile yet. Do not enter access tokens into this build.");
        root.addView(limitations);
        setContentView(scroll);
    }

    private String nativeStatusSafe() {
        try { return nativeStatus(); }
        catch (Throwable error) { return "unavailable: " + error.getClass().getSimpleName(); }
    }

    private int dp(int value) {
        return (int)(value * getResources().getDisplayMetrics().density + 0.5f);
    }

    private static final class LegacyStore extends SQLiteOpenHelper {
        LegacyStore(Context context) { super(context, "codexgen_legacy.db", null, 1); }
        public void onCreate(SQLiteDatabase db) {
            db.execSQL("CREATE TABLE observations (id INTEGER PRIMARY KEY AUTOINCREMENT, note TEXT NOT NULL, created_ms INTEGER NOT NULL)");
        }
        public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) { }
        long add(String value) {
            android.content.ContentValues row = new android.content.ContentValues();
            row.put("note", value);
            row.put("created_ms", System.currentTimeMillis());
            return getWritableDatabase().insertOrThrow("observations", null, row);
        }
        String recent() {
            StringBuilder out = new StringBuilder("Recent local observations:\n");
            android.database.Cursor cursor = getReadableDatabase().rawQuery(
                "SELECT id, note FROM observations ORDER BY id DESC LIMIT 30", null);
            try {
                while (cursor.moveToNext()) {
                    out.append("#").append(cursor.getLong(0)).append("  ")
                       .append(cursor.getString(1)).append("\n");
                }
            } finally { cursor.close(); }
            return out.toString();
        }
    }
}
