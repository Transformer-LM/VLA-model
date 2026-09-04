"""No-argument, fail-closed launcher for the frozen P027-C latent E0."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path


GPU_INDEX = 2
RUNNER = Path("<PERSONAL_RESEARCH_ROOT>/workspace/run_p027c_latent_harm.py")
RUNNER_SHA256 = "c0f5cceb76128d970fa401f286b2aba7e47a4a47afcb07a346e688e245bbd5b3"
RUN_LOCK = Path("<PERSONAL_RESEARCH_ROOT>/results/israc/P027C_LOSO_7D82_WAM_E0_RUN_LOCK.json")
RUN_LOCK_SHA256 = "236bf3003085d12a77a4862d4997747eaa62793602130a64e6004ed023c6e0a9"
PYTHON = Path("<PERSONAL_RESEARCH_ROOT>/conda/envs/fastwam-py311/bin/python")
LOG = Path("<PERSONAL_RESEARCH_ROOT>/results/israc/P027C_LOSO_7D82_WAM_E0.log")


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
    rows = [
        [part.strip() for part in line.split(",")]
        for line in query.stdout.splitlines()
        if line.strip()
    ]
    for parts in rows:
        if len(parts) == 4 and int(parts[0].strip()) == GPU_INDEX:
            return parts[1].strip(), int(parts[2].strip()), int(parts[3].strip())
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
    if sha256_file(RUNNER.resolve(strict=True)) != RUNNER_SHA256:
        raise ValueError("runner SHA-256 mismatch")
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
    # Bind CUDA to the exact UUID just checked above.  Numeric CUDA ordinals
    # can differ from nvidia-smi physical indices when CUDA_DEVICE_ORDER is
    # unset, so using "2" here would not be a safe allocation proof.
    environment["CUDA_VISIBLE_DEVICES"] = uuid
    environment["WANDB_DISABLED"] = "true"
    command = [
        # Invoke the Conda-prefix symlink as written. Resolving it to the
        # system interpreter would discard the prefix's site-packages.
        str(PYTHON),
        str(RUNNER.resolve(strict=True)),
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
