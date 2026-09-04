"""Engineering-only CUDA/model-load canary with synthetic, non-scientific inputs."""

from __future__ import annotations

import argparse
import os
import random
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch

from .canonical import atomic_write_canonical_json
from .filesystem import PersonalRootGuard, enforce_private_umask
from .host import QwenOFTActionInterface, build_strict_frozen_host, measure_engineering_parity
from .spec import verify_frozen_spec


def _observed_compute_uuid(pid: int) -> str:
    deadline = time.monotonic() + 30.0
    while time.monotonic() < deadline:
        output = subprocess.run(
            ("nvidia-smi", "--query-compute-apps=gpu_uuid,pid", "--format=csv,noheader,nounits"),
            check=True,
            text=True,
            capture_output=True,
        ).stdout
        for line in output.splitlines():
            fields = [field.strip() for field in line.split(",")]
            if len(fields) == 2 and fields[1] == str(pid):
                return fields[0]
        time.sleep(0.1)
    raise RuntimeError("Current PID did not appear in nvidia-smi compute applications")


def _configure_determinism() -> None:
    if os.environ.get("CUBLAS_WORKSPACE_CONFIG") != ":4096:8":
        raise RuntimeError("CUBLAS_WORKSPACE_CONFIG was not fixed before interpreter start")
    if os.environ.get("PYTHONHASHSEED") != "7":
        raise RuntimeError("PYTHONHASHSEED was not fixed before interpreter start")
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_float32_matmul_precision("highest")
    random.seed(7)
    np.random.seed(7)
    torch.manual_seed(7)
    torch.cuda.manual_seed_all(7)


def _bind_cuda(output: Path) -> dict:
    expected_uuid = os.environ["PGR_SELECTED_GPU_UUID"]
    selected_index = int(os.environ["PGR_SELECTED_PHYSICAL_INDEX"])
    if os.environ.get("CUDA_VISIBLE_DEVICES") != expected_uuid:
        raise RuntimeError("CUDA_VISIBLE_DEVICES does not match guarded hardware UUID")
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise RuntimeError("Guarded canary requires exactly one visible CUDA device")
    torch.cuda.init()
    torch.empty(1, device="cuda").add_(1)
    torch.cuda.synchronize()
    observed_uuid = _observed_compute_uuid(os.getpid())
    if observed_uuid != expected_uuid:
        raise RuntimeError(f"CUDA PID bound to {observed_uuid}, expected {expected_uuid}")
    handshake = {
        "cuda_device_name": torch.cuda.get_device_name(0),
        "cuda_visible_devices": expected_uuid,
        "launch_uuid": os.environ["PGR_LAUNCH_UUID"],
        "observed_gpu_uuid": observed_uuid,
        "pgid": os.getpgid(0),
        "pid": os.getpid(),
        "selected_gpu_uuid": expected_uuid,
        "selected_physical_index": selected_index,
        "visible_device_count": torch.cuda.device_count(),
    }
    atomic_write_canonical_json(output / "child_bound.json", handshake)
    return handshake


def _synthetic_examples() -> list[dict[str, object]]:
    first = np.zeros((96, 128, 3), dtype=np.uint8)
    first[:, :, 0] = 37
    first[:, :, 1] = np.arange(128, dtype=np.uint8)[None, :]
    second = np.zeros((80, 112, 3), dtype=np.uint8)
    second[:, :, 1] = 83
    second[:, :, 2] = np.arange(80, dtype=np.uint8)[:, None]
    return [{"image": [first, second], "lang": "Move the test object to the marked test area."}]


def run(checkpoint_step: int) -> dict:
    enforce_private_umask()
    spec = verify_frozen_spec()
    output = Path(os.environ["PGR_OUTPUT_DIR"])
    PersonalRootGuard().require_existing(output, regular=False)
    _configure_determinism()
    handshake = _bind_cuda(output)

    started = time.monotonic()
    host, host_audit = build_strict_frozen_host(checkpoint_step)
    host.to(device="cuda")
    torch.cuda.synchronize()
    loaded_seconds = time.monotonic() - started
    interface = QwenOFTActionInterface(host)
    parity_started = time.monotonic()
    parity = measure_engineering_parity(interface, _synthetic_examples())
    torch.cuda.synchronize()
    parity_seconds = time.monotonic() - parity_started
    if not parity.passed:
        raise RuntimeError(f"Engineering interface parity failed: {parity}")

    result = {
        "binding": handshake,
        "canary_kind": "engineering-only-no-scientific-target",
        "approval_sha256": os.environ["PGR_APPROVAL_SHA256"],
        "checkpoint_step": checkpoint_step,
        "frozen_protocol_id": spec.protocol["protocol_id"],
        "host_audit": asdict(host_audit),
        "interface_parity": asdict(parity),
        "environment_lock_sha256": os.environ["PGR_ENVIRONMENT_LOCK_SHA256"],
        "determinism": {
            "cublas_workspace_config": os.environ["CUBLAS_WORKSPACE_CONFIG"],
            "cudnn_benchmark": torch.backends.cudnn.benchmark,
            "cudnn_deterministic": torch.backends.cudnn.deterministic,
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
            "matmul_precision": torch.get_float32_matmul_precision(),
            "pythonhashseed": os.environ["PYTHONHASHSEED"],
            "tf32_cudnn": torch.backends.cudnn.allow_tf32,
            "tf32_matmul": torch.backends.cuda.matmul.allow_tf32,
        },
        "max_memory_allocated_bytes": torch.cuda.max_memory_allocated(),
        "max_memory_reserved_bytes": torch.cuda.max_memory_reserved(),
        "model_load_seconds": loaded_seconds,
        "overlay_source_sha256": os.environ["PGR_OVERLAY_SOURCE_SHA256"],
        "paid_cost_usd": 0.0,
        "parity_seconds": parity_seconds,
        "robot_trials": 0,
        "review_response_sha256": os.environ["PGR_REVIEW_RESPONSE_SHA256"],
        "runtime_paths": {
            "cuda_cache": os.environ["CUDA_CACHE_PATH"],
            "hf_home": os.environ["HF_HOME"],
            "home": os.environ["HOME"],
            "tmp": os.environ["TMPDIR"],
            "torch_extensions": os.environ["TORCH_EXTENSIONS_DIR"],
            "torch_home": os.environ["TORCH_HOME"],
            "wandb_dir": os.environ["WANDB_DIR"],
            "xdg_cache": os.environ["XDG_CACHE_HOME"],
            "xdg_config": os.environ["XDG_CONFIG_HOME"],
        },
        "sanitized_config_sha256": os.environ["PGR_SANITIZED_CONFIG_SHA256"],
        "scientific_examples_read": 0,
        "scientific_outcomes_read": 0,
        "synthetic_examples": 1,
    }
    atomic_write_canonical_json(output / "canary_metrics.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-step", type=int, choices=(1000, 5000, 10000), default=1000)
    args = parser.parse_args()
    result = run(args.checkpoint_step)
    print(
        "CANARY_PASS "
        f"step={result['checkpoint_step']} "
        f"parity={result['interface_parity']['direct_vs_interface_max_abs']:.3e} "
        f"memory={result['max_memory_allocated_bytes']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
