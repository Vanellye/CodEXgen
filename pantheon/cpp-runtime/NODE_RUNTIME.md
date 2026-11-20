# Pantheon shared Node.js runtime contract

## Pinned runtime

Every Pantheon Node.js target process must run **Node.js 11.15.0** exactly.

The version is deliberately repeated in these machine-readable entry points:

- `.nvmrc` — Node Version Manager selection
- `.node-version` — version-manager/editor integrations
- `package.json` — exact engine declaration
- `pantheon/node-runtime.json` — authoritative Pantheon runtime contract
- GitHub Actions — CI executes the runtime gate using Node.js 11.15.0

## Startup and verification gate

Run `npm test` before starting a Pantheon Node.js target. The gate compares `process.versions.node` with the exact manifest version and exits non-zero on mismatch. Deployment launchers and node images should run the same gate; do not silently fall back to a different major or patch version.

This contract pins the Node.js host runtime. It does not mean the Android app, C++11 runtime, or Python compatibility layer execute inside Node.js.

## Security boundary

Node.js 11 is end-of-life. This is a user-directed legacy compatibility pin, not a supported or secure default. Keep these processes local or isolated, avoid exposing them to untrusted network traffic, and keep third-party dependencies to a minimum. Do not place credentials in the runtime manifest or source.

A future upgrade must update all pins, CI, deployment images, and compatibility tests together, with a reviewed migration. No node may upgrade independently.
