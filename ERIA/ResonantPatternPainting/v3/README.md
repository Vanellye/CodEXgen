# ERIA Resonant Pattern Painting v3

Fold-friendly Termux + Chrome engine. The Python server binds to loopback only; browser microphone capture is user-initiated and uses Web Audio FFT (4096-sample frame). Derived descriptors include RMS, peak, spectral centroid, dominant frequency, spectral flux, zero-crossing rate and low/mid/high band ratios.

## Termux

From the repository root on the phone:

```bash
pkg update && pkg install -y python
cd ERIA/ResonantPatternPainting/v3
python eria_server.py --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765` in Chrome. Grant microphone permission after tapping Start microphone. Keep Termux running. Stop with Ctrl+C.

## Preservation and pipeline

Original paintings are saved as PNG with SHA-256 digests. `records/events.jsonl` is append-only. Evolutions are new SVG children with parent IDs and inverse parameters; reversal creates a new copy. Pattern matching compares numeric feature vectors, not semantic image content.

Prepare PANTHEON review envelope writes a TRUE NORTH DataEnvelope-shaped JSON record under `pantheon-outbox/`. It is always `quality=UNCALIBRATED`, `authorization.status=NOT_AUTHORIZED`, unsigned, and requires human review. Raw microphone audio is never uploaded or persisted. No automatic Git push, external network transmission, device control or consequential action occurs.

## Device validation

No Fold7 hardware validation is implied by this source. Measure browser sample rate, microphone start/stop, permission persistence, touch latency, battery/thermal behavior and Termux process stability on the device. The descriptors are not calibrated SPL measurements or biological measurements.
