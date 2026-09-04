"""Wait for the personal WAM training run, then run a bounded offline follow-up.

This watcher never downloads data, never launches a real robot, and uses only
the user's personal remote paths. It waits for all GPUs to become idle before
each new launch rather than sharing or preempting a device.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import time


PERSONAL = Path("<PERSONAL_RESEARCH_ROOT>")
RESULTS = PERSONAL / "results/policy-relevant-imagined-state-repair/e1"
WORK = PERSONAL / "workspace/policy-relevant-imagined-state-repair/implementation"
FASTWAM = PERSONAL / "workspace/FastWAM"
TRAIN_PID = 319900
CKPT = FASTWAM / "runs/policy_relevant_imagined_state_repair_5000/checkpoints/weights/step_005000_trainable_only.pt"
PY_WAM = PERSONAL / "conda/envs/fastwam-py311/bin/python"
PY_LIBERO = PERSONAL / "venvs/libero-eval-py310/bin/python"
PY_POLICY = PERSONAL / "conda/envs/cf-dynalign/bin/python"


def log(message: str) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    with (RESULTS / "posttrain_followup.log").open("a", encoding="utf-8") as handle:
        handle.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")


def gpu_rows() -> list[tuple[int, int, int]]:
    raw = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=index,memory.used,utilization.gpu", "--format=csv,noheader,nounits"],
        text=True,
    )
    return [
        tuple(int(part.strip()) for part in line.split(","))
        for line in raw.splitlines()
        if line.strip()
    ]


def compute_pids() -> list[int]:
    raw = subprocess.check_output(
        ["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader,nounits"],
        text=True,
    )
    return [int(line.strip()) for line in raw.splitlines() if line.strip()]


def all_idle() -> bool:
    rows = gpu_rows()
    return len(rows) == 4 and all(memory < 500 and util <= 5 for _, memory, util in rows) and not compute_pids()


def run(command: list[str], env: dict[str, str], label: str, timeout: int | None = None) -> None:
    log(f"start {label}: {' '.join(command)}")
    result = subprocess.run(command, cwd=str(WORK), env=env, text=True, capture_output=True, timeout=timeout)
    (RESULTS / f"posttrain_{label}.stdout.log").write_text(result.stdout, encoding="utf-8")
    (RESULTS / f"posttrain_{label}.stderr.log").write_text(result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"{label} failed with exit code {result.returncode}")
    log(f"done {label}")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    base_env = dict(os.environ)
    base_env.update({
        "DIFFSYNTH_MODEL_BASE_PATH": str(PERSONAL / "models/fastwam"),
        "DIFFSYNTH_SKIP_DOWNLOAD": "true",
        "DIFFSYNTH_DOWNLOAD_SOURCE": "modelscope",
        "PYTHONPATH": f"{FASTWAM}:{WORK}",
    })
    log(f"watching training pid={TRAIN_PID} checkpoint={CKPT}")
    while True:
        if CKPT.is_file():
            break
        try:
            os.kill(TRAIN_PID, 0)
        except ProcessLookupError:
            log("training exited before the expected checkpoint appeared; stopping")
            return
        time.sleep(60)
    log("checkpoint appeared; waiting for all four GPUs to be idle")
    for _ in range(180):
        if all_idle():
            break
        time.sleep(60)
    else:
        log("GPU idle gate timed out; no follow-up launch")
        return

    batches = [
        ("goal05_s29", "prepared_goal05_s29"),
        ("goal03_s43", "prepared_goal03_s43"),
        ("spatial02_s17", "prepared_spatial02_s17"),
    ]
    for name, stem in batches:
        if not all_idle():
            log(f"GPU idle gate failed before WAM batch {name}; stopping")
            return
        run(
            [str(PY_WAM), "-u", str(WORK / "run_wam_e1_inference.py"),
             "--inputs", str(RESULTS / f"{stem}.npz"),
             "--meta", str(RESULTS / f"{stem}.json"),
             "--out", str(RESULTS / f"wam_{name}_step5000"),
             "--device", "cuda:0", "--wam-steps", "2", "--video-frames", "5",
             "--ckpt", str(CKPT)],
            {**base_env, "CUDA_VISIBLE_DEVICES": "3"},
            f"wam_{name}_step5000",
            timeout=900,
        )

    if not all_idle():
        log("GPU idle gate failed before policy server; stopping")
        return
    server_log = RESULTS / "posttrain_starvla_server.log"
    server_env = dict(os.environ)
    server_env.update({"CUDA_VISIBLE_DEVICES": "2", "PYTHONPATH": str(PERSONAL / "workspace/h1-predictive-aux-starvla")})
    server = subprocess.Popen(
        [str(PY_POLICY), "-u", str(PERSONAL / "workspace/h1-predictive-aux-starvla/deployment/model_server/server_policy.py"),
         "--ckpt_path", str(PERSONAL / "checkpoints/starvla/Qwen3-VL-OFT-LIBERO-4in1/checkpoints/steps_50000_pytorch_model.pt"),
         "--port", "10097", "--use_bf16"],
        cwd=str(PERSONAL / "workspace/h1-predictive-aux-starvla"), env=server_env,
        stdout=server_log.open("w", encoding="utf-8"), stderr=subprocess.STDOUT,
    )
    try:
        for _ in range(180):
            if server.poll() is not None:
                raise RuntimeError("StarVLA server exited before listening")
            if "server listening" in server_log.read_text(encoding="utf-8", errors="ignore"):
                break
            time.sleep(1)
        else:
            raise RuntimeError("StarVLA server did not become ready")
        eval_env = dict(os.environ)
        eval_env.update({
            "MUJOCO_GL": "osmesa",
            "PYOPENGL_PLATFORM": "osmesa",
            "LIBERO_CONFIG_PATH": str(PERSONAL / "config/libero"),
            "PYTHONPATH": f"{PERSONAL / 'workspace/third_party/LIBERO'}:{PERSONAL / 'workspace/h1-predictive-aux-starvla'}:{WORK}",
        })
        for name, stem in batches:
            run(
                [str(PY_LIBERO), "-u", str(WORK / "evaluate_wam_e1_repair.py"),
                 "--inputs", str(RESULTS / f"{stem}.npz"),
                 "--meta", str(RESULTS / f"{stem}.json"),
                 "--wam", str(RESULTS / f"wam_{name}_step5000.npz"),
                 "--out", str(RESULTS / f"anchored_{name}_step5000.json"),
                 "--port", "10097", "--seed", "17", "--max-steps", "120", "--anchor-alpha", "0.25"],
                eval_env,
                f"eval_{name}_step5000",
                timeout=1800,
            )
    finally:
        if server.poll() is None:
            server.send_signal(signal.SIGTERM)
            try:
                server.wait(timeout=20)
            except subprocess.TimeoutExpired:
                server.kill()
    summary = {"status": "complete", "checkpoint": str(CKPT), "batches": [name for name, _ in batches]}
    (RESULTS / "posttrain_followup.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log("post-training follow-up complete")


if __name__ == "__main__":
    main()
