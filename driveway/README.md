# Driveway.io

A ledger and app-building starter: TypeScript core/API/web Studio plus a Kotlin Android shell.

## Safety model
- The journal is append-only. Corrections are compensating entries, never silent edits.
- Money is stored as integer minor units (USD cents).
- Point-to-dollar valuation is configurable and explicitly marked as valuation-only by default.
- External connectors are read-only stubs until credentials, scopes, and provider APIs are verified.
- No private keys, custody, transfers, withdrawals, or automatic financial posting are included.
- Production posting requires a separate authorization service and transaction-specific human approval.

## Quick start
Requirements: Node.js 20+ and npm.

```sh
cd driveway
npm install
npm run check
npm run dev
```

Open http://localhost:5173 for the Studio and http://localhost:8787/health for the API. Use `npm run dev:web` or `npm run dev:api` to run either service separately. `npm run typecheck`, `npm test`, `npm run build`, and `npm run check` are available for development validation.

## Driveway DSL
See `examples/ash-ledger.driveway` and `docs/DSL.md`.

## Android
Open `android/` in Android Studio. The starter uses a native Kotlin Activity and a local demo screen; no wallet keys or live financial connection.

## Project boundary
This starter lives on `project/driveway-io-starter` in CodEXgen. It does not change `main` or existing ERIA source files.
