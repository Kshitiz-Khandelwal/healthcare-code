from __future__ import annotations

import numpy as np
from scipy.signal import find_peaks
from scipy.stats import kurtosis, skew

from preprocessing import preprocess_lead


HANDCRAFTED_FEATURES = [
    "mean",
    "std",
    "max",
    "min",
    "energy",
    "zero_crossings",
    "skewness",
    "kurtosis",
    "peak_count",
    "heart_rate",
    "rr_mean",
    "hrv",
    "sdnn",
    "rmssd",
    "pnn50",
    "rr_range",
    "rr_cv",
]

MORPHOLOGY_FEATURES = [
    "qrs_width_proxy_mean",
    "qrs_width_proxy_std",
]


def extract_enhanced_handcrafted_features(
    signal: np.ndarray,
    fs: int = 500,
    include_morphology: bool = False,
) -> dict[str, float]:
    clean = preprocess_lead(signal, fs=fs)
    peaks, _ = find_peaks(clean, distance=int(0.3 * fs), height=0.5)

    duration = len(clean) / fs
    peak_count = len(peaks)
    heart_rate = (peak_count / duration) * 60 if duration > 0 else 0.0

    features: dict[str, float] = {
        "mean": float(np.mean(clean)),
        "std": float(np.std(clean)),
        "max": float(np.max(clean)),
        "min": float(np.min(clean)),
        "energy": float(np.sum(clean ** 2)),
        "zero_crossings": float(((clean[:-1] * clean[1:]) < 0).sum()),
        "skewness": float(skew(clean)),
        "kurtosis": float(kurtosis(clean)),
        "peak_count": float(peak_count),
        "heart_rate": float(heart_rate),
    }

    if len(peaks) > 1:
        rr_ms = np.diff(peaks) / fs * 1000.0
        rr_diff = np.diff(rr_ms)
        features.update(
            {
                "rr_mean": float(np.mean(rr_ms)),
                "hrv": float(np.std(rr_ms)),
                "sdnn": float(np.std(rr_ms)),
                "rmssd": float(np.sqrt(np.mean(rr_diff ** 2))) if len(rr_diff) else 0.0,
                "pnn50": float(np.mean(np.abs(rr_diff) > 50.0)) if len(rr_diff) else 0.0,
                "rr_range": float(np.max(rr_ms) - np.min(rr_ms)),
                "rr_cv": float(np.std(rr_ms) / (np.mean(rr_ms) + 1e-8)),
            }
        )
    else:
        features.update(
            {
                "rr_mean": 0.0,
                "hrv": 0.0,
                "sdnn": 0.0,
                "rmssd": 0.0,
                "pnn50": 0.0,
                "rr_range": 0.0,
                "rr_cv": 0.0,
            }
        )

    qrs_widths = []
    half_window = int(0.03 * fs)
    for peak in peaks:
        onset = max(0, peak - half_window)
        offset = min(len(clean), peak + half_window)
        qrs_widths.append((offset - onset) / fs * 1000.0)

    if include_morphology:
        features["qrs_width_proxy_mean"] = float(np.mean(qrs_widths)) if qrs_widths else 0.0
        features["qrs_width_proxy_std"] = float(np.std(qrs_widths)) if qrs_widths else 0.0
    return features
