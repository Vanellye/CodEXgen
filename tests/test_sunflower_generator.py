import json
import tempfile
import unittest
from pathlib import Path

from sunflower.generator import GAMMA_SYMBOLS, SunflowerGenerator, analyze_habits

class SunflowerGeneratorTests(unittest.TestCase):
    def test_detects_repeated_habit_and_generates_review_only_template(self):
        habits = [["open app", "check inbox", "close app"], ["open app", "check inbox", "close app"]]
        result = SunflowerGenerator().build(habits)
        self.assertEqual(result["patterns"][0]["symbol"], "Ɣ₁")
        self.assertEqual(result["generated_templates"][0]["symbol"], "Ɣ₃")
        self.assertTrue(result["generated_templates"][0]["requires_human_review"])
        self.assertFalse(result["generated_templates"][0]["auto_execute"])

    def test_marks_cycle_candidate(self):
        patterns = analyze_habits([["sync", "review", "sync"]])
        self.assertEqual(patterns[0].symbol, "Ɣ₂")
        self.assertEqual(patterns[0].kind, "cycle_candidate")

    def test_normalizes_whitespace_and_ignores_empty_steps(self):
        patterns = analyze_habits([["  open   app ", "", "check"], ["open app", "check"]])
        self.assertEqual(patterns[0].steps, ("open app", "check"))

    def test_rejects_invalid_repeat_threshold(self):
        with self.assertRaises(ValueError):
            SunflowerGenerator(1)

    def test_write_is_valid_utf8_json(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            SunflowerGenerator().write([["a", "b"], ["a", "b"]], output)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertIn("Ɣ✓", result["symbols"])
            self.assertTrue(result["safety"]["analysis_only"])

if __name__ == "__main__":
    unittest.main()
