from __future__ import annotations

import numpy as np
from scipy.signal import butter, filtfilt


def bandpass_filter(signal: np.ndarray, fs: int = 500, low_hz: float = 0.5, high_hz: float = 40.0, order: int = 4) -> np.ndarray:
    nyquist = fs / 2.0
    low = low_hz / nyquist
    high = high_hz / nyquist
    b, a = butter(order, [low, high], btype="band")
    return filtfilt(b, a, signal)


def zscore(signal: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    signal = np.asarray(signal, dtype=np.float32)
    return (signal - signal.mean()) / (signal.std() + eps)


def preprocess_lead(signal: np.ndarray, fs: int = 500) -> np.ndarray:
    filtered = bandpass_filter(signal, fs=fs)
    return zscore(filtered)


def preprocess_selected_leads(ecg_leads_first: np.ndarray, lead_indices: tuple[int, ...], fs: int = 500) -> list[np.ndarray]:
    return [preprocess_lead(ecg_leads_first[index], fs=fs) for index in lead_indices]

