# Generation Genesis — Constant Execution

## Runtime model

Generation Genesis uses two cooperating execution modes:

- **Termux daemon:** repeats a local generation cycle every 900 seconds by default.
- **GitHub Actions:** runs one bounded cycle on pushes to `core`, every 15 minutes, or on manual dispatch.

GitHub-hosted runners are ephemeral. The schedule is recurring, not uninterrupted. Termux must be started by the device owner and remains subject to Android battery and process-management limits.

## What the current engine generates

The current deterministic engine is `python/code_generator.py`. Its default specification produces the `UserProfile` module. Repeating an unchanged specification is intentionally idempotent: it verifies/reuses the same output rather than inventing new modules. New module families require explicit specifications or an approved input queue.

## Termux setup

From Termux:

```bash
pkg update
pkg install -y python git
termux-setup-storage
git clone -b core https://github.com/Vanellye/CodEXgen.git "$HOME/CodEXgen"
cd "$HOME/CodEXgen"
chmod +x termux/genesis-termux.sh
python tools/genesis_constant_runner.py --once
./termux/genesis-termux.sh
```

Stop with Ctrl+C. Change the interval (minimum 60 seconds) with:

```bash
GENESIS_INTERVAL=300 ./termux/genesis-termux.sh
```

The runner uses a process lock to prevent duplicate workers. It writes append-only JSON Lines records to `.eria/genesis-runs.jsonl`, with UTC timestamps, duration, source hash, output hash, repository revision, status, and outcome. Generated modules are stored in `generated_modules/`.

## Governance and boundaries

- The worker only invokes the existing deterministic generator.
- No automatic Git commit, push, merge, release, deployment, deletion, external dispatch, or hardware action occurs.
- GitHub Actions has `contents: read` permission and uploads run outputs as artifacts.
- Human review remains required before repository mutation or promotion.
- Do not put secrets, credentials, private keys, biometric templates, or sensitive personal/biological data in the run ledger.
- A successful generation cycle proves only that the generator ran; it does not prove semantic correctness of a newly supplied specification.

## Operational notes

- The GitHub schedule runs approximately every 15 minutes; GitHub may delay scheduled jobs under load.
- The Termux process is local to the device and is not started remotely by GitHub.
- The current generator has a fixed default spec. Continuous novel content generation needs a reviewed specification source and validation policy before it can be safely automated.
