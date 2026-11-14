# ERIA Repository Conversation Engine

Read-only local conversation interface for repository metadata and text evidence.

## Install
    pkg install -y python git
    cd ~/CodEXgen
    mkdir -p "$HOME/bin"
    cp tools/eria_repository_conversation.py "$HOME/bin/eria-repo-chat"
    chmod 700 "$HOME/bin/eria-repo-chat"

## Start
    eria-repo-chat "$HOME/CodEXgen"

Æị read-only format inspection:
    python tools/eria_pantheon/aei.py path/to/file.json --root .

From the conversation prompt:
    aei.inspect path/to/file.json
    aei.translate path/to/database.sqlite3

Supported deterministic adapters: JSON, CSV, XML, TOML, YAML (optional PyYAML),
SQLite in read-only mode, and bounded UTF-8 text/source previews. Unknown or binary
formats return metadata only when decoding is not safe. Æị never edits the source,
executes source code, or transmits data. “Translate” means structural interpretation,
not automatic natural-language translation or code rewriting.

Example questions:
- what is the git status?
- show all branches
- summarize commit history
- show all files and formats
- where is Pantheon defined?
- show pantheon/README.md
- find Genesis runner

One-shot query:
    python tools/eria_repository_conversation.py "$HOME/CodEXgen" --question "show all branches"

## Interpretation model
Reads Git status, branch names, commit history, tags, remote names, file paths, extensions, and bounded UTF-8 text. Search results retain path and line number. Remote URLs are hidden because they can contain credentials. Likely inline credentials are redacted and files with secret-like names are skipped.

It does not execute repository code, invoke arbitrary shell commands, modify the working tree, or change Git refs. Binary files and text files larger than 1 MB are skipped. This is a deterministic local question router, not an autonomous language model. Pantheon remains a draft specification, not an executable runtime.
