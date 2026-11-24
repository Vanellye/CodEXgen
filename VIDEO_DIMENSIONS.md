# CodEXgen — Video Dimensions & Dimensional Sequence

## Inspect actual video files
Requires Python 3.10+ and FFmpeg/ffprobe on PATH.

```bash
python -m pip install -r tools/video/requirements.txt
python tools/video/inspect_video.py --pretty path/to/clip.mp4
```

The inspector reports codec, dimensions, coded dimensions, display aspect ratio, pixel format, frame rate, duration, bitrate, stream metadata, and audio details when present. It rejects files without a video stream and returns non-zero when any input fails.

## 1D–11D conceptual video sequence
See `creative/dimensional-sequence-1-to-11.md` for the storyboard, visual motifs, stage timings, and export specifications. Higher-dimensional stages are presented as conceptual visual metaphors, not claims of experimentally observed dimensions.

## Runway workflow
1. Generate each stage as a separate shot using the storyboard.
2. Keep one consistent seed motif, lighting direction, and geometric transition language.
3. Export all shots with matching frame rate and aspect ratio.
4. Run the inspector on every render and save JSON output as an artifact.
5. Store Runway task IDs, prompt versions, asset URLs, ffprobe reports, and source commit in the evidence manifest.
6. Do not mark a render successful until the media file exists and its inspector result is recorded.
