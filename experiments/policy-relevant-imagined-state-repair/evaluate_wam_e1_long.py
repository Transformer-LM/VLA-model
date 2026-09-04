"""Longer paired closed-loop test for raw WAM imagination vs actual state."""

from __future__ import annotations

import argparse
import json
import pathlib
import time
from typing import Any

import numpy as np

from state_repair_e0 import _predict


def _pair(obs: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    return (np.ascontiguousarray(obs["agentview_image"][::-1, ::-1]), np.ascontiguousarray(obs["robot0_eye_in_hand_image"][::-1, ::-1]))


def _action(a: np.ndarray) -> np.ndarray:
    x = np.asarray(a, dtype=np.float32).copy()
    x[6] = 1.0 - 2.0 * float(x[6] > 0.5)
    return x


def _run(env: Any, init_state: Any, seed: int, first: np.ndarray, continuation: np.ndarray | None, instruction: str, client: Any, mode: str, max_steps: int) -> dict[str, Any]:
    env.seed(seed)
    env.reset()
    obs = env.set_init_state(init_state)
    for _ in range(10):
        obs, *_ = env.step([0.0] * 6 + [-1.0])
    step = 0
    queries = 0
    reward_sum = 0.0
    max_reward = 0.0
    done = False
    pending = np.asarray(first, dtype=np.float32)
    used_imagined = False
    while step < max_steps and not done:
        if len(pending) == 0:
            primary, wrist = _pair(obs)
            if mode == "raw" and not used_imagined and continuation is not None:
                pending = np.asarray(continuation, dtype=np.float32)
                used_imagined = True
            else:
                pending = _predict(client, primary, wrist, instruction)
            queries += 1
        for a in pending:
            if step >= max_steps:
                break
            obs, rew, done, _ = env.step(_action(a).tolist())
            reward_sum += float(rew)
            max_reward = max(max_reward, float(rew))
            step += 1
            if done:
                break
        pending = np.empty((0, 7), dtype=np.float32)
    return {"steps": step, "queries": queries, "reward_sum": reward_sum, "max_reward": max_reward, "done": bool(done), "used_imagined": used_imagined}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--wam", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--port", type=int, default=10097)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--max-steps", type=int, default=120)
    args = ap.parse_args()

    from libero.libero import benchmark, get_libero_path
    from libero.libero.envs import OffScreenRenderEnv
    from deployment.model_server.tools.websocket_policy_client import WebsocketClientPolicy

    data = np.load(args.inputs, allow_pickle=False)
    wam = np.load(args.wam, allow_pickle=False)
    meta = json.loads(pathlib.Path(args.meta).read_text(encoding="utf-8"))
    client = WebsocketClientPolicy(host="127.0.0.1", port=args.port)
    rows = []
    for item in meta["records"]:
        key = item["key"]
        suite = benchmark.get_benchmark_dict()[item["suite"]]()
        task = suite.get_task(int(item["task_id"]))
        init_states = suite.get_task_init_states(int(item["task_id"]))
        bddl = pathlib.Path(get_libero_path("bddl_files")) / task.problem_folder / task.bddl_file
        first = data[f"{key}_action"]
        pred_primary = wam[f"{key}_pred_primary"]
        pred_wrist = wam[f"{key}_pred_wrist"]
        raw_next = _predict(client, pred_primary, pred_wrist, item["instruction"])
        for mode in ("baseline", "raw"):
            env = OffScreenRenderEnv(bddl_file_name=bddl, camera_heights=256, camera_widths=256)
            result = _run(env, init_states[int(item["episode"])], args.seed + int(item["task_id"]), first, raw_next if mode == "raw" else None, item["instruction"], client, mode, args.max_steps)
            rows.append({**item, "mode": mode, "raw_vs_actual_next_action_l2": float(np.linalg.norm(raw_next - _predict(client, data[f"{key}_gt_primary"], data[f"{key}_gt_wrist"], item["instruction"]))), **result})
            env.close()
    client.close()
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"schema": "state-repair-e1-long-v1", "status": "paired_long_closed_loop", "records": rows, "n_records": len(rows), "created_unix": time.time()}, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out), "n_records": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
