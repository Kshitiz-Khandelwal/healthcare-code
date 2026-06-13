from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def feature_list_hash(features: Iterable[str]) -> str:
    payload = "\n".join(str(feature) for feature in features).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_model_metadata(
    *,
    model_name: str,
    dataset_size: int,
    features: list[str],
    metrics: dict[str, Any],
    seed: int,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "model_name": model_name,
        "training_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_size": int(dataset_size),
        "feature_count": len(features),
        "feature_list_hash": feature_list_hash(features),
        "seed": int(seed),
        "metrics": metrics,
    }
    if extra:
        metadata.update(extra)
    return metadata


def save_json(payload: dict[str, Any], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_and_validate_metadata(
    metadata_path: str | Path,
    features: list[str],
) -> dict[str, Any]:
    metadata_path = Path(metadata_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    expected = metadata.get("feature_list_hash")
    actual = feature_list_hash(features)
    if expected != actual:
        raise ValueError(
            "Feature-list hash mismatch: model artifacts do not belong to the same "
            f"pipeline version. Expected {expected}, got {actual}."
        )
    return metadata

