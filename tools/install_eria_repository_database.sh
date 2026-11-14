#!/usr/bin/env bash
set -euo pipefail

DB_DIR="${ERIA_DB_DIR:-${HOME}/.eria/data}"
DB_PATH="${ERIA_DB_PATH:-${DB_DIR}/eria_conversation.sqlite3}"

if ! command -v sqlite3 >/dev/null 2>&1; then
  printf '%s\n' "ERROR: sqlite3 is required. Install it in Termux with: pkg install sqlite"
  exit 1
fi

mkdir -p "$DB_DIR"

BACKUP_PATH=""
if [[ -s "$DB_PATH" ]]; then
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  BACKUP_PATH="${DB_PATH}.preinstall.${stamp}.bak"
  sqlite3 "$DB_PATH" ".backup '$BACKUP_PATH'"
  printf 'Existing database backed up to: %s\n' "$BACKUP_PATH"
fi

sqlite3 "$DB_PATH" <<'SQL'
.bail on
PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

CREATE TABLE IF NOT EXISTS schema_metadata (
    metadata_key TEXT PRIMARY KEY NOT NULL,
    metadata_value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversation_history (
    entry_id TEXT PRIMARY KEY NOT NULL,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('system', 'user', 'assistant', 'tool')),
    content TEXT NOT NULL,
    source_ref TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversation_history_conversation_time
    ON conversation_history (conversation_id, created_at);

CREATE TABLE IF NOT EXISTS repository_file_index (
    repository_path TEXT PRIMARY KEY NOT NULL,
    blob_sha TEXT NOT NULL DEFAULT '',
    commit_sha TEXT NOT NULL DEFAULT '',
    byte_size INTEGER NOT NULL DEFAULT 0 CHECK (byte_size >= 0),
    indexed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS file_metadata (
    repository_path TEXT PRIMARY KEY NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS index_runs (
    run_id TEXT PRIMARY KEY NOT NULL,
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED')),
    source_commit TEXT NOT NULL DEFAULT '',
    files_indexed INTEGER NOT NULL DEFAULT 0 CHECK (files_indexed >= 0)
);

CREATE TABLE IF NOT EXISTS migration_events (
    event_id TEXT PRIMARY KEY NOT NULL,
    migration_name TEXT NOT NULL,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details_json TEXT NOT NULL DEFAULT '{}'
);

INSERT OR IGNORE INTO schema_metadata (metadata_key, metadata_value)
VALUES ('database_name', 'ERIA repository conversation and file index');

INSERT OR IGNORE INTO schema_metadata (metadata_key, metadata_value)
VALUES ('schema_version', '1');

INSERT OR IGNORE INTO migration_events (event_id, migration_name, details_json)
VALUES (
    'eria-repository-db-v1',
    'initialize_repository_database_v1',
    '{"preserves_existing_rows":true,"classification_columns_added":false,"historical_archive_required_for_future_cleanup":true}'
);

PRAGMA user_version = 1;
COMMIT;
SQL

CHECK_RESULT="$(sqlite3 "$DB_PATH" 'PRAGMA integrity_check;')"
if [[ "$CHECK_RESULT" != "ok" ]]; then
  printf 'ERROR: database integrity check failed: %s\n' "$CHECK_RESULT" >&2
  exit 1
fi

printf 'ERIA repository database installed and integrity-checked.\n'
printf 'Database: %s\n' "$DB_PATH"
if [[ -n "$BACKUP_PATH" ]]; then
  printf 'Backup: %s\n' "$BACKUP_PATH"
fi
printf 'Schema version: %s\n' "$(sqlite3 "$DB_PATH" 'PRAGMA user_version;')"
