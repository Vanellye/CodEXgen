# ERIA Repository Database

## Location

The local SQLite database is stored outside the Git checkout by default:

`~/.eria/data/eria_conversation.sqlite3`

This is a local conversation/file-index database. It is not a replacement for Git history and is not committed to the repository.

## Install in Termux

From the CodEXgen checkout:

```bash
pkg install git sqlite
git checkout integration/pons-runtime-main
git pull --ff-only origin integration/pons-runtime-main
bash tools/install_eria_repository_database.sh
```

The installer creates the parent directory, initializes schema version 1, and runs SQLite's integrity check. If a database already exists, it first creates a SQLite-consistent backup beside the original file. It uses create-if-absent operations and does not drop tables or delete rows.

Optional custom location:

```bash
ERIA_DB_PATH="$HOME/.eria/custom/eria.sqlite3" bash tools/install_eria_repository_database.sh
```

## Schema

- `conversation_history`: conversation entries, role, source reference, timestamp.
- `repository_file_index`: repository-relative path, Git blob/commit references, byte size, index time.
- `file_metadata`: JSON metadata keyed by repository-relative path.
- `index_runs`: index-run status and source commit.
- `schema_metadata`: database identity and schema version.
- `migration_events`: append-oriented migration initialization record.

The schema does not define NEG, NULL, or VOID evidence classifications. It does not redefine ordinary programming-language null/pointer semantics or erase missing/unknown data. It does not automatically import repository files or conversation content.

## Evidence and migration boundary

Installing this schema is not the same as cleaning an existing database. No user rows are deleted or rewritten. A cleanup migration must first inspect the actual database schema, identify exact classification values and affected rows, export those original rows with provenance and hashes to a separate archive, then apply a reviewed transactional migration and verify the result. Unknown table layouts are not guessed.

The database remains local and outside Git. Do not commit the live database or its backups.
