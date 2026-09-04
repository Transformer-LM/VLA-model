"""Evaluate raw imagined vs oracle-repaired WAM future as VLA input."""

from __future__ import annotations

import argparse
import json
import pathlib
import time
from typing import Any

import numpy as np

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


def _rollout(env: Any, init_state: Any, seed: int, actions: np.ndarray) -> dict[str, Any]:
    env.seed(seed)
    env.reset()
    env.set_init_state(init_state)
    for _ in range(10):
        obs, *_ = env.step([0.0] * 6 + [-1.0])
    rewards: list[float] = []
    done = False
    for action in actions:
        obs, rew, done, _ = env.step(_libero_action(action).tolist())
        rewards.append(float(rew))
        if done:
            break
    return {
        "steps": len(rewards),
        "reward_sum": float(np.sum(rewards)) if rewards else 0.0,
        "max_reward": float(np.max(rewards)) if rewards else 0.0,
        "done": bool(done),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--wam", required=True)
    ap.add_argument("--wam-meta", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--port", type=int, default=10097)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    from libero.libero import benchmark, get_libero_path
    from libero.libero.envs import OffScreenRenderEnv
    from deployment.model_server.tools.websocket_policy_client import WebsocketClientPolicy

    data = np.load(args.inputs, allow_pickle=False)
    wam_data = np.load(args.wam, allow_pickle=False)
    meta = json.loads(pathlib.Path(args.meta).read_text(encoding="utf-8"))
    wam_meta = json.loads(pathlib.Path(args.wam_meta).read_text(encoding="utf-8"))
    if [x["key"] for x in meta["records"]] != [x["key"] for x in wam_meta["records"]]:
        raise ValueError("input/WAM metadata key mismatch")
    client = WebsocketClientPolicy(host="127.0.0.1", port=args.port)
    records: list[dict[str, Any]] = []
    for item in meta["records"]:
        key = item["key"]
        primary = data[f"{key}_primary"]
        wrist = data[f"{key}_wrist"]
        gt_primary = data[f"{key}_gt_primary"]
        gt_wrist = data[f"{key}_gt_wrist"]
        action = data[f"{key}_action"]
        pred_primary = wam_data[f"{key}_pred_primary"]
        pred_wrist = wam_data[f"{key}_pred_wrist"]
        raw_next = _predict(client, pred_primary, pred_wrist, item["instruction"])
        oracle_next = _predict(client, gt_primary, gt_wrist, item["instruction"])
        suite = benchmark.get_benchmark_dict()[item["suite"]]()
        task = suite.get_task(int(item["task_id"]))
        init_states = suite.get_task_init_states(int(item["task_id"]))
        bddl = pathlib.Path(get_libero_path("bddl_files")) / task.problem_folder / task.bddl_file
        raw_env = OffScreenRenderEnv(bddl_file_name=bddl, camera_heights=256, camera_widths=256)
        oracle_env = OffScreenRenderEnv(bddl_file_name=bddl, camera_heights=256, camera_widths=256)
        raw_roll = _rollout(raw_env, init_states[int(item["episode"])], args.seed + int(item["task_id"]), np.concatenate([action, raw_next], axis=0))
        oracle_roll = _rollout(oracle_env, init_states[int(item["episode"])], args.seed + int(item["task_id"]), np.concatenate([action, oracle_next], axis=0))
        records.append({
            **item,
            "raw_vs_oracle_next_action_l2": float(np.linalg.norm(raw_next - oracle_next)),
            "raw_next_action_shape": list(raw_next.shape),
            "oracle_next_action_shape": list(oracle_next.shape),
            "raw_imagination_rollout": raw_roll,
            "oracle_repair_rollout": oracle_roll,
            "claim_scope": "downstream probe with oracle future repair; no learned repair claim",
        })
        raw_env.close()
        oracle_env.close()
    client.close()
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "schema": "state-repair-e1-downstream-v1",
        "status": "paired_raw_vs_oracle_future",
        "records": records,
        "n_records": len(records),
        "created_unix": time.time(),
    }, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out), "n_records": len(records)}, indent=2))


if __name__ == "__main__":
    main()
