import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class IntegrityContractTests(unittest.TestCase):
 def test_indexes_are_prepare_only(self):
  a=json.loads((ROOT/"history-index.json").read_text()); b=json.loads((ROOT/"allowance-list.json").read_text())
  self.assertEqual(a["mode"],"PREPARE_ONLY"); self.assertEqual(b["mode"],"PREPARE_ONLY"); self.assertEqual(b["entries"],[])
 def test_history_is_append_only(self):
  a=json.loads((ROOT/"history-index.json").read_text()); p=a["preservation_policy"]
  self.assertFalse(p["rewrite_existing_indexes"]); self.assertFalse(p["delete_historical_records"]); self.assertTrue(p["new_v4_events_append_only"])
 def test_templates_cannot_issue_money(self):
  p=json.loads((ROOT/"allowance.example.json").read_text()); self.assertFalse(p["live_submission_enabled"]); self.assertFalse(p["configured"])
 def test_reviewer_registry_is_empty_template(self):
  r=json.loads((ROOT/"reviewer-registry.example.json").read_text()); self.assertEqual(r["reviewers"],[]); self.assertEqual(r["governance_signature"],"")
if __name__=="__main__": unittest.main()
