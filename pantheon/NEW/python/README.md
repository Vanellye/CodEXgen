# ERIA Pantheon Python bridge

This package exposes the existing native C interfaces in `pantheon/NEW`
to Python. It does not replace NEW or FaCADE, collect external data, write
to SQLite, or perform Git operations.

## Termux setup

From the repository root:

```bash
pkg install clang python -y
bash pantheon/NEW/python/test_bridge.sh
```

The script compiles the two existing C implementation files into a temporary
shared library, sets the library and package paths, and runs the Python bridge
tests. It removes the temporary build directory on exit.

## Import

After building a shared library, set its path and the package path:

```bash
export ERIA_PANTHEON_LIBRARY="$PWD/pantheon/NEW/build/liberia_pantheon.so"
export PYTHONPATH="$PWD/pantheon/NEW/python:$PYTHONPATH"
python -c "from eria_pantheon.interface import ERIAPantheonInterface; print('Pantheon bridge import OK')"
```

For a persistent build, compile from the repository root:

```bash
mkdir -p pantheon/NEW/build
clang -std=c11 -Wall -Wextra -Werror -fPIC -shared \
  -Ipantheon/NEW \
  pantheon/NEW/NEW.c \
  pantheon/NEW/FaCADE/FaCADE.c \
  -o pantheon/NEW/build/liberia_pantheon.so
```

Then:

```bash
export ERIA_PANTHEON_LIBRARY="$PWD/pantheon/NEW/build/liberia_pantheon.so"
export PYTHONPATH="$PWD/pantheon/NEW/python:$PYTHONPATH"
```

## NEW narrative example

```python
from eria_pantheon.interface import ERIAPantheonInterface

pantheon = ERIAPantheonInterface()
text = pantheon.build_narrative({
    "source_id": "public-dataset",
    "record_id": "record-001",
    "permission_basis": "public-use license",
    "purpose": "aggregate trend analysis",
    "captured_at": "2026-11-14T00:00:00Z",
    "provenance_digest": "sha256:replace-with-real-digest",
    "content_summary": "A source-reported aggregate observation.",
    "data_class": 1,       # PUBLIC
    "evidence_status": 1,  # SOURCE_REPORTED
    "authorization_confirmed": True,
})
print(text)
```

For `evidence_status=2` (independently corroborated), provide all three
fields: `proof_reference`, `proof_method`, and `proof_checked_at`.
Use `data_class=2` only for appropriately consented aggregates.

## FaCADE correction example

```python
proposal = pantheon.build_correction({
    "notice_id": "notice-01",
    "source_record_id": "record-original",
    "target_record_id": "record-followup",
    "evidence_reference": "evidence-01",
    "reason": "Add a linked supporting record.",
    "recorded_at": "2026-11-14T00:00:00Z",
    "reviewer_id": "reviewer-id",
    "relation": 2,  # CORRECTS
    "source_authorized": True,
    "link_verified": True,
})
print(proposal)
```

## Enum values

- NEW data class: `1=PUBLIC`, `2=CONSENTED_AGGREGATE`.
- NEW evidence: `1=SOURCE_REPORTED`, `2=INDEPENDENTLY_CORROBORATED`,
  `3=HYPOTHESIS`.
- FaCADE relation: `1=RESTORES`, `2=CORRECTS`, `3=SUPERSEDES`,
  `4=CONTRADICTS`, `5=DERIVED_FROM`.

The authorization and link-verification flags are upstream assertions, not
cryptographic proof. The C module labels its narrative unreviewed. Neither
function edits source records or publishes anything. Database persistence,
API routing, identity verification, and production deployment remain separate
integration tasks requiring their own tests and authorization.

## Canonical directory layout

From the repository root, the bridge and native sources are organized as:

```text
pantheon/
└── NEW/
    ├── NEW.c
    ├── NEW.h
    ├── FaCADE/
    │   ├── FaCADE.c
    │   └── FaCADE.h
    ├── build/                 # local generated shared library; not source-controlled
    │   └── liberia_pantheon.so
    └── python/
        ├── eria_pantheon/
        │   ├── __init__.py
        │   └── interface.py
        ├── tests/
        └── test_bridge.sh
```

The package loader's default library path is relative to `pantheon/NEW`, so the
persistent library belongs in `pantheon/NEW/build/`, not a repository-root
`build/` directory. Keep generated binaries local and do not commit them.
