"""Frozen identifiers and filesystem/device constants.

These values duplicate the hash-bound protocol intentionally. Runtime code must
also read and verify the frozen input bundle; this module is a fail-closed guard,
not an alternative configuration surface.
"""

from __future__ import annotations

from pathlib import Path

PROTOCOL_ID = "pgr-audit-v2-parallel-real"
FREEZE_MANIFEST_SHA256 = "21267bf7a0b34d1f101398963011697ea451a6a4a5869dd97317319bd637ea6f"
PROTOCOL_SHA256 = "a5de33299f74db4118e075f8db05cc9196f0816a014121a3b8d807b959662752"
CONFIG_SHA256 = "c70f5361352f449800ba4e5af9dc408eb1d706c0f26549b393cbfe4fe788008c"
JURY_RESPONSE_SHA256 = "4c5778ca4fd2d2f5f76c121e4d2566474ac961c73f3da718bda55af870905431"

LOGICAL_PERSONAL_ROOT = Path("<PERSONAL_RESEARCH_ROOT>")
CANONICAL_PERSONAL_ROOT = Path("<PERSONAL_RESEARCH_ROOT_ALIAS>")
ISOLATED_WORKSPACE = LOGICAL_PERSONAL_ROOT / "workspace/h1-predictive-aux-starvla"
ARTIFACT_ROOT = LOGICAL_PERSONAL_ROOT / "artifacts/h1-pgr-audit"
PREREG_ROOT = ARTIFACT_ROOT / "prereg/v2.1-21267bf7"
CODE_REVIEW_ROOT = ARTIFACT_ROOT / "code-review/v2-007"
CANARY_APPROVAL_PATH = CODE_REVIEW_ROOT / "CANARY_APPROVAL.json"
QUARANTINE_ROOT = ARTIFACT_ROOT / "quarantine"
GPU_LOCK_ROOT = LOGICAL_PERSONAL_ROOT / "locks/h1-pgr-audit/gpu"

TRAIN_PYTHON = LOGICAL_PERSONAL_ROOT / "conda/envs/cf-dynalign/bin/python3.11"
CANARY_ENVIRONMENT_LOCK = ISOLATED_WORKSPACE / "environment/canary_environment_lock.json"
CANARY_ROLE_SEED = 7
CANARY_EXPECTED_WALL_SECONDS = 600.0
CANARY_HUNG_TIMEOUT_SECONDS = 1200.0

RUNTIME_HOME = LOGICAL_PERSONAL_ROOT / "runtime-home/h1-pgr-audit"
RUNTIME_TMP = LOGICAL_PERSONAL_ROOT / "tmp/h1-pgr-audit"
RUNTIME_CACHE = LOGICAL_PERSONAL_ROOT / "cache/h1-pgr-audit"
RUNTIME_CONFIG = LOGICAL_PERSONAL_ROOT / "config/h1-pgr-audit"
RUNTIME_HF_HOME = RUNTIME_CACHE / "huggingface"
RUNTIME_TORCH_HOME = RUNTIME_CACHE / "torch"
RUNTIME_TORCH_EXTENSIONS = RUNTIME_CACHE / "torch_extensions"
RUNTIME_CUDA_CACHE = RUNTIME_CACHE / "nvidia/ComputeCache"
RUNTIME_WANDB = LOGICAL_PERSONAL_ROOT / "logs/h1-pgr-audit/wandb"

EXPECTED_GPU_UUID_BY_INDEX = {
    0: "GPU-417b37b2-bb07-cc79-ca59-2e43af96d3ea",
    1: "GPU-708fad71-ac97-0c67-85fc-15e9534b2f59",
    2: "GPU-c034ca59-aa0c-4629-ce5d-a0b5d92e2747",
    3: "GPU-aa863a6c-8482-fd6c-e957-424e559e9df4",
}
GPU_PREFERENCE = (2, 3, 0, 1)

TRAIN_SEEDS = tuple(range(20))
PRIMARY_SEEDS = tuple(range(10))
REPLICATION_SEEDS = tuple(range(10, 20))
SIMULATION_TASKS = tuple(range(10))

ACTION_HORIZON = 8
ACTION_DIM = 7
REPRESENTATION_DIM = 2560
ADAPTER_RANK = 32

CHECKPOINT_KEYSET_SHA256 = "c258f23f041e115f20626b6b4a49acf8cf01a562377ba37a94101e3331d810e0"

LIVE_ROBOT_AUTHORIZED = False
