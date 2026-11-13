import unittest
from tools.validate_policy import authorize_output

class RedWriteOnlyPolicyTests(unittest.TestCase):
    def test_allowed_new_report(self):
        self.assertEqual(authorize_output("create_new_report", "reports/run-1.json"), (True, "allow_new_scoped_artifact"))

    def test_allowed_new_evidence_manifest(self):
        self.assertTrue(authorize_output("create_new_evidence_manifest", "evidence-manifests/run-1.json")[0])

    def test_allowed_new_proposal(self):
        self.assertTrue(authorize_output("create_new_remediation_proposal", "proposals/fix-1.patch")[0])

    def test_source_tree_write_denied(self):
        self.assertEqual(authorize_output("create_new_report", "src/main.py")[1], "output_root_not_allowed")

    def test_parent_traversal_denied(self):
        self.assertEqual(authorize_output("create_new_report", "reports/../../.github/workflows/pwn.yml")[1], "unsafe_path_segment")

    def test_absolute_path_denied(self):
        self.assertEqual(authorize_output("create_new_report", "/tmp/report.json")[1], "absolute_path_denied")

    def test_backslash_denied(self):
        self.assertEqual(authorize_output("create_new_report", r"reports\\..\\secret")[1], "backslash_path_denied")

    def test_existing_target_denied(self):
        self.assertEqual(authorize_output("create_new_report", "reports/existing.json", exists=True)[1], "create_only_existing_target_denied")

    def test_symlink_denied(self):
        self.assertEqual(authorize_output("create_new_report", "reports/link.json", is_symlink=True)[1], "symlink_target_denied")

    def test_unknown_operation_denied(self):
        self.assertEqual(authorize_output("execute", "reports/x")[1], "operation_not_allowed")

    def test_empty_segment_denied(self):
        self.assertEqual(authorize_output("create_new_report", "reports//x.json")[1], "unsafe_path_segment")

if __name__ == "__main__":
    unittest.main()
