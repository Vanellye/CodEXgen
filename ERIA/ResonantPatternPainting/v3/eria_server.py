#!/usr/bin/env python3
"""ERIA v3 localhost capture API and append-only PANTHEON review outbox."""
import argparse, base64, hashlib, json, math, re, threading, uuid
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT=Path(__file__).resolve().parent
WEB=ROOT/"web"; PAINT=ROOT/"paintings"; RECORDS=ROOT/"records"; OUTBOX=ROOT/"pantheon-outbox"
for p in (WEB,PAINT,RECORDS,OUTBOX): p.mkdir(parents=True,exist_ok=True)
LEDGER=RECORDS/"events.jsonl"; LOCK=threading.RLock()
RANGES={"rms":(0,1),"peak":(0,1),"centroid_hz":(0,96000),"dominant_hz":(0,96000),
"spectral_flux":(0,1),"zero_crossing_rate":(0,1),"low_band":(0,1),"mid_band":(0,1),"high_band":(0,1),
"brightness":(0,1),"stroke_count":(0,1000000),"point_count":(0,10000000),"canvas_width":(1,8192),"canvas_height":(1,8192)}
def stamp(): return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")
def sha(b): return hashlib.sha256(b).hexdigest()
def rows():
 if not LEDGER.exists(): return []
 with LOCK,LEDGER.open(encoding="utf-8") as f:
  out=[]
  for line in f:
   try: out.append(json.loads(line))
   except ValueError: pass
  return out
def append(r):
 with LOCK,LEDGER.open("a",encoding="utf-8") as f: f.write(json.dumps(r,sort_keys=True,separators=(",",":"))+"\n"); f.flush()
def features(v):
 if not isinstance(v,dict): raise ValueError("features must be an object")
 out={}
 for k,(lo,hi) in RANGES.items():
  if k not in v: continue
  n=v[k]
  if isinstance(n,bool) or not isinstance(n,(int,float)) or not math.isfinite(n) or not lo<=n<=hi: raise ValueError("invalid feature: "+k)
  out[k]=float(n)
 return out
def safe(rel):
 p=(ROOT/rel).resolve()
 if ROOT.resolve() not in p.parents: raise ValueError("invalid path")
 return p
def lookup(i): return next((r for r in rows() if r.get("id")==i),None)
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw): super().__init__(*a,directory=str(WEB),**kw)
 def log_message(self,*a): pass
 def sendj(self,code,obj):
  b=json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type","application/json"); self.send_header("Cache-Control","no-store"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
 def body(self):
  n=int(self.headers.get("Content-Length","0"))
  if n<0 or n>12*1024*1024: raise ValueError("request too large")
  v=json.loads(self.rfile.read(n) or b"{}")
  if not isinstance(v,dict): raise ValueError("JSON object required")
  return v
 def do_GET(self):
  u=urlparse(self.path)
  if u.path=="/api/health": return self.sendj(200,{"engine":"ERIA Resonant Pattern Painting","version":3,"status":"ready","microphone_audio_persisted":False})
  if u.path=="/api/history": return self.sendj(200,{"records":rows()[-200:]})
  if u.path=="/api/matches":
   try:
    q=features(json.loads(parse_qs(u.query).get("features",["{}"])[0])); m=[]
    for r in rows():
     old=r.get("features",{}); keys=set(q)&set(old)
     if keys: m.append({"id":r["id"],"similarity":round(100*sum(max(0,1-abs(q[k]-old[k])/(RANGES[k][1]-RANGES[k][0])) for k in keys)/len(keys),2)})
    return self.sendj(200,{"matches":sorted(m,key=lambda x:x["similarity"],reverse=True)[:10]})
   except Exception as e: return self.sendj(400,{"error":str(e)})
  if u.path=="/": self.path="/index.html"
  return super().do_GET()
 def do_POST(self):
  try: v=self.body()
  except Exception as e: return self.sendj(400,{"error":str(e)})
  try:
   p=urlparse(self.path).path
   if p=="/api/save":
    m=re.fullmatch(r"data:image/png;base64,([A-Za-z0-9+/=]+)",v.get("png_data_url",""))
    if not m: raise ValueError("PNG data URL required")
    b=base64.b64decode(m.group(1),validate=True)
    if not b.startswith(b"\x89PNG\r\n\x1a\n"): raise ValueError("invalid PNG")
    f=features(v.get("features",{})); i="paint_"+uuid.uuid4().hex; path=PAINT/(i+".png")
    with path.open("xb") as h: h.write(b)
    r={"id":i,"kind":"painting","created_at":stamp(),"file":str(path.relative_to(ROOT)),"sha256":sha(b),"bytes":len(b),"features":f,"style":str(v.get("style","abstract"))[:40],"microphone_audio_persisted":False}
    append(r); return self.sendj(201,r)
   if p=="/api/evolve":
    parent=lookup(v.get("parent_id")); op=v.get("operation"); params=v.get("params",{})
    if not parent or parent.get("kind") not in ("painting","transformation","reversal"): return self.sendj(404,{"error":"parent missing"})
    if op not in ("rotate","scale","mirror","hue-shift","opacity"): raise ValueError("unsupported operation")
    src=safe(parent["file"]); raw=src.read_bytes(); uri="data:image/png;base64,"+base64.b64encode(raw).decode()
    transform=style=""; inverse={}
    if op=="rotate":
     d=float(params.get("degrees",0)); transform=f"rotate({d} 600 600)"; inverse={"degrees":-d}
    elif op=="scale":
     n=float(params.get("factor",1)); 
     if not .01<=n<=100: raise ValueError("scale out of range")
     transform=f"translate(600 600) scale({n}) translate(-600 -600)"; inverse={"factor":1/n}
    elif op=="mirror":
     axis=params.get("axis","x")
     if axis not in ("x","y"): raise ValueError("axis must be x or y")
     transform="translate(1200 0) scale(-1 1)" if axis=="x" else "translate(0 1200) scale(1 -1)"; inverse={"axis":axis}
    elif op=="hue-shift":
     d=float(params.get("degrees",0)); style=f"filter:hue-rotate({d}deg)"; inverse={"degrees":-d}
    else:
     n=float(params.get("factor",1))
     if not .01<=n<=1: raise ValueError("opacity must be .01..1")
     style=f"opacity:{n}"; inverse={"factor":min(1,1/n)}
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200"><g transform="{transform}" style="{style}"><image href="{uri}" width="1200" height="1200"/></g></svg>'
    b=svg.encode(); i="evo_"+uuid.uuid4().hex; path=PAINT/(i+".svg")
    with path.open("x",encoding="utf-8") as h: h.write(svg)
    r={"id":i,"kind":"transformation","created_at":stamp(),"parent_id":parent["id"],"file":str(path.relative_to(ROOT)),"sha256":sha(b),"operation":op,"params":params,"inverse":inverse,"features":parent.get("features",{})}
    append(r); return self.sendj(201,r)
   if p=="/api/reverse":
    target=lookup(v.get("transformation_id"))
    if not target or target.get("kind")!="transformation": return self.sendj(404,{"error":"transformation missing"})
    parent=lookup(target["parent_id"]); src=safe(parent["file"]); b=src.read_bytes(); i="rev_"+uuid.uuid4().hex; out=PAINT/(i+src.suffix)
    with out.open("xb") as h: h.write(b)
    r={"id":i,"kind":"reversal","created_at":stamp(),"parent_id":target["id"],"reverted_to":parent["id"],"file":str(out.relative_to(ROOT)),"sha256":sha(b),"features":parent.get("features",{})}
    append(r); return self.sendj(201,r)
   if p=="/api/export-pantheon":
    rec=lookup(v.get("record_id"))
    if not rec: return self.sendj(404,{"error":"record missing"})
    src=safe(rec["file"]); f=features(rec.get("features",{})); d=rec["sha256"]; i="eria-"+uuid.uuid4().hex
    audio={k:x for k,x in f.items() if k in ("rms","peak","centroid_hz","dominant_hz","spectral_flux","zero_crossing_rate","low_band","mid_band","high_band")}
    painting={k:x for k,x in f.items() if k in ("brightness","stroke_count","point_count","canvas_width","canvas_height")}
    units={"rms":"normalized-amplitude","peak":"normalized-amplitude","centroid_hz":"Hz","dominant_hz":"Hz","spectral_flux":"normalized-relative-energy","zero_crossing_rate":"crossings-per-sample","low_band":"normalized-energy-ratio","mid_band":"normalized-energy-ratio","high_band":"normalized-energy-ratio","brightness":"normalized-luminance","stroke_count":"count","point_count":"count","canvas_width":"px","canvas_height":"px","artworkBytes":"byte"}
    env={"recordId":i,"schemaVersion":1,"source":"eria.resonant-pattern-painting","observedAt":stamp(),"payload":{"paintingRecordId":rec["id"],"artworkSha256":d,"artworkBytes":src.stat().st_size,"audioFeatures":audio,"paintingFeatures":painting,"style":rec.get("style","derived"),"microphoneAudioStored":False,"interpretationStatus":"descriptive-measurements-only"},"units":units,"quality":"UNCALIBRATED","provenance":{"sourceRef":rec["file"],"sourceDigest":d,"signer":None,"signatureStatus":"not_present"},"transformations":[],"authorization":{"status":"NOT_AUTHORIZED","scope":[],"approvalRef":None},"validation":{"engineVersion":"3.0.0","measurementBasis":"WebAudio-FFT","humanReviewRequired":"true","rawMicrophoneAudioPersisted":"false"},"retention":{"policy":"local-user-controlled","rawAudio":"not-collected-or-stored"}}
    b=json.dumps(env,sort_keys=True,indent=2).encode(); out=OUTBOX/(i+".json")
    with out.open("xb") as h: h.write(b)
    append({"id":i,"kind":"pantheon-envelope","file":str(out.relative_to(ROOT)),"sha256":sha(b),"painting_id":rec["id"],"authorization_status":"NOT_AUTHORIZED"})
    return self.sendj(201,{"envelope_id":i,"file":str(out.relative_to(ROOT)),"sha256":sha(b),"authorization_status":"NOT_AUTHORIZED","review_required":True})
   return self.sendj(404,{"error":"unknown endpoint"})
  except Exception as e: return self.sendj(400,{"error":str(e)})
def main():
 p=argparse.ArgumentParser(); p.add_argument("--host",default="127.0.0.1"); p.add_argument("--port",type=int,default=8765); a=p.parse_args()
 if a.host not in ("127.0.0.1","localhost","::1"): p.error("loopback only")
 print(f"ERIA v3: http://{a.host}:{a.port}",flush=True); ThreadingHTTPServer((a.host,a.port),H).serve_forever()
if __name__=="__main__": main()
