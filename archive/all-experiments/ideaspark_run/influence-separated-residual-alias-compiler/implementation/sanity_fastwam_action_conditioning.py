#!/usr/bin/env python3
"""Smallest real-weight sanity for the action-conditioned FastWAM video path.

This is an engineering gate only.  The available checkpoint was trained with
``action_conditioned: false``; therefore the action embedding is deliberately
newly initialized and the output must never be reported as a learned LIBERO
WAM result.  The gate checks that, after loading all reusable weights, changing
only the supplied action changes future video tokens while leaving the fixed
first-frame path and action-expert output unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import torch
from hydra.utils import instantiate
from omegaconf import OmegaConf


PROTOCOL_VERSION = "P027-fastwam-ac-forward-sanity-v1"


def sha256_file(path: Path, chunk_size: int = 16 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                return digest.hexdigest()
            digest.update(chunk)


def atomic_no_clobber_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {path}")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-config", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--seed", type=int, default=20270901)
    parser.add_argument("--latent-frames", type=int, default=3)
    parser.add_argument("--latent-height", type=int, default=4)
    parser.add_argument("--latent-width", type=int, default=4)
    parser.add_argument("--action-horizon", type=int, default=8)
    parser.add_argument("--context-length", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {args.output}")
    if not args.model_config.is_file():
        raise FileNotFoundError(args.model_config)
    if not args.checkpoint.is_file():
        raise FileNotFoundError(args.checkpoint)
    if args.latent_frames <= 1:
        raise ValueError("latent-frames must exceed one")
    if args.action_horizon % (args.latent_frames - 1) != 0:
        raise ValueError("action-horizon must be divisible by latent-frames - 1")

    device = torch.device(args.device)
    if device.type != "cuda" or not torch.cuda.is_available():
        raise RuntimeError("This real-weight sanity requires CUDA")

    model_config_bytes = args.model_config.read_bytes()
    model_config_sha256 = hashlib.sha256(model_config_bytes).hexdigest()
    cfg = OmegaConf.create(model_config_bytes.decode("utf-8"))
    original_action_conditioned = bool(cfg.video_dit_config.action_conditioned)
    if original_action_conditioned:
        raise ValueError(
            "This protocol requires a source config with action_conditioned=false"
        )

    checkpoint_sha256_before = sha256_file(args.checkpoint)
    checkpoint_payload = torch.load(args.checkpoint, map_location="cpu")
    if not isinstance(checkpoint_payload, dict) or "mot" not in checkpoint_payload:
        raise ValueError("Checkpoint must contain a non-empty `mot` state dictionary")
    checkpoint_state = checkpoint_payload["mot"]
    if not isinstance(checkpoint_state, dict) or not checkpoint_state:
        raise ValueError("Checkpoint `mot` state dictionary is empty")
    checkpoint_has_action_embedding = any(
        "action_embedding" in str(key) for key in checkpoint_state.keys()
    )
    if checkpoint_has_action_embedding:
        raise ValueError(
            "This protocol requires a checkpoint trained without action embedding"
        )

    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    cfg.video_dit_config.action_conditioned = True
    cfg.video_dit_config.action_dim = int(cfg.action_dit_config.action_dim)
    model = instantiate(cfg, model_dtype=torch.bfloat16, device=str(device))

    model_state = model.mot.state_dict()
    expected_missing_keys = {
        key for key in model_state.keys() if "action_embedding" in key
    }
    if len(expected_missing_keys) != 2:
        raise ValueError(
            "Expected exactly action_embedding weight and bias after enabling the branch, "
            f"got {sorted(expected_missing_keys)}"
        )
    missing_keys = sorted(set(model_state) - set(checkpoint_state))
    unexpected_keys = sorted(set(checkpoint_state) - set(model_state))
    shape_mismatches = sorted(
        key
        for key in set(model_state).intersection(checkpoint_state)
        if tuple(model_state[key].shape) != tuple(checkpoint_state[key].shape)
    )
    if set(missing_keys) != expected_missing_keys:
        raise ValueError(
            "Checkpoint missing-key schema differs from the two newly introduced action "
            f"embedding parameters: {missing_keys}"
        )
    if unexpected_keys:
        raise ValueError(f"Checkpoint contains unexpected MoT keys: {unexpected_keys}")
    if shape_mismatches:
        raise ValueError(f"Checkpoint contains shape mismatches: {shape_mismatches}")
    incompatibility = model.mot.load_state_dict(checkpoint_state, strict=False)
    if set(incompatibility.missing_keys) != expected_missing_keys:
        raise ValueError(
            f"Runtime missing keys differ from the frozen schema: {incompatibility.missing_keys}"
        )
    if incompatibility.unexpected_keys:
        raise ValueError(
            f"Runtime reported unexpected keys: {incompatibility.unexpected_keys}"
        )

    if model.proprio_encoder is not None:
        if "proprio_encoder" not in checkpoint_payload:
            raise ValueError("Checkpoint is missing reusable proprio_encoder weights")
        model.proprio_encoder.load_state_dict(
            checkpoint_payload["proprio_encoder"], strict=True
        )
    elif "proprio_encoder" in checkpoint_payload:
        raise ValueError(
            "Checkpoint has proprio_encoder weights but instantiated model disables them"
        )
    model.eval()

    dtype = model.torch_dtype
    batch_size = 1
    video = torch.randn(
        batch_size,
        int(model.vae.model.z_dim),
        args.latent_frames,
        args.latent_height,
        args.latent_width,
        device=device,
        dtype=dtype,
    )
    noisy_action = torch.randn(
        batch_size,
        args.action_horizon,
        int(model.action_expert.action_dim),
        device=device,
        dtype=dtype,
    )
    context = torch.randn(
        batch_size,
        args.context_length,
        int(model.text_dim),
        device=device,
        dtype=dtype,
    )
    context_mask = torch.ones(
        batch_size, args.context_length, device=device, dtype=torch.bool
    )
    timestep_video = torch.full((batch_size,), 0.5, device=device, dtype=dtype)
    timestep_action = torch.full((batch_size,), 0.5, device=device, dtype=dtype)

    action_a = torch.zeros_like(noisy_action)
    action_b = torch.zeros_like(noisy_action)
    action_b[..., 0] = torch.linspace(
        -1.0, 1.0, args.action_horizon, device=device, dtype=dtype
    )

    patch_t, patch_h, patch_w = (int(value) for value in model.video_expert.patch_size)
    if args.latent_frames % patch_t != 0:
        raise ValueError("latent-frames must be divisible by the temporal patch size")
    if args.latent_height % patch_h != 0 or args.latent_width % patch_w != 0:
        raise ValueError("latent spatial shape must be divisible by patch size")
    tokens_per_frame = (
        (args.latent_height // patch_h) * (args.latent_width // patch_w)
    )
    attention_mask = model._build_mot_attention_mask(
        video_seq_len=(args.latent_frames // patch_t) * tokens_per_frame,
        action_seq_len=args.action_horizon,
        video_tokens_per_frame=tokens_per_frame,
        device=device,
    )

    torch.cuda.reset_peak_memory_stats(device)
    with torch.inference_mode():
        video_a1, predicted_action_a1 = model._joint_denoise_core(
            latents_video=video,
            latents_action=noisy_action,
            timestep_video=timestep_video,
            timestep_action=timestep_action,
            context=context,
            context_mask=context_mask,
            attention_mask=attention_mask,
            fuse_vae_embedding_in_latents=True,
            action_condition=action_a,
        )
        video_a2, predicted_action_a2 = model._joint_denoise_core(
            latents_video=video,
            latents_action=noisy_action,
            timestep_video=timestep_video,
            timestep_action=timestep_action,
            context=context,
            context_mask=context_mask,
            attention_mask=attention_mask,
            fuse_vae_embedding_in_latents=True,
            action_condition=action_a,
        )
        video_b, predicted_action_b = model._joint_denoise_core(
            latents_video=video,
            latents_action=noisy_action,
            timestep_video=timestep_video,
            timestep_action=timestep_action,
            context=context,
            context_mask=context_mask,
            attention_mask=attention_mask,
            fuse_vae_embedding_in_latents=True,
            action_condition=action_b,
        )
    torch.cuda.synchronize(device)

    repeat_video_difference = (video_a1 - video_a2).abs().float()
    ab_video_difference = (video_a1 - video_b).abs().float()
    repeat_first_frame_max_abs_diff = float(
        repeat_video_difference[:, :, :1].max().item()
    )
    repeat_future_max_abs_diff = float(
        repeat_video_difference[:, :, 1:].max().item()
    )
    repeat_future_mean_abs_diff = float(
        repeat_video_difference[:, :, 1:].mean().item()
    )
    repeat_action_output_max_abs_diff = float(
        (predicted_action_a1 - predicted_action_a2).abs().float().max().item()
    )
    first_frame_max_abs_diff = float(ab_video_difference[:, :, :1].max().item())
    future_max_abs_diff = float(ab_video_difference[:, :, 1:].max().item())
    future_mean_abs_diff = float(ab_video_difference[:, :, 1:].mean().item())
    action_output_max_abs_diff = float(
        (predicted_action_a1 - predicted_action_b).abs().float().max().item()
    )
    finite = bool(
        torch.isfinite(video_a1).all()
        and torch.isfinite(video_a2).all()
        and torch.isfinite(video_b).all()
        and torch.isfinite(predicted_action_a1).all()
        and torch.isfinite(predicted_action_a2).all()
        and torch.isfinite(predicted_action_b).all()
    )
    effect_floor = max(repeat_future_max_abs_diff * 10.0, 1.0e-5)
    mean_effect_floor = max(repeat_future_mean_abs_diff * 10.0, 1.0e-7)
    isolation_tolerance = 1.0e-6
    future_conditioning_live = bool(
        future_max_abs_diff > effect_floor
        and future_mean_abs_diff > mean_effect_floor
    )
    first_frame_isolated = bool(
        first_frame_max_abs_diff
        <= repeat_first_frame_max_abs_diff + isolation_tolerance
    )
    action_expert_isolated = bool(
        action_output_max_abs_diff
        <= repeat_action_output_max_abs_diff + isolation_tolerance
    )

    checkpoint_sha256_after = sha256_file(args.checkpoint)
    model_config_sha256_after = sha256_file(args.model_config)
    input_files_stable = bool(
        checkpoint_sha256_before == checkpoint_sha256_after
        and model_config_sha256 == model_config_sha256_after
    )

    source_paths = {
        "video_expert": Path(inspect.getsourcefile(type(model.video_expert))).resolve(),
        "mot": Path(inspect.getsourcefile(type(model.mot))).resolve(),
        "model": Path(inspect.getsourcefile(type(model))).resolve(),
        "sanity_script": Path(__file__).resolve(),
    }
    source_sha256 = {name: sha256_file(path) for name, path in source_paths.items()}
    repo_root = args.model_config.resolve().parents[2]
    git_commit = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    git_status = subprocess.run(
        ["git", "-C", str(repo_root), "status", "--short"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    passed = bool(
        finite
        and input_files_stable
        and not original_action_conditioned
        and not checkpoint_has_action_embedding
        and bool(model.video_expert.action_conditioned)
        and future_conditioning_live
        and first_frame_isolated
        and action_expert_isolated
    )

    payload = {
        "protocol_version": PROTOCOL_VERSION,
        "claim_limit": (
            "Engineering forward-path sanity only. The checkpoint was trained "
            "without action conditioning; no learned WAM, residual-transport, "
            "ranking, or VLA claim is supported."
        ),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_config": str(args.model_config.resolve()),
        "model_config_sha256": model_config_sha256,
        "model_config_sha256_after": model_config_sha256_after,
        "source_config_action_conditioned": original_action_conditioned,
        "checkpoint": str(args.checkpoint.resolve()),
        "checkpoint_sha256": checkpoint_sha256_before,
        "checkpoint_sha256_after": checkpoint_sha256_after,
        "checkpoint_step": checkpoint_payload.get("step"),
        "checkpoint_has_action_embedding": checkpoint_has_action_embedding,
        "action_embedding_freshly_initialized": not checkpoint_has_action_embedding,
        "checkpoint_missing_keys": missing_keys,
        "checkpoint_unexpected_keys": unexpected_keys,
        "checkpoint_shape_mismatches": shape_mismatches,
        "input_files_stable": input_files_stable,
        "source_paths": {name: str(path) for name, path in source_paths.items()},
        "source_sha256": source_sha256,
        "fastwam_git_commit": git_commit,
        "fastwam_git_status_short": git_status,
        "seed": args.seed,
        "device": str(device),
        "gpu_name": torch.cuda.get_device_name(device),
        "torch_dtype": str(dtype),
        "latent_shape": list(video.shape),
        "action_shape": list(action_a.shape),
        "context_shape": list(context.shape),
        "video_output_shape": list(video_a1.shape),
        "action_output_shape": list(predicted_action_a1.shape),
        "repeat_first_frame_max_abs_diff": repeat_first_frame_max_abs_diff,
        "repeat_future_max_abs_diff": repeat_future_max_abs_diff,
        "repeat_future_mean_abs_diff": repeat_future_mean_abs_diff,
        "repeat_action_output_max_abs_diff": repeat_action_output_max_abs_diff,
        "first_frame_max_abs_diff": first_frame_max_abs_diff,
        "future_max_abs_diff": future_max_abs_diff,
        "future_mean_abs_diff": future_mean_abs_diff,
        "action_output_max_abs_diff": action_output_max_abs_diff,
        "effect_floor": effect_floor,
        "mean_effect_floor": mean_effect_floor,
        "isolation_tolerance": isolation_tolerance,
        "finite": finite,
        "future_conditioning_live": future_conditioning_live,
        "first_frame_isolated": first_frame_isolated,
        "action_expert_isolated": action_expert_isolated,
        "peak_allocated_gib": torch.cuda.max_memory_allocated(device) / 1024**3,
        "passed": passed,
    }
    atomic_no_clobber_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
