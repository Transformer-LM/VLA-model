"""Run only the WAM half of E1 on prepared personal NPZ inputs."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from typing import Any

import numpy as np
import torch
from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from PIL import Image


ROOT = pathlib.Path("<PERSONAL_RESEARCH_ROOT>/workspace")
FASTWAM = ROOT / "FastWAM"
WAM_CFG = FASTWAM / "configs"
WAM_CKPT = FASTWAM / "runs/p027c_libero_videoac_learn500/P027C_VIDEOAC_500_20260901_235909/checkpoints/weights/step_000500_trainable_only.pt"
STATS = pathlib.Path("<PERSONAL_RESEARCH_ROOT>/results/israc/P027C_LIBERO_COMBINED_NORM_STATS.json")

sys.path.insert(0, str(FASTWAM))


def _resize(frame: np.ndarray, h: int = 224, w: int = 224) -> np.ndarray:
    return np.asarray(Image.fromarray(np.asarray(frame).astype(np.uint8)).resize((w, h), Image.Resampling.BILINEAR), dtype=np.uint8)


def _input_tensor(primary: np.ndarray, wrist: np.ndarray, device: str, dtype: torch.dtype) -> torch.Tensor:
    rgb = np.concatenate([_resize(primary), _resize(wrist)], axis=1)
    return torch.from_numpy(rgb).permute(2, 0, 1).unsqueeze(0).to(device=device, dtype=dtype) * (2.0 / 255.0) - 1.0


def _normalize(processor: Any, state: np.ndarray, action: np.ndarray, device: str, dtype: torch.dtype):
    raw = {
        "action": {"default": torch.as_tensor(action, dtype=torch.float32).unsqueeze(0)},
        "state": {"default": torch.as_tensor(state, dtype=torch.float32).reshape(1, -1)},
    }
    out = processor.normalizer.forward(raw)
    return out["state"]["default"][0].to(device=device, dtype=dtype), out["action"]["default"][0].to(device=device, dtype=dtype)


def _split(frame: object) -> tuple[np.ndarray, np.ndarray]:
    arr = np.asarray(frame.convert("RGB") if isinstance(frame, Image.Image) else frame, dtype=np.uint8)
    arr = np.asarray(Image.fromarray(arr).resize((448, 224), Image.Resampling.BILINEAR), dtype=np.uint8)
    return np.ascontiguousarray(arr[:, :224]), np.ascontiguousarray(arr[:, 224:448])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--wam-steps", type=int, default=2)
    ap.add_argument("--video-frames", type=int, default=5)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--ckpt", default=str(WAM_CKPT), help="trainable-only or full WAM checkpoint")
    args = ap.parse_args()

    if args.video_frames % 4 != 1:
        raise ValueError("video-frames must be 1 mod 4")
    meta = json.loads(pathlib.Path(args.meta).read_text(encoding="utf-8"))
    data = np.load(args.inputs, allow_pickle=False)

    with initialize_config_dir(version_base=None, config_dir=str(WAM_CFG)):
        cfg = compose(config_name="sim_libero", overrides=["task=p027c_libero_videoac_learn500"])
    model = instantiate(cfg.model, model_dtype=torch.bfloat16, device=args.device)
    # This personal pilot checkpoint intentionally stores only the two newly
    # trained action/proprio interfaces.  The Wan MoT backbone is loaded by
    # instantiate() from the local model cache; merge the trainable state
    # without pretending this is a full checkpoint.
    ckpt_path = pathlib.Path(args.ckpt).expanduser()
    if not ckpt_path.is_file():
        raise FileNotFoundError(f"WAM checkpoint not found: {ckpt_path}")
    payload = torch.load(str(ckpt_path), map_location="cpu")
    if "state_dict" in payload:
        incompat = model.load_state_dict(payload["state_dict"], strict=False)
        if incompat.unexpected_keys:
            raise RuntimeError(f"unexpected trainable keys: {incompat.unexpected_keys}")
    else:
        model.load_checkpoint(str(WAM_CKPT))
    model.eval()
    from fastwam.datasets.lerobot.processors.fastwam_processor import FastWAMProcessor
    from fastwam.datasets.lerobot.utils.normalizer import load_dataset_stats_from_json

    processor: FastWAMProcessor = instantiate(cfg.data.train.processor).eval()
    processor.set_normalizer_from_stats(load_dataset_stats_from_json(str(STATS)))
    outputs: dict[str, np.ndarray] = {}
    records = []
    for item in meta["records"]:
        key = item["key"]
        primary = data[f"{key}_primary"]
        wrist = data[f"{key}_wrist"]
        gt_primary = data[f"{key}_gt_primary"]
        gt_wrist = data[f"{key}_gt_wrist"]
        state = data[f"{key}_state"]
        action = data[f"{key}_action"]
        image = _input_tensor(primary, wrist, args.device, model.torch_dtype)
        proprio, action_norm = _normalize(processor, state, action, args.device, model.torch_dtype)
        with torch.inference_mode():
            pred = model.infer_joint(
                prompt=str(item["instruction"]),
                input_image=image,
                num_video_frames=args.video_frames,
                action_horizon=int(action.shape[0]),
                action=action_norm.unsqueeze(0),
                proprio=proprio,
                num_inference_steps=args.wam_steps,
                seed=args.seed + int(item["task_id"]),
                rand_device="cpu",
                tiled=False,
                test_action_with_infer_action=False,
            )
        pred_primary, pred_wrist = _split(pred["video"][-1])
        gt_cat = np.concatenate([_resize(gt_primary), _resize(gt_wrist)], axis=1).astype(np.float32)
        pred_cat = np.concatenate([pred_primary, pred_wrist], axis=1).astype(np.float32)
        mse = float(np.mean((pred_cat - gt_cat) ** 2))
        psnr = float(10.0 * np.log10((255.0 * 255.0) / max(mse, 1e-8)))
        outputs[f"{key}_pred_primary"] = pred_primary
        outputs[f"{key}_pred_wrist"] = pred_wrist
        records.append({
            **item,
            "wam_future_psnr_vs_gt": psnr,
            "wam_future_mse_vs_gt": mse,
            "pred_frame_shape": [int(pred_cat.shape[0]), int(pred_cat.shape[1]), int(pred_cat.shape[2])],
        })
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out.with_suffix(".npz"), **outputs)
    out.with_suffix(".json").write_text(json.dumps({
        "schema": "state-repair-e1-wam-output-v1",
        "status": "action_conditioned_wam_future_probe",
        "records": records,
        "wam_checkpoint": str(ckpt_path),
        "created_unix": time.time(),
    }, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out), "n_records": len(records)}, indent=2))


if __name__ == "__main__":
    main()
