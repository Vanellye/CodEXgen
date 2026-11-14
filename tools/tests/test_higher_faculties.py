import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

from eria_pantheon.higher_faculties import translate_file
from eria_pantheon.interface import ERIAPantheonInterface


class RepositoryStub:
    def __init__(self, root):
        self.root = Path(root)


class HigherFacultyPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "sample.py"
        self.original = (
            "import os\n"
            "class Example:\n"
            "    def run(self):\n"
            "        # TODO review this\n"
            "        return 1\n"
        ).encode("utf-8")
        self.source.write_bytes(self.original)

    def tearDown(self):
        self.temp.cleanup()

    def test_pipeline_order_and_provenance(self):
        result = translate_file(self.root, "sample.py")
        self.assertEqual(
            [item["stage"] for item in result["pipeline"]],
            ["Discovery", "Antithesis", "Verification", "Creation"],
        )
        self.assertTrue(result["verification"]["source_digest_matches"])
        self.assertGreater(result["translation"]["finding_count"], 0)
        self.assertGreater(result["antithesis"]["flag_count"], 0)
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertFalse(result["preservation"]["source_file_written"])
        self.assertEqual(result["pons"]["service_state"], "ON")
        self.assertFalse(result["pons"]["execution_enabled"])

    def test_interface_command_is_connected(self):
        interface = ERIAPantheonInterface(RepositoryStub(self.root))
        response = json.loads(interface.handle("aei.translate sample.py"))
        self.assertEqual(response["translator"], "Æị")
        self.assertEqual(response["subsystem"], "Higher Faculties")
        self.assertEqual(response["status"], "REVIEW_REQUIRED")

    def test_rejects_path_escape_and_non_code(self):
        with self.assertRaises(ValueError):
            translate_file(self.root, "../outside.py")
        with self.assertRaises(ValueError):
            translate_file(self.root, "sample.txt")


if __name__ == "__main__":
    unittest.main()
