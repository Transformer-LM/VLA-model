"""E0: policy sensitivity to controlled WAM-like imagined-state artifacts.

This is deliberately an oracle/engineering gate, not a WAM result.  The
simulator supplies a clean RGB observation; a deterministic patch transform
creates a physically implausible imagined-state artifact, and the clean image
is used as an oracle repair.  The test asks whether the artifact changes a
frozen StarVLA action chunk and whether the oracle repair returns it.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import time
from typing import Any

import numpy as np


def _quat2axisangle(quat: np.ndarray) -> np.ndarray:
    # Kept for parity with the StarVLA LIBERO adapter; state is recorded only.
    from scipy.spatial.transform import Rotation

    return Rotation.from_quat(np.asarray(quat)[[1, 2, 3, 0]]).as_rotvec()


def _artifact(img: np.ndarray, mode: str, seed: int) -> tuple[np.ndarray, dict[str, Any]]:
    """Apply a deterministic local displacement/erase artifact.

    The transform is not claimed to be a learned WAM corruption model.  It is
    an intervention that preserves most scene pixels while violating local
    temporal/physical consistency, suitable for an E0 causal sensitivity gate.
    """
    x = np.asarray(img).copy()
    h, w = x.shape[:2]
    rng = np.random.default_rng(seed)
    ph = max(40, int(h * 0.24))
    pw = max(40, int(w * 0.24))
    # Central tabletop region; jitter is fixed per sample and recorded.
    y0 = int(h * 0.43 + rng.integers(-max(2, h // 30), max(3, h // 30)))
    x0 = int(w * 0.38 + rng.integers(-max(2, w // 30), max(3, w // 30)))
    y0 = max(0, min(h - ph, y0))
    x0 = max(0, min(w - pw, x0))
    patch = x[y0 : y0 + ph, x0 : x0 + pw].copy()
    dy, dx = -int(h * 0.10), int(w * 0.13)
    y1 = max(0, min(h - ph, y0 + dy))
    x1 = max(0, min(w - pw, x0 + dx))
    if mode == "ghost_shift":
        x[y1 : y1 + ph, x1 : x1 + pw] = patch
    elif mode == "erase":
        # Fill with a border median to mimic an object disappearing from an
        # imagined future without changing the rest of the frame.
        border = np.concatenate(
            [x[max(0, y0 - 6) : y0, x0 : x0 + pw].reshape(-1, 3),
             x[y0 + ph : min(h, y0 + ph + 6), x0 : x0 + pw].reshape(-1, 3)],
            axis=0,
        )
        fill = np.median(border, axis=0).astype(np.uint8) if len(border) else np.zeros(3, np.uint8)
        x[y0 : y0 + ph, x0 : x0 + pw] = fill
    else:
        raise ValueError(mode)
    return x, {"mode": mode, "box": [x0, y0, pw, ph], "target": [x1, y1], "dx": dx, "dy": dy}


def _to_uint8(frame: np.ndarray) -> np.ndarray:
    a = np.asarray(frame)
    if a.dtype != np.uint8:
        a = np.clip(a, 0, 255).astype(np.uint8)
    if a.ndim != 3 or a.shape[-1] != 3:
        raise ValueError(f"expected HWC RGB, got {a.shape}")
    return np.ascontiguousarray(a)


def _predict(client: Any, primary: np.ndarray, wrist: np.ndarray, instruction: str) -> np.ndarray:
    # The released StarVLA server contract accepts HWC uint8 images and text.
    q = {
        "examples": [{"image": [_to_uint8(primary), _to_uint8(wrist)], "lang": instruction}],
        "unnorm_key": "franka",
        "do_sample": False,
        "use_ddim": True,
        "num_ddim_steps": 10,
    }
    out = client.predict_action(q)
    # WebsocketPolicyServer wraps the wrapper output under data.
    return np.asarray(out["data"]["actions"])[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-tasks", type=int, default=2)
    ap.add_argument("--episodes", type=int, default=1)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--port", type=int, default=10097)
    ap.add_argument("--execute-chunk", action="store_true", help="Replay each predicted chunk in a fresh simulator reset")
    args = ap.parse_args()

    # Imports are delayed so the script can report a clean dependency error.
    from libero.libero import benchmark, get_libero_path
    from libero.libero.envs import OffScreenRenderEnv
    from deployment.model_server.tools.websocket_policy_client import WebsocketClientPolicy

    np.random.seed(args.seed)
    client = WebsocketClientPolicy(host="127.0.0.1", port=args.port)
    records: list[dict[str, Any]] = []
    suite_names = ["libero_spatial", "libero_goal"]
    bdict = benchmark.get_benchmark_dict()
    for suite_name in suite_names:
        suite = bdict[suite_name]()
        for task_id in range(min(args.max_tasks, suite.n_tasks)):
            task = suite.get_task(task_id)
            bddl = pathlib.Path(get_libero_path("bddl_files")) / task.problem_folder / task.bddl_file
            env = OffScreenRenderEnv(
                bddl_file_name=bddl,
                camera_heights=256,
                camera_widths=256,
            )
            env.seed(args.seed + task_id)
            init_states = suite.get_task_init_states(task_id)
            for ep in range(min(args.episodes, len(init_states))):
                env.reset()
                obs = env.set_init_state(init_states[ep])
                for _ in range(10):
                    obs, *_ = env.step([0.0] * 6 + [-1.0])
                primary = np.ascontiguousarray(obs["agentview_image"][::-1, ::-1])
                wrist = np.ascontiguousarray(obs["robot0_eye_in_hand_image"][::-1, ::-1])
                instruction = str(task.language)
                # One clean, two artifact, and oracle repair calls per scene.
                ghost_img, ghost_meta = _artifact(primary, "ghost_shift", args.seed + task_id + ep)
                erase_img, erase_meta = _artifact(primary, "erase", args.seed + 101 + task_id + ep)
                conditions = [("clean", primary, wrist, None),
                              ("ghost_shift", ghost_img, wrist, ghost_meta),
                              ("erase", erase_img, wrist, erase_meta),
                              ("oracle_repair", primary, wrist, {"source": "clean_oracle"})]
                preds: dict[str, np.ndarray] = {}
                artifact_meta: dict[str, Any] = {}
                for name, pimg, wimg, meta in conditions:
                    preds[name] = _predict(client, pimg, wimg, instruction)
                    if meta is not None:
                        artifact_meta[name] = meta
                base = preds["clean"]
                for name, act in preds.items():
                    delta = act - base
                    rollout: dict[str, Any] | None = None
                    if args.execute_chunk:
                        # Same initial state for every condition: this is a
                        # paired downstream-effect probe, not a full policy
                        # evaluation.  The simulator is reset before each
                        # chunk and no real robot is involved.
                        run_env = OffScreenRenderEnv(
                            bddl_file_name=bddl,
                            camera_heights=256,
                            camera_widths=256,
                        )
                        run_env.seed(args.seed + task_id)
                        run_env.reset()
                        run_env.set_init_state(init_states[ep])
                        for _ in range(10):
                            run_env.step([0.0] * 6 + [-1.0])
                        rewards: list[float] = []
                        done_rollout = False
                        for step_action in act:
                            aa = np.asarray(step_action, dtype=np.float32).copy()
                            # StarVLA's seventh value is open_gripper in
                            # [0,1]; LIBERO expects close/open in {-1,+1}.
                            aa[6] = 1.0 - 2.0 * float(aa[6] > 0.5)
                            _, rew, done_rollout, _ = run_env.step(aa.tolist())
                            rewards.append(float(rew))
                            if done_rollout:
                                break
                        rollout = {
                            "chunk_steps": len(rewards),
                            "reward_sum": float(np.sum(rewards)),
                            "reward_max": float(np.max(rewards)) if rewards else 0.0,
                            "done": bool(done_rollout),
                        }
                        run_env.close()
                    records.append(
                        {
                            "suite": suite_name,
                            "task_id": int(task_id),
                            "episode": int(ep),
                            "instruction": instruction,
                            "condition": name,
                            "action_shape": list(act.shape),
                            "action_l2": float(np.linalg.norm(act)),
                            "delta_l2_vs_clean": float(np.linalg.norm(delta)),
                            "delta_max_abs_vs_clean": float(np.max(np.abs(delta))),
                            "first_action_clean": base[0].tolist(),
                            "first_action_condition": act[0].tolist(),
                            "artifact": artifact_meta.get(name),
                            "paired_chunk_rollout": rollout,
                        }
                    )
            env.close()
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "state-repair-e0-v1",
        "status": "engineering_oracle_gate",
        "claim_scope": "controlled image artifact sensitivity, not learned WAM performance",
        "server_port": args.port,
        "seed": args.seed,
        "records": records,
        "n_records": len(records),
        "created_unix": time.time(),
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out), "n_records": len(records)}, indent=2))


if __name__ == "__main__":
    main()
