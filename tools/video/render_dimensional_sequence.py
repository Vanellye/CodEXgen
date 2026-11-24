#!/usr/bin/env python3
"""Render the 1D–11D conceptual sequence locally with Pillow + FFmpeg; no cloud video service."""
from __future__ import annotations
import argparse, hashlib, json, math, os, shutil, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

STAGES = [
    ("1D", "LINE / ORIGIN", "A point extends into a line"),
    ("2D", "PLANE / RELATION", "A line unfolds into a coordinate plane"),
    ("3D", "VOLUME / FORM", "A plane folds into a translucent solid"),
    ("4D", "TIME / WORLDLINE", "A form leaves a temporal trail"),
    ("5D", "BRANCHING POSSIBILITIES", "One path branches into alternatives"),
    ("6D", "PARAMETER SPACE", "Branches become a parameter lattice"),
    ("7D", "FAMILIES OF GEOMETRY", "Nested surfaces reveal related forms"),
    ("8D", "TRANSFORMATION SPACE", "A shape continuously deforms"),
    ("9D", "SYMMETRY / INVARIANTS", "Transformations expose repeating structure"),
    ("10D", "UNIFIED ABSTRACT SPACE", "Earlier motifs coexist in one topology"),
    ("11D", "SYNTHESIS / HORIZON", "The motifs converge into a luminous horizon"),
]
VERSION = "1.0.0"

def font(size: int):
    for candidate in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                      "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()

def project(x, y, z, w, h, scale=1.0, angle=0.0):
    ca, sa = math.cos(angle), math.sin(angle)
    xr, yr = x*ca-z*sa, x*sa+z*ca
    perspective = 1.0 / (1.0 + yr*0.12)
    return (int(w/2 + xr*scale*perspective), int(h*0.53 - (y-yr*0.25)*scale*perspective))

def polygon(draw, points, fill, outline=(90,190,255,190), width=2):
    if len(points) >= 3:
        draw.polygon(points, fill=fill)
        draw.line(points+[points[0]], fill=outline, width=width, joint="curve")

def draw_geometry(layer, stage, t, w, h):
    d=ImageDraw.Draw(layer, "RGBA")
    cx,cy=w//2,int(h*.53); unit=min(w,h)*.22
    a=t*2*math.pi
    seed=(cx,cy)
    # The same central seed and light source persist through every stage.
    d.ellipse((cx-8,cy-8,cx+8,cy+8), fill=(210,245,255,255))
    d.ellipse((cx-20,cy-20,cx+20,cy+20), outline=(85,190,255,130), width=2)
    if stage == 0:
        d.line((cx-unit*1.5,cy,cx+unit*1.5,cy),fill=(100,210,255,230),width=5)
        x=cx-unit*1.5+3*unit*t
        d.ellipse((x-10,cy-10,x+10,cy+10),fill=(235,250,255,255))
    elif stage == 1:
        for i in range(-5,6):
            d.line((cx+i*unit/5,cy-unit,cx+i*unit/5,cy+unit),fill=(70,150,220,105),width=1)
            d.line((cx-unit,cy+i*unit/5,cx+unit,cy+i*unit/5),fill=(70,150,220,105),width=1)
        d.ellipse((cx-unit*.55,cy-unit*.55,cx+unit*.55,cy+unit*.55),outline=(120,220,255,230),width=4)
    else:
        n=4 if stage in (2,3,4,5,6,7,8,9,10) else 3
        size=unit*(.68+.08*math.sin(a))
        vertices=[]
        for i in range(n):
            theta=2*math.pi*i/n + a*.18
            vertices.append(project(math.cos(theta)*size,math.sin(theta)*size,0,w,h,1, a*.3))
        if stage == 2:
            top=[project(math.cos(2*math.pi*i/4+a*.12)*size,math.sin(2*math.pi*i/4+a*.12)*size,.5*size,w,h,1,a*.25) for i in range(4)]
            polygon(d,vertices,(35,115,190,24)); polygon(d,top,(35,115,190,22))
            for p,q in zip(vertices,top): d.line((p,q),fill=(100,205,255,190),width=3)
        elif stage == 3:
            for k in range(5):
                off=(k/4-.5)*unit*.65
                pts=[(x+off,y-off*.25) for x,y in vertices]
                d.line(pts+[pts[0]],fill=(95,195,255,150-k*18),width=3)
        elif stage == 4:
            for branch in range(5):
                theta=2*math.pi*branch/5
                end=(cx+math.cos(theta)*unit*1.45,cy+math.sin(theta)*unit*1.1)
                d.line((seed,end),fill=(80,175,255,80+int(90*t)),width=3)
                d.ellipse((end[0]-6,end[1]-6,end[0]+6,end[1]+6),fill=(170,225,255,220))
        elif stage == 5:
            for ring in range(1,5):
                rr=unit*ring/4
                for i in range(12):
                    th=2*math.pi*i/12+a*.12
                    p=(cx+math.cos(th)*rr,cy+math.sin(th)*rr)
                    d.ellipse((p[0]-3,p[1]-3,p[0]+3,p[1]+3),fill=(110,205,255,190))
            for i in range(12):
                th=2*math.pi*i/12+a*.12
                d.line((seed,(cx+math.cos(th)*unit,cy+math.sin(th)*unit)),fill=(75,150,220,90),width=1)
        elif stage == 6:
            for k in range(4):
                rr=unit*(.35+k*.2)
                box=(cx-rr,cy-rr*.65,cx+rr,cy+rr*.65)
                d.ellipse(box,outline=(100,195,255,150-k*18),width=3)
        elif stage == 7:
            pts=[]
            for i in range(80):
                th=2*math.pi*i/80
                rr=unit*(.48+.18*math.sin(5*th+a))
                pts.append((cx+math.cos(th)*rr,cy+math.sin(th)*rr*.72))
            d.line(pts+[pts[0]],fill=(105,210,255,230),width=4)
            for i in range(0,80,5): d.line((seed,pts[i]),fill=(80,160,235,80),width=1)
        elif stage == 8:
            for k in range(8):
                rr=unit*(.22+k*.1)
                d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=(90,185,255,170-k*12),width=2)
        elif stage == 9:
            for k in range(12):
                th=2*math.pi*k/12+a*.06
                p=(cx+math.cos(th)*unit,cy+math.sin(th)*unit)
                d.line((seed,p),fill=(95,185,255,125),width=2)
                d.ellipse((p[0]-7,p[1]-7,p[0]+7,p[1]+7),outline=(155,225,255,200),width=2)
        else:
            for k in range(1,8):
                rr=unit*k/7
                d.ellipse((cx-rr,cy-rr*.72,cx+rr,cy+rr*.72),outline=(90,185,255,115),width=2)
            for k in range(16):
                th=2*math.pi*k/16+a*.025
                p=(cx+math.cos(th)*unit*1.1,cy+math.sin(th)*unit*.8)
                d.line((seed,p),fill=(110,205,255,125),width=2)
    # Fine horizon/grid anchors ground the composition.
    d.line((int(w*.12),int(h*.82),int(w*.88),int(h*.82)),fill=(55,100,145,85),width=1)
    return layer

def render_frame(index, total, width, height, fps):
    stage=min(len(STAGES)-1,index//(total//len(STAGES)))
    local=index%(total//len(STAGES))
    span=max(1,total//len(STAGES))
    t=local/span
    bg=Image.new("RGBA",(width,height),(4,7,16,255))
    d=ImageDraw.Draw(bg,"RGBA")
    # Restrained atmospheric stars, deterministic from frame index.
    for k in range(70):
        x=(k*7919+index*13)%width; y=(k*3571+index*7)%height
        d.point((x,y),fill=(55,105,150,65))
    glow=Image.new("RGBA",(width,height),(0,0,0,0))
    draw_geometry(glow,stage,t,width,height)
    glow=glow.filter(ImageFilter.GaussianBlur(max(3,width//180)))
    bg=Image.alpha_composite(bg,glow)
    crisp=Image.new("RGBA",(width,height),(0,0,0,0))
    draw_geometry(crisp,stage,t,width,height)
    bg=Image.alpha_composite(bg,crisp)
    d=ImageDraw.Draw(bg,"RGBA")
    title_size=max(18,width//38); sub_size=max(12,width//85)
    d.text((int(width*.06),int(height*.075)),STAGES[stage][0],font=font(title_size),fill=(210,240,255,255))
    d.text((int(width*.06),int(height*.075)+title_size+8),STAGES[stage][1],font=font(sub_size),fill=(120,195,235,245))
    d.text((int(width*.06),int(height*.9)),STAGES[stage][2],font=font(max(11,width//100)),fill=(135,155,180,220))
    # Progress rail across the eleven stages.
    x0,x1=int(width*.06),int(width*.94); y=int(height*.96)
    d.line((x0,y,x1,y),fill=(35,65,90,180),width=3)
    px=x0+(x1-x0)*index/max(1,total-1)
    d.line((x0,y,px,y),fill=(90,195,255,230),width=4)
    return bg.convert("RGB")

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",default="artifacts/dimensional-1d-11d.mp4")
    ap.add_argument("--width",type=int,default=1280)
    ap.add_argument("--height",type=int,default=720)
    ap.add_argument("--fps",type=int,default=24)
    ap.add_argument("--seconds-per-stage",type=float,default=10)
    ap.add_argument("--crf",type=int,default=20)
    ap.add_argument("--preset",default="medium")
    args=ap.parse_args()
    if args.width<320 or args.height<180 or args.fps<1 or args.seconds_per_stage<=0:
        ap.error("width >= 320, height >= 180, fps >= 1 and seconds-per-stage > 0 required")
    if not shutil.which("ffmpeg"):
        ap.error("ffmpeg is required on PATH (install FFmpeg; no Runway/API required)")
    output=Path(args.output); output.parent.mkdir(parents=True,exist_ok=True)
    frames_per_stage=round(args.fps*args.seconds_per_stage)
    total=frames_per_stage*len(STAGES)
    command=["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24",
             "-s",f"{args.width}x{args.height}","-r",str(args.fps),"-i","-",
             "-an","-c:v","libx264","-pix_fmt","yuv420p","-preset",args.preset,
             "-crf",str(args.crf),"-movflags","+faststart",str(output)]
    started=time.time()
    proc=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for i in range(total):
            frame=render_frame(i,total,args.width,args.height,args.fps)
            proc.stdin.write(frame.tobytes())
            if (i+1)%max(1,args.fps*5)==0:
                print(f"Rendered {i+1}/{total} frames",file=sys.stderr,flush=True)
        proc.stdin.close()
        code=proc.wait()
        if code: raise subprocess.CalledProcessError(code,command)
    except Exception:
        if proc.poll() is None: proc.kill()
        raise
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    manifest={
        "status":"RENDERED","generator":"CodEXgen local Pillow/FFmpeg renderer",
        "generator_version":VERSION,"rendered_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
        "output":str(output),"sha256":digest,"bytes":output.stat().st_size,
        "width":args.width,"height":args.height,"fps":args.fps,
        "seconds_per_stage":args.seconds_per_stage,"stage_count":len(STAGES),
        "duration_seconds":round(total/args.fps,3),"frame_count":total,
        "source_commit":os.getenv("GITHUB_SHA") or os.getenv("SOURCE_COMMIT") or "UNRECORDED",
        "stages":[{"dimension":s[0],"title":s[1],"concept":s[2]} for s in STAGES],
        "interpretation":"Conceptual mathematical visualizations, not evidence of observed physical dimensions."
    }
    manifest_path=output.with_suffix(output.suffix+".manifest.json")
    manifest_path.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2))
if __name__=="__main__":
    main()
