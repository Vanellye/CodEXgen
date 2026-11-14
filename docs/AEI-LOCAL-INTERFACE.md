# Æị Local Interface

The browser interface is served by a loopback-only Python bridge. It calls the
existing eria_pantheon.aei.inspect_file implementation; it does not duplicate
the parser or create a second data path.

## Termux

From the repository root:

    pkg install -y python
    PYTHONPATH=tools python tools/eria_aei_server.py --root . --port 8765

Open http://127.0.0.1:8765/ in the Android browser.

Enter a repository-relative path such as README.md or a known test fixture.
The server binds only to 127.0.0.1. It exposes a status endpoint and one POST
inspection endpoint, limits request bodies, and delegates path validation,
symlink rejection, size limits, hashing, and read-only SQLite handling to Æị.

Stop the server with Ctrl+C. This bridge is local-only; it does not expose an
external API, perform writes, or transmit inspected data to a remote service.
