import subprocess, tempfile, unittest
from pathlib import Path
from tools.eria_glob import GlobBootstrap, GlobEngine

class GlobEngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)/"repo"; self.root.mkdir()
        (self.root/"main.py").write_text("ok"); (self.root/"src").mkdir(); (self.root/"src"/"mod.py").write_text("x")
        (self.root/"node_modules").mkdir(); (self.root/"node_modules"/"ignored.py").write_text("x")
        (self.root/".env").write_text("secret"); self.engine=GlobEngine(self.root)
    def tearDown(self): self.tmp.cleanup()
    def test_recursive_pattern_matches_root_and_nested(self):
        result=self.engine.scan("**/*.py"); self.assertEqual([x["path"] for x in result["matches"]],["main.py","src/mod.py"]); self.assertTrue(result["read_only"])
    def test_default_exclusions_and_sensitive_names(self):
        paths=[x["path"] for x in self.engine.scan("**/*")["matches"]]
        self.assertNotIn("node_modules/ignored.py",paths); self.assertNotIn(".env",paths)
    def test_traversal_and_absolute_patterns_rejected(self):
        for p in ("../*.py","/etc/passwd","C:/secret",""):
            with self.assertRaises(ValueError): self.engine.scan(p)
    def test_limit_is_bounded(self):
        with self.assertRaises(ValueError): self.engine.scan("**/*",limit=5001)

class GlobBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)/"repo"; self.root.mkdir()
        subprocess.run(["git","init","-q",str(self.root)],check=True)
        subprocess.run(["git","-C",str(self.root),"config","user.email","test@example.invalid"],check=True)
        subprocess.run(["git","-C",str(self.root),"config","user.name","ERIA Test"],check=True)
        (self.root/"README.md").write_text("fixture"); subprocess.run(["git","-C",str(self.root),"add","README.md"],check=True)
        subprocess.run(["git","-C",str(self.root),"commit","-qm","fixture"],check=True)
        self.service=GlobBootstrap(self.root,Path(self.tmp.name)/"approvals.sqlite3")
    def tearDown(self): self.tmp.cleanup()
    def test_exact_approval_and_one_shot_create(self):
        req=self.service.create_request([{"path":"tools/new.py","content":"# approved\n"}],"reviewed bootstrap")
        with self.assertRaisesRegex(ValueError,"Exact new-file"): self.service.approve(req["request_id"],req["scope_sha256"],"yes")
        grant=self.service.approve(req["request_id"],req["scope_sha256"],req["confirmation_phrase"])
        self.assertFalse((self.root/"tools/new.py").exists()); result=self.service.apply(grant["grant_id"])
        self.assertEqual(result["status"],"CREATED"); self.assertFalse(result["git_staged"])
        with self.assertRaises(ValueError): self.service.apply(grant["grant_id"])
    def test_existing_path_cannot_be_overwritten(self):
        with self.assertRaisesRegex(ValueError,"new files only"): self.service.create_request([{"path":"README.md","content":"overwrite"}],"no")
    def test_head_change_invalidates_request(self):
        req=self.service.create_request([{"path":"new.txt","content":"x"}],"provenance")
        (self.root/"change.txt").write_text("x"); subprocess.run(["git","-C",str(self.root),"add","change.txt"],check=True); subprocess.run(["git","-C",str(self.root),"commit","-qm","advance"],check=True)
        with self.assertRaisesRegex(ValueError,"changed"): self.service.approve(req["request_id"],req["scope_sha256"],req["confirmation_phrase"])

if __name__=="__main__": unittest.main()
