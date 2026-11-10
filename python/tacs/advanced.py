"""TACS advanced operations. Writes are explicit, append-only, and never mount media."""
from __future__ import annotations
import hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path
from typing import Any,Iterable
from .core import SCHEMA_VERSION,TacsError,canonical_json_bytes,collect_tags,serialize_language_cadence

def _git(repo:Path,*args:str):
    try:return subprocess.run(["git","-C",str(repo),*args],check=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding="utf-8",errors="replace")
    except FileNotFoundError as exc:raise TacsError("git executable was not found") from exc

def verify_git_tag_signature(repository,tag_ref:str,trusted_signers:Iterable[str],ssh_allowed_signers_file=None)->dict[str,Any]:
    repo=Path(repository).expanduser().resolve()
    if not tag_ref.startswith("refs/tags/"):tag_ref="refs/tags/"+tag_ref
    if not re.fullmatch(r"refs/tags/[A-Za-z0-9._/-]+",tag_ref) or ".." in tag_ref.split("/"):raise TacsError("invalid tag ref")
    kind=_git(repo,"cat-file","-t",tag_ref)
    if kind.returncode or kind.stdout.strip()!="tag":raise TacsError("embedded signatures require an annotated tag")
    raw=_git(repo,"cat-file","-p",tag_ref)
    if raw.returncode:raise TacsError("could not read annotated tag object")
    if "-----BEGIN PGP SIGNATURE-----" not in raw.stdout and "-----BEGIN SSH SIGNATURE-----" not in raw.stdout:
        return {"valid":False,"reason":"unsigned","tag_ref":tag_ref,"signer":None}
    prefix=[]
    if ssh_allowed_signers_file is not None:
        allowed=Path(ssh_allowed_signers_file).expanduser().resolve()
        if not allowed.is_file():raise TacsError("SSH allowed-signers file does not exist")
        prefix=["-c","gpg.format=ssh","-c","gpg.ssh.allowedSignersFile="+str(allowed)]
    result=_git(repo,*prefix,"verify-tag","--raw",tag_ref)
    if result.returncode:return {"valid":False,"reason":"cryptographic_verification_failed","tag_ref":tag_ref,"signer":None,"diagnostic":(result.stderr or result.stdout).strip()[:1000]}
    output=(result.stdout or "")+"\n"+(result.stderr or "")
    gpg=set(x.upper() for x in re.findall(r"\[GNUPG:\]\s+VALIDSIG\s+([0-9A-Fa-f]+)",output))
    ssh=set(re.findall(r'Good "git" signature for ([^\s]+) with ',output))
    trusted={str(x).strip() for x in trusted_signers if str(x).strip()}
    matched=sorted(gpg.intersection({x.upper() for x in trusted}) or ssh.intersection(trusted))
    if not matched:return {"valid":False,"reason":"signer_not_allowlisted","tag_ref":tag_ref,"signer":sorted(gpg|ssh)}
    return {"valid":True,"reason":"cryptographically_valid_and_pinned","tag_ref":tag_ref,"signer":matched[0],"signature_type":"ssh" if ssh else "openpgp"}

def discover_removable_media()->list[dict[str,str]]:
    """Discover mounted removable devices only; never mounts/ejects/writes."""
    found=[]
    if sys.platform.startswith("linux"):
        info=Path("/proc/self/mountinfo")
        if not info.is_file():return found
        for line in info.read_text(encoding="utf-8",errors="replace").splitlines():
            fields=line.split()
            if "-" not in fields or len(fields)<7:continue
            sep=fields.index("-");mm=fields[2]
            mount=fields[4].replace("\\040"," ").replace("\\011","\t").replace("\\134","\\")
            source=fields[sep+2] if len(fields)>sep+2 else "unknown";removable=False
            try:
                device=(Path("/sys/dev/block")/mm).resolve()
                for parent in (device,*device.parents):
                    marker=parent/"removable"
                    if marker.is_file():removable=marker.read_text(encoding="ascii").strip()=="1";break
            except (OSError,RuntimeError):pass
            if removable:found.append({"mountpoint":mount,"source":source,"removable":"true"})
    elif sys.platform=="darwin":
        volumes=Path("/Volumes")
        if volumes.is_dir():
            for item in sorted(volumes.iterdir(),key=lambda p:p.name):
                if not item.is_mount():continue
                info=subprocess.run(["diskutil","info",str(item)],capture_output=True,text=True,check=False)
                if info.returncode==0 and re.search(r"Removable Media:\s*Removable",info.stdout,re.I):
                    found.append({"mountpoint":str(item.resolve()),"source":"diskutil","removable":"true"})
    elif os.name=="nt":
        import ctypes
        get_type=ctypes.windll.kernel32.GetDriveTypeW
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            root=letter+":\\"
            if os.path.exists(root) and get_type(root)==2:found.append({"mountpoint":root,"source":"windows-removable-drive","removable":"true"})
    return found

def append_correction(chain_directory,parent_record_path,source_tag_ref:str,resulting_target_object_id:str,reason:str,evidence:list[str],before:Any,after:Any,reviewer:str,tests:list[str],approved:bool)->dict[str,str]:
    if not approved:raise TacsError("correction write requires explicit approval")
    parent=Path(parent_record_path).expanduser().resolve()
    if not parent.is_file():raise TacsError("parent record does not exist")
    raw=parent.read_bytes()
    try:
        if not isinstance(json.loads(raw.decode("utf-8")),dict):raise TacsError("parent record must be a JSON object")
    except (UnicodeDecodeError,json.JSONDecodeError) as exc:raise TacsError("parent record is not valid UTF-8 JSON") from exc
    if not re.fullmatch(r"[0-9a-f]{40,64}",resulting_target_object_id):raise TacsError("resulting target must be a full Git object ID")
    if not source_tag_ref.startswith("refs/tags/"):source_tag_ref="refs/tags/"+source_tag_ref
    if not re.fullmatch(r"refs/tags/[A-Za-z0-9._/-]+",source_tag_ref):raise TacsError("invalid source tag ref")
    if not all(isinstance(x,str) and x.strip() for x in (reason,reviewer)):raise TacsError("reason and reviewer are required")
    if not isinstance(evidence,list) or not all(isinstance(x,str) and x.strip() for x in evidence):raise TacsError("evidence must be non-empty strings")
    if not isinstance(tests,list) or not all(isinstance(x,str) and x.strip() for x in tests):raise TacsError("tests must be non-empty strings")
    parent_digest=hashlib.sha256(raw).hexdigest()
    record={"schema_version":SCHEMA_VERSION,"record_type":"tacs-correction","parent_record_sha256":parent_digest,"source_tag_ref":source_tag_ref,"resulting_target_object_id":resulting_target_object_id,"reason":reason,"evidence":evidence,"before":before,"after":after,"reviewer":reviewer,"tests":tests,"approved":True}
    digest=hashlib.sha256(canonical_json_bytes(record)).hexdigest();record["record_sha256"]=digest
    payload=canonical_json_bytes(record);directory=Path(chain_directory).expanduser().resolve();directory.mkdir(parents=True,exist_ok=True);destination=directory/(digest+".json")
    try:fd=os.open(str(destination),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError as exc:raise TacsError("correction record already exists; refusing overwrite") from exc
    try:
        with os.fdopen(fd,"wb") as handle:handle.write(payload);handle.flush();os.fsync(handle.fileno())
    except Exception:
        try:destination.unlink()
        except OSError:pass
        raise
    return {"path":str(destination),"record_sha256":digest,"parent_record_sha256":parent_digest}

def _write_new(path:Path,content:bytes):
    fd=os.open(str(path),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,"wb") as handle:handle.write(content);handle.flush();os.fsync(handle.fileno())

def export_bundle(repository,metadata:Any,destination,confirmation:str,signature_path=None,public_key_path=None)->dict[str,str]:
    root=Path(destination).expanduser().resolve()
    if confirmation!=str(root):raise TacsError("destination confirmation must exactly match: "+str(root))
    mounts={str(Path(x["mountpoint"]).expanduser().resolve()) for x in discover_removable_media()}
    if str(root) not in mounts:raise TacsError("destination is not a detected mounted removable-media root")
    if not root.is_dir():raise TacsError("destination directory does not exist")
    metadata_bytes,metadata_digest=serialize_language_cadence(metadata);collected=collect_tags(repository)
    manifest={"schema_version":SCHEMA_VERSION,"bundle_type":"TACS-portable-provenance","repository":collected["repository"],"collector":collected["collector"],"tag_count":len(collected["tags"]),"tags":collected["tags"],"language_cadence_sha256":metadata_digest}
    manifest_bytes=canonical_json_bytes(manifest);manifest_digest=hashlib.sha256(manifest_bytes).hexdigest();bundle=root/"TACS";bundle.mkdir(mode=0o700)
    try:
        (bundle/"language").mkdir();(bundle/"records").mkdir()
        _write_new(bundle/"manifest.json",manifest_bytes);_write_new(bundle/"manifest.sha256",(manifest_digest+"\n").encode("ascii"))
        _write_new(bundle/"language"/"language-cadence.json",metadata_bytes)
        for item in collected["tags"]:_write_new(bundle/"records"/(item["record_sha256"]+".json"),canonical_json_bytes(item))
        if signature_path is not None:
            sig=Path(signature_path).expanduser().resolve()
            if not sig.is_file() or public_key_path is None:raise TacsError("signature and public key are both required")
            from .core import verify_ed25519_signature
            tmp=bundle/".manifest.verify.tmp";_write_new(tmp,manifest_bytes)
            try:valid=verify_ed25519_signature(tmp,sig,public_key_path)
            finally:tmp.unlink(missing_ok=True)
            if not valid:raise TacsError("provided detached signature is invalid")
            _write_new(bundle/"manifest.sig",sig.read_bytes());_write_new(bundle/"manifest.pub",Path(public_key_path).read_bytes())
        _write_new(bundle/"README.txt",b"TACS provenance bundle. Verify manifest.sha256 and manifest.sig when present.\n")
    except Exception:shutil.rmtree(bundle,ignore_errors=True);raise
    return {"bundle_path":str(bundle),"manifest_sha256":manifest_digest}

def promote_successor_tag(repository,correction_record_path,trusted_signers:Iterable[str],apply:bool=False,ssh_allowed_signers_file=None)->dict[str,Any]:
    path=Path(correction_record_path).expanduser().resolve()
    if not path.is_file():raise TacsError("correction record does not exist")
    try:record=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:raise TacsError("correction record is unreadable JSON") from exc
    if not isinstance(record,dict) or record.get("record_type")!="tacs-correction" or record.get("approved") is not True:raise TacsError("promotion requires an approved TACS correction record")
    digest=record.get("record_sha256");unsigned=dict(record);unsigned.pop("record_sha256",None)
    if digest!=hashlib.sha256(canonical_json_bytes(unsigned)).hexdigest():raise TacsError("correction record digest mismatch")
    repo=Path(repository).expanduser().resolve();verified=verify_git_tag_signature(repo,record["source_tag_ref"],trusted_signers,ssh_allowed_signers_file)
    if not verified["valid"]:raise TacsError("source tag signature is not trusted: "+verified["reason"])
    target=record.get("resulting_target_object_id")
    if _git(repo,"cat-file","-t",target).returncode:raise TacsError("corrected target object is missing")
    slug=re.sub(r"[^A-Za-z0-9._-]+","-",record["source_tag_ref"].split("/")[-1]).strip("-.") or "ancestral"
    name="tacs/"+slug+"/"+digest[:16];full_ref="refs/tags/"+name;exists=_git(repo,"show-ref","--verify","--quiet",full_ref)
    if exists.returncode==0:raise TacsError("successor tag already exists; refusing overwrite")
    if exists.returncode!=1:raise TacsError("could not determine successor tag availability")
    message="TACS verified successor\nSource: "+record["source_tag_ref"]+"\nCorrection-SHA256: "+digest+"\nParent-SHA256: "+record["parent_record_sha256"]+"\nSigner: "+str(verified["signer"])+"\n"
    plan={"source_tag_ref":record["source_tag_ref"],"successor_tag_ref":full_ref,"target_object_id":target,"source_signer":verified["signer"],"applied":False}
    if not apply:return plan
    created=_git(repo,"tag","-s","--cleanup=verbatim","-m",message,name,target)
    if created.returncode:raise TacsError("signed successor tag creation failed: "+(created.stderr or created.stdout).strip())
    plan["applied"]=True;return plan

def _main(argv=None):
    import argparse
    parser=argparse.ArgumentParser(prog="tacs-advanced");commands=parser.add_subparsers(dest="command",required=True)
    v=commands.add_parser("verify-tag");v.add_argument("--repo",default=".");v.add_argument("--tag",required=True);v.add_argument("--trusted-signer",action="append",required=True);v.add_argument("--ssh-allowed-signers-file")
    commands.add_parser("discover-media")
    c=commands.add_parser("correct");c.add_argument("--chain-dir",required=True);c.add_argument("--parent-record",required=True);c.add_argument("--source-tag-ref",required=True);c.add_argument("--target",required=True);c.add_argument("--reason",required=True);c.add_argument("--evidence",action="append",default=[]);c.add_argument("--before-json",required=True);c.add_argument("--after-json",required=True);c.add_argument("--reviewer",required=True);c.add_argument("--test",action="append",default=[]);c.add_argument("--approve",action="store_true")
    e=commands.add_parser("export");e.add_argument("--repo",default=".");e.add_argument("--metadata",required=True);e.add_argument("--destination",required=True);e.add_argument("--confirm-destination",required=True);e.add_argument("--signature");e.add_argument("--public-key")
    p=commands.add_parser("promote");p.add_argument("--repo",default=".");p.add_argument("--correction-record",required=True);p.add_argument("--trusted-signer",action="append",required=True);p.add_argument("--ssh-allowed-signers-file");p.add_argument("--apply",action="store_true")
    args=parser.parse_args(argv)
    try:
        if args.command=="verify-tag":result=verify_git_tag_signature(args.repo,args.tag,args.trusted_signer,args.ssh_allowed_signers_file)
        elif args.command=="discover-media":result=discover_removable_media()
        elif args.command=="correct":result=append_correction(args.chain_dir,args.parent_record,args.source_tag_ref,args.target,args.reason,args.evidence,json.loads(args.before_json),json.loads(args.after_json),args.reviewer,args.test,args.approve)
        elif args.command=="export":result=export_bundle(args.repo,json.loads(Path(args.metadata).read_text(encoding="utf-8")),args.destination,args.confirm_destination,args.signature,args.public_key)
        else:result=promote_successor_tag(args.repo,args.correction_record,args.trusted_signer,args.apply,args.ssh_allowed_signers_file)
        print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
        if args.command=="verify-tag" and not result.get("valid"):return 1
    except (TacsError,OSError,json.JSONDecodeError) as exc:print("tacs: "+str(exc),file=sys.stderr);return 2
    return 0
if __name__=="__main__":raise SystemExit(_main())
