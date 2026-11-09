"""Simple module code generator (extracted from cold dump)."""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass, field
from pathlib import Path

# Fixed, deterministic default used by the pre-commit regenerator.
DEFAULT_SPEC = {
    "module_name": "UserProfile",
    "attributes": ["user_id", "username", "clearance_level", "active_status"],
    "base_class": "SecureEntity",
}


@dataclass
class ModuleSpecification:
    module_name: str
    attributes: list[str] = field(default_factory=list)
    base_class: str = "BaseModel"


class CodeGeneratorEngine:
    def __init__(self, output_dir: str = "./generated_modules"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def render_template(self, spec: ModuleSpecification) -> str:
        lines = [
            f"# Auto-generated module: {spec.module_name}",
            "from typing import Any",
            "",
            f"class {spec.module_name}({spec.base_class}):",
            "    def __init__(self, data: dict[str, Any]):",
            "        super().__init__()",
        ]
        for attr in spec.attributes:
            lines.append(f'        self.{attr} = data.get("{attr}", None)')
        lines.extend(
            [
                "",
                "    def __repr__(self) -> str:",
                f'        return f"<{spec.module_name} attributes={spec.attributes}>"',
                "",
            ]
        )
        return "\n".join(lines)

    def build_module(self, spec: ModuleSpecification) -> str:
        code_content = self.render_template(spec)
        file_path = os.path.join(
            self.output_dir, f"{spec.module_name.lower()}_module.py"
        )
        # Write only when content changes to keep mtimes stable when possible.
        path = Path(file_path)
        if path.exists() and path.read_text(encoding="utf-8") == code_content:
            return file_path
        path.write_text(code_content, encoding="utf-8", newline="\n")
        return file_path


def _repo_generated_dir() -> str:
    return str(Path(__file__).resolve().parent.parent / "generated_modules")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic CodEXgen module generator")
    parser.add_argument(
        "--out",
        default=_repo_generated_dir(),
        help="Output directory for generated module files (default: <repo>/generated_modules)",
    )
    args = parser.parse_args(argv)

    spec = ModuleSpecification(**DEFAULT_SPEC)
    engine = CodeGeneratorEngine(output_dir=args.out)
    generated_path = engine.build_module(spec)
    print(f"Modular code successfully generated and saved to: {generated_path}")
    return ơ


if __name__ == "__main__":
    raise SystemExit(main())
