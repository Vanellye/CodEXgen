"""Stride medium-interaction simulator: haze, water, optical/acoustic and gamma models.

All waveforms and detector events are synthetic software data. This module does not
control emitters, create ionizing radiation, or assert that encoded information
reorganizes matter or biological tissue.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json, math
from typing import Any

class ModelSafetyError(ValueError):
    """Raised when a simulation input is outside documented bounds."""

@dataclass(frozen=True)
class Medium:
    name: str
    extinction_per_m: float
    refractive_index: float
    acoustic_absorption_db_per_m: float

@dataclass(frozen=True)
class SignalSpec:
    frequency_hz: float = 11.0
    sample_rate_hz: int = 11000
    duration_s: float = 1.0
    amplitude: float = 0.5
    modulation: str = "am"

@dataclass(frozen=True)
class OpticalResult:
    medium: str
    path_length_m: float
    transmittance: float
    scattered_fraction: float
    refractive_index: float
    note: str

@dataclass(frozen=True)
class AcousticResult:
    medium: str
    path_length_m: float
    attenuation_db: float
    amplitude_ratio: float
    note: str

@dataclass(frozen=True)
class GammaResult:
    photon_energy_kev: float
    attenuation_coefficient_per_cm: float
    thickness_cm: float
    uncollided_transmission: float
    detector_efficiency: float
    expected_detected_counts: float
    note: str

@dataclass(frozen=True)
class SignalResult:
    frequency_hz: float
    sample_rate_hz: int
    duration_s: float
    sample_count: int
    peak: float
    rms: float
    digest_sha256: str
    samples: tuple[float, ...]

HAZE = Medium("haze/aerosol (illustrative)", 0.18, 1.0003, 0.02)
WATER = Medium("water (illustrative visible-light model)", 0.08, 1.333, 0.01)

def _finite(name: str, value: float, low: float, high: float) -> float:
    if not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ModelSafetyError(f"{name} must be finite and within [{low}, {high}].")
    return float(value)

def simulate_digital_signal(payload: dict[str, Any], spec: SignalSpec = SignalSpec()) -> SignalResult:
    """Create a bounded in-memory baseband waveform; no physical transmission occurs."""
    if not isinstance(payload, dict) or not payload:
        raise ValueError("payload must be a non-empty JSON object")
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    frequency = _finite("frequency_hz", spec.frequency_hz, 0.1, 1111.0)
    amplitude = _finite("amplitude", spec.amplitude, 0.0, 0.8)
    duration = _finite("duration_s", spec.duration_s, 0.01, 2.0)
    if spec.sample_rate_hz < 20 * frequency or spec.sample_rate_hz > 100_000:
        raise ModelSafetyError("sample_rate_hz must be >=20x carrier and <=100000")
    if spec.modulation not in {"am", "pm", "fm"}:
        raise ModelSafetyError("modulation must be am, pm, or fm")
    digest = hashlib.sha256(raw).hexdigest()
    count = int(spec.sample_rate_hz * duration)
    if count > 200_000:
        raise ModelSafetyError("sample count exceeds simulation cap")
    nibbles = [int(ch, 16) for ch in digest[:16]]
    samples = []
    for i in range(count):
        t = i / spec.sample_rate_hz
        envelope = nibbles[min(int(t * 16 / duration), 15)] / 15.0
        phase = 2 * math.pi * frequency * t
        if spec.modulation == "am":
            value = amplitude * (0.15 + 0.85 * envelope) * math.sin(phase)
        elif spec.modulation == "pm":
            value = amplitude * math.sin(phase + (envelope - 0.5) * math.pi)
        else:
            value = amplitude * math.sin(phase + 0.15 * math.sin(2 * math.pi * envelope * t))
        samples.append(value)
    peak = max((abs(v) for v in samples), default=0.0)
    rms = math.sqrt(sum(v * v for v in samples) / count) if count else 0.0
    return SignalResult(frequency, spec.sample_rate_hz, duration, count, peak, rms, digest, tuple(samples))

def optical_interaction(medium: Medium, path_length_m: float, incident_intensity: float = 1.0) -> OpticalResult:
    """Beer-Lambert direct-beam transmission; loss is not separated into scatter/absorption."""
    distance = _finite("path_length_m", path_length_m, 0.0, 1000.0)
    _finite("incident_intensity", incident_intensity, 0.0, 1_000_000.0)
    extinction = _finite("extinction_per_m", medium.extinction_per_m, 0.0, 100.0)
    transmission = math.exp(-extinction * distance)
    return OpticalResult(medium.name, distance, transmission, 1.0 - transmission,
                         medium.refractive_index,
                         "Illustrative direct-beam loss; scattering and absorption are not separated.")

def acoustic_interaction(medium: Medium, path_length_m: float, incident_amplitude: float = 1.0) -> AcousticResult:
    distance = _finite("path_length_m", path_length_m, 0.0, 1000.0)
    amplitude = _finite("incident_amplitude", incident_amplitude, 0.0, 1_000_000.0)
    coeff = _finite("acoustic_absorption_db_per_m", medium.acoustic_absorption_db_per_m, 0.0, 100.0)
    loss_db = coeff * distance
    ratio = 10 ** (-loss_db / 20.0)
    return AcousticResult(medium.name, distance, loss_db, amplitude * ratio,
                          "Simplified absorption-only model; no sound is emitted.")

def gamma_detector_model(photon_energy_kev: float, attenuation_coefficient_per_cm: float,
                         thickness_cm: float, emitted_photon_count: int,
                         detector_efficiency: float = 0.25) -> GammaResult:
    """Passive idealized attenuation/count estimate; no radiation source or dose control."""
    energy = _finite("photon_energy_kev", photon_energy_kev, 1.0, 10000.0)
    mu = _finite("attenuation_coefficient_per_cm", attenuation_coefficient_per_cm, 0.0, 100.0)
    thickness = _finite("thickness_cm", thickness_cm, 0.0, 1000.0)
    efficiency = _finite("detector_efficiency", detector_efficiency, 0.0, 1.0)
    if not isinstance(emitted_photon_count, int) or not 0 <= emitted_photon_count <= 10**12:
        raise ModelSafetyError("emitted_photon_count must be an integer from 0 to 10^12")
    transmission = math.exp(-mu * thickness)
    expected = emitted_photon_count * transmission * efficiency
    return GammaResult(energy, mu, thickness, transmission, efficiency, expected,
                       "Idealized uncollided-photon estimate; not dosimetry or radiation-source guidance.")

def run_medium_suite(payload: dict[str, Any], path_length_m: float = 1.0) -> dict[str, Any]:
    """Run haze and water models plus 11 Hz and 1111 Hz digital signal summaries."""
    signal_11 = simulate_digital_signal(payload, SignalSpec(frequency_hz=11.0))
    signal_1111 = simulate_digital_signal(payload, SignalSpec(frequency_hz=1111.0, sample_rate_hz=30000))
    return {
        "signals": {
            "11_hz": {k: v for k, v in asdict(signal_11).items() if k != "samples"},
            "1111_hz": {k: v for k, v in asdict(signal_1111).items() if k != "samples"},
        },
        "media": {
            "haze": {"optical": asdict(optical_interaction(HAZE, path_length_m)),
                     "acoustic": asdict(acoustic_interaction(HAZE, path_length_m))},
            "water": {"optical": asdict(optical_interaction(WATER, path_length_m)),
                      "acoustic": asdict(acoustic_interaction(WATER, path_length_m))},
        },
        "gamma": "Call gamma_detector_model with measured material-specific coefficients; passive simulation only.",
    }
