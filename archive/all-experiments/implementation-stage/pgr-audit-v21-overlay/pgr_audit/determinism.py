"""Role-separated deterministic process setup."""

from __future__ import annotations

import hashlib
import os
import random
from typing import Any

import numpy as np


REQUIRED_PRE_CUDA_ENV = {
    "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
    "TOKENIZERS_PARALLELISM": "false",
}


def role_seed(role: str, train_seed: int, master_seed: int = 1701) -> int:
    if not role:
        raise ValueError("role must be non-empty")
    material = f"PGR-Audit-v2|role={role}|train_seed={train_seed}|master={master_seed}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big", signed=False)


def configure_pre_cuda_environment(seed: int) -> dict[str, str]:
    values = {**REQUIRED_PRE_CUDA_ENV, "PYTHONHASHSEED": str(seed)}
    for key, expected in values.items():
        current = os.environ.get(key)
        if current not in (None, expected):
            raise RuntimeError(f"Determinism environment mismatch for {key}: {current!r} != {expected!r}")
        os.environ[key] = expected
    return values


def seed_process(seed: int) -> tuple[np.random.Generator, dict[str, Any]]:
    configure_pre_cuda_environment(seed)
    random.seed(seed)
    np.random.seed(seed % (2**32))
    generator = np.random.Generator(np.random.PCG64(seed))

    import torch

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_float32_matmul_precision("highest")

    report = {
        "seed": seed,
        "environment": {key: os.environ[key] for key in (*REQUIRED_PRE_CUDA_ENV, "PYTHONHASHSEED")},
        "torch_deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "cudnn_deterministic": torch.backends.cudnn.deterministic,
        "cudnn_benchmark": torch.backends.cudnn.benchmark,
        "cuda_matmul_allow_tf32": torch.backends.cuda.matmul.allow_tf32,
        "cudnn_allow_tf32": torch.backends.cudnn.allow_tf32,
        "float32_matmul_precision": torch.get_float32_matmul_precision(),
    }
    return generator, report
