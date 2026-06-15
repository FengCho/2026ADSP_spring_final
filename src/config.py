"""Project-wide constants for EEG window-length study."""

FS: int = 512
CLASS_NAMES: dict[int, str] = {1: "Relax", 2: "Focus", 3: "Blink"}
ALPHA_BAND: tuple[float, float] = (8.0, 13.0)
BETA_BAND: tuple[float, float] = (13.0, 30.0)
DEFAULT_BANDPASS: tuple[float, float] = (1.0, 40.0)
DEFAULT_SUBJECTS: list[str] = ["S1", "S2"]
SUBJECT_DISPLAY_NAMES: dict[str, str] = {
    "S1": "S1",
    "S2": "S2",
}
DEFAULT_WINDOWS_SEC: list[int] = [1, 2, 4, 6, 8]


def subject_display_name(subject_id: str) -> str:
    """Map internal data folder ID to anonymized report label."""
    return SUBJECT_DISPLAY_NAMES.get(subject_id, subject_id)
