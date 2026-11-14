import hashlib, json, tempfile, time, unittest
from pathlib import Path
from tools.eria_pantheon.approval import sign_grant
from tools.eria_pantheon.patch_executor import execute_exact_patch, PatchHold

class ExactPatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root/"tools").mkdir()
        (self.root/"tools"/"sample.py").write_text("old = True\n")
        self.key = "x"*48
        self.replacement = "new = True\n"
        self.digest = hashlib.sha256(self.replacement.encode()).hexdigest()
    def tearDown(self): self.tmp.cleanup()
    def grant(self, path="tools/sample.py", digest=None, grant_id="patch-1"):
        now=int(time.time())
        return sign_grant({"grant_id":grant_id,"nonce":grant_id+"-nonce",
            "capability":"eria.source.write","scope":path,"patch_sha256":digest or self.digest,
            "issued_at":now-1,"expires_at":now+300}, self.key)
    def test_exact_grant_replaces_file_and_audits(self):
        result=execute_exact_patch(self.root,relative_path="tools/sample.py",
            replacement=self.replacement,grant=self.grant(),signing_key=self.key)
        self.assertEqual(result["status"],"APPLIED")
        self.assertEqual((self.root/"tools"/"sample.py").read_text(),self.replacement)
        row=json.loads((self.root/"storage"/"approvals"/"patch-executions.jsonl").read_text())
        self.assertEqual(row["result"],"APPLIED")
    def test_hash_mismatch_holds_without_write(self):
        with self.assertRaises(PatchHold):
            execute_exact_patch(self.root,relative_path="tools/sample.py",
                replacement=self.replacement,grant=self.grant(digest="a"*64),signing_key=self.key)
        self.assertEqual((self.root/"tools"/"sample.py").read_text(),"old = True\n")
    def test_replay_is_rejected(self):
        args=dict(repository=self.root,relative_path="tools/sample.py",
            replacement=self.replacement,grant=self.grant(),signing_key=self.key)
        execute_exact_patch(**args)
        with self.assertRaises(PatchHold): execute_exact_patch(**args)
    def test_protected_and_traversal_paths_hold(self):
        for path in ("../main.py","storage/settings.json",".git/config","main.py"):
            with self.subTest(path=path), self.assertRaises(PatchHold):
                execute_exact_patch(self.root,relative_path=path,replacement=self.replacement,
                    grant=self.grant(path=path),signing_key=self.key)
    def test_symlink_target_holds(self):
        (self.root/"tools"/"link.py").symlink_to(self.root/"tools"/"sample.py")
        with self.assertRaises(PatchHold):
            execute_exact_patch(self.root,relative_path="tools/link.py",
                replacement=self.replacement,grant=self.grant("tools/link.py"),signing_key=self.key)

if __name__=="__main__": unittest.main()
