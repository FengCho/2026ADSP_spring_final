"""Smoke tests for window sweep experiment."""

import json
from pathlib import Path

import numpy as np

from src.experiments.window_sweep import run_experiment


def _write_synthetic_dataset(tmp_path: Path) -> Path:
    """Create minimal synthetic dataset matching filename contract."""
    data_dir = tmp_path / "data"
    fs = 512
    duration = 20
    n = fs * duration
    t = np.arange(n) / fs

    for subject in ["S1", "S2"]:
        subj_dir = data_dir / subject
        subj_dir.mkdir(parents=True)
        for class_id in [1, 2]:
            alpha_amp = 1.5 if class_id == 1 else 0.8
            for seg in range(1, 4):
                signal = (
                    alpha_amp * np.sin(2 * np.pi * 10 * t)
                    + 0.5 * np.sin(2 * np.pi * 20 * t)
                    + 0.1 * np.random.randn(n)
                )
                fname = subj_dir / f"{subject}_{class_id}_{seg}.txt"
                np.savetxt(fname, signal)

    return data_dir


def test_window_sweep_generates_figures(tmp_path: Path):
    data_dir = _write_synthetic_dataset(tmp_path)
    out_dir = tmp_path / "figures"
    summary = run_experiment(
        data_dir,
        out_dir,
        subjects=["S1", "S2"],
        windows_sec=[1, 2],
    )

    expected_pdfs = [
        "psd_example.pdf",
        "alpha_beta_boxplot.pdf",
        "resolution_tradeoff.pdf",
        "cohens_d_vs_window.pdf",
        "cohens_d_beta_vs_window.pdf",
        "bme_window_comparison.pdf",
    ]
    for name in expected_pdfs:
        assert (out_dir / name).exists(), f"Missing {name}"

    assert (out_dir / "summary.json").exists()
    with (out_dir / "summary.json").open(encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded == summary
    assert "1" in loaded
    assert "cohens_d_rel_alpha" in loaded["1"]["S1"]
    assert "cohens_d_rel_beta" in loaded["1"]["S1"]
    assert "S2" in loaded["1"]
