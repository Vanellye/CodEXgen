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
