import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

from eria_pantheon.ai import AiiConversation
from eria_pantheon.interface import ERIAPantheonInterface


class RepositoryStub:
    def __init__(self, root):
        self.root = Path(root)


class AiiHigherFacultyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "service.py"
        self.original = (
            'import os\n'
            'import sqlite3\n'
            'def launch(command):\n'
            '    """Launch a local helper process."""\n'
            '    os.system(command)\n'
            '    return True\n'
        )
        self.source.write_text(self.original, encoding="utf-8")
        (self.root / "legacy.py").write_text(
            "def launch(command):\n    return False\n", encoding="utf-8"
        )
        self.ai = AiiConversation(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_function_purpose_and_dependencies(self):
        purpose = self.ai.ask_higher_faculty("service.py", "Why does this function exist?")
        self.assertIn("function_purpose", purpose["analysis"])
        self.assertEqual(purpose["analysis"]["function_purpose"][0]["name"], "launch")
        self.assertIn("local helper process", purpose["analysis"]["function_purpose"][0]["purpose"])
        deps = self.ai.ask_higher_faculty("service.py", "What dependencies does it require?")
        names = [item["name"] for item in deps["analysis"]["dependencies"]]
        self.assertIn("os", names)
        self.assertIn("sqlite3", names)

    def test_conflicts_and_security(self):
        conflicts = self.ai.ask_higher_faculty("service.py", "Identify conflicting implementations.")
        self.assertTrue(any(item["path"] == "legacy.py" for item in conflicts["analysis"]["conflicting_implementations"]))
        security = self.ai.ask_higher_faculty("service.py", "Explain the security implications.")
        self.assertTrue(any(item["rule"] == "shell_execution" for item in security["analysis"]["security_implications"]))

    def test_improvement_and_translation_comparison(self):
        improvement = self.ai.ask_higher_faculty("service.py", "Propose an improved implementation.")
        self.assertTrue(improvement["analysis"]["improvement_proposals"])
        comparison = self.ai.ask_higher_faculty("service.py", "Compare original source with English translation.")
        self.assertGreater(comparison["analysis"]["source_translation_comparison"]["finding_count"], 0)
        self.assertEqual(self.source.read_text(encoding="utf-8"), self.original)

    def test_explicit_file_comparison_and_interface(self):
        result = self.ai.ask_higher_faculty(
            "service.py", "Compare these implementations.", comparison_path="legacy.py"
        )
        self.assertIsNotNone(result["comparison"])
        self.assertFalse(result["comparison"]["same_bytes"])
        interface = ERIAPantheonInterface(RepositoryStub(self.root))
        payload = json.loads(interface.handle(
            'ai.higher service.py --question "What dependencies does it require?"'
        ))
        self.assertEqual(payload["status"], "answered")
        self.assertEqual(payload["pons"]["service_state"], "ON")
        self.assertFalse(payload["pons"]["execution_enabled"])


if __name__ == "__main__":
    unittest.main()
