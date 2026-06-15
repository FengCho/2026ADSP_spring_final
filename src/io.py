"""EEG segment I/O and filename parsing."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

_FILENAME_RE = re.compile(
    r"^(?P<subject>S[12])_(?P<class_id>[123])_(?P<segment_id>\d+)\.txt$"
)


def parse_filename(path: Path) -> tuple[str, int, int]:
    """Parse ``{subject}_{class}_{segment}.txt`` into components."""
    match = _FILENAME_RE.match(path.name)
    if match is None:
        msg = f"Unexpected filename format: {path.name}"
        raise ValueError(msg)
    return (
        match.group("subject"),
        int(match.group("class_id")),
        int(match.group("segment_id")),
    )


def load_segment(path: Path) -> np.ndarray:
    """Load a single EEG segment as a 1-D float array."""
    data = np.loadtxt(path, dtype=np.float64)
    return np.asarray(data, dtype=np.float64).ravel()


def list_segments(
    data_dir: Path,
    *,
    subjects: list[str] | None = None,
    classes: list[int] | None = None,
) -> list[Path]:
    """List segment files, optionally filtered by subject and class."""
    paths: list[Path] = []
    subject_set = set(subjects) if subjects is not None else None
    class_set = set(classes) if classes is not None else None

    for subject_dir in sorted(data_dir.iterdir()):
        if not subject_dir.is_dir():
            continue
        subject_id = subject_dir.name
        if subject_set is not None and subject_id not in subject_set:
            continue
        for path in sorted(subject_dir.glob("*.txt")):
            try:
                _, class_id, _ = parse_filename(path)
            except ValueError:
                continue
            if class_set is not None and class_id not in class_set:
                continue
            paths.append(path)
    return paths
