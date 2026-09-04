#!/usr/bin/env python3
"""Freeze the combined LIBERO v2.1 normalization statistics for P027-C.

This script deliberately computes statistics through FastWAM's own dataset and
processor implementation.  The output is written once, validated, hashed, and
accompanied by a provenance manifest.  It never reads or writes shared paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

from hydra.utils import instantiate
from omegaconf import OmegaConf

from fastwam.utils import misc, pytorch_utils


PERSONAL_ROOT = Path("<PERSONAL_RESEARCH_ROOT>").resolve()
EXPECTED_CODEBASE_VERSION = "v2.1"
EXPECTED_ACTION_DIM = 7
EXPECTED_STATE_DIM = 8
EXPECTED_DATASET_COUNT = 4


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_personal(path: Path, *, label: str) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(PERSONAL_ROOT)
    except ValueError as exc:
        raise ValueError(f"{label} must stay under {PERSONAL_ROOT}: {resolved}") from exc
    return resolved


def _finite_tree(value: Any, *, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            _finite_tree(item, path=f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _finite_tree(item, path=f"{path}[{index}]")
        return
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(float(value)):
            raise ValueError(f"Non-finite statistic at {path}: {value}")


def _vector_len(value: Any, *, label: str) -> int:
    if not isinstance(value, list):
        raise TypeError(f"{label} must be a list, got {type(value).__name__}")
    return len(value)


def _validate_stats(stats: dict[str, Any]) -> None:
    _finite_tree(stats)
    if int(stats.get("num_episodes", 0)) <= 0:
        raise ValueError("num_episodes must be positive")
    if int(stats.get("num_transition", 0)) <= 0:
        raise ValueError("num_transition must be positive")

    for family, expected_dim in (("action", EXPECTED_ACTION_DIM), ("state", EXPECTED_STATE_DIM)):
        family_stats = stats.get(family)
        if not isinstance(family_stats, dict) or set(family_stats) != {"default"}:
            raise ValueError(f"Expected exactly {family}.default statistics")
        default = family_stats["default"]
        for key in ("global_min", "global_max", "global_mean", "global_std", "global_q01", "global_q99"):
            if key not in default:
                raise ValueError(f"Missing {family}.default.{key}")
            if _vector_len(default[key], label=f"{family}.default.{key}") != expected_dim:
                raise ValueError(f"{family}.default.{key} has the wrong dimension")
        if any(float(x) < 0.0 for x in default["global_std"]):
            raise ValueError(f"{family}.default.global_std contains a negative value")
        if any(float(low) > float(high) for low, high in zip(default["global_min"], default["global_max"])):
            raise ValueError(f"{family}.default has global_min > global_max")
        if any(float(low) > float(high) for low, high in zip(default["global_q01"], default["global_q99"])):
            raise ValueError(f"{family}.default has global_q01 > global_q99")


def _validate_dataset_config(data_config: Any) -> list[dict[str, Any]]:
    target = str(data_config.train.get("_target_", ""))
    if target != "fastwam.datasets.lerobot.robot_video_dataset.RobotVideoDataset":
        raise ValueError(f"P027-C requires the v2.1 RobotVideoDataset reader, got {target!r}")
    dataset_dirs = [Path(str(item)).resolve() for item in data_config.train.dataset_dirs]
    if len(dataset_dirs) != EXPECTED_DATASET_COUNT or len(set(dataset_dirs)) != EXPECTED_DATASET_COUNT:
        raise ValueError(f"Expected {EXPECTED_DATASET_COUNT} distinct LIBERO datasets")

    action_shape = int(data_config.train.shape_meta.action[0].shape)
    state_shape = int(data_config.train.shape_meta.state[0].shape)
    if action_shape != EXPECTED_ACTION_DIM or state_shape != EXPECTED_STATE_DIM:
        raise ValueError(f"Expected action/state dims 7/8, got {action_shape}/{state_shape}")

    records: list[dict[str, Any]] = []
    for dataset_dir in dataset_dirs:
        _require_personal(dataset_dir, label="dataset_dir")
        info_path = dataset_dir / "meta" / "info.json"
        if not info_path.is_file():
            raise FileNotFoundError(info_path)
        info = json.loads(info_path.read_text(encoding="utf-8"))
        version = str(info.get("codebase_version", ""))
        if version != EXPECTED_CODEBASE_VERSION:
            raise ValueError(f"{dataset_dir} is {version!r}, expected {EXPECTED_CODEBASE_VERSION!r}")
        features = info.get("features", {})
        action_feature_shape = features.get("action", {}).get("shape")
        state_feature_shape = features.get("observation.state", {}).get("shape")
        if action_feature_shape != [EXPECTED_ACTION_DIM] or state_feature_shape != [EXPECTED_STATE_DIM]:
            raise ValueError(
                f"{dataset_dir} metadata has action/state shapes "
                f"{action_feature_shape}/{state_feature_shape}, expected [7]/[8]"
            )
        records.append(
            {
                "dataset_dir": str(dataset_dir),
                "info_path": str(info_path),
                "info_sha256": _sha256(info_path),
                "codebase_version": version,
                "total_episodes": int(info.get("total_episodes", 0)),
                "total_frames": int(info.get("total_frames", 0)),
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=2701)
    args = parser.parse_args()

    config_path = _require_personal(args.data_config, label="data_config")
    output_path = _require_personal(args.output, label="output")
    manifest_path = _require_personal(args.manifest, label="manifest")
    if output_path == manifest_path:
        raise ValueError("output and manifest must be distinct paths")
    for destination in (output_path, manifest_path):
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite locked output: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)

    # Nest under `data` so ${data.train.*} interpolations resolve exactly as in training.
    root_config = OmegaConf.create({"data": OmegaConf.load(config_path)})
    OmegaConf.resolve(root_config)
    dataset_records = _validate_dataset_config(root_config.data)
    train_config = root_config.data.train
    train_config.pretrained_norm_stats = None
    train_config.use_text_embed_cache = False

    pytorch_utils.set_global_seed(int(args.seed))
    with tempfile.TemporaryDirectory(prefix="p027c_norm_stats_", dir=str(output_path.parent)) as tmp:
        work_dir = Path(tmp).resolve()
        misc.register_work_dir(str(work_dir))
        dataset = instantiate(train_config)
        source_stats = work_dir / "dataset_stats.json"
        if not source_stats.is_file():
            raise FileNotFoundError(f"FastWAM did not write expected statistics: {source_stats}")
        stats = json.loads(source_stats.read_text(encoding="utf-8"))
        _validate_stats(stats)
        # source_stats is created inside output_path.parent, so a hard link is
        # atomic and fails with EEXIST if another process wins the destination.
        os.link(source_stats, output_path)

    output_hash = _sha256(output_path)
    manifest = {
        "protocol": "P027C-LIBERO-COMBINED-NORM-STATS-v1",
        "seed": int(args.seed),
        "data_config": str(config_path),
        "data_config_sha256": _sha256(config_path),
        "output": str(output_path),
        "output_sha256": output_hash,
        "dataset_count": len(dataset_records),
        "datasets": dataset_records,
        "expected_action_dim": EXPECTED_ACTION_DIM,
        "expected_state_dim": EXPECTED_STATE_DIM,
        "num_episodes": int(stats["num_episodes"]),
        "num_transition": int(stats["num_transition"]),
    }
    temp_manifest = manifest_path.with_name(f".{manifest_path.name}.{os.getpid()}.tmp")
    with temp_manifest.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.link(temp_manifest, manifest_path)
    finally:
        temp_manifest.unlink(missing_ok=True)
    if _sha256(output_path) != output_hash:
        raise RuntimeError("Locked normalization statistics changed while the manifest was committed")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
