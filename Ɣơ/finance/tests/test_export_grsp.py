import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "export-grsp.py"

def test_export_refuses_to_overwrite_source_ledger(tmp_path):
    source = tmp_path / "events.jsonl"
    source.write_text('{"event":"kept"}\n', encoding="utf-8")
    original = source.read_bytes()
    run = subprocess.run([sys.executable, str(SCRIPT), str(source), str(source)],
                         capture_output=True, text=True)
    assert run.returncode != 0
    assert "HOLD" in run.stderr
    assert source.read_bytes() == original

def test_export_writes_separate_grsp_and_preserves_ledger(tmp_path):
    source = tmp_path / "events.jsonl"
    target = tmp_path / "events.GRSP"
    raw = b'{"event":"kept"}\n'
    source.write_bytes(raw)
    run = subprocess.run([sys.executable, str(SCRIPT), str(source), str(target)],
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    result = json.loads(target.read_text(encoding="utf-8"))
    assert result["mode"] == "AUDIT_EXPORT_ONLY"
    assert result["record_count"] == 1
    assert source.read_bytes() == raw
