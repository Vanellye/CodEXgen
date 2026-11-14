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


## Unified repository dashboard

The same local server serves the browser dashboard and the native Android Jetpack Compose dashboard:

- Browser UI: `http://127.0.0.1:8765/repository`
- Status: `GET /api/status`
- PONS policy: `GET /api/pons/status`
- Authorization review queue: `GET /api/pons/requests`
- Create a review proposal: `POST /api/pons/requests`
- Indexed paths: `GET /api/files?q=...`
- Safe text preview: `GET /api/files/detail?path=...`
- Source provenance: `GET /api/provenance?q=...`
- Local audit history: `GET /api/audit`
- Refresh metadata and source hashes: `POST /api/index` with an empty JSON object

The Android app and browser UI expose five matching areas: Overview, Files, Provenance, Audit, and PONS. The native app polls the local service while the dashboard is open. Start the Termux server first, then open ERIA on the same device.

### Provenance and audit behavior

- The index stores file paths, extensions, sizes, timestamps, and SHA-256 for eligible files up to 5 MiB. A blank hash means it was not computed.
- Hashes describe bytes at the last index refresh; refresh after modifying source files.
- The detail endpoint uses the repository engine's path containment checks, text/binary checks, size limit, and secret-value redaction. It returns a bounded preview, not an editable file.
- SQLite audit events are append-only: database triggers reject update and delete operations.
- Authorization review requests are durable proposals with status `HOLD`. Creating a request never creates a grant or enables a capability.
- This service does not create derived content. Any future transform must preserve source identity and source hash and record a separate derived hash.

### Boundaries

The dashboard is an inspection and proposal surface. It does not create or cryptographically verify grants, approve protected execution, mutate Git, or transmit repository contents. PONS remains an application-level policy gate, not an OS sandbox or identity provider. Keep the server bound to loopback. SQLite stores metadata, audit events, authorization proposals, and chat history, not authoritative source-file contents.
