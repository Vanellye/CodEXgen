# Frequency measurement archive

Every original measurement is an immutable observation. New measurements grow from the original by creating child records; never edit the parent.

Preserve where available: measurement ID; parent measurement ID; measured value and unit; timestamp with timezone and clock source; instrument make/model and asset ID; calibration status/date; sampling rate; duration; resolution/bandwidth; uncertainty; waveform and source conditions; amplitude and units; modulation; environment; sensor/probe and placement; raw-data object ID and SHA-256; operator/process identity; protocol version; authorization/audit ID; and derivation links.

Keep raw samples separate from processed values. Missing values are unknown, not zero. Every average, spectrum, conversion, or interpretation must link to exact parent data and transformation/code version. Preserve units and significant precision.
