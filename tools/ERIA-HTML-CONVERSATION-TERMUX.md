# ERIA HTML Conversation — Termux

This local web interface connects the existing repository conversation engine,
PONS adapter, code-bypass module, and a SQLite metadata/history database.

## Start

From the repository checkout in Termux:

```sh
cd "$HOME/ERIA-MASTER"
python tools/eria_conversation_server.py . --port 8765
```

Open this address in the Android browser:

```
http://127.0.0.1:8765
```

Stop the server with `Ctrl+C` in Termux.

## Storage

The default SQLite database is:

```
~/.eria/data/eria_conversation.sqlite3
```

It stores conversation messages and a refreshable repository path/metadata
index. It does not copy source file contents into SQLite. The database is
outside the Git checkout by default.

## Included features

- Chat with the existing `eria_repository_conversation.py` engine.
- Integration status through `integration.status`.
- Indexed repository path search.
- Refresh repository file metadata index.
- Persist chat history by browser session.
- Connect to the PONS adapter when the package is installed.

## Boundaries

- Binds only to loopback (127.0.0.1 / localhost / ::1).
- No arbitrary SQL, shell, or file-write API is exposed.
- Repository questions use the existing read-only Git allowlist.
- The code bypass is explicit and writes an audit record outside the repository.
- The bypass skips translation and outbound transmission; it is not a privilege
  escalation or security-control bypass.
- No Git history rewrite, push, merge, branch mutation, or remote transmission.
- SQLite is a local convenience database, not an authoritative source of truth.
- Source and derived representations retain separate hashes and non-authoritative
  status in the PONS envelope.

Python 3 standard library only; no pip installation is required.


## Repository dashboard

The same local server also serves the repository dashboard:

- Browser UI: `http://127.0.0.1:8765/repository`
- Status API: `GET /api/status`
- PONS policy: `GET /api/pons/status`
- Indexed paths: `GET /api/files?q=...`
- Refresh metadata index: `POST /api/index` with an empty JSON object

The Android app's native Jetpack Compose repository screen uses the same loopback API at `127.0.0.1:8765`. Start the Termux server first, then open ERIA on the same device.

The dashboard is an inspection surface. PONS status is informational; this UI does not create or cryptographically verify grants and does not authorize protected execution. Keep the server bound to loopback. SQLite stores chat history and repository file metadata, not source-file contents.
