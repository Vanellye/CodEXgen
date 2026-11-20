PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS dataset (
 dataset_id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
 source_uri TEXT NOT NULL, source_type TEXT NOT NULL, retrieved_at TEXT,
 content_sha256 TEXT, byte_length INTEGER, row_count INTEGER, grain TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('PENDING','INGESTED','VALIDATED','QUARANTINED')),
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS source_record (
 source_record_id TEXT PRIMARY KEY, dataset_id TEXT NOT NULL REFERENCES dataset(dataset_id),
 source_key TEXT NOT NULL, source_payload_json TEXT NOT NULL, payload_sha256 TEXT NOT NULL,
 observed_at TEXT, UNIQUE(dataset_id,source_key,payload_sha256)
);
CREATE TABLE IF NOT EXISTS metric_definition (
 metric_id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, description TEXT NOT NULL,
 expression TEXT NOT NULL, unit TEXT NOT NULL, numerator TEXT, denominator TEXT,
 grain TEXT NOT NULL, owner TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS analysis_run (
 analysis_id TEXT PRIMARY KEY, dataset_id TEXT NOT NULL REFERENCES dataset(dataset_id),
 title TEXT NOT NULL, query_spec_json TEXT NOT NULL, result_json TEXT NOT NULL,
 result_sha256 TEXT NOT NULL, started_at TEXT NOT NULL, completed_at TEXT NOT NULL,
 analyst TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('SUCCEEDED','FAILED','NEEDS_DATA'))
);
CREATE TABLE IF NOT EXISTS revision_event (
 revision_id TEXT PRIMARY KEY, object_type TEXT NOT NULL, object_id TEXT NOT NULL,
 previous_revision_id TEXT, operation TEXT NOT NULL, content_sha256 TEXT NOT NULL,
 actor TEXT NOT NULL, reason TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS evidence_event (
 evidence_id TEXT PRIMARY KEY, subject_type TEXT NOT NULL, subject_id TEXT NOT NULL,
 evidence_uri TEXT NOT NULL, evidence_kind TEXT NOT NULL, content_sha256 TEXT,
 source_title TEXT, publisher TEXT, published_at TEXT, retrieved_at TEXT NOT NULL,
 notes TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS approval_event (
 approval_id TEXT PRIMARY KEY, subject_type TEXT NOT NULL, subject_id TEXT NOT NULL,
 reviewer_login TEXT NOT NULL, reviewer_identity_verified INTEGER NOT NULL CHECK(reviewer_identity_verified IN (0,1)),
 signature_verified INTEGER NOT NULL CHECK(signature_verified IN (0,1)), scope TEXT NOT NULL,
 decision TEXT NOT NULL CHECK(decision IN ('APPROVE','REJECT')), issued_at TEXT NOT NULL,
 expires_at TEXT NOT NULL, revoked INTEGER NOT NULL DEFAULT 0 CHECK(revoked IN (0,1)), signature_ref TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS source_record_no_update BEFORE UPDATE ON source_record BEGIN SELECT RAISE(ABORT,'source_record is append-only'); END;
CREATE TRIGGER IF NOT EXISTS source_record_no_delete BEFORE DELETE ON source_record BEGIN SELECT RAISE(ABORT,'source_record is append-only'); END;
CREATE TRIGGER IF NOT EXISTS revision_event_no_update BEFORE UPDATE ON revision_event BEGIN SELECT RAISE(ABORT,'revision_event is append-only'); END;
CREATE TRIGGER IF NOT EXISTS revision_event_no_delete BEFORE DELETE ON revision_event BEGIN SELECT RAISE(ABORT,'revision_event is append-only'); END;
CREATE TRIGGER IF NOT EXISTS evidence_event_no_update BEFORE UPDATE ON evidence_event BEGIN SELECT RAISE(ABORT,'evidence_event is append-only'); END;
CREATE TRIGGER IF NOT EXISTS evidence_event_no_delete BEFORE DELETE ON evidence_event BEGIN SELECT RAISE(ABORT,'evidence_event is append-only'); END;
CREATE TRIGGER IF NOT EXISTS approval_event_no_update BEFORE UPDATE ON approval_event BEGIN SELECT RAISE(ABORT,'approval_event is append-only'); END;
CREATE TRIGGER IF NOT EXISTS approval_event_no_delete BEFORE DELETE ON approval_event BEGIN SELECT RAISE(ABORT,'approval_event is append-only'); END;
CREATE VIEW IF NOT EXISTS v_dataset_summary AS SELECT dataset_id,title,source_uri,source_type,row_count,grain,status,content_sha256,retrieved_at FROM dataset;
