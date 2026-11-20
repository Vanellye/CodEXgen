import json
import pathlib
import unicodedata
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "shared/eria-glyphic-energy/registry.json").read_text(encoding="utf-8"))

class GlyphicEnergyRegistryTests(unittest.TestCase):
    def test_unique_ids_and_glyphs(self):
        glyphs = REGISTRY["glyphs"]
        self.assertEqual(len({g["id"] for g in glyphs}), len(glyphs))
        self.assertEqual(len({g["glyph"] for g in glyphs}), len(glyphs))

    def test_codepoints_and_unicode_names_match(self):
        for item in REGISTRY["glyphs"]:
            actual_points = [f"U+{ord(ch):04X}" for ch in item["glyph"]]
            self.assertEqual(actual_points, item["codepoints"], item["id"])
            actual_name = " + ".join(unicodedata.name(ch) for ch in item["glyph"])
            self.assertEqual(actual_name, item["unicode_name"], item["id"])

    def test_both_scripts_are_represented(self):
        scripts = {g["script"] for g in REGISTRY["glyphs"]}
        self.assertEqual(scripts, {"egyptian_hieroglyphs", "cuneiform"})

    def test_queneoforum_alias_is_preserved(self):
        aliases = REGISTRY["script_aliases"]["cuneiform"]
        self.assertIn("Qunəiforum", aliases)
        self.assertIn("queneoforum", aliases)

    def test_symbolic_energy_is_not_a_physical_measurement(self):
        energy = REGISTRY["energy_model"]
        self.assertEqual(energy["classification"], "symbolic_metadata_only")
        self.assertIsNone(energy["unit"])
        self.assertFalse(REGISTRY["policy"]["physical_energy_measurement"])
        self.assertFalse(REGISTRY["policy"]["biological_mapping"])

    def test_data_only_no_execution_or_silent_conversion(self):
        policy = REGISTRY["policy"]
        self.assertEqual(policy["token_mode"], "data_only")
        self.assertFalse(policy["code_execution"])
        self.assertFalse(policy["silent_conversion"])
        self.assertTrue(policy["preserve_original_codepoints"])

    def test_semantics_remain_unassigned(self):
        for item in REGISTRY["glyphs"]:
            self.assertEqual(item["symbolic_role"], "unassigned")
            self.assertIsNone(item["energy_annotation"])
            self.assertIsNone(item["transliteration"])

if __name__ == "__main__":
    unittest.main()
