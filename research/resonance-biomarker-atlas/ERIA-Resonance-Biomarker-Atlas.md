# ERIA: Resonance & Biological Systems Research Atlas

**Research synthesis | 15 November 2026**

> Educational research framework only. Not a clinical protocol, diagnosis, treatment recommendation, or claim that sound/frequency exposure reverses aging or controls biology.

## Executive synthesis

This atlas connects four research layers while keeping them distinct:

1. **Stimulus engineering:** frequency, waveform, amplitude, spectrum, modulation, timing, spatial field, and calibrated dose.
2. **Biological measurement:** electrical, mechanical, metabolic, molecular, physiological, or morphological signals.
3. **Statistical inference:** reliability, effect size, uncertainty, confounding, causal identification, and replication.
4. **Human governance:** consent, privacy, safety, provenance, independent review, and authorized repository changes.

A tunable signal is not automatically a biological intervention. A biological signal that changes is not automatically a beneficial outcome. A measurable left-right difference is not automatically disease.

## 1. Resonance, tuning, and living systems

In a physical system, resonance describes enhanced response under particular coupling conditions. The response depends on system modes, damping, geometry, boundary conditions, and the driving waveform. A sweep experiment can characterize a response curve, but the curve must name both the input and the measured output.

Living systems are complex, variable, nonlinear, and actively regulated. They should not be assumed to behave like one isolated oscillator. The term **resonate tuning** is operationalized here as reproducible input-response characterization, not as a search for a universal healing frequency.

A reproducible stimulus record should include:
- Frequency or spectrum, including harmonics and bandwidth.
- Waveform, modulation, and duty cycle.
- Calibrated amplitude/intensity at the target.
- Duration, onset/offset, repetition, and timing.
- Device, firmware, playback route, distance, coupling, and environment.
- Sensor channel, calibration, sampling rate, and uncertainty.

**Resonance is not entrainment.** Entrainment requires evidence of synchronization to a periodic driver, not merely a spectral peak or transient response. Phase relationships, credible controls, replication, and artifact checks are needed.

Sound pressure waves, music, infrasound, ultrasound, and electromagnetic or optical exposures are different modalities. They have different measurement units, dose characteristics, and hazards. A frequency label alone cannot establish a tissue-level effect. Evidence that rhythmic auditory cueing helps a defined movement task does not prove that arbitrary tones or frequency sequences repair cells, lengthen telomeres, reverse aging, or treat disease.

### Research questions
- Does a calibrated stimulus alter a prespecified physiological feature compared with credible sham and silence?
- Is the effect frequency-specific, or explained by attention, expectation, loudness, breathing, movement, or stress?
- Does it persist after the stimulus ends and replicate on another day?
- Is there a dose-response relationship, threshold, saturation, or adverse response?
- Is the effect larger than instrument noise and test-retest variability?

## 2. Physiological signals and bioelectric measurement

A raw physiological trace may contain the target signal, movement artifacts, electrical interference, electrode drift, environmental noise, and processing artifacts. Preserve raw samples and document every transformation.

| Signal | Measures | Key considerations |
|---|---|---|
| EEG | Scalp voltage differences reflecting summed neural activity | Montage, reference, impedance, sampling, state, artifacts, expert interpretation |
| ECG | Electrical activity associated with cardiac cycles | Electrodes, sampling, beat detection, ectopic beats, rhythm context |
| HRV | Variation between normal heart beats | Clean NN intervals, posture, breathing, time, context, duration |
| EMG | Electrical activity associated with muscle activation | Placement, contraction state, cross-talk, motion |
| Respiration | Breathing frequency and pattern | Sensor method, posture, voluntary control, speech, exertion |
| Temperature/optical | Surface or tissue-related physical signals | Calibration, ambient conditions, perfusion, geometry, contact |

EEG is sensitive to electrode placement, reference, filtering, sampling, impedance, participant state, and artifact. IFCN/ILAE routine and sleep EEG standards describe technical recommendations; the 2023 consensus reports 256 Hz as a minimum sampling rate for routine EEG and recommends low electrode impedance. These standards are not a self-diagnosis guide and do not validate consumer headset interpretations.

An EEG frequency band is a descriptive signal feature, not a direct meter of intelligence, consciousness, healing, emotional truth, or a specific brain state in isolation.

HRV summarizes variation in intervals between successive normal beats. It is affected by autonomic regulation, respiration, posture, activity, circadian timing, medication, health status, age, and recording quality. Research recommendations support standardized short-term recordings (often five minutes) and adequate ECG sampling. HRV is not a universal score of wellness, resilience, vagal tone, or biological age.

When combining playback with EEG, ECG, respiration, or motion, use a shared time base or documented synchronization method. Bluetooth buffering and operating-system latency can introduce uncertain delays. Preserve exact stimulus file hashes and actual event markers.

## 3. Asymmetrical biological markers

“Asymmetrical bio markers” is not a single validated biomarker class. This atlas uses it as a proposed umbrella for bilateral differences, directional asymmetry, fluctuating asymmetry, and side-specific physiological features.

Three patterns must be distinguished:

- **Directional asymmetry:** a population-level tendency for one side to differ consistently from the other.
- **Antisymmetry:** measurements tend to favor one of two opposite forms rather than small deviations around zero.
- **Fluctuating asymmetry (FA):** small random deviations around a population mean near zero, sometimes investigated as a candidate indicator of developmental instability.

Candidate domains include morphology (paired lengths or landmarks), physiology (temperature, muscle activation, sensory threshold, perfusion), neurophysiology (lateralized activity in a defined task), and molecular sampling where tissue-specific sampling is justified. Behavioral laterality is a phenotype and should not automatically be called a biomarker.

For paired measurements (L) and (R):
- Signed difference: (D = R - L).
- Relative asymmetry: (AI = (R-L)/((R+L)/2)), when the denominator is meaningful.
- Log ratio: (ln(R/L)), for strictly positive values.

Signed differences preserve direction; absolute differences discard it. Choose the metric before analysis. Estimate measurement error with repeated blinded measurements, evaluate directional asymmetry and distribution shape, examine allometry, and consider age, handedness, injury, posture, and development when relevant.

A small left-right difference is not automatically pathology, diagnosis, stress, or an actionable target. Bodies are not perfectly symmetric. Avoid post-hoc selection of whichever asymmetry looks most striking.

## 4. Biomarker qualification and evidence discipline

The FDA BEST framework defines a biomarker as a measured characteristic indicating normal biological processes, pathogenic processes, or responses to exposure or intervention. Biomarker types include molecular, histologic, radiographic, and physiologic characteristics. The categories include susceptibility/risk, diagnostic, monitoring, prognostic, predictive, pharmacodynamic/response, and safety. A biomarker is not the same as how a person feels, functions, or survives.

### Context of use
Every proposed biomarker should specify:
- Exact measured characteristic and method.
- Biomarker category and intended decision.
- Population/model and conditions.
- Interpretation and action supported by the result.
- Analytical performance, uncertainty, and limitations.

FDA qualification guidance makes context of use central: evidence needs depend on the exact use. Qualification of a biomarker does not automatically qualify a particular test or device.

### Evidence ladder
1. **Concept:** biological rationale and alternative explanations.
2. **Analytical validity:** calibration, repeatability, reproducibility, range, detection limits, and error.
3. **Biological/clinical validity:** appropriate cohorts, prespecified analyses, confounder control, independent replication.
4. **Clinical utility:** meaningful decision value, feasibility, benefits, and harms.
5. **Qualified use:** evidence adequate for a narrow context of use and ongoing performance monitoring.

## 5. A staged research program

Begin with non-invasive observational and engineering work, not attempts to manipulate biology using unvalidated energy exposure.

| Phase | Work | Gate |
|---|---|---|
| A. Bench | Calibrate playback, sensors, clocks, and environmental instruments with known test signals | Traceable procedure and uncertainty |
| B. Reliability | Repeat measurements under standardized baseline conditions | Test-retest error, inter-rater reliability, artifact rates |
| C. Baseline | Prespecified physiology and context variables | Baseline distributions and confounder map |
| D. Controlled study | Only after safety/ethics review; randomized, counterbalanced stimulus/sham | Preregistered protocol, calibration, stop criteria |
| E. Replication | Independent sample, operator, or site | Reproducible effect and generalizability |

Example hypotheses:
- The acoustic stimulus can be reproduced within a prespecified tolerance.
- The chosen physiological feature has acceptable test-retest reliability.
- Stimulus and sham differ on one preregistered outcome after appropriate controls.
- A proposed bilateral index remains stable after blinded remeasurement and adjustment for scale and posture.

No hypothesis presupposes therapeutic benefit. Null results, failed replications, and abandoned hypotheses are valuable when preserved honestly.

## 6. Practical experiment record

Record a non-identifying study ID; stimulus file name and SHA-256; sample rate, bit depth, channels; playback device and firmware; output route and latency; calibrated sound level; microphone and calibration details; participant consent and protocol status; sensor model, placement, firmware, sampling rate; event markers; interruptions and discomfort; preprocessing and code version; exclusions; and reviewer/approval records.

Signal-processing sequence:
1. Inspect raw data before filtering.
2. Record filters, resampling, windows, and artifact rules.
3. Keep originals immutable; version derived files and scripts.
4. Estimate noise floor and SNR where applicable.
5. Analyze only domains justified by the hypothesis.
6. Test apparent synchronization against suitable surrogate or permutation controls.
7. Report exclusions, sensitivity analyses, adverse events, and null outcomes.

## 7. Safety, ethics, and human factors

Human studies require informed consent, privacy controls, proportionate risk assessment, and independent ethical review where applicable. Sound can cause discomfort or hearing injury at excessive levels. Electrical stimulation, lasers, bright light, and radiofrequency exposure are different hazards and should not be collapsed into “frequency” as if interchangeable.

Do not improvise high-intensity devices or expose the brain, eyes, or body to experimental settings based on this document. Define stopping criteria for discomfort, unexpected symptoms, equipment malfunction, and poor data quality. Protect biometric and physiological data; do not use experimental markers to diagnose, rank, employ, insure, or determine eligibility of individuals.

Photobiomodulation is a separate modality from sound resonance. A 2025 clinical consensus and umbrella review describe modality- and indication-specific evidence; certainty varies across outcomes. These reviews do not establish age reversal, telomere lengthening, or general systemic rejuvenation.

## 8. ERIA data architecture and governance

Suggested collection:
- `README.md`: scope, evidence labels, navigation.
- `figures/`: original diagrams with captions and provenance.
- `protocols/`: approved, versioned study protocols.
- `data-dictionary/`: units, field definitions, missingness, quality flags.
- `analysis/`: reproducible code, environments, synthetic fixtures.
- `evidence/`: references, claim-to-source map, review dates.
- `governance/`: approvals, access policy, change log.

Each dataset should preserve non-identifying study ID, source file hash, acquisition timestamp and timezone, device/firmware, calibration record, protocol version, consent/ethics status, transformation version, and lineage pointer. SHA-256 verifies byte integrity, not scientific accuracy.

Repository writes remain reviewable. Keep `main` protected; use the dedicated branch, validate hashes, and request human review before merge. Automated analysis is not authorization. Preserve provenance, test claims against evidence, make uncertainty visible, and keep privileged actions accountable to people.

## 9. Interpretation matrix

| Observation | Defensible interpretation | Avoid claiming |
|---|---|---|
| Spectral peak during playback | Recorded signal contains energy at that frequency in this setup | Tissue or brain has been healed |
| EEG band power changes | Processed scalp signal differs under defined conditions | Mental state or treatment benefit proven |
| HRV differs between sessions | Beat-interval variability differs under those conditions | Person is healthier or biologically younger |
| Paired measurement differs | A measured difference exists; error and context remain to be assessed | Asymmetry diagnoses disease |
| Group result is statistically significant | Data are incompatible with a specified null under model assumptions | Large, causal, useful, or replicated effect |

## 10. Roadmap and decision gates

1. Define operational terms and measurement units.
2. Build synthetic-data signal pipelines and tests.
3. Bench-calibrate sensors and playback.
4. Conduct blinded baseline repeatability work.
5. Prepare preregistered, ethics-reviewed protocol.
6. Conduct controlled study and independent replication.
7. Evaluate context of use and decision utility; retire unsupported markers.

## Core formulas

- Signed bilateral difference: (D=R-L).
- Relative asymmetry: (AI=(R-L)/((R+L)/2)).
- Log ratio: (ln(R/L)), for positive values.
- Power SNR in dB: (10\log_{10}(P_{signal}/P_{noise})).

Report effect sizes with confidence intervals, not p-values alone. Select reliability statistics appropriate to the design and report model assumptions.

## Selected references

1. FDA, [About Biomarkers and Qualification](https://www.fda.gov/drugs/biomarker-qualification-program/about-biomarkers-and-qualification).
2. FDA, [Context of Use](https://www.fda.gov/drugs/biomarker-qualification-program/context-use).
3. FDA, [Qualifying a Biomarker through the Biomarker Qualification Program](https://www.fda.gov/drugs/biomarker-qualification-program/qualifying-biomarker-through-biomarker-qualification-program).
4. Peltola et al. (2023), [Routine and sleep EEG: Minimum recording standards of the IFCN and ILAE](https://pmc.ncbi.nlm.nih.gov/articles/PMC10006292/), *Clinical Neurophysiology* 147:108-120.
5. Quintana et al. (2017), [Heart Rate Variability and Cardiac Vagal Tone in Psychophysiological Research](https://pmc.ncbi.nlm.nih.gov/articles/PMC5316555/).
6. ESC/NASPE Task Force (1996), [Heart rate variability: standards of measurement, physiological interpretation, and clinical use](https://doi.org/10.1111/j.1542-474X.1996.tb00275.x).
7. Maghfour et al. (2025), [Evidence-based consensus on the clinical application of photobiomodulation](https://pubmed.ncbi.nlm.nih.gov/40253006/), *Journal of the American Academy of Dermatology* 93(2):429-443.
8. (2025), [Effects of photobiomodulation on multiple health outcomes: an umbrella review](https://pubmed.ncbi.nlm.nih.gov/40770824/).
9. FDA/ICH E16 (2011), [Biomarkers related to drug or biotechnology product development](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/e16-biomarkers-related-drug-or-biotechnology-product-development-context-structure-and-format).

This is a scoped research synthesis, not an exhaustive systematic review. Formal studies and clinical or regulatory claims require current targeted literature review and expert review.
