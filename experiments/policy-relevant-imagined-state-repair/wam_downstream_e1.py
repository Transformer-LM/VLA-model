"""E1: action-conditioned WAM imagined-state downstream probe.

This is a small, paired pilot.  A frozen StarVLA proposes an action chunk;
an action-conditioned FastWAM predicts a short future clip; the predicted
last frame is then used as the next StarVLA observation.  The same first
chunk is executed in LIBERO to provide an oracle future observation.  We
compare raw-imagination and oracle-repaired downstream decisions.

The script deliberately reports WAM/video and downstream effects separately.
It is not a claim that a 500-step WAM is a production-quality simulator.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time
from typing import Any

import numpy as np
import torch
from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from omegaconf import OmegaConf
from PIL import Image


PERSONAL_ROOT = pathlib.Path(os.environ.get("VLA_WAM_PERSONAL_ROOT", ".")).expanduser()
ROOT = PERSONAL_ROOT / "workspace"
FASTWAM = ROOT / "FastWAM"
WAM_CFG = FASTWAM / "configs"
WAM_CKPT = FASTWAM / "runs/p027c_libero_videoac_learn500/P027C_VIDEOAC_500_20260901_235909/checkpoints/weights/step_000500_trainable_only.pt"
STATS = PERSONAL_ROOT / "results/israc/P027C_LIBERO_COMBINED_NORM_STATS.json"

sys.path.insert(0, str(FASTWAM))
sys.path.insert(0, str(ROOT / "h1-predictive-aux-starvla"))


def _predict_vla(client: Any, primary: np.ndarray, wrist: np.ndarray, instruction: str) -> np.ndarray:
    q = {
        "examples": [{"image": [np.ascontiguousarray(primary), np.ascontiguousarray(wrist)], "lang": instruction}],
        "unnorm_key": "franka",
        "do_sample": False,
        "use_ddim": True,
        "num_ddim_steps": 10,
    }
    out = client.predict_action(q)
    return np.asarray(out["data"]["actions"])[0].astype(np.float32)


def _libero_action(a: np.ndarray) -> np.ndarray:
    x = np.asarray(a, dtype=np.float32).copy()
    if x.shape[-1] >= 7:
        x[6] = 1.0 - 2.0 * float(x[6] > 0.5)
    return x


def _frame_pair(obs: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    # LIBERO returns camera images upside down in the same way as the E0
    # StarVLA adapter; retain the established paired preprocessing.
    primary = np.ascontiguousarray(obs["agentview_image"][::-1, ::-1])
    wrist = np.ascontiguousarray(obs["robot0_eye_in_hand_image"][::-1, ::-1])
    return primary, wrist


def _resize_frame(frame: np.ndarray, h: int = 224, w: int = 448) -> np.ndarray:
    arr = np.asarray(frame)
    if arr.shape[:2] != (h, w):
        arr = np.asarray(Image.fromarray(arr.astype(np.uint8)).resize((w, h), Image.Resampling.BILINEAR))
    if arr.ndim != 3 or arr.shape[-1] != 3:
        raise ValueError(f"expected HWC RGB frame, got {arr.shape}")
    return np.ascontiguousarray(arr.astype(np.uint8))


def _split_wam_frame(frame: Any) -> tuple[np.ndarray, np.ndarray]:
    arr = np.asarray(frame.convert("RGB") if isinstance(frame, Image.Image) else frame)
    arr = _resize_frame(arr)
    return np.ascontiguousarray(arr[:, :224]), np.ascontiguousarray(arr[:, 224:448])


def _norm_action(processor: Any, action: np.ndarray) -> torch.Tensor:
    # FastWAM is trained on min/max-normalized action/state dictionaries.
    raw = {
        "action": {"default": torch.as_tensor(action, dtype=torch.float32).unsqueeze(0)},
        "state": {"default": torch.zeros((1, 8), dtype=torch.float32)},
    }
    normalized = processor.normalizer.forward(raw)
    return normalized["action"]["default"][0]


def _rollout(env: Any, init_state: Any, seed: int, actions: np.ndarray) -> tuple[dict[str, Any], dict[str, Any]]:
    env.seed(seed)
    env.reset()
    obs = env.set_init_state(init_state)
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
    }, obs


def _build_wam(device: str) -> tuple[Any, Any, Any]:
    # Compose the already-resolved personal action-conditioned config.  No
    # network access is needed; all Wan assets are cached in my_data.
    with initialize_config_dir(version_base=None, config_dir=str(WAM_CFG)):
        cfg = compose(config_name="sim_libero", overrides=["task=p027c_libero_videoac_learn500"])
    cfg.model.action_dit_pretrained_path = str(PERSONAL_ROOT / "models/fastwam/ActionDiT_Wan22_14d_h1024_bf16.pt")
    cfg.model.video_dit_config.action_conditioned = True
    cfg.model.video_dit_config.action_dim = 7
    model = instantiate(cfg.model, model_dtype=torch.bfloat16, device=device)
    model.load_checkpoint(str(WAM_CKPT))
    model.eval()
    from fastwam.datasets.lerobot.processors.fastwam_processor import FastWAMProcessor
    from fastwam.datasets.lerobot.utils.normalizer import load_dataset_stats_from_json

    processor: FastWAMProcessor = instantiate(cfg.data.train.processor).eval()
    processor.set_normalizer_from_stats(load_dataset_stats_from_json(str(STATS)))
    return cfg, model, processor


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--wam-device", default="cuda:0")
    ap.add_argument("--policy-port", type=int, default=10097)
    ap.add_argument("--suite", default="libero_spatial")
    ap.add_argument("--max-tasks", type=int, default=2)
    ap.add_argument("--episode", type=int, default=0)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--wam-steps", type=int, default=2)
    ap.add_argument("--video-frames", type=int, default=5)
    ap.add_argument("--action-horizon", type=int, default=8)
    args = ap.parse_args()

    if args.video_frames % 4 != 1:
        raise ValueError("video-frames must be 1 mod 4 for Wan VAE temporal alignment")
    from libero.libero import benchmark, get_libero_path
    from libero.libero.envs import OffScreenRenderEnv
    from deployment.model_server.tools.websocket_policy_client import WebsocketClientPolicy
    from experiments.libero.eval_libero_single import _obs_to_model_input
    from fastwam.datasets.lerobot.robot_video_dataset import DEFAULT_PROMPT

    cfg, wam, processor = _build_wam(args.wam_device)
    client = WebsocketClientPolicy(host="127.0.0.1", port=args.policy_port)
    bdict = benchmark.get_benchmark_dict()
    suite = bdict[args.suite]()
    records: list[dict[str, Any]] = []

    for task_id in range(min(args.max_tasks, suite.n_tasks)):
        task = suite.get_task(task_id)
        init_states = suite.get_task_init_states(task_id)
        if args.episode >= len(init_states):
            continue
        bddl = pathlib.Path(get_libero_path("bddl_files")) / task.problem_folder / task.bddl_file
        instruction = str(task.language)

        env = OffScreenRenderEnv(bddl_file_name=bddl, camera_heights=256, camera_widths=256)
        env.seed(args.seed + task_id)
        env.reset()
        obs = env.set_init_state(init_states[args.episode])
        for _ in range(10):
            obs, *_ = env.step([0.0] * 6 + [-1.0])
        primary, wrist = _frame_pair(obs)
        vla_action = _predict_vla(client, primary, wrist, instruction)
        vla_action = vla_action[: args.action_horizon]

        # WAM input uses the same two-camera horizontal representation as its
        # training data.  The exact raw action is normalized only for WAM.
        image, proprio, _ = _obs_to_model_input(
            obs, cfg=cfg, processor=processor, width=448, height=224,
            device=args.wam_device, dtype=wam.torch_dtype,
        )
        action_norm = _norm_action(processor, vla_action).to(device=args.wam_device, dtype=wam.torch_dtype)
        with torch.inference_mode():
            predicted = wam.infer_joint(
                prompt=DEFAULT_PROMPT.format(task=instruction),
                input_image=image,
                num_video_frames=args.video_frames,
                action_horizon=args.action_horizon,
                action=action_norm.unsqueeze(0),
                proprio=proprio,
                num_inference_steps=args.wam_steps,
                seed=args.seed + task_id,
                rand_device="cpu",
                tiled=False,
                test_action_with_infer_action=False,
            )
        pred_primary, pred_wrist = _split_wam_frame(predicted["video"][-1])

        # Ground-truth future after exactly the proposed first chunk.
        gt_rollout_env = OffScreenRenderEnv(bddl_file_name=bddl, camera_heights=256, camera_widths=256)
        gt_rollout, gt_obs = _rollout(gt_rollout_env, init_states[args.episode], args.seed + task_id, vla_action)
        gt_primary, gt_wrist = _frame_pair(gt_obs)
        pred_cat = np.concatenate([pred_primary, pred_wrist], axis=1).astype(np.float32)
        gt_cat = np.concatenate([gt_primary, gt_wrist], axis=1).astype(np.float32)
        mse = float(np.mean((pred_cat - gt_cat) ** 2))
        psnr = float(10.0 * np.log10((255.0 * 255.0) / max(mse, 1e-8)))

        # Query the downstream VLA in three conditions.  raw uses the WAM
        # imagined last frame; oracle uses the actual simulator frame.
        raw_next = _predict_vla(client, pred_primary, pred_wrist, instruction)
        oracle_next = _predict_vla(client, gt_primary, gt_wrist, instruction)
        raw_roll_env = OffScreenRenderEnv(bddl_file_name=bddl, camera_heights=256, camera_widths=256)
        oracle_roll_env = OffScreenRenderEnv(bddl_file_name=bddl, camera_heights=256, camera_widths=256)
        raw_roll, _ = _rollout(raw_roll_env, init_states[args.episode], args.seed + task_id, np.concatenate([vla_action, raw_next], axis=0))
        oracle_roll, _ = _rollout(oracle_roll_env, init_states[args.episode], args.seed + task_id, np.concatenate([vla_action, oracle_next], axis=0))
        records.append({
            "suite": args.suite,
            "task_id": int(task_id),
            "episode": int(args.episode),
            "instruction": instruction,
            "vla_action_shape": list(vla_action.shape),
            "wam_video_frames": int(args.video_frames),
            "wam_inference_steps": int(args.wam_steps),
            "wam_future_psnr_vs_gt": psnr,
            "initial_chunk_rollout": gt_rollout,
            "raw_imagination_next_action_l2": float(np.linalg.norm(raw_next)),
            "oracle_repair_next_action_l2": float(np.linalg.norm(oracle_next)),
            "raw_vs_oracle_next_action_l2": float(np.linalg.norm(raw_next - oracle_next)),
            "raw_imagination_rollout": raw_roll,
            "oracle_repair_rollout": oracle_roll,
            "claim_scope": "action-conditioned WAM downstream probe; no learned repair claim",
        })
        for e in (env, gt_rollout_env, raw_roll_env, oracle_roll_env):
            e.close()

    client.close()
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "state-repair-e1-wam-downstream-v1",
        "status": "paired_action_conditioned_wam_probe",
        "seed": args.seed,
        "records": records,
        "n_records": len(records),
        "wam_checkpoint": str(WAM_CKPT),
        "created_unix": time.time(),
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out), "n_records": len(records)}, indent=2))


if __name__ == "__main__":
    main()
