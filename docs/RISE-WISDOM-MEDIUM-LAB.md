# Rise & Shine + Wisdom + Medium Signal Lab

This forward integration adds an idempotent lifecycle-to-Wisdom bridge and a simulation-only medium-response engine.

- Rise/Wisdom: `python/olpirt/rise_wisdom_bridge.py` persists already-committed lifecycle revisions and optionally forwards new records to caller-supplied Wisdom and telemetry sinks. It is passive and opt-in.
- Haze + water: Beer-Lambert direct-beam transmission and simplified acoustic absorption models, with explicitly illustrative default coefficients.
- Digital signals: in-memory AM/PM/FM baseband simulations at 11 Hz and 1111 Hz; no physical output or network transmission.
- Gamma: passive idealized photon attenuation and expected detector-count model. It is not a dose calculator, radiation source design, or exposure guide.

Replace illustrative material coefficients only with measured, documented values. For physical experiments, use calibrated sensors, independent controls, and qualified facilities. Encoded data alone is not a mechanism for reorganizing matter or biological tissue.

Run: `PYTHONPATH=python python -m unittest discover -s tests -v`
