"""Tests for EEG segment I/O."""

from pathlib import Path

import numpy as np

from src.io import list_segments, load_segment, parse_filename


def test_parse_filename():
    path = Path("S1_1_15.txt")
    subject, class_id, segment_id = parse_filename(path)
    assert subject == "S1"
    assert class_id == 1
    assert segment_id == 15


def test_load_segment_shape(project_root: str):
    data_dir = Path(project_root) / "data" / "S1"
    path = data_dir / "S1_1_1.txt"
    x = load_segment(path)
    assert x.shape == (10240,)
    assert np.isfinite(x).all()


def test_list_segments_all(project_root: str):
    data_dir = Path(project_root) / "data"
    paths = list_segments(data_dir)
    assert len(paths) == 180


def test_list_segments_relax_focus(project_root: str):
    data_dir = Path(project_root) / "data"
    paths = list_segments(data_dir, classes=[1, 2])
    assert len(paths) == 120
