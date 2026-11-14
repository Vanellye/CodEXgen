# Æị Hybrid Workbench

A mobile-first, adaptive interface for the ERIA ecosystem. The workbench combines a unified shell with separate workspaces for ERIA runtime operations, Pantheon integration, SQLite/provenance, decoder tools, and governance.

## Entry point

- `interfaces/aie-workbench/index.html`

The existing `tools/eria_conversation.html` is intentionally left unchanged. This is an additive interface on a separate integration branch.

## Architecture

- **Hybrid:** one navigation shell with distinct workspaces and clear capability boundaries.
- **Adaptive:** compact bottom navigation on phones; persistent workspace rail on wider screens; fold/landscape layouts use available width.
- **Mobile-first:** safe-area insets, large touch targets, responsive tiles, keyboard-friendly inputs, and reduced-motion support.
- **ERIA adapter:** uses only the existing routes already used by the current console:
  - `GET /api/platform/status`
  - `POST /api/scan`
  - `POST /api/decode`
- **Pantheon:** explicitly marked as an integration boundary. No live API route is invented.
- **SQLite:** displays only the database identity and counters returned by ERIA. The browser does not open or mutate the database.

## API assumptions to verify against the live server

The status panel tolerates absent response fields. It looks for `scans`, `source_files`, `decoder_jobs`, `derived_artifacts`, and `database`.

The scan request sends an empty JSON object. The decoder sends `source_id`, `mode`, and `value`. Confirm these contracts against the actual Termux server before relying on them operationally.

The default API URL is same-origin when served over HTTP(S), otherwise `http://127.0.0.1:8778`. The URL is stored in browser local storage. Serve the page from the actual ERIA HTTP server or configure the correct API origin; opening it as a local file may be blocked by browser CORS rules.

## Preservation and authorization

This interface does not:
- rewrite Git history, force-push, merge, or delete branches;
- modify ERIA or Pantheon source files;
- directly query, migrate, vacuum, or delete SQLite records;
- claim that a Pantheon endpoint or artifact-import endpoint exists.

Before future database mutations, require a verified backup, recorded before-state counts and hashes, schema/foreign-key inspection, a transaction, and post-operation integrity checks. Original source records and provenance remain the authority; derived outputs must retain source lineage.

## Termux smoke test

1. Fetch this branch without checking it out over an existing working tree:
   ```bash
   cd "$HOME/ERIA-MASTER"
   git fetch origin integration/aie-hybrid-mobile-console
   git show origin/integration/aie-hybrid-mobile-console:interfaces/aie-workbench/index.html >/dev/null
   ```
2. Copy the interface to a location served by the already-running ERIA HTTP server only after confirming its static-file root:
   ```bash
   mkdir -p "$HOME/eria_platform_ui"
   git show origin/integration/aie-hybrid-mobile-console:interfaces/aie-workbench/index.html > "$HOME/eria_platform_ui/index.html"
   ```
3. Verify the API independently:
   ```bash
   curl -fsS http://127.0.0.1:8778/api/platform/status
   ```
4. Open the page through the server's verified static route. Do not assume `/` serves this directory until the server configuration confirms it.

Do not run two ERIA server processes against the same SQLite database unless the server's locking and single-writer behavior have been explicitly validated.
