"""Compare raw WAM, a simple anchored repair, and oracle future in LIBERO."""

from __future__ import annotations

import argparse
import json
import pathlib
import time
from typing import Any

import numpy as np
from PIL import Image

from state_repair_e0 import _predict


def pair(obs: dict[str, Any]):
    return (np.ascontiguousarray(obs["agentview_image"][::-1, ::-1]), np.ascontiguousarray(obs["robot0_eye_in_hand_image"][::-1, ::-1]))


def act(a):
    x = np.asarray(a, dtype=np.float32).copy(); x[6] = 1.0 - 2.0 * float(x[6] > 0.5); return x


def resize(x, n=224):
    return np.asarray(Image.fromarray(np.asarray(x).astype(np.uint8)).resize((n, n), Image.Resampling.BILINEAR), dtype=np.uint8)


def rollout(env, init_state, seed, first, continuation, instruction, client, mode, max_steps):
    env.seed(seed); env.reset(); obs = env.set_init_state(init_state)
    for _ in range(10): obs, *_ = env.step([0.0] * 6 + [-1.0])
    step = 0; queries = 0; reward_sum = 0.0; max_reward = 0.0; done = False; pending = np.asarray(first, dtype=np.float32); used = False
    while step < max_steps and not done:
        if len(pending) == 0:
            p, w = pair(obs)
            if mode in ("raw", "anchored", "oracle") and not used:
                pending = np.asarray(continuation, dtype=np.float32); used = True
            else:
                pending = _predict(client, p, w, instruction)
            queries += 1
        for a in pending:
            if step >= max_steps: break
            obs, rew, done, _ = env.step(act(a).tolist()); reward_sum += float(rew); max_reward = max(max_reward, float(rew)); step += 1
            if done: break
        pending = np.empty((0, 7), dtype=np.float32)
    return {"steps": step, "queries": queries, "reward_sum": reward_sum, "max_reward": max_reward, "done": bool(done), "used_repair": used}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--inputs", required=True); ap.add_argument("--meta", required=True); ap.add_argument("--wam", required=True); ap.add_argument("--out", required=True); ap.add_argument("--port", type=int, default=10097); ap.add_argument("--seed", type=int, default=7); ap.add_argument("--max-steps", type=int, default=120); ap.add_argument("--anchor-alpha", type=float, default=0.25); args = ap.parse_args()
    from libero.libero import benchmark, get_libero_path
    from libero.libero.envs import OffScreenRenderEnv
    from deployment.model_server.tools.websocket_policy_client import WebsocketClientPolicy
    data = np.load(args.inputs, allow_pickle=False); wam = np.load(args.wam, allow_pickle=False); meta = json.loads(pathlib.Path(args.meta).read_text(encoding="utf-8")); client = WebsocketClientPolicy(host="127.0.0.1", port=args.port); rows = []
    for item in meta["records"]:
        key = item["key"]; suite = benchmark.get_benchmark_dict()[item["suite"]](); task = suite.get_task(int(item["task_id"])); init_states = suite.get_task_init_states(int(item["task_id"])); bddl = pathlib.Path(get_libero_path("bddl_files")) / task.problem_folder / task.bddl_file
        first = data[f"{key}_action"]; initial_p = resize(data[f"{key}_primary"]); initial_w = resize(data[f"{key}_wrist"]); raw_p = wam[f"{key}_pred_primary"]; raw_w = wam[f"{key}_pred_wrist"]; gt_p = resize(data[f"{key}_gt_primary"]); gt_w = resize(data[f"{key}_gt_wrist"])
        anchored_p = np.clip(args.anchor_alpha * raw_p.astype(np.float32) + (1.0 - args.anchor_alpha) * initial_p.astype(np.float32), 0, 255).astype(np.uint8); anchored_w = np.clip(args.anchor_alpha * raw_w.astype(np.float32) + (1.0 - args.anchor_alpha) * initial_w.astype(np.float32), 0, 255).astype(np.uint8)
        raw_next = _predict(client, raw_p, raw_w, item["instruction"]); anchored_next = _predict(client, anchored_p, anchored_w, item["instruction"]); oracle_next = _predict(client, gt_p, gt_w, item["instruction"])
        for mode, continuation in (("baseline", None), ("raw", raw_next), ("anchored", anchored_next), ("oracle", oracle_next)):
            env = OffScreenRenderEnv(bddl_file_name=bddl, camera_heights=256, camera_widths=256)
            result = rollout(env, init_states[int(item["episode"])], args.seed + int(item["task_id"]), first, continuation, item["instruction"], client, mode, args.max_steps)
            rows.append({**item, "mode": mode, "raw_vs_oracle_next_action_l2": float(np.linalg.norm(raw_next - oracle_next)), "anchored_vs_oracle_next_action_l2": float(np.linalg.norm(anchored_next - oracle_next)), "anchor_alpha": args.anchor_alpha, **result}); env.close()
    client.close(); out = pathlib.Path(args.out); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps({"schema": "state-repair-e1-anchored-v1", "status": "raw_anchored_oracle_paired", "records": rows, "n_records": len(rows), "created_unix": time.time()}, indent=2), encoding="utf-8"); print(json.dumps({"out": str(out), "n_records": len(rows)}, indent=2))


if __name__ == "__main__": main()
