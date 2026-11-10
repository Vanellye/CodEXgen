package com.vanellye.codexgen.jobs;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/** App-private local JOB storage. Export/import is explicit and never overwrites IDs. */
public final class JobStore extends SQLiteOpenHelper {
    private static final String DB_NAME = "stride_jobs.db";
    private static final int DB_VERSION = 1;
    public JobStore(Context context) { super(context, DB_NAME, null, DB_VERSION); }

    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE jobs (id TEXT PRIMARY KEY, title TEXT NOT NULL, purpose TEXT NOT NULL, state TEXT NOT NULL, stage TEXT NOT NULL, parent_id TEXT, created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL)");
        db.execSQL("CREATE TABLE events (id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL, event_type TEXT NOT NULL, detail TEXT, created_at INTEGER NOT NULL)");
        db.execSQL("CREATE INDEX events_job_idx ON events(job_id,id)");
    }
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        // Versioned migrations are intentionally explicit; never drop user JOB data.
        throw new IllegalStateException("No migration path from JOB database version " + oldVersion);
    }
    private boolean contains(SQLiteDatabase db, String table, String id) {
        Cursor c = db.query(table, new String[]{"id"}, "id=?", new String[]{id}, null, null, null);
        try { return c.moveToFirst(); } finally { c.close(); }
    }
    private void event(SQLiteDatabase db, String id, String type, String detail) {
        ContentValues v = new ContentValues();
        v.put("job_id", id); v.put("event_type", type); v.put("detail", detail);
        v.put("created_at", System.currentTimeMillis()); db.insertOrThrow("events", null, v);
    }
    public synchronized String create(String title, String purpose, String parentId) {
        if (title == null || title.trim().length() == 0 || purpose == null || purpose.trim().length() == 0)
            throw new IllegalArgumentException("Title and purpose are required.");
        SQLiteDatabase db = getWritableDatabase(); db.beginTransaction();
        String id = java.util.UUID.randomUUID().toString(); long now = System.currentTimeMillis();
        try {
            if (parentId != null && !contains(db, "jobs", parentId))
                throw new IllegalArgumentException("Parent JOB not found.");
            ContentValues v = new ContentValues(); v.put("id", id); v.put("title", title.trim());
            v.put("purpose", purpose.trim()); v.put("state", "open"); v.put("stage", "notice");
            v.put("parent_id", parentId); v.put("created_at", now); v.put("updated_at", now);
            db.insertOrThrow("jobs", null, v); event(db, id, "created", "parent=" + parentId);
            db.setTransactionSuccessful();
        } finally { db.endTransaction(); }
        return id;
    }
    public synchronized boolean transition(String id, String state) {
        if (!("active".equals(state) || "paused".equals(state) || "completed".equals(state) || "archived".equals(state)))
            throw new IllegalArgumentException("Unsupported dashboard transition.");
        SQLiteDatabase db = getWritableDatabase(); db.beginTransaction();
        try {
            Cursor c = db.query("jobs", new String[]{"state"}, "id=?", new String[]{id}, null, null, null);
            if (!c.moveToFirst()) { c.close(); return false; }
            String old = c.getString(0); c.close();
            boolean allowed = ("open".equals(old) && ("active".equals(state)||"paused".equals(state)||"completed".equals(state)||"archived".equals(state)))
                || ("active".equals(old) && ("paused".equals(state)||"completed".equals(state)))
                || ("paused".equals(old) && ("active".equals(state)||"completed".equals(state)||"archived".equals(state)))
                || ("completed".equals(old) && "active".equals(state));
            if (!allowed) return false;
            ContentValues v = new ContentValues(); v.put("state", state); v.put("updated_at", System.currentTimeMillis());
            db.update("jobs", v, "id=?", new String[]{id}); event(db, id, "transition", old + " -> " + state);
            db.setTransactionSuccessful(); return true;
        } finally { db.endTransaction(); }
    }
    public synchronized JSONArray list() throws JSONException {
        JSONArray out = new JSONArray(); SQLiteDatabase db = getReadableDatabase();
        Cursor c = db.query("jobs", null, null, null, null, null, "updated_at DESC");
        try { while (c.moveToNext()) {
            JSONObject o = new JSONObject(); o.put("id", c.getString(c.getColumnIndexOrThrow("id")));
            o.put("title", c.getString(c.getColumnIndexOrThrow("title")));
            o.put("purpose", c.getString(c.getColumnIndexOrThrow("purpose")));
            o.put("state", c.getString(c.getColumnIndexOrThrow("state")));
            o.put("stage", c.getString(c.getColumnIndexOrThrow("stage")));
            o.put("parent_id", c.isNull(c.getColumnIndexOrThrow("parent_id")) ? JSONObject.NULL : c.getString(c.getColumnIndexOrThrow("parent_id")));
            o.put("created_at", c.getLong(c.getColumnIndexOrThrow("created_at")));
            o.put("updated_at", c.getLong(c.getColumnIndexOrThrow("updated_at"))); out.put(o);
        }} finally { c.close(); } return out;
    }
    public synchronized String exportJson() throws JSONException {
        JSONObject root = new JSONObject(); root.put("schema", "codexgen.android.jobs.v1");
        root.put("exported_at", System.currentTimeMillis()); root.put("jobs", list());
        JSONArray events = new JSONArray(); Cursor c = getReadableDatabase().query("events", null, null, null, null, null, "id ASC");
        try { while (c.moveToNext()) {
            JSONObject e = new JSONObject(); e.put("job_id", c.getString(c.getColumnIndexOrThrow("job_id")));
            e.put("event_type", c.getString(c.getColumnIndexOrThrow("event_type")));
            e.put("detail", c.getString(c.getColumnIndexOrThrow("detail")));
            e.put("created_at", c.getLong(c.getColumnIndexOrThrow("created_at"))); events.put(e);
        }} finally { c.close(); }
        root.put("events", events); return root.toString(2);
    }

    /** Export one JOB and its events for a first-time, non-overwriting Python bridge import. */
    public synchronized String exportJobJson(String id) throws JSONException {
        SQLiteDatabase db=getReadableDatabase();
        Cursor c=db.query("jobs",null,"id=?",new String[]{id},null,null,null);
        JSONObject job;
        try {
            if(!c.moveToFirst()) throw new JSONException("JOB not found.");
            job=new JSONObject();
            job.put("id",c.getString(c.getColumnIndexOrThrow("id")));
            job.put("title",c.getString(c.getColumnIndexOrThrow("title")));
            job.put("purpose",c.getString(c.getColumnIndexOrThrow("purpose")));
            job.put("state",c.getString(c.getColumnIndexOrThrow("state")));
            job.put("stage",c.getString(c.getColumnIndexOrThrow("stage")));
            int parent=c.getColumnIndexOrThrow("parent_id");
            job.put("parent_id",c.isNull(parent)?JSONObject.NULL:c.getString(parent));
            job.put("created_at",c.getLong(c.getColumnIndexOrThrow("created_at")));
            job.put("updated_at",c.getLong(c.getColumnIndexOrThrow("updated_at")));
        } finally { c.close(); }
        JSONArray jobs=new JSONArray(); jobs.put(job);
        JSONArray events=new JSONArray();
        Cursor e=db.query("events",null,"job_id=?",new String[]{id},null,null,"id ASC");
        try { while(e.moveToNext()) {
            JSONObject item=new JSONObject();
            item.put("job_id",e.getString(e.getColumnIndexOrThrow("job_id")));
            item.put("event_type",e.getString(e.getColumnIndexOrThrow("event_type")));
            item.put("detail",e.getString(e.getColumnIndexOrThrow("detail")));
            item.put("created_at",e.getLong(e.getColumnIndexOrThrow("created_at")));
            events.put(item);
        }} finally { e.close(); }
        JSONObject root=new JSONObject(); root.put("schema","codexgen.android.jobs.v1");
        root.put("exported_at",System.currentTimeMillis()); root.put("jobs",jobs); root.put("events",events);
        return root.toString();
    }

    public synchronized int importJson(String raw) throws JSONException {
        JSONObject root = new JSONObject(raw);
        if (!"codexgen.android.jobs.v1".equals(root.optString("schema"))) throw new JSONException("Unsupported JOB export.");
        JSONArray jobs = root.getJSONArray("jobs"), events = root.optJSONArray("events");
        SQLiteDatabase db = getWritableDatabase(); db.beginTransaction(); int count = 0;
        try {
            for (int i=0;i<jobs.length();i++) {
                JSONObject o = jobs.getJSONObject(i); String id = o.getString("id");
                if (contains(db, "jobs", id))
                    throw new JSONException("JOB already exists; import will not overwrite " + id);
                String state = o.optString("state","open"), stage = o.optString("stage","notice");
                if (!("open".equals(state)||"active".equals(state)||"paused".equals(state)||"blocked".equals(state)||"adapted".equals(state)||"completed".equals(state)||"archived".equals(state)))
                    throw new JSONException("Invalid JOB state.");
                ContentValues v = new ContentValues(); v.put("id",id); v.put("title",o.getString("title"));
                v.put("purpose",o.getString("purpose")); v.put("state",state); v.put("stage",stage);
                if (!o.isNull("parent_id")) v.put("parent_id",o.getString("parent_id"));
                v.put("created_at",o.optLong("created_at",System.currentTimeMillis()));
                v.put("updated_at",o.optLong("updated_at",System.currentTimeMillis()));
                db.insertOrThrow("jobs",null,v); count++;
            }
            if (events != null) for (int i=0;i<events.length();i++) {
                JSONObject e=events.getJSONObject(i);
                if (!contains(db,"jobs",e.getString("job_id"))) continue;
                ContentValues v=new ContentValues();v.put("job_id",e.getString("job_id"));
                v.put("event_type",e.getString("event_type"));v.put("detail",e.optString("detail",""));
                v.put("created_at",e.optLong("created_at",System.currentTimeMillis()));db.insert("events",null,v);
            }
            db.setTransactionSuccessful();
        } finally { db.endTransaction(); } return count;
    }
}
