# ERIA Root Inventory (read-only)

This utility inventories filesystem paths on an Android device that is **already rooted** and whose installed root manager grants Termux access. It does not root the phone, exploit vulnerabilities, change permissions, remount filesystems, or read file contents.

## Install in Termux

```bash
pkg update
pkg install -y findutils coreutils
cd ~/CodEXgen
chmod +x termux/eria-root-inventory.sh
```

## Run

```bash
./termux/eria-root-inventory.sh
```

The script asks the installed `su` manager for root authorization. Approve only if you recognize the request. If root is unavailable or denied, it exits without attempting a bypass.

Optional output path:

```bash
./termux/eria-root-inventory.sh "$HOME/eria-root-inventory.txt"
```

Audit records are appended to `$HOME/.eria/root-inventory.tsv` (override with `ERIA_ROOT_AUDIT`). Each record includes UTC time, device model, execution mode, find exit status, entry/error counts, script SHA-256, and inventory SHA-256.

## Scope and safeguards

- Scans from `/` and traverses mounted filesystems.
- Prunes volatile `/proc`, `/sys`, `/dev`, and `/run` trees.
- Lists paths only; does not open file contents.
- Does not follow symbolic links (the default `find` behavior).
- Does not modify target files or directories.
- Permission failures are recorded; no bypass is attempted.
- The inventory may contain sensitive filenames. Keep the output and audit file private (the script uses a restrictive umask).

Root access is powerful. Review the script before granting the `su` request. Android Verified Boot, bootloader state, Knox, and device-specific protections remain in force.
