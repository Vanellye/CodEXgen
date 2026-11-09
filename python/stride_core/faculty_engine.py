"""Higher Faculties engine for Stride.

Implements measurable software capabilities: perception summaries, creative
recombination, bounded adaptive calibration, and signal-channel coordination.
This is not a model of human consciousness, supernatural powers, or biological
modulation. It emits structured digital recommendations only.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Any, Iterable


class FacultyInputError(ValueError):
    """Raised for malformed or out-of-range faculty inputs."""


@dataclass(frozen=True)
class PerceptionResult:
    feature_scores: dict[str, float]
    strongest_feature: str | None
    confidence: float
    uncertainty: float
    evidence_count: int


@dataclass(frozen=True)
class CreativeResult:
    concepts: tuple[str, ...]
    combinations: tuple[str, ...]
    seed_digest: str
    note: str


@dataclass(frozen=True)
class AdaptationResult:
    prediction: float
    observation: float
    prior_error: float
    corrected_prediction: float
    posterior_error: float
    gain: float


@dataclass(frozen=True)
class ChannelPlan:
    channel: str
    carrier_hz: float
    phase_degrees: float
    priority: float
    mode: str


def _number(name: str, value: Any, low: float, high: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FacultyInputError(f"{name} must be numeric")
    value = float(value)
    if not math.isfinite(value) or not low <= value <= high:
        raise FacultyInputError(f"{name} must be finite and within [{low}, {high}]")
    return value


def assess_perception(observations: dict[str, float], weights: dict[str, float] | None = None) -> PerceptionResult:
    """Rank supplied numeric features and report normalized evidence confidence."""
    if not isinstance(observations, dict) or not observations:
        raise FacultyInputError("observations must be a non-empty mapping")
    if len(observations) > 128:
        raise FacultyInputError("at most 128 features are supported")
    weights = weights or {}
    scores: dict[str, float] = {}
    for key, raw in observations.items():
        if not isinstance(key, str) or not key.strip() or len(key) > 80:
            raise FacultyInputError("feature names must be non-empty strings up to 80 chars")
        value = _number(f"observation[{key}]", raw, -1_000_000, 1_000_000)
        weight = _number(f"weight[{key}]", weights.get(key, 1.0), 0.0, 10.0)
        scores[key] = abs(value) * weight
    total = sum(scores.values())
    peak = max(scores.values())
    confidence = peak / total if total else 0.0
    return PerceptionResult(scores, max(scores, key=scores.get) if peak else None,
                            confidence, 1.0 - confidence, len(scores))


def generate_ideas(concepts: Iterable[str], max_combinations: int = 12) -> CreativeResult:
    """Create deterministic pairwise concept prompts; no claim of sentience."""
    clean = tuple(dict.fromkeys(str(x).strip() for x in concepts if str(x).strip()))
    if not 2 <= len(clean) <= 32:
        raise FacultyInputError("provide 2 to 32 non-empty concepts")
    if not isinstance(max_combinations, int) or not 1 <= max_combinations <= 64:
        raise FacultyInputError("max_combinations must be an integer from 1 to 64")
    payload = json.dumps(clean, ensure_ascii=False, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()
    pairs = []
    for i, left in enumerate(clean):
        for right in clean[i + 1:]:
            pairs.append(f"Explore how {left} could inform {right}")
            if len(pairs) >= max_combinations:
                break
        if len(pairs) >= max_combinations:
            break
    return CreativeResult(clean, tuple(pairs), digest,
                          "Idea prompts are synthetic suggestions requiring human review.")


def adapt_prediction(prediction: float, observation: float, gain: float = 0.25) -> AdaptationResult:
    """Apply a bounded scalar correction; this is a generic control primitive."""
    p = _number("prediction", prediction, -1_000_000, 1_000_000)
    o = _number("observation", observation, -1_000_000, 1_000_000)
    k = _number("gain", gain, 0.0, 1.0)
    error = o - p
    corrected = p + k * error
    return AdaptationResult(p, o, abs(error), corrected, abs(o - corrected), k)


def coordinate_channels(channels: Iterable[dict[str, Any]]) -> tuple[ChannelPlan, ...]:
    """Return a bounded digital channel plan; does not drive physical emitters."""
    items = list(channels)
    if not 1 <= len(items) <= 16:
        raise FacultyInputError("provide 1 to 16 channels")
    plans = []
    seen = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise FacultyInputError("each channel must be an object")
        name = item.get("name")
        if not isinstance(name, str) or not name.strip() or name in seen:
            raise FacultyInputError("channel names must be unique non-empty strings")
        seen.add(name)
        hz = _number("carrier_hz", item.get("carrier_hz"), 0.1, 1111.0)
        priority = _number("priority", item.get("priority", 1.0), 0.0, 1.0)
        mode = item.get("mode", "digital")
        if mode not in {"digital", "optical_model", "acoustic_model", "sensor_input"}:
            raise FacultyInputError("unsupported channel mode")
        plans.append(ChannelPlan(name, hz, (index * 360.0 / len(items)) % 360.0,
                                 priority, mode))
    return tuple(plans)


def run_faculty_suite(observations: dict[str, float], concepts: Iterable[str],
                      prediction: float, measured: float,
                      channels: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Compose the four faculties into one auditable, JSON-ready report."""
    perception = assess_perception(observations)
    creativity = generate_ideas(concepts)
    adaptation = adapt_prediction(prediction, measured)
    plan = coordinate_channels(channels)
    return {
        "framework": "higher_faculties_software_v1",
        "faculties": {
            "perception": asdict(perception),
            "creativity": asdict(creativity),
            "adaptive_intelligence": asdict(adaptation),
            "signal_coordination": [asdict(x) for x in plan],
        },
        "governance": {
            "execution": "digital planning only",
            "physical_emission": False,
            "biological_modulation_claim": False,
            "human_review_required": True,
        },
    }
