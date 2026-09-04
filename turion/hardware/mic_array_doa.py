"""
Direction-of-arrival (DOA) estimation for the 4-mic INMP441 array
(firmware/mic_array/mic_array.ino on the ESP32). Reads framed 4-channel PCM
over serial and estimates which direction a sound came from via GCC-PHAT
cross-correlation between mic pairs -- an angle the pan-tilt neck can turn
toward.

Not yet tested against real hardware. MIC_POSITIONS and the serial port name
need to be set once the mic array is physically built into the InMoov head.
"""
from __future__ import annotations

import struct

import numpy as np
import serial

FRAME_MAGIC = 0x4D494334
HEADER_FMT = "<IH"
HEADER_SIZE = struct.calcsize(HEADER_FMT)
SAMPLE_RATE = 8000
SOUND_SPEED_M_S = 343.0
SILENCE_THRESHOLD = 50.0  # mean abs sample value below this is treated as no signal

# Mic positions in metres, relative to the head's center. Placeholder spacing --
# update once the InMoov head is built and real mic positions are measured.
MIC_POSITIONS = {
    "front": (0.0, 0.04, 0.0),
    "back": (0.0, -0.04, 0.0),
    "left": (-0.04, 0.0, 0.0),
    "right": (0.04, 0.0, 0.0),
}
CHANNEL_ORDER = ("front", "back", "left", "right")


def open_serial(port: str, baud: int = 921600) -> serial.Serial:
    return serial.Serial(port, baudrate=baud, timeout=1.0)


def _read_frame(ser: serial.Serial) -> np.ndarray | None:
    """Reads one 4-channel frame, resyncing on the magic header if bytes were dropped."""
    header = ser.read(HEADER_SIZE)
    if len(header) < HEADER_SIZE:
        return None
    magic, n_samples = struct.unpack(HEADER_FMT, header)
    if magic != FRAME_MAGIC or n_samples == 0:
        return None
    payload = ser.read(n_samples * 4 * 2)
    if len(payload) < n_samples * 4 * 2:
        return None
    return np.frombuffer(payload, dtype="<i2").reshape(n_samples, 4).astype(np.float64)


def _gcc_phat(sig: np.ndarray, ref: np.ndarray, fs: int, max_tau: float) -> float:
    """Estimated time delay (seconds) of `sig` relative to `ref`, via GCC-PHAT."""
    n = sig.shape[0] + ref.shape[0]
    SIG = np.fft.rfft(sig, n=n)
    REF = np.fft.rfft(ref, n=n)
    cross = SIG * np.conj(REF)
    cross /= np.abs(cross) + 1e-10
    corr = np.fft.irfft(cross, n=n)
    max_shift = int(min(max_tau * fs, n // 2))
    corr = np.concatenate((corr[-max_shift:], corr[: max_shift + 1]))
    shift = int(np.argmax(np.abs(corr))) - max_shift
    return shift / float(fs)


def estimate_direction(samples: np.ndarray) -> float | None:
    """
    Given one frame of shape (n_samples, 4) in CHANNEL_ORDER, estimate the
    azimuth angle (degrees, 0 = front, positive = clockwise/right) the sound
    most likely came from. Returns None if the frame is too quiet to bother.
    """
    if np.abs(samples).mean() < SILENCE_THRESHOLD:
        return None

    channels = {name: samples[:, i] for i, name in enumerate(CHANNEL_ORDER)}

    baseline_fb = np.linalg.norm(
        np.subtract(MIC_POSITIONS["front"], MIC_POSITIONS["back"])
    )
    baseline_lr = np.linalg.norm(
        np.subtract(MIC_POSITIONS["left"], MIC_POSITIONS["right"])
    )

    tau_fb = _gcc_phat(channels["front"], channels["back"], SAMPLE_RATE, baseline_fb / SOUND_SPEED_M_S)
    tau_lr = _gcc_phat(channels["left"], channels["right"], SAMPLE_RATE, baseline_lr / SOUND_SPEED_M_S)

    x = np.clip(tau_lr * SOUND_SPEED_M_S / baseline_lr, -1.0, 1.0)
    y = np.clip(-tau_fb * SOUND_SPEED_M_S / baseline_fb, -1.0, 1.0)
    return float(np.degrees(np.arctan2(x, y)))


def direction_stream(ser: serial.Serial):
    """Generator yielding an estimated azimuth angle (or None) for each incoming frame."""
    while True:
        frame = _read_frame(ser)
        if frame is None:
            continue
        yield estimate_direction(frame)
