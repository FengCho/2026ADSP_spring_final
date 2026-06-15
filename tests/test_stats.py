"""Tests for statistical helpers."""

import numpy as np

from src.stats import cohens_d, coefficient_of_variation


def test_cohens_d_known_values():
    group_a = np.array([2.0, 4.0, 6.0, 8.0])
    group_b = np.array([1.0, 2.0, 3.0, 4.0])
    d = cohens_d(group_a, group_b)
    # Manual pooled SD calculation
    var_a = np.var(group_a, ddof=1)
    var_b = np.var(group_b, ddof=1)
    pooled = np.sqrt(((3 * var_a + 3 * var_b) / 6))
    expected = (np.mean(group_a) - np.mean(group_b)) / pooled
    assert abs(d - expected) < 1e-10


def test_coefficient_of_variation():
    x = np.array([10.0, 12.0, 8.0, 10.0])
    cv = coefficient_of_variation(x)
    expected = np.std(x, ddof=1) / np.mean(x)
    assert abs(cv - expected) < 1e-10
