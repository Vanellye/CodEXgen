# Æị Standalone (Termux)

This is a standalone Termux-hosted web application. It is separate from the Android APK project.

## Requirements
- Termux with Python installed
- The existing ERIA API already running locally (default: `http://127.0.0.1:8778`)

## Install and launch
From the repository root:
```bash
pkg install python -y
cd aie-standalone
bash start.sh
```
Open `http://127.0.0.1:8780/` in the phone browser.

The included Python server serves its own `www/index.html` and reverse-proxies only `/api/*` to the configured ERIA API. This keeps browser API calls same-origin and avoids requiring permissive CORS settings on ERIA.

## Configure a different existing API origin
```bash
ERIA_API_ORIGIN=http://127.0.0.1:8778 AIE_PORT=8780 bash start.sh
```
Do not start a second ERIA API process to satisfy this app. If the API is not running, the UI reports it as disconnected.

## Stop
Press Ctrl+C in the Termux session. No database files are created or modified by this standalone host.

## Routes used
- `GET /api/platform/status`
- `POST /api/scan`
- `POST /api/decode`

These are the existing interface contract assumptions and must be verified against the live server before operational use. No Pantheon API is invented or called.
