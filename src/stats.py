"""Statistical helpers for effect size and variability."""

from __future__ import annotations

import numpy as np


def cohens_d(group_a: np.ndarray, group_b: np.ndarray) -> float:
    """Cohen's d using pooled standard deviation."""
    a = np.asarray(group_a, dtype=np.float64)
    b = np.asarray(group_b, dtype=np.float64)
    if len(a) < 2 or len(b) < 2:
        return 0.0
    var_a = np.var(a, ddof=1)
    var_b = np.var(b, ddof=1)
    pooled = np.sqrt(((len(a) - 1) * var_a + (len(b) - 1) * var_b) / (len(a) + len(b) - 2))
    if pooled == 0:
        return 0.0
    return float((np.mean(a) - np.mean(b)) / pooled)


def coefficient_of_variation(x: np.ndarray) -> float:
    """Coefficient of variation (std / mean)."""
    arr = np.asarray(x, dtype=np.float64)
    mean = np.mean(arr)
    if mean == 0:
        return 0.0
    return float(np.std(arr, ddof=1) / abs(mean))
