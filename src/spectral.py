"""Spectral analysis: Welch PSD, band power, and windowing."""

from __future__ import annotations

import numpy as np
from scipy.signal import welch

from src.config import ALPHA_BAND, BETA_BAND, DEFAULT_BANDPASS, FS


def freq_resolution(fs: int, nperseg: int) -> float:
    """Frequency resolution Δf = fs / nperseg."""
    return fs / nperseg


def welch_psd(
    x: np.ndarray,
    *,
    fs: int = FS,
    nperseg: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute Welch PSD with 50% overlap."""
    noverlap = nperseg // 2
    freqs, pxx = welch(x, fs=fs, nperseg=nperseg, noverlap=noverlap)
    return freqs, pxx


def bandpower(
    f: np.ndarray,
    pxx: np.ndarray,
    band: tuple[float, float],
) -> float:
    """Integrate PSD over a frequency band."""
    mask = (f >= band[0]) & (f <= band[1])
    if not np.any(mask):
        return 0.0
    return float(np.trapezoid(pxx[mask], f[mask]))


def relative_bandpowers(
    x: np.ndarray,
    *,
    nperseg: int,
    fs: int = FS,
) -> dict[str, float]:
    """Compute relative alpha, beta, and alpha/beta ratio."""
    freqs, pxx = welch_psd(x, fs=fs, nperseg=nperseg)
    total = bandpower(freqs, pxx, DEFAULT_BANDPASS)
    alpha = bandpower(freqs, pxx, ALPHA_BAND)
    beta = bandpower(freqs, pxx, BETA_BAND)
    if total <= 0:
        return {"rel_alpha": 0.0, "rel_beta": 0.0, "alpha_beta_ratio": 0.0}
    rel_alpha = alpha / total
    rel_beta = beta / total
    ratio = rel_alpha / rel_beta if rel_beta > 0 else 0.0
    return {
        "rel_alpha": rel_alpha,
        "rel_beta": rel_beta,
        "alpha_beta_ratio": ratio,
    }


def window_segments(
    x: np.ndarray,
    win_samples: int,
    overlap: float = 0.5,
) -> list[np.ndarray]:
    """Split signal into overlapping windows."""
    if win_samples <= 0:
        return []
    step = max(1, int(win_samples * (1.0 - overlap)))
    segments: list[np.ndarray] = []
    for start in range(0, len(x) - win_samples + 1, step):
        segments.append(x[start : start + win_samples])
    return segments
