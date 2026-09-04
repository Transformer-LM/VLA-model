#!/usr/bin/env python3
"""Independently replay a saved natural-policy transcript from benchmark reset.

This verifier never calls the VLA server.  It starts from the named LIBERO
benchmark initial state, replays the recorded wait actions and every recorded
low-level action, and recomputes task success, rewards, states, RGB digests,
contacts, and saved chunk-boundary states.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any

import numpy as np


PERSONAL_ROOT = Path("<PERSONAL_RESEARCH_ROOT>").resolve()


def sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def confined_file(value: Any, label: str) -> Path:
    path = Path(str(value)).resolve()
    if path == PERSONAL_ROOT or PERSONAL_ROOT not in path.parents:
        raise ValueError(f"{label} outside personal root: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"missing {label}: {path}")
    return path


def digest(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def contact_rows(env: Any) -> list[dict[str, Any]]:
    model = env.env.sim.model
    rows: list[dict[str, Any]] = []
    for index in range(int(env.env.sim.data.ncon)):
        contact = env.env.sim.data.contact[index]
        left, right = sorted((int(contact.geom1), int(contact.geom2)))
        rows.append({
            "geom_ids": [left, right],
            "geom_names": [model.geom_id2name(left), model.geom_id2name(right)],
            "body_names": [
                model.body_id2name(int(model.geom_bodyid[left])),
                model.body_id2name(int(model.geom_bodyid[right])),
            ],
        })
    rows.sort(key=lambda row: tuple(row["geom_ids"]))
    return rows


def strict_json(path: Path) -> dict[str, Any]:
    def reject(value: str) -> None:
        raise ValueError(f"non-finite JSON constant: {value}")

    value = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject)
    if not isinstance(value, dict):
        raise ValueError("source manifest must be an object")
    return value


def git_value(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.decode("utf-8", errors="strict")


def verify_policy_identity(source: dict[str, Any]) -> tuple[bool, str]:
    if source.get("source_schema_version") != "P026-source-v1":
        return False, "legacy source has no cryptographic policy provenance"
    provenance = source.get("policy_provenance")
    if not isinstance(provenance, dict) or provenance.get("schema_version") != (
        "starvla-policy-provenance-v1"
    ):
        raise ValueError("P026 source lacks policy provenance")
    checkpoint = confined_file(provenance["checkpoint_path"], "policy checkpoint")
    metadata = provenance.get("server_handshake_metadata")
    if not isinstance(metadata, dict) or metadata.get("env") != "starvla_policy_server":
        raise ValueError("P026 source lacks StarVLA server handshake")
    if Path(str(metadata.get("ckpt_path", ""))).resolve() != checkpoint:
        raise ValueError("server-announced checkpoint differs from provenance path")
    if checkpoint.stat().st_size != int(provenance["checkpoint_size_bytes"]):
        raise ValueError("policy checkpoint size changed")
    if sha256_file(checkpoint) != str(provenance["checkpoint_sha256"]):
        raise ValueError("policy checkpoint SHA-256 changed")
    if int(metadata["action_chunk_size"]) != int(source["action_chunk_size"]):
        raise ValueError("server/source action chunk sizes disagree")

    code_root = Path(str(provenance["policy_code_root"])).resolve()
    if code_root == PERSONAL_ROOT or PERSONAL_ROOT not in code_root.parents or not code_root.is_dir():
        raise ValueError("policy code root is unavailable or outside personal storage")
    critical = provenance.get("critical_source_sha256")
    if not isinstance(critical, dict) or not critical:
        raise ValueError("policy critical-source hashes missing")
    for relative, expected in critical.items():
        path = (code_root / str(relative)).resolve()
        if code_root not in path.parents or not path.is_file():
            raise ValueError("invalid policy critical-source path")
        if sha256_file(path) != str(expected):
            raise ValueError(f"policy source changed: {relative}")
    collector = Path(__file__).resolve().with_name("collect_starvla_natural_rollout.py")
    if sha256_file(collector) != str(provenance["collector_sha256"]):
        raise ValueError("source collector changed")
    if git_value(code_root, "rev-parse", "HEAD").strip() != str(
        provenance["policy_git_commit"]
    ):
        raise ValueError("policy git commit changed")
    status = git_value(code_root, "status", "--porcelain=v1", "--untracked-files=all")
    diff = git_value(code_root, "diff", "--binary", "HEAD")
    if hashlib.sha256(status.encode("utf-8")).hexdigest() != str(
        provenance["policy_git_status_sha256"]
    ):
        raise ValueError("policy git dirty-status snapshot changed")
    if hashlib.sha256(diff.encode("utf-8")).hexdigest() != str(
        provenance["policy_git_diff_sha256"]
    ):
        raise ValueError("policy git diff snapshot changed")
    inference = provenance.get("inference")
    if not isinstance(inference, dict) or inference != {
        "unnorm_key": "franka",
        "action_ensemble": False,
        "use_ddim": True,
        "num_ddim_steps": 10,
        "image_size": [224, 224],
    }:
        raise ValueError("unexpected P026 policy inference configuration")
    return True, "checkpoint, handshake, code snapshot, collector, and inference verified"


def verify_policy_lock(source: dict[str, Any], lock_path: Path) -> tuple[bool, str, dict[str, Any]]:
    lock = strict_json(lock_path)
    if lock.get("kind") != "israc_p026_policy_and_roster_lock_v1" or (
        lock.get("frozen_before_confirmatory_rollouts") is not True
    ):
        raise ValueError("unexpected or unfrozen P026 policy lock")
    if source.get("policy_provenance") != lock.get("policy_provenance"):
        raise ValueError("source policy provenance differs from precollection lock")
    initialization = source.get("initialization", {})
    roster_key = {
        "suite_name": initialization.get("suite_name"),
        "task_id": int(initialization.get("task_id", -1)),
        "episode_index": int(initialization.get("episode_index", -1)),
        "seed": int(source.get("seed", -1)),
    }
    if roster_key not in lock.get("source_roster", []):
        raise ValueError("source is outside precollection task/episode/seed roster")
    collection = lock.get("collection", {})
    if int(source.get("num_steps_wait", -1)) != int(collection.get("num_steps_wait", -2)):
        raise ValueError("source wait steps differ from policy lock")
    if int(source.get("max_steps", -1)) != int(collection.get("max_steps", -2)):
        raise ValueError("source max steps differ from policy lock")
    source_time = datetime.fromisoformat(str(source["created_at_utc"]).replace("Z", "+00:00"))
    lock_time = datetime.fromisoformat(str(lock["created_at_utc"]).replace("Z", "+00:00"))
    if source_time <= lock_time:
        raise ValueError("source timestamp does not follow precollection policy lock")
    for label in ("policy_code_bundle", "preregistration"):
        reference = lock.get(label)
        if not isinstance(reference, dict):
            raise ValueError(f"policy lock lacks {label}")
        path = confined_file(reference["path"], label)
        if sha256_file(path) != str(reference["sha256"]):
            raise ValueError(f"policy-lock {label} hash mismatch")
        if label == "policy_code_bundle" and path.stat().st_size != int(reference["size_bytes"]):
            raise ValueError("policy code bundle size mismatch")
    return True, "precollection policy, code bundle, preregistration, and roster lock verified", lock


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--policy-lock")
    args = parser.parse_args()
    if os.environ.get("MUJOCO_GL", "").casefold() != "osmesa":
        raise RuntimeError("registered OSMesa environment is required")
    source_path = confined_file(args.source, "source rollout")
    output = Path(args.output).resolve()
    if output == PERSONAL_ROOT or PERSONAL_ROOT not in output.parents or output.exists():
        raise ValueError("unsafe or existing output path")
    source = strict_json(source_path)
    if source.get("kind") != "israc_frozen_starvla_natural_policy_support_rollout":
        raise ValueError("unexpected source kind")
    policy_identity_verified, policy_identity_status = verify_policy_identity(source)
    policy_lock_verified = False
    policy_lock_status = "not requested"
    policy_lock_path: Path | None = None
    if args.policy_lock is not None:
        policy_lock_path = confined_file(args.policy_lock, "P026 policy lock")
        policy_lock_verified, policy_lock_status, _ = verify_policy_lock(
            source, policy_lock_path
        )
    initialization = source.get("initialization")
    if not isinstance(initialization, dict) or initialization.get("source") != (
        "libero_benchmark_initial_state"
    ):
        raise ValueError("source lacks benchmark initialization")
    arrays_path = confined_file(source["arrays"], "source arrays")
    bddl_path = confined_file(source["bddl"], "source BDDL")
    with np.load(arrays_path, allow_pickle=False) as archive:
        boundary_steps = np.asarray(archive["boundary_steps"], dtype=np.int64)
        boundary_states = np.asarray(archive["boundary_states"], dtype=np.float64)
        executed = np.asarray(archive["executed_actions"], dtype=np.float32)
        stored_rewards = np.asarray(archive["rewards"], dtype=np.float32)
    frames = source.get("frames")
    if not isinstance(frames, list) or len(frames) != len(executed):
        raise ValueError("source frame/action lengths disagree")
    if len(stored_rewards) != len(executed):
        raise ValueError("source reward/action lengths disagree")

    from libero.libero import benchmark
    from libero.libero.envs import OffScreenRenderEnv

    suite = benchmark.get_benchmark_dict()[str(initialization["suite_name"])]()
    states = suite.get_task_init_states(int(initialization["task_id"]))
    episode_index = int(initialization["episode_index"])
    if not 0 <= episode_index < len(states):
        raise ValueError("invalid benchmark episode index")
    benchmark_state = np.asarray(states[episode_index], dtype=np.float64)

    env = OffScreenRenderEnv(
        bddl_file_name=str(bddl_path), camera_heights=256, camera_widths=256
    )
    state_mismatches = 0
    rgb_mismatches = 0
    wrist_rgb_mismatches = 0
    contact_mismatches = 0
    reward_mismatches = 0
    boundary_mismatches = 0
    max_boundary_abs = 0.0
    replay_rewards: list[float] = []
    done = False
    try:
        env.seed(int(source["seed"]))
        observation = env.reset()
        observation = env.set_init_state(benchmark_state)
        wait_action = [0.0] * 6 + [-1.0]
        for _ in range(int(source.get("num_steps_wait", 0))):
            observation, _, _, _ = env.step(wait_action)

        boundary_by_step = {
            int(step): np.asarray(boundary_states[index], dtype=np.float64)
            for index, step in enumerate(boundary_steps)
        }
        for step, action in enumerate(executed):
            if step in boundary_by_step:
                actual_boundary = np.asarray(env.get_sim_state(), dtype=np.float64)
                expected_boundary = boundary_by_step[step]
                if actual_boundary.shape != expected_boundary.shape:
                    boundary_mismatches += 1
                    max_boundary_abs = 1e300
                else:
                    difference = float(np.max(np.abs(actual_boundary - expected_boundary)))
                    max_boundary_abs = max(max_boundary_abs, difference)
                    boundary_mismatches += int(difference != 0.0)
            observation, reward, done, _ = env.step(action.tolist())
            replay_rewards.append(float(reward))
            expected = frames[step]
            state_mismatches += int(
                digest(np.asarray(env.get_sim_state())) != str(expected["state_sha256"])
            )
            rgb_mismatches += int(
                digest(np.asarray(observation["agentview_image"]))
                != str(expected["agent_rgb_sha256"])
            )
            if "wrist_rgb_sha256" in expected:
                wrist_rgb_mismatches += int(
                    digest(np.asarray(observation["robot0_eye_in_hand_image"]))
                    != str(expected["wrist_rgb_sha256"])
                )
            elif args.policy_lock is not None:
                wrist_rgb_mismatches += 1
            contact_mismatches += int(contact_rows(env) != expected["contacts"])
            reward_mismatches += int(float(reward) != float(expected["reward"]))
            reward_mismatches += int(float(reward) != float(stored_rewards[step]))
            if bool(done) != bool(expected["done"]):
                reward_mismatches += 1
            if done and step != len(executed) - 1:
                reward_mismatches += 1
                break
    finally:
        env.close()

    passed = bool(
        done
        and replay_rewards
        and max(replay_rewards) >= 1.0
        and state_mismatches == 0
        and rgb_mismatches == 0
        and wrist_rgb_mismatches == 0
        and contact_mismatches == 0
        and reward_mismatches == 0
        and boundary_mismatches == 0
        and max_boundary_abs == 0.0
        and source.get("done") is True
        and float(source.get("reward_max", 0.0)) == max(replay_rewards)
        and (
            source.get("source_schema_version") != "P026-source-v1"
            or policy_identity_verified
        )
        and (args.policy_lock is None or policy_lock_verified)
    )
    report = {
        "kind": "israc_source_admission_replay_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_rollout": str(source_path),
        "source_rollout_sha256": sha256_file(source_path),
        "source_arrays": str(arrays_path),
        "source_arrays_sha256": sha256_file(arrays_path),
        "task_asset_bddl_sha256": sha256_file(bddl_path),
        "initialization": initialization,
        "environment_seed": int(source["seed"]),
        "replayed_action_steps": len(executed),
        "replay_done": bool(done),
        "replay_reward_max": max(replay_rewards) if replay_rewards else 0.0,
        "state_digest_mismatches": state_mismatches,
        "rgb_digest_mismatches": rgb_mismatches,
        "wrist_rgb_digest_mismatches": wrist_rgb_mismatches,
        "contact_mismatches": contact_mismatches,
        "reward_or_done_mismatches": reward_mismatches,
        "boundary_state_mismatches": boundary_mismatches,
        "boundary_state_max_abs": max_boundary_abs,
        "passed": passed,
        "policy_identity_verified": policy_identity_verified,
        "policy_identity_status": policy_identity_status,
        "policy_lock_verified": policy_lock_verified,
        "policy_lock_status": policy_lock_status,
        "policy_lock": ({
            "path": str(policy_lock_path),
            "sha256": sha256_file(policy_lock_path),
        } if policy_lock_path is not None else None),
        "claim_limit": (
            "Independent saved-action replay; authenticates task success and transcript "
            "reproducibility, but does not authenticate which VLA produced the actions."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
