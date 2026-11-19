# Ɣơ Repository Bot

The bot is a local, deterministic file transformer. It reads an explicitly supplied input file and either prints the encoded result or writes to an explicitly supplied output path. It never executes encoded content and does not make network requests.

## Run

```sh
python language/og/bot/yoro_bot.py --profile reversible --input sample.bin
python language/og/bot/yoro_bot.py --profile lossy --input sample.bin --output sample.og
```

## Profiles

- `reversible`: Ɣơ/2, maps zero bits to ☆ and one bits to k, preserving all eight positions per byte.
- `lossy`: Ɣơ/L1, removes zero-bit positions and has no decoder. Treat output as a lossy summary, never as a backup.

## Multi-platform contract

Keep the byte-level algorithms normative and implement thin adapters for:
- Python desktop/CI: reference bot in this directory.
- Android/Kotlin: a local-file adapter calling equivalent byte-array transforms.
- Web/JavaScript: a browser or Node adapter calling equivalent Uint8Array transforms.

All adapters must share the same prefixes, byte ordering, separators, malformed-input rules, and fixture vectors. Platform adapters must not silently change profiles. No adapter may execute decoded or encoded content.

## Repository governance

Work on profile-specific feature branches. Run independent tests and review the exact commit before promotion. Do not write directly to protected `main`; no automated merge or privileged action is authorized by this bot.
