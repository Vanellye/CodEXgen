import tempfile, subprocess, unittest
from pathlib import Path
from engineering import EngineeringWorkspace, PolicyError

class EngineeringPolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"; self.root.mkdir()
        subprocess.run(["git","init","-b","feature/test"],cwd=self.root,check=True,capture_output=True)
        subprocess.run(["git","config","user.email","test@example.invalid"],cwd=self.root)
        subprocess.run(["git","config","user.name","Test"],cwd=self.root)
        (self.root/"sample.py").write_text("value = 1\n")
        subprocess.run(["git","add","."],cwd=self.root,check=True)
        subprocess.run(["git","commit","-m","fixture"],cwd=self.root,check=True,capture_output=True)
        self.ws=EngineeringWorkspace(str(self.root),str(Path(self.tmp.name)/"state"))
    def tearDown(self): self.tmp.cleanup()
    def test_read(self): self.assertEqual(self.ws.read("sample.py")["content"],"value = 1\n")
    def test_requires_approval(self):
        p=self.ws.propose("sample.py","value = 2\n","test")
        with self.assertRaises(PolicyError): self.ws.approve(p["id"],False)
        self.assertEqual((self.root/"sample.py").read_text(),"value = 1\n")
    def test_approved_write(self):
        p=self.ws.propose("sample.py","value = 3\n","approved test")
        self.assertEqual(self.ws.approve(p["id"],True)["status"],"applied")
    def test_stale_hash(self):
        p=self.ws.propose("sample.py","value = 4\n","stale test")
        (self.root/"sample.py").write_text("other = 9\n")
        with self.assertRaises(PolicyError): self.ws.approve(p["id"],True)
    def test_database_denied(self):
        with self.assertRaises(PolicyError): self.ws.read("data.sqlite3")
    def test_traversal_denied(self):
        with self.assertRaises(PolicyError): self.ws.read("../outside.py")

if __name__ == "__main__": unittest.main()
