"""Tests for preprocessing pipeline."""

import numpy as np

from src.config import FS
from src.preprocess import bandpass, preprocess, remove_dc
from src.spectral import welch_psd
from tests.conftest import synthetic_eeg


def test_remove_dc():
    x = np.ones(1000) * 5.0 + np.random.randn(1000) * 0.01
    y = remove_dc(x)
    assert abs(np.mean(y)) < 0.01


def test_bandpass_energy_in_passband():
    x = synthetic_eeg(duration_s=4.0, fs=FS, seed=0)
    y = bandpass(remove_dc(x))
    freqs, pxx = welch_psd(y, fs=FS, nperseg=FS)
    in_band = (freqs >= 1) & (freqs <= 40)
    out_band = (freqs > 40) & (freqs <= FS / 2)
    energy_in = np.trapezoid(pxx[in_band], freqs[in_band])
    energy_out = np.trapezoid(pxx[out_band], freqs[out_band])
    assert energy_in > energy_out * 5


def test_preprocess_runs():
    x = synthetic_eeg(duration_s=2.0)
    y = preprocess(x)
    assert len(y) == len(x)
    assert np.isfinite(y).all()
