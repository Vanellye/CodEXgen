import subprocess,tempfile,unittest
from pathlib import Path
from tools.eria_quality_bridge import QualityBridge
from tools.eria_pons_approval import PonsApprovalService
from tools.eria_pact import PactRuntime,parse_program

class PactTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); base=Path(self.tmp.name); self.root=base/"repo"; self.root.mkdir()
  def g(*a): subprocess.run(["git","-C",str(self.root),*a],check=True,capture_output=True)
  g("init","-q"); g("config","user.email","test@example.invalid"); g("config","user.name","PACT Test"); g("branch","-M","feature/pact-test")
  (self.root/"a.py").write_text("def shared():\n    return 1\n")
  (self.root/"b.py").write_text("def shared():\n    return 2\n")
  g("add","a.py","b.py"); g("commit","-qm","fixture")
  q=QualityBridge(self.root,base/"source.sqlite3",base/"qualitative"); q.refresh(); self.ap=PonsApprovalService(q,self.root)
  prop=q.prepare_proposal("shared"); req=self.ap.create_request(prop["proposal_id"]); parent=self.ap.approve(req["request_id"],req["scope_sha256"],req["confirmation_phrase"])
  patch="diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -1,2 +1,2 @@\n def shared():\n-    return 1\n+    return 3\n"
  pr=self.ap.create_patch_request(parent["grant_id"],patch); pg=self.ap.approve_patch(pr["patch_request_id"],pr["patch_sha256"],pr["confirmation_phrase"])
  self.pg=pg["patch_grant_id"]; self.rt=PactRuntime(self.ap,"owner/repo")
 def tearDown(self): self.tmp.cleanup()
 def test_arbitrary_commands_rejected(self):
  with self.assertRaisesRegex(ValueError,"unsupported syntax"): parse_program("APPLY PATCH x\nRUN rm -rf /")
 def test_apply_and_commit_require_transaction_approval(self):
  src=f'APPLY PATCH {self.pg}\nCOMMIT MESSAGE "PACT approved change"\n'; r=self.rt.create_request(src)
  with self.assertRaisesRegex(ValueError,"confirmation phrase"): self.rt.approve(r["request_id"],r["plan_sha256"],"yes")
  grant=self.rt.approve(r["request_id"],r["plan_sha256"],r["confirmation_phrase"]); out=self.rt.execute(grant["grant_id"])
  self.assertEqual(out["status"],"COMPLETED"); self.assertEqual((self.root/"a.py").read_text(),"def shared():\n    return 3\n")
  msg=subprocess.run(["git","-C",str(self.root),"log","-1","--pretty=%s"],capture_output=True,text=True,check=True).stdout.strip()
  self.assertEqual(msg,"PACT approved change")
  with self.assertRaisesRegex(ValueError,"one-shot"):
   self.rt.execute(grant["grant_id"])
 def test_main_branch_is_prohibited(self):
  subprocess.run(["git","-C",str(self.root),"branch","-M","main"],check=True)
  with self.assertRaisesRegex(ValueError,"branch/HEAD changed|main/master writes are prohibited"):
   self.rt.create_request(f"APPLY PATCH {self.pg}\n")
if __name__=="__main__": unittest.main()
