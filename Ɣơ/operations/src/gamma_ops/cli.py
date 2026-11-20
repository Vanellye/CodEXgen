"""Read-only terminal entry point for .coddoc and operable registries."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .coddoc import load_coddoc, ordered_events
from .readiness import readiness_result, ready_records

def _load_json(path: str) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("input JSON root must be an object")
    return value

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="eria-observer", description="Read-only ERIA Runflow observer")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate a .coddoc file")
    validate.add_argument("path")
    timeline = commands.add_parser("timeline", help="print authored event order")
    timeline.add_argument("path")
    catalog = commands.add_parser("catalog", help="list operable readiness states")
    catalog.add_argument("--registry", default="Ɣơ/operations/registry/operables.json")
    ready = commands.add_parser("ready", help="list only independently reviewed READY_TO_OPEN records")
    ready.add_argument("--registry", default="Ɣơ/operations/registry/operables.json")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            document = load_coddoc(args.path)
            print(json.dumps({"valid": True, "document_id": document["document_id"],
                              "source_sha256": document["_source_sha256"]}, indent=2))
            return 0
        if args.command == "timeline":
            document = load_coddoc(args.path)
            for event in ordered_events(document):
                when = event["occurred_at"] or "NOT_RECORDED"
                refs = ", ".join(event["source_refs"])
                print(f'{event["sequence"]:04d} | {when} | {event["event_id"]} | {event["observation"]} | {refs}')
            return 0
        registry = _load_json(args.registry)
        if args.command == "catalog":
            for record in registry.get("operables", []):
                if isinstance(record, dict):
                    print(f'{record.get("operable_id", "UNKNOWN")} | {record.get("readiness_state", "UNKNOWN")} | {record.get("execution_tier", "UNKNOWN")}')
            return 0
        eligible = ready_records(registry, repository_root=".")
        print(json.dumps({"ready_to_open": [item.get("operable_id") for item in eligible]}, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        print(f"HOLD: {exc}")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
