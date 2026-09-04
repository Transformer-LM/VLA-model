"""Check batched calibration rollout against the frozen scalar implementation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import torch


def import_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    evaluator = import_module(
        "calibrated_transport_v2",
        Path("<PERSONAL_RESEARCH_ROOT>/workspace/run_p027c_calibrated_transport_v3.py"),
    )
    support = evaluator.load_support(
        Path("<PERSONAL_RESEARCH_ROOT>/workspace/run_p027c_latent_harm.py")
    )
    torch.manual_seed(9)
    generator = np.random.default_rng(9)
    model = support.DeltaWAM(5, 3, 8, 2).eval()
    trace = support.Trace(
        states=np.zeros((5, 3), dtype=np.float32),
        actions=generator.normal(size=(4, 2)).astype(np.float32),
        active=np.zeros(5, dtype=bool),
    )
    tensors = tuple(
        torch.tensor(value, dtype=torch.float32)
        for value in (
            np.zeros(5),
            np.ones(5),
            np.zeros(3),
            np.ones(3),
        )
    )
    residual = np.array([0.2, -0.3, 0.5], dtype=np.float32)
    configurations = [(0.0, 0.0), (0.2, 0.5), (1.0, 1.0)]
    device = torch.device("cpu")
    batched = evaluator.rollout_endpoint_grid(
        support,
        model,
        trace,
        residual,
        configurations,
        tensors,
        device,
    )
    scalar = np.stack(
        [
            support.rollout_endpoint(
                model,
                trace,
                None if alpha == 0.0 else residual * np.float32(alpha),
                decay,
                tensors,
                device,
            )
            for alpha, decay in configurations
        ]
    )
    maximum_delta = float(np.max(np.abs(batched - scalar)))
    print({"maximum_absolute_delta": maximum_delta})
    if not np.allclose(batched, scalar, atol=1e-6, rtol=1e-6):
        raise AssertionError("batched and scalar rollouts differ")


if __name__ == "__main__":
    main()
