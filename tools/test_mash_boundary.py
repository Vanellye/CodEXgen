import os
import tempfile
import unittest

from mash_boundary import (
    BoundaryViolation,
    CreateOnlyArtifactStore,
    ExecutionBoundaryGuard,
    PROHIBITED_CAPABILITIES,
)


class BoundaryTests(unittest.TestCase):
    def test_allowlisted_generation_and_validation(self):
        guard = ExecutionBoundaryGuard()
        for capability in ("code.generate", "code.validate", "tests.isolated", "review.present"):
            guard.authorize(capability)

    def test_every_prohibited_capability_is_denied(self):
        guard = ExecutionBoundaryGuard()
        for capability in PROHIBITED_CAPABILITIES:
            with self.subTest(capability=capability):
                with self.assertRaises(BoundaryViolation):
                    guard.authorize(capability)

    def test_unknown_capability_is_denied(self):
        with self.assertRaises(BoundaryViolation):
            ExecutionBoundaryGuard().authorize("runtime.do_anything")

    def test_create_new_file(self):
        with tempfile.TemporaryDirectory() as root:
            with CreateOnlyArtifactStore(root, ExecutionBoundaryGuard()) as store:
                store.write_new("artifact.txt", b"first")
            with open(os.path.join(root, "artifact.txt"), "rb") as stream:
                self.assertEqual(stream.read(), b"first")

    def test_existing_file_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as root:
            target = os.path.join(root, "artifact.txt")
            with open(target, "wb") as stream:
                stream.write(b"original")
            with CreateOnlyArtifactStore(root, ExecutionBoundaryGuard()) as store:
                with self.assertRaises(FileExistsError):
                    store.write_new("artifact.txt", b"replacement")
            with open(target, "rb") as stream:
                self.assertEqual(stream.read(), b"original")

    def test_path_traversal_and_absolute_paths_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            with CreateOnlyArtifactStore(root, ExecutionBoundaryGuard()) as store:
                for path in ("../escape", "/absolute", "a/../escape", "./dot", "a//b"):
                    with self.subTest(path=path):
                        with self.assertRaises(BoundaryViolation):
                            store.write_new(path, b"x")

    def test_symlink_file_is_not_followed_or_replaced(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as outside:
            target = os.path.join(outside, "secret.txt")
            with open(target, "wb") as stream:
                stream.write(b"untouched")
            os.symlink(target, os.path.join(root, "link"))
            with CreateOnlyArtifactStore(root, ExecutionBoundaryGuard()) as store:
                with self.assertRaises(FileExistsError):
                    store.write_new("link", b"overwrite")
            with open(target, "rb") as stream:
                self.assertEqual(stream.read(), b"untouched")

    def test_symlink_directory_is_not_traversed(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as outside:
            os.symlink(outside, os.path.join(root, "linked"))
            with CreateOnlyArtifactStore(root, ExecutionBoundaryGuard()) as store:
                with self.assertRaises(OSError):
                    store.write_new("linked/payload", b"x")

    def test_non_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            with CreateOnlyArtifactStore(root, ExecutionBoundaryGuard()) as store:
                with self.assertRaises(TypeError):
                    store.write_new("artifact.txt", "not bytes")


if __name__ == "__main__":
    unittest.main()
