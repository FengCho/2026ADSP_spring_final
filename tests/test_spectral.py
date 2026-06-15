"""Tests for spectral analysis functions."""

import numpy as np
import pytest

from src.config import FS
from src.spectral import freq_resolution, relative_bandpowers, welch_psd


def test_freq_resolution():
    assert freq_resolution(512, 512) == 1.0
    assert freq_resolution(512, 2048) == 0.25


def test_pure_10hz_alpha_dominant():
    t = np.arange(FS * 4) / FS
    x = np.sin(2 * np.pi * 10 * t)
    result = relative_bandpowers(x, nperseg=FS, fs=FS)
    assert result["rel_alpha"] > result["rel_beta"]
    assert result["rel_alpha"] > 0.5


def test_welch_psd_shape():
    x = np.random.randn(FS * 2)
    freqs, pxx = welch_psd(x, fs=FS, nperseg=FS)
    assert len(freqs) == len(pxx)
    assert freqs[1] - freqs[0] == pytest.approx(1.0)
