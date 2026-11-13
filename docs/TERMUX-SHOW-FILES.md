# ERIA Show Files (Termux)

Read-only directory inventory that includes hidden files and folders (names beginning with a dot). It does not read file contents, follow symbolic links, change permissions, request root, or bypass Android storage controls.

## Install

From the repository root:

```bash
chmod +x termux/eria-show-files.sh
mkdir -p "$HOME/bin"
cp termux/eria-show-files.sh "$HOME/bin/eria-show-files"
chmod +x "$HOME/bin/eria-show-files"
```

If `$HOME/bin` is not on PATH, run it with `$HOME/bin/eria-show-files`.

## Use

```bash
# Inventory the Termux home directory, including dotfiles
eria-show-files

# Inventory shared storage after granting Termux storage permission
termux-setup-storage
eria-show-files "$HOME/storage/shared"

# Inventory a specific project
eria-show-files "$HOME/CodEXgen"
```

The output is written to `$HOME/eria-file-inventory.txt` by default. Override it with `ERIA_FILE_LIST=/path/to/list.txt`.

## Limits

Android denies access to protected app data and other apps' private directories unless the operating system grants access. This tool reports inaccessible paths and continues where possible; it does not attempt root escalation, permission bypass, or hidden-data extraction. The Pantheon contract in `pantheon/FILESYSTEM_INVENTORY.ptn` is a draft specification, not executable language code.
