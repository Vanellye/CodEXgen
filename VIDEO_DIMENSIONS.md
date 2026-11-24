# CodEXgen — Video Dimensions & Dimensional Sequence

## Inspect existing videos
Requires Python 3.10+ and FFmpeg/ffprobe on PATH.

```bash
python -m pip install -r tools/video/requirements.txt
python tools/video/inspect_video.py --pretty path/to/clip.mp4
```

## Generate the 1D–11D film locally (no Runway)
This is a procedural renderer using Python, Pillow, and FFmpeg. It requires no Runway account, API key, cloud generation service, or paid video plan.

Install dependencies:
```bash
python -m pip install -r tools/video/requirements.txt
# Install FFmpeg using your OS package manager and ensure ffmpeg/ffprobe are on PATH.
```

Render the complete 110-second 16:9 film:
```bash
python tools/video/render_dimensional_sequence.py --output artifacts/dimensional-1d-11d.mp4
```

Render a quick preview:
```bash
python tools/video/render_dimensional_sequence.py --seconds-per-stage 2 --width 640 --height 360 --fps 12 --output artifacts/dimensional-preview.mp4
```

Customize resolution, frame rate, stage duration, encoder preset, and output path with command-line options. The renderer writes an adjacent JSON manifest containing the render parameters, stage list, source commit when available, duration, frame count, file size, and SHA-256 digest.

## Technical inspection
```bash
python tools/video/inspect_video.py --pretty artifacts/dimensional-1d-11d.mp4
```

## Storyboard and provenance
See `creative/dimensional-sequence-1-to-11.md`. The generated stages are conceptual visual metaphors for mathematical ideas, not claims that higher physical dimensions have been experimentally observed. No Runway task IDs or external media assets are required.
