#!/usr/bin/env python3
"""ERIA Resonant Pattern Painting v2 local server/API."""
from __future__ import annotations
import argparse, hashlib, json, threading, time
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT=Path(__file__).resolve().parent
WEB=ROOT/"web"; RECORDS=ROOT/"records"; PAINTINGS=ROOT/"paintings"
for folder in (WEB,RECORDS,PAINTINGS): folder.mkdir(parents=True,exist_ok=True)
LEDGER=RECORDS/"transformations.jsonl"; LOCK=threading.Lock()
def sha(data): return hashlib.sha256(data).hexdigest()
def rows():
    if not LEDGER.exists(): return []
    out=[]
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        try: out.append(json.loads(line))
        except ValueError: pass
    return out
def append(record):
    with LOCK,LEDGER.open("a",encoding="utf-8") as f: f.write(json.dumps(record,separators=(",",":"))+"\n")
def vector(obj):
    keys=("rms","peak","centroid_hz","dominant_hz","spectral_flux","brightness","saturation","edge_density","symmetry","complexity","tempo_bpm")
    return {k:float(obj[k]) for k in keys if isinstance(obj.get(k),(int,float))}
def similarity(a,b):
    ks=set(a)&set(b)
    if not ks:return 0.0
    return round(100*sum(1-min(1,abs(a[k]-b[k])/max(1,abs(a[k]),abs(b[k]))) for k in ks)/len(ks),2)
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=str(WEB),**kw)
    def log_message(self,fmt,*args): print("[ERIA] "+fmt%args)
    def reply(self,code,obj):
        data=json.dumps(obj).encode();self.send_response(code);self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(data)));self.end_headers();self.wfile.write(data)
    def do_GET(self):
        u=urlparse(self.path)
        if u.path=="/api/history":
            r=rows();return self.reply(200,{"count":len(r),"records":r[-250:]})
        if u.path=="/api/matches":
            q=parse_qs(u.query);f=vector(json.loads(q.get("features",["{}"])[0]))
            m=[{"id":r.get("id"),"similarity":similarity(f,r.get("features",{}))} for r in rows() if r.get("features")]
            return self.reply(200,{"matches":sorted(m,key=lambda x:x["similarity"],reverse=True)[:10]})
        if u.path=="/": self.path="/index.html"
        return super().do_GET()
    def do_POST(self):
        u=urlparse(self.path);n=int(self.headers.get("Content-Length","0"))
        if n>20_000_000:return self.reply(413,{"error":"payload too large"})
        try:o=json.loads(self.rfile.read(n) or b"{}")
        except ValueError:return self.reply(400,{"error":"invalid JSON"})
        if u.path=="/api/save":
            svg=o.get("svg","")
            if not isinstance(svg,str) or not svg.startswith("<svg"):return self.reply(400,{"error":"expected SVG"})
            data=svg.encode();ident="eria_"+str(int(time.time()*1000))+"_"+sha(data)[:8]
            path=PAINTINGS/(ident+".svg")
            with path.open("x",encoding="utf-8") as f:f.write(svg)
            meta=o.get("metadata",{});r={"id":ident,"kind":"painting","created_utc":datetime.now(timezone.utc).isoformat(),"file":str(path.relative_to(ROOT)),"sha256":sha(data),"features":vector(meta.get("features",{})),"metadata":meta}
            append(r);return self.reply(201,r)
        if u.path=="/api/evolve":
            parent=o.get("parent_id");op=o.get("operation");src=next((x for x in rows() if x.get("id")==parent),None)
            if not src:return self.reply(404,{"error":"parent not found"})
            if op not in ("rotate","scale","mirror","hue-shift","opacity"):return self.reply(400,{"error":"unsupported operation"})
            original=ROOT/src.get("file","")
            if not original.is_file():return self.reply(409,{"error":"parent artwork missing"})
            svg=original.read_text(encoding="utf-8");a=svg.find(">");b=svg.rfind("</svg>")
            if a<0 or b<=a:return self.reply(422,{"error":"malformed SVG"})
            p=o.get("params",{});inverse={};transform="";style=""
            if op=="rotate":
                d=float(p.get("degrees",0));transform=f"rotate({d} 600 600)";inverse={"degrees":-d}
            elif op=="scale":
                f=max(.01,min(100,float(p.get("factor",1))));transform=f"translate(600 600) scale({f}) translate(-600 -600)";inverse={"factor":1/f}
            elif op=="mirror":
                axis=p.get("axis","x");transform="translate(1200 0) scale(-1 1)" if axis=="x" else "translate(0 1200) scale(1 -1)";inverse={"axis":axis}
            elif op=="hue-shift":
                d=float(p.get("degrees",0));style=f"filter:hue-rotate({d}deg)";inverse={"degrees":-d}
            elif op=="opacity":
                f=max(.01,min(1,float(p.get("factor",1))));style=f"opacity:{f}";inverse={"factor":1/f}
            child=svg[:a+1]+f'<g transform="{transform}" style="{style}">'+svg[a+1:b]+"</g>"+svg[b:]
            data=child.encode();ident="evo_"+str(int(time.time()*1000))+"_"+sha(data)[:8];path=PAINTINGS/(ident+".svg")
            with path.open("x",encoding="utf-8") as f:f.write(child)
            r={"id":ident,"kind":"transformation","created_utc":datetime.now(timezone.utc).isoformat(),"parent_id":parent,"file":str(path.relative_to(ROOT)),"sha256":sha(data),"operation":op,"params":p,"inverse":inverse,"features":src.get("features",{})}
            append(r);return self.reply(201,r)
        if u.path=="/api/reverse":
            t=next((x for x in rows() if x.get("id")==o.get("transformation_id") and x.get("kind")=="transformation"),None)
            if not t:return self.reply(404,{"error":"transformation not found"})
            parent=next((x for x in rows() if x.get("id")==t.get("parent_id")),None)
            if not parent or not (ROOT/parent.get("file","")).is_file():return self.reply(409,{"error":"parent unavailable"})
            data=(ROOT/parent["file"]).read_bytes();ident="rev_"+str(int(time.time()*1000))+"_"+sha(data)[:8];path=PAINTINGS/(ident+".svg")
            with path.open("xb") as f:f.write(data)
            r={"id":ident,"kind":"transformation","created_utc":datetime.now(timezone.utc).isoformat(),"parent_id":t["id"],"reverted_to":parent["id"],"file":str(path.relative_to(ROOT)),"sha256":sha(data),"operation":"reverse-to-parent","features":parent.get("features",{})}
            append(r);return self.reply(201,r)
        return self.reply(404,{"error":"unknown endpoint"})
def main():
    p=argparse.ArgumentParser();p.add_argument("--host",default="127.0.0.1");p.add_argument("--port",type=int,default=8765);a=p.parse_args()
    print(f"ERIA v2: http://{a.host}:{a.port}");ThreadingHTTPServer((a.host,a.port),Handler).serve_forever()
if __name__=="__main__":main()
