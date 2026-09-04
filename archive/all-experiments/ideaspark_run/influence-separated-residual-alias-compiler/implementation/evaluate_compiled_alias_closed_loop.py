"""Closed-loop frozen-StarVLA evaluation of one compiled physical alias pair."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path("<PERSONAL_RESEARCH_ROOT>").resolve()


def existing(raw: str) -> Path:
    path = Path(raw).resolve()
    if path == ROOT or ROOT not in path.parents or not path.exists():
        raise ValueError(path)
    return path


def new_output(raw: str) -> Path:
    path = Path(raw).resolve()
    if path == ROOT or ROOT not in path.parents or path.exists() or path.with_suffix(".npz").exists():
        raise ValueError(path)
    return path


def image_hash(observation: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    digest.update(np.ascontiguousarray(observation["agentview_image"]).tobytes())
    digest.update(np.ascontiguousarray(observation["robot0_eye_in_hand_image"]).tobytes())
    return digest.hexdigest()


def to_action(raw: dict[str, Any]) -> np.ndarray:
    translation = np.asarray(raw["world_vector"], dtype=np.float32).reshape(3)
    rotation = np.asarray(raw["rotation_delta"], dtype=np.float32).reshape(3)
    opened = float(np.asarray(raw["open_gripper"], dtype=np.float32).reshape(-1)[0])
    gripper = np.asarray([-1.0 if opened > 0.5 else 1.0], dtype=np.float32)
    return np.concatenate((translation, rotation, gripper))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler-result", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=17778)
    parser.add_argument("--max-steps", type=int, default=250)
    args = parser.parse_args()
    compiler_path = existing(args.compiler_result)
    output = new_output(args.output)
    compiler = json.loads(compiler_path.read_text(encoding="utf-8"))
    if not compiler.get("passed") or not compiler.get("best_pairs"):
        raise ValueError("compiler result has no certified pair")
    pair = compiler["best_pairs"][0]
    rollout_path = existing(compiler["rollout"])
    rollout = json.loads(rollout_path.read_text(encoding="utf-8"))
    arrays = np.load(existing(rollout["arrays"]))
    index = int(compiler["candidate_chunk_index"])
    start_state = np.asarray(arrays["boundary_states"][index], dtype=np.float64)
    geom_ids = tuple(int(value) for value in pair["geom_ids"])
    world_values = (float(pair["left_value"]), float(pair["right_value"]))

    from libero.libero.envs import OffScreenRenderEnv
    from examples.LIBERO.eval_files.model2libero_interface import ModelClient

    env = OffScreenRenderEnv(
        bddl_file_name=str(existing(rollout["bddl"])),
        camera_heights=256,
        camera_widths=256,
    )
    client = ModelClient(
        host=args.host,
        port=args.port,
        unnorm_key="franka",
        action_ensemble=False,
        use_ddim=True,
        num_ddim_steps=10,
    )
    original_solref = np.asarray(env.env.sim.model.geom_solref, dtype=np.float64).copy()
    world_rows = []
    action_payload: dict[str, np.ndarray] = {}
    first_chunks = []
    try:
        for world_index, value in enumerate(world_values):
            env.seed(int(rollout["seed"]))
            env.reset()
            observation = env.set_init_state(start_state)
            env.env.sim.model.geom_solref[:] = original_solref
            ids = np.asarray(geom_ids, dtype=np.int64)
            env.env.sim.model.geom_solref[ids, 0] = value
            env.env.sim.model.geom_solref[ids, 1] = 1.0
            env.env.sim.forward()
            observation = env.env._get_observations(force_update=True)
            initial_hash = image_hash(observation)
            client.reset(str(rollout["instruction"]))
            actions = []
            rewards = []
            state_hashes = []
            done = False
            first_chunk = None
            for step in range(args.max_steps):
                agent = np.ascontiguousarray(observation["agentview_image"][::-1, ::-1])
                wrist = np.ascontiguousarray(observation["robot0_eye_in_hand_image"][::-1, ::-1])
                response = client.step(
                    example={"image": [agent, wrist], "lang": str(rollout["instruction"])},
                    step=step,
                )
                if step == 0:
                    if client.raw_actions is None:
                        raise RuntimeError("missing first action chunk")
                    first_chunk = np.asarray(client.raw_actions, dtype=np.float32).copy()
                action = to_action(response["raw_action"])
                observation, reward, done, _ = env.step(action.tolist())
                actions.append(action)
                rewards.append(float(reward))
                state_hashes.append(
                    hashlib.sha256(np.asarray(env.get_sim_state()).tobytes()).hexdigest()
                )
                if done:
                    break
            if first_chunk is None:
                raise RuntimeError("empty closed-loop rollout")
            first_chunks.append(first_chunk)
            action_array = np.stack(actions, axis=0)
            action_payload[f"world_{world_index}_actions"] = action_array
            world_rows.append(
                {
                    "world_index": world_index,
                    "solref_time_constant": value,
                    "initial_image_sha256": initial_hash,
                    "steps": len(actions),
                    "done": bool(done),
                    "reward_max": max(rewards) if rewards else 0.0,
                    "first_chunk_sha256": hashlib.sha256(first_chunk.tobytes()).hexdigest(),
                    "final_state_sha256": state_hashes[-1] if state_hashes else None,
                }
            )
    finally:
        env.close()

    first_chunk_max_abs = float(np.max(np.abs(first_chunks[0] - first_chunks[1])))
    common_steps = min(len(action_payload["world_0_actions"]), len(action_payload["world_1_actions"]))
    action_max_abs = float(np.max(np.abs(
        action_payload["world_0_actions"][:common_steps] - action_payload["world_1_actions"][:common_steps]
    ))) if common_steps else 0.0
    arrays_path = output.with_suffix(".npz")
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(arrays_path, **action_payload)
    payload = {
        "kind": "israc_compiled_alias_closed_loop_frozen_starvla_e0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "claim_limit": (
            "One compiler-selected pair and one saved boundary of one task; evaluates frozen VLA "
            "closed loop without a WAM. This is not multi-task correction-harm evidence."
        ),
        "compiler_result": str(compiler_path),
        "compiler_certificate_sha256": pair["certificate_sha256"],
        "candidate_chunk_index": index,
        "geom_ids": list(geom_ids),
        "worlds": world_rows,
        "initial_images_identical": world_rows[0]["initial_image_sha256"] == world_rows[1]["initial_image_sha256"],
        "first_policy_chunks_identical": first_chunk_max_abs == 0.0,
        "first_policy_chunk_max_abs": first_chunk_max_abs,
        "closed_loop_action_max_abs_over_common_steps": action_max_abs,
        "success_outcomes_differ": world_rows[0]["done"] != world_rows[1]["done"],
        "arrays": str(arrays_path),
        "arguments": vars(args),
    }
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, output)
    print(json.dumps({
        "initial_images_identical": payload["initial_images_identical"],
        "first_policy_chunks_identical": payload["first_policy_chunks_identical"],
        "success_outcomes_differ": payload["success_outcomes_differ"],
        "worlds": world_rows,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
