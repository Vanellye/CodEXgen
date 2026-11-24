#!/usr/bin/env python3
"""Inspect video streams and report technical dimensions using ffprobe."""
import argparse, json, subprocess, sys
from fractions import Fraction
from pathlib import Path

def probe(path: str) -> dict:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Video file does not exist: {p}")
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=filename,format_name,duration,size,bit_rate:"
        "stream=index,codec_type,codec_name,profile,width,height,coded_width,coded_height,"
        "sample_aspect_ratio,display_aspect_ratio,avg_frame_rate,r_frame_rate,nb_frames,"
        "pix_fmt,bit_rate,duration,sample_rate,channels,channel_layout",
        "-of", "json", str(p)
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    if not video_streams:
        raise ValueError("No video stream found")
    for s in video_streams:
        rate = s.get("avg_frame_rate", "0/1")
        try:
            s["fps_numeric"] = round(float(Fraction(rate)), 6)
        except (ValueError, ZeroDivisionError):
            s["fps_numeric"] = None
        w, h = s.get("width"), s.get("height")
        s["aspect_ratio_numeric"] = round(w / h, 6) if w and h else None
        s["aspect_ratio_label"] = f"{w}:{h}" if w and h else None
    return {"format": data.get("format", {}), "streams": streams,
            "video_streams": video_streams}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("videos", nargs="+", help="Video paths")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    reports, failed = [], []
    for file in args.videos:
        try:
            reports.append({"file": file, **probe(file)})
        except Exception as exc:
            failed.append({"file": file, "error": str(exc)})
    output = {"reports": reports, "errors": failed}
    print(json.dumps(output, indent=2 if args.pretty else None))
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
