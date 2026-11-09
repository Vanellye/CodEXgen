"""Simple module code generator (extracted from cold dump)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field


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
        template = f'''# Auto-generated module: {spec.module_name}
from typing import Any

class {spec.module_name}({spec.base_class}):
    def __init__(self, data: dict[str, Any]):
        super().__init__()
'''
        for attr in spec.attributes:
            template += f'        self.{attr} = data.get("{attr}", None)\n'

        template += f'''
    def __repr__(self) -> str:
        return f"<{spec.module_name} attributes={spec.attributes}>"
'''
        return template

    def build_module(self, spec: ModuleSpecification) -> str:
        code_content = self.render_template(spec)
        file_path = os.path.join(
            self.output_dir, f"{spec.module_name.lower()}_module.py"
        )
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code_content)
        return file_path


if __name__ == "__main__":
    input_payload = {
        "module_name": "UserProfile",
        "attributes": ["user_id", "username", "clearance_level", "active_status"],
        "base_class": "SecureEntity",
    }
    spec = ModuleSpecification(**input_payload)
    engine = CodeGeneratorEngine(
        output_dir=os.path.join(os.path.dirname(__file__), "..", "generated_modules")
    )
    generated_path = engine.build_module(spec)
    print(f"Modular code successfully generated and saved to: {generated_path}")
