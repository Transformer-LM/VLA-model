"""Collect one frozen-StarVLA natural LIBERO rollout with chunk-boundary states.

This collector establishes policy support only.  It does not construct an
alias, alter simulator physics, call a WAM, or claim task success.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
from typing import Any

import numpy as np


PERSONAL_ROOT = Path("<PERSONAL_RESEARCH_ROOT>").resolve()


def personal_path(raw: str, *, must_exist: bool) -> Path:
    path = Path(raw).resolve()
    if path != PERSONAL_ROOT and PERSONAL_ROOT not in path.parents:
        raise ValueError(f"path is outside personal root: {path}")
    if must_exist and not path.exists():
        raise FileNotFoundError(path)
    return path


def digest(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def file_sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def git_value(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.decode("utf-8", errors="strict")


def policy_provenance(client: Any, model_client_class: Any) -> dict[str, Any]:
    metadata = dict(client._server_metadata)
    if metadata.get("env") != "starvla_policy_server":
        raise ValueError("connected action server did not identify as StarVLA")
    checkpoint = personal_path(str(metadata.get("ckpt_path", "")), must_exist=True)
    if not checkpoint.is_file():
        raise ValueError("P026 requires one hashable checkpoint file")
    client_file = Path(inspect.getfile(model_client_class)).resolve()
    code_root = client_file.parents[3]
    if code_root == PERSONAL_ROOT or PERSONAL_ROOT not in code_root.parents:
        raise ValueError("StarVLA client code is outside personal root")
    critical_paths = [
        client_file,
        code_root / "deployment/model_server/server_policy.py",
        code_root / "deployment/model_server/policy_wrapper.py",
        code_root / "starVLA/model/framework/base_framework.py",
    ]
    critical_hashes = {}
    for path in critical_paths:
        if not path.is_file():
            raise FileNotFoundError(path)
        critical_hashes[str(path.relative_to(code_root))] = file_sha256(path)
    commit = git_value(code_root, "rev-parse", "HEAD").strip()
    status = git_value(code_root, "status", "--porcelain=v1", "--untracked-files=all")
    diff = git_value(code_root, "diff", "--binary", "HEAD")
    return {
        "schema_version": "starvla-policy-provenance-v1",
        "server_handshake_metadata": metadata,
        "checkpoint_path": str(checkpoint),
        "checkpoint_size_bytes": checkpoint.stat().st_size,
        "checkpoint_sha256": file_sha256(checkpoint),
        "policy_code_root": str(code_root),
        "policy_git_commit": commit,
        "policy_git_status_sha256": hashlib.sha256(status.encode("utf-8")).hexdigest(),
        "policy_git_status_line_count": len(status.splitlines()),
        "policy_git_diff_sha256": hashlib.sha256(diff.encode("utf-8")).hexdigest(),
        "critical_source_sha256": critical_hashes,
        "collector_sha256": file_sha256(Path(__file__).resolve()),
        "inference": {
            "unnorm_key": client.unnorm_key,
            "action_ensemble": bool(client.action_ensemble),
            "use_ddim": bool(client.use_ddim),
            "num_ddim_steps": int(client.num_ddim_steps),
            "image_size": list(client.image_size),
        },
    }


def libero_action(row: np.ndarray) -> np.ndarray:
    value = np.asarray(row, dtype=np.float32).reshape(-1)
    if value.size != 7:
        raise ValueError(f"expected seven action dimensions, got {value.shape}")
    gripper = -1.0 if float(value[6]) > 0.5 else 1.0
    return np.concatenate((value[:6], np.asarray([gripper], dtype=np.float32)))


def contact_pairs(env: Any) -> list[dict[str, Any]]:
    model = env.env.sim.model
    rows: list[dict[str, Any]] = []
    for index in range(int(env.env.sim.data.ncon)):
        contact = env.env.sim.data.contact[index]
        left, right = sorted((int(contact.geom1), int(contact.geom2)))
        rows.append(
            {
                "geom_ids": [left, right],
                "geom_names": [model.geom_id2name(left), model.geom_id2name(right)],
                "body_names": [
                    model.body_id2name(int(model.geom_bodyid[left])),
                    model.body_id2name(int(model.geom_bodyid[right])),
                ],
            }
        )
    rows.sort(key=lambda row: tuple(row["geom_ids"]))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bddl")
    parser.add_argument("--suite-name")
    parser.add_argument("--task-id", type=int)
    parser.add_argument("--episode-index", type=int, default=0)
    parser.add_argument("--num-steps-wait", type=int, default=0)
    parser.add_argument("--output", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=17778)
    parser.add_argument("--seed", type=int, default=20260831)
    parser.add_argument("--max-steps", type=int, default=48)
    args = parser.parse_args()

    if os.environ.get("MUJOCO_GL", "").casefold() != "osmesa":
        raise RuntimeError("registered OSMesa environment is required")
    if (args.bddl is None) == (args.suite_name is None):
        raise ValueError("provide exactly one of --bddl or --suite-name")
    benchmark_init_state = None
    benchmark_metadata: dict[str, Any] = {"source": "direct_bddl_reset"}
    if args.suite_name is not None:
        if args.task_id is None:
            raise ValueError("--task-id is required with --suite-name")
        from libero.libero import benchmark, get_libero_path

        suite = benchmark.get_benchmark_dict()[args.suite_name]()
        task = suite.get_task(args.task_id)
        initial_states = suite.get_task_init_states(args.task_id)
        if not 0 <= args.episode_index < len(initial_states):
            raise IndexError("episode index is outside benchmark initial states")
        bddl = personal_path(
            str(Path(get_libero_path("bddl_files")) / task.problem_folder / task.bddl_file),
            must_exist=True,
        )
        benchmark_init_state = initial_states[args.episode_index]
        benchmark_metadata = {
            "source": "libero_benchmark_initial_state",
            "suite_name": args.suite_name,
            "task_id": args.task_id,
            "episode_index": args.episode_index,
        }
    else:
        bddl = personal_path(args.bddl, must_exist=True)
    output = personal_path(args.output, must_exist=False)
    if output.exists() or output.with_suffix(".npz").exists():
        raise FileExistsError(f"refusing to overwrite output stem: {output}")

    from libero.libero.envs import OffScreenRenderEnv
    from examples.LIBERO.eval_files.model2libero_interface import ModelClient

    env = OffScreenRenderEnv(
        bddl_file_name=str(bddl), camera_heights=256, camera_widths=256
    )
    client = ModelClient(
        host=args.host,
        port=args.port,
        unnorm_key="franka",
        action_ensemble=False,
        use_ddim=True,
        num_ddim_steps=10,
    )
    frozen_policy_provenance = policy_provenance(client, ModelClient)
    try:
        env.seed(args.seed)
        observation = env.reset()
        if benchmark_init_state is not None:
            observation = env.set_init_state(benchmark_init_state)
        for _ in range(args.num_steps_wait):
            observation, _, _, _ = env.step([0.0] * 6 + [-1.0])
        instruction = str(env.language_instruction)
        client.reset(instruction)

        boundary_steps: list[int] = []
        boundary_states: list[np.ndarray] = []
        chunks: list[np.ndarray] = []
        executed: list[np.ndarray] = []
        rewards: list[float] = []
        frame_records: list[dict[str, Any]] = []
        done = False

        for step in range(args.max_steps):
            if step % int(client.action_chunk_size) == 0:
                boundary_steps.append(step)
                boundary_states.append(np.asarray(env.get_sim_state(), dtype=np.float64).copy())

            agent = np.ascontiguousarray(observation["agentview_image"][::-1, ::-1])
            wrist = np.ascontiguousarray(observation["robot0_eye_in_hand_image"][::-1, ::-1])
            response = client.step(
                example={"image": [agent, wrist], "lang": instruction}, step=step
            )
            if step % int(client.action_chunk_size) == 0:
                if client.raw_actions is None:
                    raise RuntimeError("server returned no action chunk")
                chunks.append(
                    np.stack([libero_action(row) for row in client.raw_actions], axis=0)
                )

            raw = response["raw_action"]
            action = np.concatenate(
                (
                    np.asarray(raw["world_vector"], dtype=np.float32).reshape(3),
                    np.asarray(raw["rotation_delta"], dtype=np.float32).reshape(3),
                    np.asarray(
                        [-1.0 if float(np.asarray(raw["open_gripper"]).reshape(-1)[0]) > 0.5 else 1.0],
                        dtype=np.float32,
                    ),
                )
            )
            observation, reward, done, info = env.step(action.tolist())
            executed.append(action)
            rewards.append(float(reward))
            frame_records.append(
                {
                    "step": step,
                    "reward": float(reward),
                    "done": bool(done),
                    "state_sha256": digest(np.asarray(env.get_sim_state())),
                    "agent_rgb_sha256": digest(np.asarray(observation["agentview_image"])),
                    "wrist_rgb_sha256": digest(
                        np.asarray(observation["robot0_eye_in_hand_image"])
                    ),
                    "contacts": contact_pairs(env),
                }
            )
            if done:
                break

        arrays_path = output.with_suffix(".npz")
        output.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            arrays_path,
            boundary_steps=np.asarray(boundary_steps, dtype=np.int64),
            boundary_states=np.stack(boundary_states, axis=0),
            action_chunks=np.stack(chunks, axis=0),
            executed_actions=np.stack(executed, axis=0),
            rewards=np.asarray(rewards, dtype=np.float32),
        )
        manifest = {
            "kind": "israc_frozen_starvla_natural_policy_support_rollout",
            "source_schema_version": "P026-source-v1",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "claim_limit": (
                "One natural frozen-StarVLA LIBERO rollout; policy-support evidence only, "
                "not an alias, WAM, correction-harm, multi-task, or success result."
            ),
            "bddl": str(bddl),
            "task": bddl.name,
            "instruction": instruction,
            "seed": args.seed,
            "initialization": benchmark_metadata,
            "num_steps_wait": args.num_steps_wait,
            "max_steps": args.max_steps,
            "executed_steps": len(executed),
            "action_chunk_size": int(client.action_chunk_size),
            "chunk_count": len(chunks),
            "done": bool(done),
            "reward_max": max(rewards) if rewards else 0.0,
            "boundary_steps": boundary_steps,
            "arrays": str(arrays_path),
            "frames": frame_records,
            "policy_provenance": frozen_policy_provenance,
        }
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(temporary, output)
        print(json.dumps({key: manifest[key] for key in (
            "kind", "task", "instruction", "executed_steps", "chunk_count", "done", "reward_max"
        )}, sort_keys=True))
    finally:
        env.close()


if __name__ == "__main__":
    main()
