import tempfile
import unittest
import wave
import struct
from pathlib import Path

from tools.eria_quality_mixer import scan, mix_wav


class QualityMixerTests(unittest.TestCase):
    def test_assessment_records_hashes_and_does_not_modify_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "sample.py"
            source.write_text("def alpha():\n    eval('1 + 1')\n", encoding="utf-8")
            before = source.read_bytes()
            report = scan(root)
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(report["summary"]["files_assessed"], 1)
            self.assertEqual(report["findings"][0]["rule"], "ERIA001")
            self.assertEqual(len(report["files"][0]["sha256"]), 64)

    def test_audio_mix_is_peak_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inputs = []
            for n, value in enumerate((20000, 20000)):
                path = root / f"track{n}.wav"
                with wave.open(str(path), "wb") as w:
                    w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
                    w.writeframes(struct.pack("<hh", value, -value))
                inputs.append(path)
            out = root / "mix.wav"
            result = mix_wav(inputs, out)
            with wave.open(str(out), "rb") as w:
                samples = struct.unpack("<hh", w.readframes(2))
            self.assertLessEqual(max(map(abs, samples)), 32767)
            self.assertEqual(result["tracks"], [str(x) for x in inputs])

    def test_rejects_mismatched_audio(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = []
            for n, rate in enumerate((8000, 16000)):
                path = root / f"track{n}.wav"
                with wave.open(str(path), "wb") as w:
                    w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
                    w.writeframes(struct.pack("<h", 100))
                paths.append(path)
            with self.assertRaises(ValueError):
                mix_wav(paths, root / "out.wav")


if __name__ == "__main__":
    unittest.main()
