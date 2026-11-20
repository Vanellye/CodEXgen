# BS-ANALYTICS — CodEXgen patch

This additive module introduces a BaseSpace analytics starter without modifying existing application sources.

## Contents
- `db/bs_analytics_schema.sql`: SQLite schema for datasets, source records, metrics, analysis runs, evidence, revisions, and approval receipts.
- `schemas/dataset-manifest.schema.json`: JSON Schema for dataset manifests.
- `web/index.html`: responsive local CSV explorer; computes SHA-256 using Web Crypto and visualizes row counts by a selected field.
- `docs/SOURCE-CONTRACT.md`: ingestion, evidence, integrity, privacy, and authorization rules.
- `tests/test_schema.py`: SQLite DDL and append-only guard tests.

## Source-backed operation
The UI starts with a clearly labeled illustrative fixture. Load an actual CSV to produce an analysis from its rows. The browser computes a SHA-256 digest for the selected file and groups rows by a chosen column. The file is processed locally and is not uploaded.

The SQL file is a local reference database schema, not a provisioned or hosted database. Populate it only through a separately authorized ingestion service.

## Validation
Run `python -m unittest discover -s basespace/analytics/tests -v`.
Tests cover SQL schema creation and immutability triggers; they do not validate a hosted service or production ingestion pipeline.
