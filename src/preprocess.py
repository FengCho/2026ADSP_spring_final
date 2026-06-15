"""EEG preprocessing: DC removal and bandpass filtering."""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, sosfiltfilt

from src.config import DEFAULT_BANDPASS, FS


def remove_dc(x: np.ndarray) -> np.ndarray:
    """Remove DC offset by subtracting the mean."""
    return x - np.mean(x)


def bandpass(
    x: np.ndarray,
    low: float = DEFAULT_BANDPASS[0],
    high: float = DEFAULT_BANDPASS[1],
    order: int = 4,
    fs: int = FS,
) -> np.ndarray:
    """Apply zero-phase Butterworth bandpass filter."""
    sos = butter(order, [low, high], btype="bandpass", fs=fs, output="sos")
    return sosfiltfilt(sos, x)


def preprocess(x: np.ndarray) -> np.ndarray:
    """Standard pipeline: remove DC then 1–40 Hz bandpass."""
    return bandpass(remove_dc(x))
