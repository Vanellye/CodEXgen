import hashlib
import unittest
from dataclasses import replace

from hypotheticals.fiction_contract import (
    BRANCH_DOMAIN, EVIDENCE_STATUS, FictionArtifactError,
    create_artifact, validate_artifact,
)


class FictionContractTests(unittest.TestCase):
    def test_artifact_is_bound_to_branch_domain_and_content_digest(self):
        content = "Illustrative narrative only."
        record = create_artifact("sample-001", "hypotheticals/example.py", content)
        self.assertEqual(record.domain, BRANCH_DOMAIN)
        self.assertEqual(record.content_sha256, hashlib.sha256(content.encode()).hexdigest())
        self.assertEqual(record.evidence_status, EVIDENCE_STATUS)
        validate_artifact(record)

    def test_domain_cannot_be_reassigned_across_branch_identity(self):
        record = create_artifact("sample-001", "hypotheticals/example.py", "text")
        with self.assertRaises(FictionArtifactError):
            validate_artifact(replace(record, domain="other-domain"))

    def test_fiction_cannot_self_promote_to_empirical_evidence(self):
        record = create_artifact("sample-001", "hypotheticals/example.py", "text")
        with self.assertRaises(FictionArtifactError):
            validate_artifact(replace(record, classification="validated"))

    def test_invalid_identifier_and_non_text_content_are_rejected(self):
        with self.assertRaises(FictionArtifactError):
            create_artifact("../unsafe", "hypotheticals/example.py", "text")
        with self.assertRaises(FictionArtifactError):
            create_artifact("sample-002", "hypotheticals/example.py", None)


if __name__ == "__main__":
    unittest.main()
