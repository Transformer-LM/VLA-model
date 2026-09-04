"""Small paired closed-loop pilot for WAM-artifact downstream harm.

This does not claim a learned WAM.  At each policy query, a controlled local
image artifact stands in for a physically implausible imagined observation.
The clean image is the oracle-repair condition.  Every condition starts from
the exact same LIBERO initial state and executes the resulting action chunks.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import time
from typing import Any

import numpy as np

from state_repair_e0 import _artifact, _to_uint8, _predict


def _env_factory(task: Any, bddl: pathlib.Path):
    from libero.libero.envs import OffScreenRenderEnv

    return OffScreenRenderEnv(bddl_file_name=bddl, camera_heights=256, camera_widths=256)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--port", type=int, default=10097)
    ap.add_argument("--suite", default="libero_spatial")
    ap.add_argument("--task-id", type=int, default=0)
    ap.add_argument("--episode", type=int, default=0)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--max-steps", type=int, default=120)
    ap.add_argument("--conditions", default="clean,ghost_shift,erase,oracle_repair")
    args = ap.parse_args()

    from libero.libero import benchmark, get_libero_path
    from deployment.model_server.tools.websocket_policy_client import WebsocketClientPolicy

    bdict = benchmark.get_benchmark_dict()
    suite = bdict[args.suite]()
    task = suite.get_task(args.task_id)
    init_states = suite.get_task_init_states(args.task_id)
    if args.episode >= len(init_states):
        raise IndexError(f"episode {args.episode} unavailable; n={len(init_states)}")
    bddl = pathlib.Path(get_libero_path("bddl_files")) / task.problem_folder / task.bddl_file
    instruction = str(task.language)
    results: list[dict[str, Any]] = []
    client = WebsocketClientPolicy(host="127.0.0.1", port=args.port)

    conditions = [x.strip() for x in args.conditions.split(",") if x.strip()]
    allowed = {"clean", "ghost_shift", "erase", "oracle_repair"}
    unknown = set(conditions) - allowed
    if unknown:
        raise ValueError(f"unknown conditions: {sorted(unknown)}")
    for condition in conditions:
        env = _env_factory(task, bddl)
        env.seed(args.seed + args.task_id)
        env.reset()
        obs = env.set_init_state(init_states[args.episode])
        for _ in range(10):
            obs, *_ = env.step([0.0] * 6 + [-1.0])
        step = 0
        n_queries = 0
        reward_sum = 0.0
        max_reward = 0.0
        done = False
        action_changes: list[float] = []
        while step < args.max_steps and not done:
            primary = np.ascontiguousarray(obs["agentview_image"][::-1, ::-1])
            wrist = np.ascontiguousarray(obs["robot0_eye_in_hand_image"][::-1, ::-1])
            if condition == "ghost_shift":
                query_img, _ = _artifact(primary, "ghost_shift", args.seed + step)
            elif condition == "erase":
                query_img, _ = _artifact(primary, "erase", args.seed + 101 + step)
            else:
                query_img = primary
            act_chunk = _predict(client, query_img, wrist, instruction)
            n_queries += 1

            # For a paired action-change diagnostic, also obtain clean action
            # at the same observation when using an artifact condition.
            if condition in ("ghost_shift", "erase"):
                clean_chunk = _predict(client, primary, wrist, instruction)
                action_changes.append(float(np.linalg.norm(act_chunk - clean_chunk)))

            for step_action in act_chunk:
                if step >= args.max_steps:
                    break
                aa = np.asarray(step_action, dtype=np.float32).copy()
                aa[6] = 1.0 - 2.0 * float(aa[6] > 0.5)
                obs, rew, done, _ = env.step(aa.tolist())
                reward_sum += float(rew)
                max_reward = max(max_reward, float(rew))
                step += 1
                if done:
                    break
        results.append(
            {
                "suite": args.suite,
                "task_id": args.task_id,
                "episode": args.episode,
                "instruction": instruction,
                "condition": condition,
                "steps": step,
                "queries": n_queries,
                "reward_sum": reward_sum,
                "max_reward": max_reward,
                "done": bool(done),
                "mean_action_change_vs_clean": float(np.mean(action_changes)) if action_changes else 0.0,
                "action_change_samples": len(action_changes),
            }
        )
        env.close()
    client.close()
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "schema": "state-repair-closedloop-e0-v1",
                "status": "paired_controlled_artifact_pilot",
                "claim_scope": "downstream sensitivity and short closed-loop effect; no learned WAM claim",
                "seed": args.seed,
                "max_steps": args.max_steps,
                "conditions": conditions,
                "results": results,
                "created_unix": time.time(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"out": str(out), "n_conditions": len(results)}, indent=2))


if __name__ == "__main__":
    main()
