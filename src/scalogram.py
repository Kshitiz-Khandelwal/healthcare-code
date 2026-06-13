from __future__ import annotations

from pathlib import Path

import numpy as np
import pywt
from PIL import Image

from preprocessing import preprocess_selected_leads


DEFAULT_LEAD_INDICES = (0, 1, 10)  # I, II, V5 in standard 12-lead order
DEFAULT_LEAD_NAMES = ("I", "II", "V5")


def cwt_scalogram(
    signal: np.ndarray,
    fs: int = 500,
    wavelet: str = "cmor1.5-1.0",
    min_hz: float = 0.5,
    max_hz: float = 40.0,
    n_freqs: int = 128,
    target_size: tuple[int, int] = (224, 224),
) -> np.ndarray:
    freqs = np.linspace(min_hz, max_hz, n_freqs)
    scales = pywt.frequency2scale(wavelet, freqs / fs)
    coeffs, _ = pywt.cwt(signal, scales, wavelet, sampling_period=1 / fs)
    power = np.log1p(np.abs(coeffs) ** 2)
    power = (power - power.min()) / (power.max() - power.min() + 1e-8)
    image = (power * 255).astype(np.uint8)
    resized = Image.fromarray(image).resize(target_size, Image.Resampling.BILINEAR)
    return np.asarray(resized, dtype=np.uint8)


def build_3channel_scalogram(
    ecg_leads_first: np.ndarray,
    fs: int = 500,
    lead_indices: tuple[int, int, int] = DEFAULT_LEAD_INDICES,
    target_size: tuple[int, int] = (224, 224),
) -> np.ndarray:
    preprocessed = preprocess_selected_leads(ecg_leads_first, lead_indices=lead_indices, fs=fs)
    channels = [cwt_scalogram(lead, fs=fs, target_size=target_size) for lead in preprocessed]
    return np.stack(channels, axis=-1)


def save_scalogram_png(image: np.ndarray, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image).save(output_path)
    return output_path

