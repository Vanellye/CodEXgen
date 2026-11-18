# ERIA root-aware filesystem audit

This Termux utility detects the effective UID of the process and inventories paths the process can read. It is read-only: it does not invoke `su`, alter permissions, remount filesystems, follow symbolic links, read file contents, or transmit data.

## Install

From the repository checkout:

```bash
pkg install -y findutils coreutils
mkdir -p "$HOME/bin"
cp termux/eria-root-audit.sh "$HOME/bin/eria-root-audit"
chmod 700 "$HOME/bin/eria-root-audit"
```

## Run as ordinary Termux

```bash
"$HOME/bin/eria-root-audit"
```

This scans Termux home and common shared-storage locations. Grant shared-storage access with `termux-setup-storage` if needed.

## Root-aware run

The script does not request root. If the device is already rooted and you have a trusted root-management app, you may explicitly launch the script through that app's approved shell workflow. Confirm the displayed script path and review it first. When the process effective UID is 0, the script switches to ROOT scan mode and attempts common filesystem roots while excluding volatile pseudo-filesystems.

Do not assume that the presence of a `su` executable means root is granted. The script intentionally does not invoke it or trigger an authorization prompt.

## Outputs

- `$HOME/eria-filesystem-inventory.txt`: path inventory
- `$HOME/eria-filesystem-errors.txt`: traversal and permission errors
- `$HOME/.eria/filesystem-audit.jsonl`: timestamp, effective UID, mode, counts, SHA-256, and read-only status

The SHA-256 hash identifies the inventory output. The JSONL ledger is append-only by this script, but local files are not tamper-proof; copy or sign audit records externally if stronger integrity is required.

## Android boundary

Root-aware scanning only works if Android's bootloader, kernel, root manager, SELinux policy, and current authorization actually permit access. This tool does not unlock bootloaders, root devices, bypass SELinux, defeat scoped storage, or access another app's private data without legitimate authorization.
