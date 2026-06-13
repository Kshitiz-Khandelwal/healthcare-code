from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def load_efficientnet_backbone(model_name: str, device: str | None = None):
    import torch
    from torch import nn
    from torchvision import models

    resolved_device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    if model_name == "efficientnet_b0":
        weights = models.EfficientNet_B0_Weights.DEFAULT
        model = models.efficientnet_b0(weights=weights)
        expected_dim = 1280
    elif model_name == "efficientnet_b4":
        weights = models.EfficientNet_B4_Weights.DEFAULT
        model = models.efficientnet_b4(weights=weights)
        expected_dim = 1792
    else:
        raise ValueError(f"Unsupported EfficientNet model: {model_name}")

    model.classifier = nn.Identity()
    model.eval().to(resolved_device)
    return model, weights.transforms(), resolved_device, expected_dim


def extract_embedding_from_image(
    image: Image.Image | np.ndarray | str | Path,
    *,
    model,
    transform,
    device: str,
    expected_dim: int,
) -> np.ndarray:
    import torch

    if isinstance(image, (str, Path)):
        pil_image = Image.open(image).convert("RGB")
    elif isinstance(image, np.ndarray):
        pil_image = Image.fromarray(image).convert("RGB")
    else:
        pil_image = image.convert("RGB")

    tensor = transform(pil_image).unsqueeze(0).to(device)
    with torch.inference_mode():
        embedding = model(tensor).detach().cpu().numpy().ravel()

    if embedding.shape[0] != expected_dim:
        raise ValueError(
            f"Unexpected embedding dimension {embedding.shape[0]}; expected {expected_dim}."
        )
    if not np.isfinite(embedding).all():
        raise ValueError("Embedding contains NaN or infinite values.")
    return embedding.astype(np.float32, copy=False)

