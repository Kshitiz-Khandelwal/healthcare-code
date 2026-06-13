from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.io import loadmat


NORMAL_CODES = {"426783006"}

ARRHYTHMIA_CODES = {
    "164889003",  # atrial fibrillation
    "164890007",
    "426177001",
}

LABEL_MAP = {
    0: "Normal",
    1: "Arrhythmia",
    2: "Other / Unknown",
}


@dataclass(frozen=True)
class ECGRecord:
    record_id: str
    mat_path: Path
    hea_path: Path
    age: int
    sex: int
    dx_codes: tuple[str, ...]
    label: int
    label_name: str
    sampling_frequency: int
    n_leads: int
    n_samples: int


def map_dx_to_label(dx_codes: Iterable[str]) -> int:
    codes = {str(code).strip() for code in dx_codes if str(code).strip()}
    if codes & NORMAL_CODES:
        return 0
    if codes & ARRHYTHMIA_CODES:
        return 1
    return 2


def _safe_int(value: str, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def parse_hea_file(hea_path: str | Path) -> dict:
    hea_path = Path(hea_path)
    lines = hea_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if not lines:
        raise ValueError(f"Empty header file: {hea_path}")

    header_parts = lines[0].split()
    record_id = header_parts[0]
    n_leads = _safe_int(header_parts[1], 12) if len(header_parts) > 1 else 12
    sampling_frequency = _safe_int(header_parts[2], 500) if len(header_parts) > 2 else 500
    n_samples = _safe_int(header_parts[3], 0) if len(header_parts) > 3 else 0

    age = -1
    sex = -1
    dx_codes: tuple[str, ...] = tuple()

    for line in lines:
        clean = line.strip()
        if clean.startswith("#Age:"):
            raw_age = clean.split(":", 1)[1].strip()
            age = int(raw_age) if raw_age.isdigit() else -1
        elif clean.startswith("#Sex:"):
            raw_sex = clean.split(":", 1)[1].strip().lower()
            if raw_sex == "male":
                sex = 1
            elif raw_sex == "female":
                sex = 0
        elif clean.startswith("#Dx:"):
            dx_raw = clean.split(":", 1)[1].strip()
            dx_codes = tuple(code.strip() for code in dx_raw.split(",") if code.strip())

    label = map_dx_to_label(dx_codes)
    return {
        "record_id": record_id,
        "age": age,
        "sex": sex,
        "dx_codes": dx_codes,
        "label": label,
        "label_name": LABEL_MAP[label],
        "sampling_frequency": sampling_frequency,
        "n_leads": n_leads,
        "n_samples": n_samples,
    }


def discover_records(dataset_root: str | Path, limit: int | None = None) -> list[ECGRecord]:
    dataset_root = Path(dataset_root)
    mat_paths = sorted(dataset_root.rglob("*.mat"))

    records: list[ECGRecord] = []
    for mat_path in mat_paths:
        if limit is not None and len(records) >= limit:
            break

        hea_path = mat_path.with_suffix(".hea")
        if not hea_path.exists():
            continue
        try:
            meta = parse_hea_file(hea_path)
        except Exception:
            continue

        if meta["n_samples"] <= 0:
            try:
                meta = {
                    **meta,
                    "n_samples": int(load_ecg_mat(mat_path).shape[1]),
                }
            except Exception:
                continue

        records.append(
            ECGRecord(
                record_id=meta["record_id"],
                mat_path=mat_path,
                hea_path=hea_path,
                age=meta["age"],
                sex=meta["sex"],
                dx_codes=meta["dx_codes"],
                label=meta["label"],
                label_name=meta["label_name"],
                sampling_frequency=meta["sampling_frequency"],
                n_leads=meta["n_leads"],
                n_samples=meta["n_samples"],
            )
        )
    return records


def load_ecg_mat(mat_path: str | Path) -> np.ndarray:
    mat = loadmat(mat_path)
    if "val" in mat:
        data = mat["val"]
    else:
        keys = [key for key in mat.keys() if not key.startswith("__")]
        if not keys:
            raise ValueError(f"No ECG array found in {mat_path}")
        data = mat[keys[0]]

    data = np.asarray(data, dtype=np.float32)

    # Return shape as (leads, samples). Many WFDB MATLAB files store (12, 5000).
    if data.ndim != 2:
        raise ValueError(f"Expected 2D ECG array, got shape {data.shape} in {mat_path}")
    if data.shape[0] > data.shape[1]:
        data = data.T
    return data

