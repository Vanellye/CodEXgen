import os
import tempfile
import unittest

from tools.execution_boundary_guard import AuthorizationGrant, ExecutionBoundaryGuard
from tools.storage_adapter import CreateOnlyStorageAdapter, StorageDenied


class StorageBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = self.temp.name
        for name in ("reports", "evidence-manifests", "proposals"):
            os.mkdir(os.path.join(self.root, name), 0o700)
        self.root_fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        self.guard = ExecutionBoundaryGuard(lambda grant: grant.signature == "test-valid")
        self.events = []
        self.adapter = CreateOnlyStorageAdapter(self.root_fd, self.guard, self.events.append)
        self.grant = AuthorizationGrant(
            actor="synthetic-reviewer",
            approval_ref="TEST-APPROVAL-1",
            operation="create_new_report",
            output_prefix="reports/",
            expires_at=4_000_000_000,
            source_revision="synthetic-revision",
            human_approved=True,
            revoked=False,
            signature="test-valid",
        )

    def tearDown(self):
        self.adapter.close()
        os.close(self.root_fd)
        self.temp.cleanup()

    def test_authorized_create_is_private_and_new(self):
        result = self.adapter.create("create_new_report", "reports/result.txt", b"synthetic report", self.grant)
        target = os.path.join(self.root, "reports", "result.txt")
        self.assertTrue(result["created"])
        self.assertEqual(result["mode"], 0o600)
        self.assertEqual(os.stat(target).st_mode & 0o777, 0o600)
        self.assertEqual(open(target, "rb").read(), b"synthetic report")

    def test_existing_file_cannot_be_overwritten(self):
        target = os.path.join(self.root, "reports", "existing.txt")
        with open(target, "wb") as stream:
            stream.write(b"original")
        with self.assertRaisesRegex(StorageDenied, "create_only_existing_target_denied"):
            self.adapter.create("create_new_report", "reports/existing.txt", b"replacement", self.grant)
        self.assertEqual(open(target, "rb").read(), b"original")

    def test_source_tree_modification_denied(self):
        with self.assertRaises(StorageDenied):
            self.adapter.create("create_new_report", "src/main.py", b"change", self.grant)

    def test_parent_traversal_denied(self):
        with self.assertRaises(StorageDenied):
            self.adapter.create("create_new_report", "reports/../../src/main.py", b"x", self.grant)

    def test_symlink_directory_denied(self):
        outside = os.path.join(self.root, "outside")
        os.mkdir(outside)
        os.symlink(outside, os.path.join(self.root, "reports", "linked"))
        with self.assertRaises(StorageDenied):
            self.adapter.create("create_new_report", "reports/linked/escape.txt", b"x", self.grant)

    def test_missing_human_approval_denied(self):
        grant = AuthorizationGrant(**{**self.grant.__dict__, "human_approved": False})
        with self.assertRaises(StorageDenied):
            self.adapter.create("create_new_report", "reports/no.txt", b"x", grant)

    def test_expired_or_revoked_grants_denied(self):
        expired = AuthorizationGrant(**{**self.grant.__dict__, "expires_at": 1})
        revoked = AuthorizationGrant(**{**self.grant.__dict__, "revoked": True})
        for grant in (expired, revoked):
            with self.subTest(grant=grant):
                with self.assertRaises(StorageDenied):
                    self.adapter.create("create_new_report", "reports/no.txt", b"x", grant)

    def test_wrong_operation_or_scope_denied(self):
        wrong_op = AuthorizationGrant(**{**self.grant.__dict__, "operation": "create_new_evidence_manifest"})
        wrong_scope = AuthorizationGrant(**{**self.grant.__dict__, "output_prefix": "proposals/"})
        for grant in (wrong_op, wrong_scope):
            with self.subTest(grant=grant):
                with self.assertRaises(StorageDenied):
                    self.adapter.create("create_new_report", "reports/no.txt", b"x", grant)

    def test_unverified_grant_denied(self):
        invalid = AuthorizationGrant(**{**self.grant.__dict__, "signature": "invalid"})
        with self.assertRaises(StorageDenied):
            self.adapter.create("create_new_report", "reports/no.txt", b"x", invalid)

    def test_sensitive_and_execution_operations_denied(self):
        denied = (
            "write_existing_source", "overwrite", "read_secrets", "credential_harvesting",
            "secret_extraction", "shell", "execute", "exploit_payload",
            "network_dispatch", "webhook_dispatch", "hidden_execution",
            "hardware_activation", "biological_intervention",
        )
        for operation in denied:
            with self.subTest(operation=operation):
                with self.assertRaises(StorageDenied):
                    self.adapter.create(operation, "reports/no.txt", b"x", self.grant)

    def test_decisions_are_audited_without_content(self):
        with self.assertRaises(StorageDenied):
            self.adapter.create("read_secrets", "reports/no.txt", b"do-not-log", self.grant)
        self.assertEqual(self.events[-1]["decision"], "DENY")
        self.assertNotIn("content", self.events[-1])
        self.assertNotIn("do-not-log", repr(self.events[-1]))


if __name__ == "__main__":
    unittest.main()
