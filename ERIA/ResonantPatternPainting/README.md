# ERIA Resonant Pattern Painting v2

This module adds a local Android-friendly painting interface and a Python HTTP server.

## Features
- Live microphone capture via browser `getUserMedia`.
- Real frequency-domain analysis using Web Audio `AnalyserNode` FFT data.
- Touch/mouse painting on a responsive canvas.
- Pattern matching against prior saved feature vectors.
- New immutable SVG child generations for rotate, scale, mirror, hue-shift and opacity.
- Reversal creates a new copy of the exact parent artwork; no parent is overwritten.
- Append-only JSONL transformation ledger.

## Termux
```bash
pkg install python
cd ~/CodEXgen/ERIA/ResonantPatternPainting
python eria_server.py --host 127.0.0.1 --port 8765
```
Open `http://127.0.0.1:8765` in Chrome on the same device and grant microphone permission. Localhost is used so browser microphone permission can be granted without exposing the server to the network.

## Git safety
This feature is isolated on `feature/eria-resonant-painting-v2`. It was created from `main`; no changes were made to `main`, and no merge or force-push was performed.

## Data and limitations
Microphone audio is analyzed in the browser and only derived numeric descriptors are sent to the local API when saving. Similarity scores compare numeric feature vectors; they are not semantic judgments. FFT features are artistic controls, not medical or biological measurements. Original SVG generations remain unchanged; evolution and reversal are recorded as new files.
