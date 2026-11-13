"""Deterministic mirror-arithmetic and oscillation diagnostics.

These functions inspect supplied values only. They do not read or mutate Git
branches, hardware, instruments, or runtime state. The main/round/master cycle
is a logical verification sequence, not a branch synchronization operation.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

LANE_CYCLE = ("main", "round", "master")


@dataclass(frozen=True)
class MirrorResult:
    expected_product: float
    forward_product: float
    reverse_product: float
    commutative_match: bool
    forward_matches_expected: bool
    reverse_matches_expected: bool
    defect_detected: bool


def _finite(value: float, field: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        raise ValueError(f"{field} must be a finite number")


def mirror_multiply(
    left: float,
    right: float,
    forward_product: float,
    reverse_product: float,
    *,
    rel_tol: float = 1e-12,
    abs_tol: float = 1e-12,
) -> MirrorResult:
    """Compare independently supplied L×R and R×L results against expectation."""
    for name, value in (
        ("left", left), ("right", right),
        ("forward_product", forward_product), ("reverse_product", reverse_product),
        ("rel_tol", rel_tol), ("abs_tol", abs_tol),
    ):
        _finite(value, name)
    if rel_tol < 0 or abs_tol < 0:
        raise ValueError("tolerances must be non-negative")
    expected = float(left) * float(right)
    _finite(expected, "expected_product")
    commutative = math.isclose(forward_product, reverse_product, rel_tol=rel_tol, abs_tol=abs_tol)
    forward_ok = math.isclose(forward_product, expected, rel_tol=rel_tol, abs_tol=abs_tol)
    reverse_ok = math.isclose(reverse_product, expected, rel_tol=rel_tol, abs_tol=abs_tol)
    return MirrorResult(
        expected, float(forward_product), float(reverse_product),
        commutative, forward_ok, reverse_ok,
        not (commutative and forward_ok and reverse_ok),
    )


def analyze_oscillation(samples: Sequence[float], *, tolerance: float = 1e-12) -> dict[str, object]:
    """Report alternating behavior and amplitude; never infer a physical cause."""
    if len(samples) < 3:
        raise ValueError("at least three samples are required")
    _finite(tolerance, "tolerance")
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    values = [float(value) for value in samples]
    for value in values:
        _finite(value, "sample")
    mean = sum(values) / len(values)
    centered = [value - mean for value in values]
    signs = [1 if value > tolerance else -1 if value < -tolerance else 0 for value in centered]
    nonzero = [sign for sign in signs if sign]
    crossings = sum(a != b for a, b in zip(nonzero, nonzero[1:]))
    alternating = len(nonzero) >= 3 and all(a != b for a, b in zip(nonzero, nonzero[1:]))
    amplitude = max(values) - min(values)
    return {
        "sample_count": len(values),
        "mean": mean,
        "peak_to_peak": amplitude,
        "sign_crossings": crossings,
        "alternating_about_mean": alternating,
        "oscillation_detected": alternating and amplitude > tolerance,
        "cause_determined": False,
    }


def audit_round_robin(lanes: Sequence[str]) -> dict[str, object]:
    """Check repeated main→round→master coverage without changing any branch."""
    if not lanes:
        raise ValueError("at least one lane is required")
    normalized = tuple(lanes)
    if any(lane not in LANE_CYCLE for lane in normalized):
        raise ValueError("lanes must be main, round, or master")
    complete_cycles = len(normalized) // len(LANE_CYCLE)
    expected = tuple(LANE_CYCLE[index % len(LANE_CYCLE)] for index in range(len(normalized)))
    ordered = normalized == expected
    return {
        "sequence": list(normalized),
        "complete_cycles": complete_cycles,
        "partial_cycle_lanes": list(normalized[complete_cycles * len(LANE_CYCLE):]),
        "order_valid": ordered,
        "branch_mutation_performed": False,
        "main_modified": False,
        "master_modified": False,
    }
