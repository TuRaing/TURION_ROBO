"""Mic capture — records audio from the default microphone."""

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000  # Whisper expects 16kHz mono


def record(duration_seconds: float) -> np.ndarray:
    """Record a fixed `duration_seconds` of audio and return it as a float32 mono array."""
    audio = sd.rec(
        int(duration_seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    return audio.flatten()


def record_until_silence(
    max_seconds: float = 30,
    silence_duration: float = 1.5,
    calibration_seconds: float = 0.5,
    noise_multiplier: float = 3.0,
    min_threshold: float = 0.01,
    block_seconds: float = 0.1,
) -> np.ndarray:
    """Record from the mic until the speaker pauses for `silence_duration` seconds
    (or `max_seconds` is reached, as a safety cap). Avoids feeding Whisper long
    stretches of dead air, which causes hallucinated text.

    The first `calibration_seconds` of audio are used to measure the room's
    background noise level, so the silence threshold adapts to mic gain/room
    noise instead of using one fixed number.
    """
    block_size = int(block_seconds * SAMPLE_RATE)
    silence_blocks_needed = int(silence_duration / block_seconds)
    max_blocks = int(max_seconds / block_seconds)
    calibration_blocks = max(1, int(calibration_seconds / block_seconds))

    chunks = []
    silence_run = 0
    speech_started = False

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32") as stream:
        # Calibrate against ambient noise first.
        noise_levels = []
        for _ in range(calibration_blocks):
            block, _ = stream.read(block_size)
            block = block.flatten()
            chunks.append(block)
            noise_levels.append(np.max(np.abs(block)))
        noise_floor = float(np.mean(noise_levels)) if noise_levels else 0.0
        silence_threshold = max(min_threshold, noise_floor * noise_multiplier)

        for _ in range(max_blocks - calibration_blocks):
            block, _ = stream.read(block_size)
            block = block.flatten()
            chunks.append(block)

            is_loud = np.max(np.abs(block)) > silence_threshold
            if is_loud:
                speech_started = True
                silence_run = 0
            elif speech_started:
                silence_run += 1
                if silence_run >= silence_blocks_needed:
                    break

    return np.concatenate(chunks) if chunks else np.array([], dtype="float32")
