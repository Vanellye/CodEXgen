import unittest

from pons11_grants import (
    CommandSpec, MAX_GRANT_SECONDS, PONS11Grant, audit_decision, validate_grant,
)


class PONS11GrantTests(unittest.TestCase):
    def setUp(self):
        self.grant = PONS11Grant(
            grant_id="grant-test-1", actor="operator", approval_ref="approval-1",
            issued_at=1000, expires_at=1000 + MAX_GRANT_SECONDS,
            commands=(CommandSpec("/usr/bin/git", ("status", "--short")),),
            working_directories=("/workspace/ERIA",),
            human_approved=True, revoked=False, root=False,
            deployment=False, may_modify_main=False, signature="signed",
        )
        self.kwargs = dict(
            requested_executable="/usr/bin/git",
            requested_arguments=("status", "--short"),
            working_directory="/workspace/ERIA",
            trusted_executables=("/usr/bin/git",),
            trusted_working_directories=("/workspace/ERIA",),
            signature_verifier=lambda grant: grant.signature == "signed",
            now=1001,
        )

    def test_exact_allowlisted_invocation_passes(self):
        decision = validate_grant(self.grant, **self.kwargs)
        self.assertTrue(decision.allowed)

    def test_argument_change_is_denied(self):
        kwargs = dict(self.kwargs, requested_arguments=("push", "origin", "main"))
        self.assertEqual(validate_grant(self.grant, **kwargs).reason,
                         "command_or_arguments_not_allowlisted")

    def test_expired_grant_is_denied(self):
        self.assertEqual(validate_grant(self.grant, **dict(self.kwargs, now=1660)).reason,
                         "grant_expired")

    def test_grant_longer_than_11_minutes_is_denied(self):
        grant = PONS11Grant(**{**self.grant.__dict__, "expires_at": 1661})
        self.assertEqual(validate_grant(grant, **self.kwargs).reason,
                         "grant_duration_exceeds_11_minutes")

    def test_root_deployment_and_main_are_denied(self):
        for field, reason in (
            ("root", "root_privilege_prohibited"),
            ("deployment", "deployment_prohibited"),
            ("may_modify_main", "main_modification_prohibited"),
        ):
            grant = PONS11Grant(**{**self.grant.__dict__, field: True})
            self.assertEqual(validate_grant(grant, **self.kwargs).reason, reason)

    def test_untrusted_signature_fails_closed(self):
        kwargs = dict(self.kwargs, signature_verifier=lambda grant: False)
        self.assertEqual(validate_grant(self.grant, **kwargs).reason,
                         "signature_or_revocation_verification_failed")

    def test_working_directory_must_be_in_scope(self):
        kwargs = dict(self.kwargs, working_directory="/workspace/other")
        self.assertEqual(validate_grant(self.grant, **kwargs).reason,
                         "working_directory_out_of_scope")

    def test_audit_sink_receives_allow_and_deny_decisions(self):
        events = []
        decision = validate_grant(self.grant, **self.kwargs)
        audit_decision(events.append, self.grant, decision, "/usr/bin/git",
                       ("status", "--short"), "/workspace/ERIA")
        self.assertEqual(len(events), 1)
        self.assertTrue(events[0]["allowed"])
        with self.assertRaises(TypeError):
            audit_decision(None, self.grant, decision, "/usr/bin/git", (), "/workspace/ERIA")


if __name__ == "__main__":
    unittest.main()
