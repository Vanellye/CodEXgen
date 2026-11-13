# Transmission Audio Contract

## Flow

1. The sender places raw signed PCM16 audio bytes in a `TransmissionFrame`.
2. The frame's SHA-256 integrity is checked by the internal transceiver.
3. `WavAudioTransmissionEndpoint` converts the received payload to a standard RIFF/WAVE byte stream and can write it to a caller-selected local file.
4. `TransmissionAudioPlayer.play(file)` is a separate, explicit local playback action.

## PCM format

- Signed 16-bit little-endian PCM.
- 8 kHz through 192 kHz sample rate.
- Mono or stereo.
- Payload must contain complete sample frames.

The WAV writer does not resample, decode compressed audio, or synthesize missing samples. If the sender transmits compressed MP3/AAC/Opus bytes, those bytes must be decoded to PCM before this endpoint is used.

## Authorization and boundaries

Receiving a transmission does not create a file or start playback by itself. The caller must explicitly invoke `writeWavFile` to create a file and separately invoke `TransmissionAudioPlayer.play` to play it. Playback is local through Android's media stack. This implementation does not send audio to Bluetooth, a remote service, a webhook, or another device, and it does not change call-audio routing.

## Verification

`WavAudioTransmissionTest` verifies RIFF/WAVE headers, sample rate, payload length, malformed PCM rejection, and the in-memory transceiver-to-WAV path. Android-device playback still requires a device/emulator run.


## Registered frequency metadata

The repository-level nominal values `FREQ-556` (556 Hz), `FREQ-772` (772 Hz), and `FREQ-420` (420 Hz) are documented in the root `FREQUENCY-REGISTER.md`. Their presence here does not configure the PCM sample rate, synthesize tones, alter payloads, or select a playback route. They are not a complete signal specification.

The current transmission path remains payload-based: it accepts caller-supplied PCM16 samples and does not synthesize a waveform from these frequency labels. File creation and local playback remain separate explicit calls. No Bluetooth, remote, webhook, or physical output is enabled by this metadata.
