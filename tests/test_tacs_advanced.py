import hashlib,json,subprocess,tempfile,unittest,shutil
from pathlib import Path
from unittest.mock import patch
from tacs import TacsError
from tacs.advanced import append_correction,discover_removable_media,export_bundle

def git(repo,*args):
    return subprocess.run(["git","-C",str(repo),*args],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True).stdout.strip()
def make_repo(root):
    git(root,"init","-q");git(root,"config","user.name","TACS Test");git(root,"config","user.email","tacs@example.invalid")
    (root/"seed.txt").write_text("ancestry\n",encoding="utf-8");git(root,"add","seed.txt");git(root,"commit","-qm","seed");git(root,"tag","lightweight")
def metadata():
    return {"schema_version":1,"language":{"schema_version":1,"tokens":[{"token_id":"rise","glyph":"ơ","pronunciation":"oh","gloss":"emergence","role":"state"}]},"cadence":{"schema_version":1,"phases":[{"index":0,"token_ids":["rise"],"beats":1}],"tempo":None}}

class TacsCorrectionTests(unittest.TestCase):
    def test_append_only_and_approval_gate(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);parent=root/"parent.json";parent.write_bytes(b'{"record_type":"ancestral-tag"}\n');chain=root/"chain"
            args=(chain,parent,"release","a"*40,"reason",["evidence"],{"old":1},{"new":1},"reviewer",["test"])
            with self.assertRaises(TacsError):append_correction(*args,False)
            result=append_correction(*args,True);path=Path(result["path"]);record=json.loads(path.read_text())
            self.assertEqual(record["record_sha256"],result["record_sha256"])
            self.assertEqual(record["parent_record_sha256"],hashlib.sha256(parent.read_bytes()).hexdigest())
            before=path.read_bytes()
            with self.assertRaises(TacsError):append_correction(*args,True)
            self.assertEqual(path.read_bytes(),before)
    def test_rejects_bad_parent_or_target(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);parent=root/"p";parent.write_text("bad")
            with self.assertRaises(TacsError):append_correction(root/"c",parent,"release","bad","reason",["e"],{},{},"r",["t"],True)

class TacsExportTests(unittest.TestCase):
    def test_bundle_is_digest_checked_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);repo=root/"repo";repo.mkdir();make_repo(repo);usb=root/"usb";usb.mkdir()
            with patch("tacs.advanced.discover_removable_media",return_value=[{"mountpoint":str(usb),"source":"/dev/mock","removable":"true"}]):
                result=export_bundle(repo,metadata(),usb,str(usb));bundle=Path(result["bundle_path"]);manifest=(bundle/"manifest.json").read_bytes()
                self.assertEqual(hashlib.sha256(manifest).hexdigest(),(bundle/"manifest.sha256").read_text().strip())
                self.assertTrue((bundle/"language"/"language-cadence.json").is_file())
                self.assertEqual(json.loads(manifest)["tag_count"],1)
                with self.assertRaises(FileExistsError):export_bundle(repo,metadata(),usb,str(usb))
    def test_requires_exact_destination_confirmation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with patch("tacs.advanced.discover_removable_media",return_value=[{"mountpoint":str(root),"source":"mock","removable":"true"}]):
                with self.assertRaises(TacsError):export_bundle(root,metadata(),root,"/wrong")

class TacsDiscoveryTests(unittest.TestCase):
    def test_discovery_is_read_only(self):
        result=discover_removable_media()
        self.assertIsInstance(result,list)
        self.assertTrue(all("mountpoint" in item and item["removable"]=="true" for item in result))


class TacsEmbeddedSignatureTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("gpg"), "GPG is required for embedded tag-signature integration test")
    def test_pinned_signed_tag_and_successor_promotion(self):
        import os
        from tacs.advanced import verify_git_tag_signature, promote_successor_tag
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);repo=root/"repo";repo.mkdir();home=root/"gnupg";home.mkdir(mode=0o700)
            old_home=os.environ.get("GNUPGHOME");os.environ["GNUPGHOME"]=str(home)
            try:
                subprocess.run(["gpg","--batch","--passphrase","","--quick-generate-key",
                    "TACS CI <tacs-ci@example.invalid>","ed25519","sign","0"],
                    check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                listing=subprocess.run(["gpg","--with-colons","--list-keys"],check=True,
                    stdout=subprocess.PIPE,text=True).stdout
                fingerprint=next(line.split(":")[9] for line in listing.splitlines() if line.startswith("fpr:"))
                target=make_repo(repo)
                git(repo,"config","user.signingkey",fingerprint)
                git(repo,"config","gpg.program","gpg")
                git(repo,"tag","-s","-m","signed release","release")
                verified=verify_git_tag_signature(repo,"release",[fingerprint])
                self.assertTrue(verified["valid"])
                self.assertEqual(verified["signer"],fingerprint)
                parent=root/"ancestral.json";parent.write_text('{"kind":"tag"}\n')
                correction=append_correction(root/"chain",parent,"release",target,
                    "reviewed correction",["test evidence"],{"state":"old"},{"state":"new"},
                    "ci-reviewer",["unit tests"],True)
                plan=promote_successor_tag(repo,correction["path"],[fingerprint],apply=False)
                self.assertFalse(plan["applied"])
                original=git(repo,"rev-parse","refs/tags/release")
                applied=promote_successor_tag(repo,correction["path"],[fingerprint],apply=True)
                self.assertTrue(applied["applied"])
                self.assertEqual(git(repo,"cat-file","-t",applied["successor_tag_ref"]),"tag")
                self.assertEqual(git(repo,"rev-parse","refs/tags/release"),original)
            finally:
                if old_home is None:os.environ.pop("GNUPGHOME",None)
                else:os.environ["GNUPGHOME"]=old_home

if __name__=="__main__":unittest.main()
