# Pantheon Source Digest

Pantheon is a local-first, non-executing source-analysis tool for CodEXgen. It creates
structural catalogs from Python files that the operator explicitly approves.

## Safety contract

- Only exact, relative .py paths supplied with --approve are read.
- Wildcards, directory recursion, absolute paths, traversal, and symbolic-link inputs are rejected.
- Source is decoded and parsed with Python's ast module. It is never imported, evaluated, or executed.
- Generated modules contain metadata catalogs (component names, signatures, docstrings, source hashes), not copied source bodies.
- Source and output roots must be separate, non-overlapping directory trees.
- The output directory must be empty or not yet exist. Existing artifacts are never silently replaced.
- Generated text is syntax-compiled for validation, not executed.
- Every run writes a JSON provenance manifest with approved paths, SHA-256 hashes, component inventory, and generated artifact hashes.

## Run

From the repository root:

    python -m python.pantheon --source-root python --output-dir pantheon_generated/run-001 --approve code_generator.py adaptive_governance.py

Choose a fresh output directory for each run. Review the manifest and generated catalogs
before any later integration. This phase does not modify main, rewrite source history,
install dependencies, or automatically wire generated components into the application.

## Tests

    python -m unittest tests.test_pantheon_engine -v

The test suite uses temporary directories and synthetic source fixtures; it does not run
any CodEXgen source file.
