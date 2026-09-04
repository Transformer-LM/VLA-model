"""No-argument, fail-closed launcher for calibrated residual transport E0."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path


GPU_INDEX = 2
EVALUATOR = Path("<PERSONAL_RESEARCH_ROOT>/workspace/run_p027c_calibrated_transport_v3.py")
EVALUATOR_SHA256 = "5390e1e71563a60cbd582a97d25caeadbd7a12b25b39025f36b95c8da6f245f6"
RUN_LOCK = Path(
    "<PERSONAL_RESEARCH_ROOT>/results/israc/"
    "P027C_LOSO_7D82_CALIBRATED_E0_RUN_LOCK.json"
)
RUN_LOCK_SHA256 = "d843fd527c18cf46a2b8f4420f7811ab79810169fd0b04e7cdd80dc1220bb495"
PYTHON = Path("<PERSONAL_RESEARCH_ROOT>/conda/envs/fastwam-py311/bin/python")
LOG = Path(
    "<PERSONAL_RESEARCH_ROOT>/results/israc/P027C_LOSO_7D82_CALIBRATED_E0.log"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def gpu_row() -> tuple[str, int, int]:
    query = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=index,uuid,memory.used,utilization.gpu",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    for line in query.stdout.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) == 4 and int(parts[0]) == GPU_INDEX:
            return parts[1], int(parts[2]), int(parts[3])
    raise RuntimeError(f"GPU {GPU_INDEX} was absent from nvidia-smi")


def compute_gpu_uuids() -> set[str]:
    query = subprocess.run(
        [
            "nvidia-smi",
            "--query-compute-apps=gpu_uuid,pid",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return {
        line.split(",", 1)[0].strip()
        for line in query.stdout.splitlines()
        if line.strip()
    }


def main() -> int:
    if len(sys.argv) != 1:
        raise ValueError("this frozen launcher accepts no arguments")
    if sha256_file(EVALUATOR.resolve(strict=True)) != EVALUATOR_SHA256:
        raise ValueError("evaluator SHA-256 mismatch")
    if sha256_file(RUN_LOCK.resolve(strict=True)) != RUN_LOCK_SHA256:
        raise ValueError("run-lock SHA-256 mismatch")
    if not PYTHON.is_file():
        raise FileNotFoundError(PYTHON)
    if LOG.exists():
        raise FileExistsError(LOG)
    uuid, memory_used, utilization = gpu_row()
    busy_gpu_uuids = compute_gpu_uuids()
    if memory_used >= 500 or utilization > 5 or uuid in busy_gpu_uuids:
        raise RuntimeError(
            f"GPU {GPU_INDEX} is not eligible: memory={memory_used} MiB, "
            f"utilization={utilization}%, compute_process={uuid in busy_gpu_uuids}"
        )
    environment = os.environ.copy()
    environment["CUDA_VISIBLE_DEVICES"] = uuid
    environment["WANDB_DISABLED"] = "true"
    command = [
        str(PYTHON),
        str(EVALUATOR.resolve(strict=True)),
        "--run-lock",
        str(RUN_LOCK.resolve(strict=True)),
        "--run-lock-sha256",
        RUN_LOCK_SHA256,
    ]
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("xb") as log_handle:
        log_handle.write(
            (
                f"gpu={GPU_INDEX} uuid={uuid} memory_used_mib={memory_used} "
                f"utilization_percent={utilization}\n"
            ).encode("utf-8")
        )
        log_handle.flush()
        os.fsync(log_handle.fileno())
        completed = subprocess.run(
            command,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            check=False,
        )
        log_handle.flush()
        os.fsync(log_handle.fileno())
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
