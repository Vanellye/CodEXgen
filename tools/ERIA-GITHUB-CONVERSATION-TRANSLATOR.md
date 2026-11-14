# ERIA GitHub Conversation Data Translator

## Purpose

A read-only Termux tool for retrieving GitHub repository metadata, issue/PR
conversation comments and individual repository text files. Retrieved data is
organized into a structured ERIA response with source URLs, retrieval time,
response SHA-256 and limitations.

This is a data retrieval and evidence-structuring tool. It does not claim that
plain data serialization is a natural-language translation. A separate language
provider can be connected later through an explicit adapter.

## Security and governance

- Uses HTTP GET only.
- Accepts a token only from `ERIA_GITHUB_TOKEN`; never put tokens in source or shell history.
- Never writes to GitHub, changes branches, commits, pushes, merges, or executes retrieved code.
- Refuses path traversal and limits each response to 2 MB.
- Writes optional local output with exclusive-create semantics; existing files are not overwritten.
- Treats repository content and comments as untrusted input.
- Preserves evidence URLs and response hashes in the result.

## Termux setup

```bash
pkg update -y
pkg install python git -y
cd "$HOME/ERIA-ANCHOR-b549dea"
git fetch origin
git switch feature/eria-canonical-conversion-engine
git pull --ff-only origin feature/eria-canonical-conversion-engine
```

For a private repository, set a fine-grained GitHub token with read-only Contents
and Issues permissions. Do not grant write permissions.

```bash
export ERIA_GITHUB_TOKEN='YOUR_READ_ONLY_TOKEN'
```

Avoid saving the token in a tracked file or sharing terminal screenshots that
show it. Unset it after use:

```bash
unset ERIA_GITHUB_TOKEN
```

## Commands

Repository metadata:

```bash
python tools/eria_github_conversation_translator.py \
  --repo Vanellye/CodEXgen --repo-info --pretty
```

Issue or pull-request discussion:

```bash
python tools/eria_github_conversation_translator.py \
  --repo Vanellye/CodEXgen --issue 123 --pretty
```

One repository file at a selected branch:

```bash
python tools/eria_github_conversation_translator.py \
  --repo Vanellye/CodEXgen \
  --file tools/ERIA-CANONICAL-CONVERSION.md \
  --ref feature/eria-canonical-conversion-engine \
  --pretty
```

Save a new local JSON result without overwriting an existing file:

```bash
mkdir -p "$HOME/storage/shared/ERIA/translations"
python tools/eria_github_conversation_translator.py \
  --repo Vanellye/CodEXgen --repo-info \
  --output "$HOME/storage/shared/ERIA/translations/repository.json"
```

## Tests

```bash
python -m unittest discover -s tests \
  -p 'test_eria_github_conversation_translator.py' -v
```

## Current scope and limitations

The first version retrieves repository metadata, one issue/PR discussion page
(up to 100 comments), and one text file. It does not yet recursively crawl
repository history or all issue pages. It structures and summarizes evidence;
it does not generate a claim of semantic translation into another human
language. A provider-backed translation adapter and independent PONS/AVS
validation integration remain future implementation steps.
