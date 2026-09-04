"""Prepare paired LIBERO inputs for the action-conditioned WAM probe."""

from __future__ import annotations

import argparse
import json
import pathlib
import time
from typing import Any

import numpy as np
from scipy.spatial.transform import Rotation

from state_repair_e0 import _predict


def _frame_pair(obs: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    return (
        np.ascontiguousarray(obs["agentview_image"][::-1, ::-1]),
        np.ascontiguousarray(obs["robot0_eye_in_hand_image"][::-1, ::-1]),
    )


def _libero_action(a: np.ndarray) -> np.ndarray:
    x = np.asarray(a, dtype=np.float32).copy()
    x[6] = 1.0 - 2.0 * float(x[6] > 0.5)
    return x


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--port", type=int, default=10097)
    ap.add_argument("--suite", default="libero_spatial")
    ap.add_argument("--max-tasks", type=int, default=2)
    ap.add_argument("--episode", type=int, default=0)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--action-horizon", type=int, default=8)
    args = ap.parse_args()

    from libero.libero import benchmark, get_libero_path
    from libero.libero.envs import OffScreenRenderEnv
    from deployment.model_server.tools.websocket_policy_client import WebsocketClientPolicy

    suite = benchmark.get_benchmark_dict()[args.suite]()
    client = WebsocketClientPolicy(host="127.0.0.1", port=args.port)
    records: list[dict[str, Any]] = []
    arrays: dict[str, np.ndarray] = {}
    for task_id in range(min(args.max_tasks, suite.n_tasks)):
        task = suite.get_task(task_id)
        init_states = suite.get_task_init_states(task_id)
        if args.episode >= len(init_states):
            continue
        bddl = pathlib.Path(get_libero_path("bddl_files")) / task.problem_folder / task.bddl_file
        env = OffScreenRenderEnv(bddl_file_name=bddl, camera_heights=256, camera_widths=256)
        env.seed(args.seed + task_id)
        env.reset()
        obs = env.set_init_state(init_states[args.episode])
        for _ in range(10):
            obs, *_ = env.step([0.0] * 6 + [-1.0])
        primary, wrist = _frame_pair(obs)
        state = np.concatenate((
            obs["robot0_eef_pos"],
            # LIBERO quaternion is xyzw; FastWAM uses the same axis-angle
            # convention as its evaluation adapter.
            Rotation.from_quat(np.asarray(obs["robot0_eef_quat"])).as_rotvec(),
            obs["robot0_gripper_qpos"],
        )).astype(np.float32)
        instruction = str(task.language)
        action = _predict(client, primary, wrist, instruction)[: args.action_horizon]
        for a in action:
            obs, *_ = env.step(_libero_action(a).tolist())
        gt_primary, gt_wrist = _frame_pair(obs)
        key = f"task{task_id}"
        arrays[f"{key}_primary"] = primary
        arrays[f"{key}_wrist"] = wrist
        arrays[f"{key}_gt_primary"] = gt_primary
        arrays[f"{key}_gt_wrist"] = gt_wrist
        arrays[f"{key}_action"] = action.astype(np.float32)
        arrays[f"{key}_state"] = state
        records.append({
            "key": key,
            "suite": args.suite,
            "task_id": int(task_id),
            "episode": int(args.episode),
            "instruction": instruction,
            "action_shape": list(action.shape),
        })
        env.close()
    client.close()
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out.with_suffix(".npz"), **arrays)
    out.with_suffix(".json").write_text(json.dumps({
        "schema": "state-repair-e1-inputs-v1",
        "seed": args.seed,
        "records": records,
        "created_unix": time.time(),
    }, indent=2), encoding="utf-8")
    print(json.dumps({"npz": str(out.with_suffix('.npz')), "json": str(out.with_suffix('.json')), "n_records": len(records)}, indent=2))


if __name__ == "__main__":
    main()
