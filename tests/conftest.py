"""Shared test fixtures and synthetic signal helpers."""

from __future__ import annotations

import numpy as np
import pytest


def synthetic_eeg(
    duration_s: float,
    fs: int = 512,
    alpha_amp: float = 1.0,
    beta_amp: float = 0.5,
    noise_std: float = 0.2,
    seed: int = 42,
) -> np.ndarray:
    """Generate synthetic single-channel EEG with alpha and beta components."""
    rng = np.random.default_rng(seed)
    n = int(duration_s * fs)
    t = np.arange(n) / fs
    return (
        alpha_amp * np.sin(2 * np.pi * 10 * t)
        + beta_amp * np.sin(2 * np.pi * 20 * t)
        + noise_std * rng.standard_normal(n)
    )


@pytest.fixture
def project_root() -> str:
    from pathlib import Path

    return str(Path(__file__).resolve().parents[1])
