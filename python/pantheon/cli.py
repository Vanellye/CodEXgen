"""Command-line entry point for the Pantheon source catalog generator."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .engine import AnalysisError, generate_pantheon_modules

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze explicitly approved Python files without executing them.")
    parser.add_argument("--source-root", type=Path, default=Path("python"))
    parser.add_argument("--output-dir", type=Path, default=Path("pantheon_generated"))
    parser.add_argument(
        "--approve", nargs="+", required=True, metavar="RELATIVE_PATH",
        help="Exact .py file paths relative to --source-root; wildcards are not supported.",
    )
    return parser

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = generate_pantheon_modules(args.source_root, args.output_dir, args.approve)
    except (AnalysisError, OSError) as exc:
        print(f"Pantheon stopped safely: {exc}")
        return 2
    print(json.dumps({
        "status": "generated",
        "output_dir": str(args.output_dir),
        "approved_file_count": len(manifest["approved_sources"]),
        "generated_module_count": len(manifest["generated_artifacts"]),
        "execution_performed": False,
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
