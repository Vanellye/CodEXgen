"""Deterministic Sunflower generator for repetitive and circular workflows.

The generator proposes reusable templates; it never executes user workflows.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

GAMMA_SYMBOLS = {
    "Ɣ": "pattern family / root",
    "Ɣ₀": "observed source habit",
    "Ɣ₁": "repeated sequence",
    "Ɣ₂": "circular or recurring loop",
    "Ɣ₃": "normalized reusable template",
    "Ɣ✓": "human-reviewed candidate",
    "Ɣ!": "ambiguous or unsafe; stop for review",
}

@dataclass(frozen=True)
class HabitPattern:
    symbol: str
    kind: str
    steps: tuple[str, ...]
    occurrences: int
    suggestion: str
    requires_review: bool = True

    def to_dict(self) -> dict:
        result = asdict(self)
        result["steps"] = list(self.steps)
        return result


def _clean_steps(steps: Iterable[str]) -> tuple[str, ...]:
    cleaned = []
    for step in steps:
        value = re.sub(r"\s+", " ", str(step)).strip()
        if value:
            cleaned.append(value)
    return tuple(cleaned)


def analyze_habits(habits: Iterable[Iterable[str]], min_repeats: int = 2) -> list[HabitPattern]:
    """Find repeated ordered sequences and simple explicit cycles across habits."""
    if min_repeats < 2:
        raise ValueError("min_repeats must be at least 2")
    sequences = [_clean_steps(h) for h in habits]
    sequences = [s for s in sequences if s]
    counts = Counter(sequences)
    patterns: list[HabitPattern] = []
    for seq, count in sorted(counts.items(), key=lambda item: (item[0], -item[1])):
        if count >= min_repeats:
            patterns.append(HabitPattern(
                symbol="Ɣ₁", kind="repeated_sequence", steps=seq,
                occurrences=count,
                suggestion="Extract these steps into a named, user-triggered reusable routine.",
            ))
        # A sequence that returns to its opening step is a cycle candidate.
        if len(seq) >= 3 and seq[0].casefold() == seq[-1].casefold():
            patterns.append(HabitPattern(
                symbol="Ɣ₂", kind="cycle_candidate", steps=seq,
                occurrences=count,
                suggestion="Inspect the loop boundary; add an exit condition or consolidate duplicate work.",
            ))
    return patterns


class SunflowerGenerator:
    def __init__(self, min_repeats: int = 2):
        if min_repeats < 2:
            raise ValueError("min_repeats must be at least 2")
        self.min_repeats = min_repeats

    def build(self, habits: Iterable[Iterable[str]]) -> dict:
        patterns = analyze_habits(habits, self.min_repeats)
        return {
            "generator": "Sunflower",
            "version": 1,
            "symbols": GAMMA_SYMBOLS,
            "patterns": [p.to_dict() for p in patterns],
            "generated_templates": [
                {"symbol": "Ɣ₃", "name": f"routine_{i + 1}", "steps": list(p.steps),
                 "requires_human_review": True, "auto_execute": False}
                for i, p in enumerate(patterns) if p.kind == "repeated_sequence"
            ],
            "safety": {
                "analysis_only": True,
                "no_automatic_execution": True,
                "no_silent_data_mutation": True,
                "review_symbol": "Ɣ✓",
                "stop_symbol": "Ɣ!",
            },
        }

    def write(self, habits: Iterable[Iterable[str]], output: Path) -> Path:
        payload = json.dumps(self.build(habits), ensure_ascii=False, indent=2) + "\n"
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.exists() or output.read_text(encoding="utf-8") != payload:
            output.write_text(payload, encoding="utf-8", newline="\n")
        return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sunflower Ɣ workflow-pattern generator")
    parser.add_argument("input", type=Path, help="JSON file containing an array of step arrays")
    parser.add_argument("--out", type=Path, default=Path("sunflower-report.json"))
    parser.add_argument("--min-repeats", type=int, default=2)
    args = parser.parse_args(argv)
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or any(not isinstance(item, list) for item in raw):
        parser.error("input must be a JSON array of arrays of step strings")
    result = SunflowerGenerator(args.min_repeats).write(raw, args.out)
    print(f"Sunflower report generated: {result}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
