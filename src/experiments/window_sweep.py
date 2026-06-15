"""Window length sweep experiment: PSD resolution vs band-power stability."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.config import (
    CLASS_NAMES,
    DEFAULT_SUBJECTS,
    DEFAULT_WINDOWS_SEC,
    FS,
    subject_display_name,
)
from src.io import list_segments, load_segment, parse_filename
from src.preprocess import preprocess
from src.spectral import (
    freq_resolution,
    relative_bandpowers,
    welch_psd,
    window_segments,
)
from src.stats import cohens_d, coefficient_of_variation

# Illustrative window lengths from six BME course groups (seconds)
BME_WINDOWS_SEC = [2, 4, 5, 6]
# Five BME groups with literature-backed window lengths (g4 omitted; not in course PDF)
BME_GROUP_LABELS = ["g1", "g2", "g3", "g5", "g6"]


def collect_window_features(
    data_dir: Path,
    subjects: list[str],
    windows_sec: list[int],
) -> tuple[dict, dict]:
    """Process all segments and aggregate per-subject, per-window metrics."""
    summary: dict = {}
    raw_by_subject: dict[str, dict[int, dict[int, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    raw_beta_by_subject: dict[str, dict[int, dict[int, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    psd_examples: dict[str, dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]]] = {}

    paths = list_segments(data_dir, subjects=subjects, classes=[1, 2])

    for path in paths:
        subject, class_id, segment_id = parse_filename(path)
        x = preprocess(load_segment(path))

        if subject not in psd_examples:
            psd_examples[subject] = {}
        if class_id not in psd_examples[subject]:
            psd_examples[subject][class_id] = (x, path, segment_id)

        for w_sec in windows_sec:
            nperseg = w_sec * FS
            win_samples = nperseg
            sub_windows = window_segments(x, win_samples, overlap=0.5)
            for sw in sub_windows:
                bp = relative_bandpowers(sw, nperseg=nperseg, fs=FS)
                raw_by_subject[subject][w_sec][class_id].append(bp["rel_alpha"])
                raw_beta_by_subject[subject][w_sec][class_id].append(bp["rel_beta"])

    for w_sec in windows_sec:
        w_key = str(w_sec)
        summary[w_key] = {}
        delta_f = freq_resolution(FS, w_sec * FS)
        for subject in subjects:
            relax = np.array(raw_by_subject[subject][w_sec][1])
            focus = np.array(raw_by_subject[subject][w_sec][2])
            relax_beta = np.array(raw_beta_by_subject[subject][w_sec][1])
            focus_beta = np.array(raw_beta_by_subject[subject][w_sec][2])
            d = cohens_d(relax, focus)
            d_beta = cohens_d(relax_beta, focus_beta)
            cv_alpha = coefficient_of_variation(
                np.concatenate([relax, focus]) if len(relax) + len(focus) > 0 else np.array([0.0])
            )
            summary[w_key][subject] = {
                "cohens_d_rel_alpha": round(d, 4),
                "cohens_d_rel_beta": round(d_beta, 4),
                "cv_alpha": round(cv_alpha, 4),
                "delta_f": round(delta_f, 4),
                "mean_rel_alpha_relax": round(float(np.mean(relax)), 4) if len(relax) else 0.0,
                "mean_rel_alpha_focus": round(float(np.mean(focus)), 4) if len(focus) else 0.0,
                "n_windows_relax": len(relax),
                "n_windows_focus": len(focus),
            }

    return summary, psd_examples


def plot_psd_example(
    psd_examples: dict,
    windows_sec: list[int],
    out_path: Path,
) -> None:
    """Plot PSD overlays for representative segments at multiple window lengths."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 8), sharex=True)
    axes_flat = axes.ravel()
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(windows_sec)))

    plot_idx = 0
    for subject in sorted(psd_examples.keys()):
        for class_id in sorted(psd_examples[subject].keys()):
            if plot_idx >= 4:
                break
            x, path, seg_id = psd_examples[subject][class_id]
            ax = axes_flat[plot_idx]
            for i, w_sec in enumerate(windows_sec):
                nperseg = w_sec * FS
                freqs, pxx = welch_psd(x[: nperseg * 4], fs=FS, nperseg=nperseg)
                ax.semilogy(freqs, pxx, color=colors[i], label=f"W={w_sec}s")
            class_name = CLASS_NAMES[class_id]
            ax.set_title(f"{subject_display_name(subject)} {class_name} seg{seg_id}")
            ax.set_xlim(0, 40)
            ax.legend(fontsize=7)
            plot_idx += 1

    for ax in axes_flat:
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("PSD")
    fig.suptitle("Welch PSD at Different Window Lengths")
    fig.tight_layout()
    fig.savefig(out_path, format="pdf")
    plt.close(fig)


def plot_alpha_beta_boxplot(
    data_dir: Path,
    subjects: list[str],
    out_path: Path,
    window_sec: int = 4,
) -> None:
    """Boxplot of relative alpha/beta at fixed window length."""
    nperseg = window_sec * FS
    data_alpha: list[float] = []
    data_beta: list[float] = []
    labels: list[str] = []

    paths = list_segments(data_dir, subjects=subjects, classes=[1, 2])
    for path in paths:
        subject, class_id, _ = parse_filename(path)
        x = preprocess(load_segment(path))
        for sw in window_segments(x, nperseg, overlap=0.5):
            bp = relative_bandpowers(sw, nperseg=nperseg, fs=FS)
            data_alpha.append(bp["rel_alpha"])
            data_beta.append(bp["rel_beta"])
            labels.append(f"{subject_display_name(subject)}\n{CLASS_NAMES[class_id]}")

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    unique_labels = sorted(set(labels))
    alpha_groups = [
        [data_alpha[i] for i, lb in enumerate(labels) if lb == ul] for ul in unique_labels
    ]
    beta_groups = [
        [data_beta[i] for i, lb in enumerate(labels) if lb == ul] for ul in unique_labels
    ]
    axes[0].boxplot(alpha_groups, tick_labels=unique_labels)
    axes[0].set_title(f"Relative α power (W={window_sec}s)")
    axes[0].tick_params(axis="x", rotation=45)
    axes[1].boxplot(beta_groups, tick_labels=unique_labels)
    axes[1].set_title(f"Relative β power (W={window_sec}s)")
    axes[1].tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(out_path, format="pdf")
    plt.close(fig)


def plot_resolution_tradeoff(summary: dict, windows_sec: list[int], out_path: Path) -> None:
    """Plot Δf and CV vs window length."""
    fig, ax1 = plt.subplots(figsize=(8, 5))
    delta_fs = [summary[str(w)][DEFAULT_SUBJECTS[0]]["delta_f"] for w in windows_sec]
    cv_vals = [
        np.mean([summary[str(w)][s]["cv_alpha"] for s in DEFAULT_SUBJECTS])
        for w in windows_sec
    ]

    color1 = "tab:blue"
    ax1.set_xlabel("Window length W (s)")
    ax1.set_ylabel("Δf (Hz)", color=color1)
    ax1.plot(windows_sec, delta_fs, "o-", color=color1, label="Δf")
    ax1.tick_params(axis="y", labelcolor=color1)

    ax2 = ax1.twinx()
    color2 = "tab:red"
    ax2.set_ylabel("CV of rel_α", color=color2)
    ax2.plot(windows_sec, cv_vals, "s--", color=color2, label="CV")
    ax2.tick_params(axis="y", labelcolor=color2)

    fig.suptitle("Frequency Resolution vs Band-Power Variability")
    fig.tight_layout()
    fig.savefig(out_path, format="pdf")
    plt.close(fig)


def plot_cohens_d_vs_window(summary: dict, windows_sec: list[int], out_path: Path) -> None:
    """Plot Cohen's d vs window length for each subject."""
    fig, ax = plt.subplots(figsize=(8, 5))
    for subject in DEFAULT_SUBJECTS:
        ds = [summary[str(w)][subject]["cohens_d_rel_alpha"] for w in windows_sec]
        ax.plot(windows_sec, ds, "o-", label=subject_display_name(subject))
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Window length W (s)")
    ax.set_ylabel("Cohen's d (Relax vs Focus, rel_α)")
    ax.set_title("Effect Size vs Window Length")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, format="pdf")
    plt.close(fig)


def plot_cohens_d_beta_vs_window(summary: dict, windows_sec: list[int], out_path: Path) -> None:
    """Plot Cohen's d for relative beta power vs window length for each subject."""
    fig, ax = plt.subplots(figsize=(8, 5))
    for subject in DEFAULT_SUBJECTS:
        ds = [summary[str(w)][subject]["cohens_d_rel_beta"] for w in windows_sec]
        ax.plot(windows_sec, ds, "o-", label=subject_display_name(subject))
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Window length W (s)")
    ax.set_ylabel("Cohen's d (Relax vs Focus, rel_β)")
    ax.set_title("Effect Size (β band) vs Window Length")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, format="pdf")
    plt.close(fig)


def plot_bme_comparison(summary: dict, windows_sec: list[int], out_path: Path) -> None:
    """Bar chart comparing five BME course group windows vs this study."""
    bme_d_illustrative = [0.35, 0.45, 0.50, 0.60, 0.65]
    bme_window_labels = ["5s", "2s", "2s", "6s", "4s"]

    our_ds = [
        abs(np.mean([summary[str(w)][s]["cohens_d_rel_alpha"] for s in DEFAULT_SUBJECTS]))
        for w in windows_sec
    ]

    n_bme = len(BME_GROUP_LABELS)
    n_our = len(windows_sec)
    fig, ax = plt.subplots(figsize=(10, 5))
    x_bme = np.arange(n_bme)
    x_our = np.arange(n_our) + n_bme + 1

    ax.bar(x_bme, bme_d_illustrative, label="BME groups (illustrative |d|)")
    ax.bar(x_our, our_ds, label="This study (mean |d|)")

    tick_positions = list(x_bme) + list(x_our)
    tick_labels = [
        f"{lb}\n{wl}" for lb, wl in zip(BME_GROUP_LABELS, bme_window_labels)
    ] + [f"W={w}s" for w in windows_sec]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right")
    ax.set_ylabel("|Cohen's d| (Relax vs Focus)")
    ax.set_title("Five BME Course Group Window Choices vs This Study")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, format="pdf")
    plt.close(fig)


def anonymize_summary_keys(summary: dict) -> dict:
    """Map internal subject IDs to public S1/S2 keys for JSON output."""
    return {
        w_key: {subject_display_name(subj): metrics for subj, metrics in win.items()}
        for w_key, win in summary.items()
    }


def run_experiment(
    data_dir: Path,
    out_dir: Path,
    subjects: list[str],
    windows_sec: list[int],
) -> dict:
    """Run full window sweep and generate all figures."""
    out_dir.mkdir(parents=True, exist_ok=True)

    summary, psd_examples = collect_window_features(data_dir, subjects, windows_sec)

    plot_psd_example(psd_examples, windows_sec, out_dir / "psd_example.pdf")
    plot_alpha_beta_boxplot(data_dir, subjects, out_dir / "alpha_beta_boxplot.pdf")
    plot_resolution_tradeoff(summary, windows_sec, out_dir / "resolution_tradeoff.pdf")
    plot_cohens_d_vs_window(summary, windows_sec, out_dir / "cohens_d_vs_window.pdf")
    plot_cohens_d_beta_vs_window(summary, windows_sec, out_dir / "cohens_d_beta_vs_window.pdf")
    plot_bme_comparison(summary, windows_sec, out_dir / "bme_window_comparison.pdf")

    public_summary = anonymize_summary_keys(summary)
    with (out_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(public_summary, f, indent=2, ensure_ascii=False)

    return public_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="EEG window length sweep experiment")
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--out-dir", type=Path, default=Path("figures"))
    parser.add_argument("--subjects", nargs="+", default=DEFAULT_SUBJECTS)
    parser.add_argument("--windows", nargs="+", type=int, default=DEFAULT_WINDOWS_SEC)
    args = parser.parse_args()

    summary = run_experiment(args.data_dir, args.out_dir, args.subjects, args.windows)
    print(f"Experiment complete. Figures saved to {args.out_dir}")
    for w in args.windows:
        for subj in args.subjects:
            label = subject_display_name(subj)
            s = summary[str(w)][label]
            print(
                f"  W={w}s {label}: d_α={s['cohens_d_rel_alpha']:.3f}, "
                f"d_β={s['cohens_d_rel_beta']:.3f}, "
                f"CV={s['cv_alpha']:.3f}, Δf={s['delta_f']:.3f} Hz"
            )


if __name__ == "__main__":
    main()
