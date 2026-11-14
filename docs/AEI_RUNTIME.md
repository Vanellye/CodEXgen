# ERIA Æị Runtime

Æị is the evidence-grounded interpretation and conversation layer inside ERIA.
It is implemented as three cooperating parts:

- `eria_database_translator.py`: reads files through ordinary filesystem paths,
  identifies supported formats, builds a canonical envelope, and writes a
  separate derived export plus a SHA-256 manifest.
- `eria_aei_conversation.py`: deterministic conversational orchestration over
  the read-only repository inspector and the ERIA SQLite adapter.
- `eria_aei_interface.py` + `eria_aei_interface.html`: loopback-only browser
  console and JSON API.

## Safety and evidence contract

1. Source files are never edited or deleted by the translator.
2. Existing output paths are rejected; exports are new derived files.
3. Every translation records the source path, source SHA-256, source format,
   output path, output SHA-256, and translator version.
4. SQLite sources are opened with `mode=ro` and `PRAGMA query_only=ON`.
   Normal read-only SQLite mode is intentional: it can see committed WAL
   frames. Do not substitute SQLite's `immutable=1` mode for live databases.
5. SQLite table exports currently read at most 100,000 rows per table.
   The envelope includes `row_count`, `rows_limit`, and `truncated`; a
   truncated table must not be treated as a complete export.
6. Unknown binary files are retained as base64 opaque payloads. No encoding
   guess or lossy conversion is attempted.
7. Repository conversation is deterministic and local. It is not an embedded
   general-purpose LLM, and it does not execute repository code or mutate Git.
8. Evidence labels describe what was observed. A file hash proves byte identity,
   not the truth of statements contained in that file.

## Supported source and export formats

Source readers: JSON, JSONL/NDJSON, CSV, TSV, XML, TOML, UTF-8 text/Markdown/log,
SQLite, and opaque binary.

Derived exports: JSON (canonical envelope), TXT, CSV, JSONL, and XML. A
conversion is only allowed when the source content can be represented in the
requested target format. Unsupported or ambiguous conversions return an error
instead of silently dropping structure.

“Any filesystem” means any filesystem path that the running Termux/Android
process can read and to which it has permission to write the separate output.
Unmounted, permission-denied, encrypted, or inaccessible paths are not
implicitly available.

## Termux usage

From the repository checkout on the `GOD` branch:

```bash
python tools/eria_aei_conversation.py . -q "Show repository status"
python tools/eria_aei_conversation.py . -q "file:tools/eria_database_translator.py"
python tools/eria_database_translator.py /path/to/source.json \
  --to json --output /path/to/derived/source.canonical.json
python -m unittest discover -s tests -p 'test_eria_database_translator.py' -v
python tools/eria_aei_interface.py . --host 127.0.0.1 --port 8771
```

Open `http://127.0.0.1:8771` in the Android browser on the same device.

## Local HTTP contract

- `GET /`: serves the Æị HTML console.
- `GET /api/status`: reports the selected repository and the local
  read-only/deterministic operating mode.
- `POST /api/chat`: accepts JSON `{"message":"..."}` and returns a JSON
  response containing `status`, `intent`, `answer`, `evidence`, and
  `limits` when applicable.

The server binds only to loopback (`127.0.0.1`, `localhost`, or `::1`).
It is not an internet-facing service. Do not expose it by changing the host
binding or adding a public tunnel without a separate security review.

## Verification status

The regression suite covers SQLite file-signature detection, WAL-aware
read-only SQLite ingestion, source-hash preservation, no-overwrite behavior,
and lossless opaque-binary capture. Tests must be run on the target Termux
checkout before calling the device runtime verified.
