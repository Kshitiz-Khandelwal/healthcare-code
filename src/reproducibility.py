from __future__ import annotations

import os
import random
from typing import Any

import numpy as np


def set_global_seed(seed: int = 42) -> dict[str, Any]:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)

    state: dict[str, Any] = {
        "seed": seed,
        "python": True,
        "numpy": True,
        "torch": False,
        "cuda": False,
    }

    try:
        import torch

        torch.manual_seed(seed)
        state["torch"] = True
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            state["cuda"] = True
        if hasattr(torch.backends, "cudnn"):
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass

    return state

