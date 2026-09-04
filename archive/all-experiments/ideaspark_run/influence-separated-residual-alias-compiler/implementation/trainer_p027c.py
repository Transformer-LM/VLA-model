import logging
import json
import hashlib
import inspect
import os
import re
from math import ceil
from pathlib import Path
import time

import numpy as np
import torch
from accelerate import Accelerator
from omegaconf import DictConfig
from PIL import Image
from torch.optim.lr_scheduler import ConstantLR, CosineAnnealingLR, LinearLR, SequentialLR
from torch.utils.data import DataLoader, default_collate

from .utils.fs import ensure_dir
from .utils.logging_config import get_logger, setup_logging
from .utils.pytorch_utils import set_global_seed
from .utils.samplers import ResumableEpochSampler
from .utils.video_io import save_mp4
from .utils.video_metrics import pil_frames_to_video_tensor, video_psnr, video_ssim

logger = get_logger(__name__)


class Wan22Trainer:
    def __init__(self, model, train_dataset, val_dataset=None, *, cfg: DictConfig):
        self.model = model
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.cfg = cfg
        self.output_dir = str(cfg.output_dir)
        self.learning_rate = float(cfg.learning_rate)
        self.weight_decay = float(cfg.weight_decay)
        self.batch_size = int(cfg.batch_size)
        self.num_workers = int(cfg.num_workers)
        self.num_epochs = int(cfg.num_epochs)
        max_steps = cfg.max_steps
        self.max_steps = int(max_steps) if max_steps is not None else None
        self.log_every = int(cfg.log_every)
        self.save_every = int(cfg.save_every)
        self.save_final = bool(cfg.get("save_final", True))
        self.save_trainable_final = bool(cfg.get("save_trainable_final", False))
        self.action_swap_eval_num_batches = int(cfg.get("action_swap_eval_num_batches", 0))
        self.action_swap_eval_at_start = bool(cfg.get("action_swap_eval_at_start", False))
        self.action_swap_eval_at_end = bool(cfg.get("action_swap_eval_at_end", False))
        self.action_swap_eval_index_stride = int(cfg.get("action_swap_eval_index_stride", 1))
        self.action_swap_eval_index_offset = int(cfg.get("action_swap_eval_index_offset", 0))
        self.eval_only = bool(cfg.get("eval_only", False))
        raw_eval_checkpoint = cfg.get("eval_only_trainable_checkpoint")
        self.eval_only_trainable_checkpoint = (
            str(raw_eval_checkpoint) if raw_eval_checkpoint not in (None, "", "null") else None
        )
        raw_expected_eval_step = cfg.get("expected_eval_checkpoint_step")
        self.expected_eval_checkpoint_step = (
            int(raw_expected_eval_step) if raw_expected_eval_step is not None else None
        )
        raw_expected_eval_sha256 = cfg.get("expected_eval_checkpoint_sha256")
        self.expected_eval_checkpoint_sha256 = (
            str(raw_expected_eval_sha256).strip().lower()
            if raw_expected_eval_sha256 not in (None, "", "null")
            else None
        )
        if self.action_swap_eval_num_batches < 0:
            raise ValueError("action_swap_eval_num_batches must be non-negative.")
        if self.action_swap_eval_index_stride <= 0:
            raise ValueError("action_swap_eval_index_stride must be positive.")
        self.require_finite_train_step = bool(cfg.get("require_finite_train_step", False))
        self.require_optimizer_step = bool(cfg.get("require_optimizer_step", False))
        self.require_positive_grad_norm = bool(cfg.get("require_positive_grad_norm", False))
        expected_world_size = cfg.get("expected_world_size")
        self.expected_world_size = int(expected_world_size) if expected_world_size is not None else None
        expected_distributed_type = cfg.get("expected_distributed_type")
        self.expected_distributed_type = (
            str(expected_distributed_type).strip().upper() if expected_distributed_type is not None else None
        )
        expected_zero_stage = cfg.get("expected_zero_stage")
        self.expected_zero_stage = int(expected_zero_stage) if expected_zero_stage is not None else None
        raw_trainable_prefixes = cfg.get("trainable_parameter_prefixes")
        self.trainable_parameter_prefixes = (
            tuple(str(item) for item in raw_trainable_prefixes)
            if raw_trainable_prefixes is not None
            else None
        )
        expected_trainable_numel = cfg.get("expected_trainable_numel")
        self.expected_trainable_numel = (
            int(expected_trainable_numel) if expected_trainable_numel is not None else None
        )
        raw_expected_trainable_names = cfg.get("expected_trainable_parameter_names")
        self.expected_trainable_parameter_names = (
            tuple(str(item) for item in raw_expected_trainable_names)
            if raw_expected_trainable_names is not None
            else None
        )
        self.eval_every = int(cfg.eval_every)
        self.eval_num_inference_steps = int(cfg.eval_num_inference_steps)
        self.gradient_accumulation_steps = int(cfg.gradient_accumulation_steps)
        self.max_grad_norm = float(cfg.max_grad_norm)
        self.seed = int(cfg.seed)
        
        self.resume = cfg.resume
        self.mixed_precision = str(cfg.mixed_precision).strip().lower()
        if self.mixed_precision not in {"no", "fp16", "bf16"}:
            raise ValueError(
                f"Unsupported mixed_precision: {cfg.mixed_precision}. "
                "Expected one of: ['no', 'fp16', 'bf16']."
            )
        self.wandb_enabled = bool(cfg.wandb.enabled)

        self.accelerator = Accelerator(
            gradient_accumulation_steps=self.gradient_accumulation_steps,
            mixed_precision=self.mixed_precision,
            step_scheduler_with_optimizer=False,
        )

        distributed_type = getattr(self.accelerator.distributed_type, "name", str(self.accelerator.distributed_type)).upper()
        deepspeed_plugin = self.accelerator.state.deepspeed_plugin
        zero_stage = None
        if deepspeed_plugin is not None:
            zero_stage = deepspeed_plugin.deepspeed_config.get("zero_optimization", {}).get("stage")
            if zero_stage is not None:
                zero_stage = int(zero_stage)
        if self.expected_world_size is not None and self.accelerator.num_processes != self.expected_world_size:
            raise RuntimeError(
                f"Expected world_size={self.expected_world_size}, got {self.accelerator.num_processes}."
            )
        if self.expected_distributed_type is not None and distributed_type != self.expected_distributed_type:
            raise RuntimeError(
                f"Expected distributed_type={self.expected_distributed_type}, got {distributed_type}."
            )
        if self.expected_zero_stage is not None and zero_stage != self.expected_zero_stage:
            raise RuntimeError(f"Expected DeepSpeed ZeRO stage={self.expected_zero_stage}, got {zero_stage}.")

        logger.info(
            "Accelerate training: distributed_type=%s zero_stage=%s world_size=%d process_index=%d cfg_mixed_precision=%s accelerator_mixed_precision=%s grad_accum=%d grad_clip=%.4f",
            distributed_type,
            zero_stage if zero_stage is not None else "unknown",
            self.accelerator.num_processes,
            self.accelerator.process_index,
            self.mixed_precision,
            self.accelerator.mixed_precision,
            self.gradient_accumulation_steps,
            self.max_grad_norm,
        )
        logger.info("using accelerator.device=%s", self.accelerator.device)
        worker_init_fn = set_global_seed(self.seed, get_worker_init_fn=True)
        self._assert_dataset_length_consistent(self.train_dataset, "train_dataset")
        if self.val_dataset is not None:
            self._assert_dataset_length_consistent(self.val_dataset, "val_dataset")

        # Freeze non-trainable modules before optimizer/deepspeed initialization.
        # The default preserves full-DiT training. P027-C can instead train
        # only the newly initialized 7D/8D action-conditioning interfaces.
        self._apply_configured_train_mode(self.model)
        trainable_named_params = [
            (name, parameter) for name, parameter in self.model.named_parameters() if parameter.requires_grad
        ]
        if not trainable_named_params:
            raise ValueError("No trainable parameters remain after applying trainable_parameter_prefixes.")
        trainable_params = [parameter for _, parameter in trainable_named_params]
        trainable_numel = sum(parameter.numel() for parameter in trainable_params)
        total_numel = sum(parameter.numel() for parameter in self.model.parameters())
        trainable_names = tuple(name for name, _ in trainable_named_params)
        if self.expected_trainable_numel is not None and trainable_numel != self.expected_trainable_numel:
            raise RuntimeError(
                f"Expected {self.expected_trainable_numel} trainable parameters, got {trainable_numel}."
            )
        if (
            self.expected_trainable_parameter_names is not None
            and set(trainable_names) != set(self.expected_trainable_parameter_names)
        ):
            raise RuntimeError(
                "Trainable parameter names differ from the locked E0 set: "
                f"expected={sorted(self.expected_trainable_parameter_names)} actual={sorted(trainable_names)}"
            )
        logger.info(
            "Trainable parameter audit: tensors=%d numel=%d total_numel=%d fraction=%.8f prefixes=%s names=%s",
            len(trainable_named_params),
            trainable_numel,
            total_numel,
            trainable_numel / max(total_numel, 1),
            self.trainable_parameter_prefixes,
            list(trainable_names),
        )
        self.optimizer = torch.optim.AdamW(
            trainable_params,
            lr=self.learning_rate,
            weight_decay=self.weight_decay,
            betas=(0.9, 0.95),
            # ZeRO-2 on 40 GB A100s has enough steady-state memory, but the
            # default foreach Adam update creates a multi-GB temporary tensor.
            # The scalar implementation avoids that transient allocation.
            foreach=False,
        )
        
        self.train_loader = self._build_loader(self.train_dataset, worker_init_fn=worker_init_fn)
        total_train_steps = self._estimate_total_train_steps()
        self.max_steps = total_train_steps
        warmup_steps = int(total_train_steps * 0.05)
        self.scheduler = self._build_scheduler(
            scheduler_type=cfg.lr_scheduler_type,
            total_train_steps=total_train_steps,
            warmup_steps=warmup_steps,
        )
        self.global_step = 0
        self.epoch = 0
        self.batch_in_epoch = 0

        self.checkpoint_root = os.path.join(self.output_dir, "checkpoints")
        self.weights_dir = os.path.join(self.checkpoint_root, "weights")
        self.state_dir = os.path.join(self.checkpoint_root, "state")
        self.eval_dir = os.path.join(self.output_dir, "eval")

        ensure_dir(self.output_dir)
        ensure_dir(self.checkpoint_root)
        ensure_dir(self.weights_dir)
        ensure_dir(self.state_dir)
        ensure_dir(self.eval_dir)

        if bool(getattr(self.model, "compile_training_denoise", False)):
            logger.info("Compiling training denoise forward/backward before DeepSpeed initialization.")
            compile_start = time.perf_counter()
            warmup_loader = DataLoader(
                self.train_dataset,
                batch_size=self.batch_size,
                shuffle=False,
                sampler=self.train_sampler,
                num_workers=0,
            )
            warmup_sample = next(iter(warmup_loader))
            with self.accelerator.autocast():
                warmup_loss, _ = self.model.training_loss(warmup_sample)
            warmup_loss.backward()
            self.optimizer.zero_grad(set_to_none=True)
            if torch.cuda.is_available():
                torch.cuda.synchronize(self.accelerator.device)
            logger.info(
                "Finished training denoise compile warmup in %.2f seconds.",
                time.perf_counter() - compile_start,
            )
            set_global_seed(self.seed)

        self.model, self.optimizer, self.train_loader, self.scheduler = self.accelerator.prepare(
            self.model, self.optimizer, self.train_loader, self.scheduler
        )
        self.optimizer.zero_grad(set_to_none=True)
        self.wandb_run = None
        self._init_wandb()
        self._resume_or_load_checkpoint()

        val_size = len(self.val_dataset) if self.val_dataset is not None else len(self.train_dataset)
        logger.info("Train/val dataset size: %d/%d", len(self.train_dataset), val_size)

    def _init_wandb(self):
        if not self.wandb_enabled or not self.accelerator.is_main_process:
            return
        try:
            import wandb
        except ImportError as e:
            raise ImportError(
                "wandb logging is enabled in config (`wandb.enabled=true`) but wandb is not installed."
            ) from e

        self.wandb_run = wandb.init(
            entity=self.cfg.wandb.workspace,
            project=self.cfg.wandb.project,
            name=self.cfg.wandb.name,
            group=None if self.cfg.wandb.group in (None, "null", "") else str(self.cfg.wandb.group),
            mode=self.cfg.wandb.mode,
            dir=self.output_dir,
        )
        logger.info(
            "Initialized wandb run: workspace=%s project=%s name=%s",
            self.cfg.wandb.workspace,
            self.cfg.wandb.project,
            self.cfg.wandb.name,
        )

    def _wandb_log(self, payload: dict):
        if self.wandb_run is None:
            return
        self.wandb_run.log(payload, step=self.global_step)

    def _finish_wandb(self):
        if self.wandb_run is None:
            return
        self.wandb_run.finish()
        self.wandb_run = None

    def _build_loader(self, dataset, worker_init_fn=None):
        self.train_sampler = ResumableEpochSampler(
            dataset=dataset,
            seed=self.seed,
            batch_size=self.batch_size,
            num_processes=self.accelerator.num_processes,
        )
        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=False,
            sampler=self.train_sampler,
            num_workers=self.num_workers,
            pin_memory=torch.cuda.is_available(),
            worker_init_fn=worker_init_fn,
        )

    def _assert_dataset_length_consistent(self, dataset, dataset_name: str):
        if not hasattr(dataset, "__len__"):
            raise TypeError(f"`{dataset_name}` must implement __len__ for rank consistency checks.")

        local_length = len(dataset)
        gathered_lengths = self.accelerator.gather(
            torch.tensor([local_length], device=self.accelerator.device, dtype=torch.int64)
        ).reshape(-1)
        if torch.all(gathered_lengths == gathered_lengths[0]):
            return

        if self.accelerator.is_main_process:
            print(f"[dataset-check] {dataset_name} length mismatch across ranks after initialization:")
            for rank, rank_length in enumerate(gathered_lengths.cpu().tolist()):
                print(f"rank {rank}: {rank_length}")
        self.accelerator.wait_for_everyone()
        raise RuntimeError(
            f"{dataset_name} length mismatch across ranks: {gathered_lengths.cpu().tolist()}"
        )

    def _estimate_total_train_steps(self) -> int:
        if self.max_steps is not None:
            return max(int(self.max_steps), 1)

        if not hasattr(self.train_dataset, "__len__"):
            raise TypeError("`train_dataset` must implement __len__ when `max_steps` is None.")

        num_processes = max(int(self.accelerator.num_processes), 1)
        global_batch_size = max(self.batch_size * num_processes, 1)
        micro_steps_per_epoch = max(ceil(len(self.train_dataset) / global_batch_size), 1)
        opt_steps_per_epoch = max(
            ceil(micro_steps_per_epoch / self.gradient_accumulation_steps),
            1,
        )
        return max(opt_steps_per_epoch * self.num_epochs, 1)

    def _build_scheduler(self, scheduler_type, total_train_steps: int, warmup_steps: int = 0):
        scheduler_type = str(scheduler_type).strip().lower()
        total_train_steps = max(int(total_train_steps), 1)
        warmup_steps = min(max(int(warmup_steps), 0), total_train_steps - 1)

        remaining_steps = max(total_train_steps - warmup_steps, 1)
        if scheduler_type == "cosine":
            main_scheduler = CosineAnnealingLR(
                self.optimizer,
                T_max=remaining_steps,
                eta_min=self.learning_rate * 0.01,
            )
        elif scheduler_type == "constant":
            main_scheduler = ConstantLR(self.optimizer, factor=1.0, total_iters=remaining_steps)
        else:
            raise ValueError(
                f"Unsupported lr_scheduler_type: {scheduler_type}. "
                "Expected one of: ['cosine', 'constant']."
            )

        if warmup_steps <= 0:
            return main_scheduler

        warmup_scheduler = LinearLR(
            self.optimizer,
            start_factor=1.0 / warmup_steps,
            end_factor=1.0,
            total_iters=warmup_steps,
        )
        return SequentialLR(
            self.optimizer,
            schedulers=[warmup_scheduler, main_scheduler],
            milestones=[warmup_steps],
        )
    
    def _estimate_eta(self):
        elapsed = max(time.perf_counter() - self.run_start_time, 1e-6)
        done_steps = max(self.global_step - self.run_start_step, 1)
        steps_per_sec = done_steps / elapsed
        remaining_steps = max(self.max_steps - self.global_step, 0)
        eta_seconds = int(remaining_steps / max(steps_per_sec, 1e-9))
        eta_h, eta_rem = divmod(eta_seconds, 3600)
        eta_m, eta_s = divmod(eta_rem, 60)
        return f"{eta_h:02d}:{eta_m:02d}:{eta_s:02d}", steps_per_sec

    def _resume_or_load_checkpoint(self):
        resume = self.resume
        if not resume:
            return
        resume_path = Path(str(resume))
        if resume_path.is_dir():
            logger.info("Resuming full training state from directory: %s", resume)
            self.load_training_state(str(resume_path))
            return
        if not resume_path.exists():
            raise FileNotFoundError(f"Resume checkpoint not found: {resume}")
        logger.info("Loading weight checkpoint only: %s", resume)
        self.accelerator.unwrap_model(self.model).load_checkpoint(str(resume_path), optimizer=None)
        logger.warning("Loaded .pt weights only; optimizer/scheduler/step were not restored under ZeRO2.")

    def _set_dit_only_train_mode(self):
        logger.info("Applying configured trainable parameter policy.")
        model = self.accelerator.unwrap_model(self.model)
        self._apply_configured_train_mode(model)

    def _apply_configured_train_mode(self, model):
        model.eval()
        model.requires_grad_(False)
        model.dit.train()
        proprio_encoder = getattr(model, "proprio_encoder", None)
        if self.trainable_parameter_prefixes is None:
            model.dit.requires_grad_(True)
            if proprio_encoder is not None:
                proprio_encoder.train()
                proprio_encoder.requires_grad_(True)
            return

        if not self.trainable_parameter_prefixes:
            raise ValueError("trainable_parameter_prefixes cannot be empty; omit it for full-DiT training.")
        matched_by_prefix = {prefix: [] for prefix in self.trainable_parameter_prefixes}
        for name, parameter in model.named_parameters():
            for prefix in self.trainable_parameter_prefixes:
                if name.startswith(prefix):
                    parameter.requires_grad_(True)
                    matched_by_prefix[prefix].append(name)
                    break
        unmatched = [prefix for prefix, names in matched_by_prefix.items() if not names]
        if unmatched:
            raise ValueError(f"Trainable parameter prefixes matched no parameters: {unmatched}")
        if proprio_encoder is not None and any(
            name.startswith("proprio_encoder.")
            for names in matched_by_prefix.values()
            for name in names
        ):
            proprio_encoder.train()

    @staticmethod
    def _to_batched_eval_sample(sample):
        video = sample["video"]
        prompt = sample["prompt"]
        action = sample.get("action", None)
        proprio = sample.get("proprio", None)
        context = sample.get("context", None)
        context_mask = sample.get("context_mask", None)

        if not isinstance(video, torch.Tensor):
            raise TypeError(
                f"Expected tensor video for evaluation, got {type(video)}. "
                "Evaluation now expects `video` with shape [3,T,H,W] or [B,3,T,H,W]."
            )
        if video.ndim == 4:
            video = video.unsqueeze(0)
        if video.ndim != 5:
            raise ValueError(f"Expected video shape [3,T,H,W] or [B,3,T,H,W], got {tuple(video.shape)}")
        num_video_frames = video.shape[2]
        if num_video_frames <= 1:
            raise ValueError(f"`sample['video']` must have at least 2 frames for action evaluation, got {num_video_frames}")

        if isinstance(prompt, str):
            prompt = [prompt]
        elif isinstance(prompt, tuple):
            prompt = list(prompt)
        elif not isinstance(prompt, list):
            raise TypeError(f"Expected prompt type str/list[str], got {type(prompt)}")
        if len(prompt) != video.shape[0]:
            raise ValueError(f"Prompt batch mismatch: len(prompt)={len(prompt)} vs video batch={video.shape[0]}")
        
        action_horizon = None
        action = None
        if "action" in sample:
            action = sample["action"]
            if not isinstance(action, torch.Tensor):
                raise TypeError(
                    f"`sample['action']` must be a torch.Tensor, got {type(action)}"
                )
            if action.ndim == 2:
                action = action.unsqueeze(0)
            if action.ndim != 3:
                raise ValueError(f"`sample['action']` must be 3D [B, T, a_dim], got shape {tuple(action.shape)}")
            if action.shape[1] % (num_video_frames - 1) != 0:
                raise ValueError(f"`sample['action']` temporal dimension must be divisible by video frames-1={num_video_frames - 1}, got {action.shape[1]}")
            action_horizon = int(action.shape[1])

        proprio = None
        if "proprio" in sample:
            proprio = sample["proprio"]
            if not isinstance(proprio, torch.Tensor):
                raise TypeError(f"`sample['proprio']` must be a torch.Tensor, got {type(proprio)}")
            if proprio.ndim == 2:
                proprio = proprio.unsqueeze(0)
            if proprio.ndim != 3:
                raise ValueError(f"`sample['proprio']` must be 3D [B, T, d], got shape {tuple(proprio.shape)}")

        if context is not None or context_mask is not None:
            if context is None or context_mask is None:
                raise ValueError("`context` and `context_mask` must both exist in eval sample.")
            if context.ndim == 2:
                context = context.unsqueeze(0)
            if context_mask.ndim == 1:
                context_mask = context_mask.unsqueeze(0)
            if context.ndim != 3 or context_mask.ndim != 2:
                raise ValueError(
                    f"`context/context_mask` must be [B,L,D]/[B,L], got {tuple(context.shape)} and {tuple(context_mask.shape)}"
                )

        return {
            "video": video,
            "prompt": prompt,
            "action": action,
            "proprio": proprio,
            "context": context,
            "context_mask": context_mask,
            "action_horizon": action_horizon,
        }

    @torch.no_grad()
    def evaluate(self):
        if self.val_dataset is None:
            return None

        model = self.accelerator.unwrap_model(self.model)
        was_dit_training = model.dit.training
        model.eval()

        # eval_index = (self.global_step + self.accelerator.process_index) % len(self.val_dataset)
        rng = torch.Generator(device="cpu").manual_seed(self.global_step + self.accelerator.process_index)
        eval_index = torch.randint(0, len(self.val_dataset), (1,), generator=rng).item()
        sample = self._to_batched_eval_sample(self.val_dataset[eval_index])

        # 1. training loss
        with self.accelerator.autocast():
            val_loss, _ = model.training_loss(sample)
            val_loss = val_loss.float().item()
        
        prompt = sample["prompt"][0]
        video0 = sample["video"][0] # Tensor [3, T, H, W] in (-1, 1)
        action = sample["action"][0] if "action" in sample and sample["action"] is not None else None
        proprio = sample["proprio"][0, 0] if "proprio" in sample and sample["proprio"] is not None else None # from [1, T, d] to [d]
        input_image = video0[:, 0].unsqueeze(0)
        _, num_frames, _, _ = video0.shape

        # 2. inference and video saving
        infer_kwargs = {
            "input_image": input_image,
            "num_frames": num_frames,
            "action": action,
            "action_horizon": sample['action_horizon'],
            "proprio": proprio,
            "text_cfg_scale": 1.0,
            "action_cfg_scale": 1.0,
            "num_inference_steps": self.eval_num_inference_steps,
            "seed": 42,
            "tiled": False,
        }
        if sample["context"] is not None:
            infer_kwargs["prompt"] = None
            infer_kwargs["context"] = sample["context"][0]
            infer_kwargs["context_mask"] = sample["context_mask"][0]
        else:
            infer_kwargs["prompt"] = prompt

        pred = model.infer(
            **infer_kwargs,
        )
        
        pred_video = pred["video"]
        pred_action = pred.get("action", None)

        # 3. inference metrics against GT video
        pred_video_tensor = pil_frames_to_video_tensor(pred_video)
        gt_video_tensor = ((video0.detach().float().cpu().clamp(-1.0, 1.0) + 1.0) * 0.5).contiguous()

        assert pred_video_tensor.shape == gt_video_tensor.shape, (
            "Eval infer prediction/GT shape mismatch: "
            f"pred={tuple(pred_video_tensor.shape)} vs gt={tuple(gt_video_tensor.shape)}"
        )

        psnr_rollout_vs_gt = video_psnr(pred=pred_video_tensor, target=gt_video_tensor)
        ssim_rollout_vs_gt = video_ssim(pred=pred_video_tensor, target=gt_video_tensor)

        action_l1 = None
        action_l2 = None
        if action is not None and pred_action is not None:
            if sample["proprio"] is None:
                raise ValueError("Eval sample must contain `proprio` for action denormalization.")
            proprio = sample["proprio"].detach().to(device="cpu", dtype=torch.float32)
            
            processor = self.val_dataset.lerobot_dataset.processor

            denorm_actions = {}
            action_meta = processor.shape_meta["action"]
            state_meta = processor.shape_meta["state"]
            for action_name, raw_action in (("pred", pred_action), ("gt", action)):
                if not isinstance(raw_action, torch.Tensor):
                    raise TypeError(f"{action_name} action must be a torch.Tensor, got {type(raw_action)}")
                if raw_action.ndim == 2:
                    action_btd = raw_action.unsqueeze(0)
                elif raw_action.ndim == 3 and raw_action.shape[0] == 1:
                    action_btd = raw_action
                else:
                    raise ValueError(
                        f"{action_name} action must have shape [T, D] or [1, T, D], got {tuple(raw_action.shape)}"
                    )
                action_btd = action_btd.detach().to(device="cpu", dtype=torch.float32)

                batch = {
                    "action": action_btd,
                    "state": proprio,
                }
                batch = processor.action_state_merger.backward(batch)
                batch = processor.normalizer.backward(batch)
                merged_batch = {
                    "action": {meta["key"]: batch["action"][meta["key"]].squeeze(0) for meta in action_meta},
                    "state": {meta["key"]: batch["state"][meta["key"]].squeeze(0) for meta in state_meta},
                }
                merged_batch = processor.action_state_merger.forward(merged_batch)
                denorm_action = merged_batch["action"].unsqueeze(0)
                if denorm_action.ndim != 3 or denorm_action.shape[0] != 1:
                    raise ValueError(
                        f"Denormalized {action_name} action must have shape [1, T, D], got {tuple(denorm_action.shape)}"
                    )
                denorm_actions[action_name] = denorm_action

            pred_action_denorm = denorm_actions["pred"]
            gt_action_denorm = denorm_actions["gt"]

            if pred_action_denorm.shape != gt_action_denorm.shape:
                raise ValueError(
                    "Predicted action/GT action shape mismatch after denormalization: "
                    f"pred={tuple(pred_action_denorm.shape)} vs gt={tuple(gt_action_denorm.shape)}"
                )
            action_diff = pred_action_denorm - gt_action_denorm
            action_l1 = action_diff.abs().mean().item()
            action_l2 = action_diff.pow(2).mean().item()

        # 4. VAE reconstruction metrics against GT video
        gt_video_batch = video0.unsqueeze(0).to(device=model.device, dtype=model.torch_dtype)
        vae_latents = model._encode_video_latents(gt_video_batch, tiled=False)
        vae_recon_video = model._decode_latents(vae_latents, tiled=False)
        vae_video_tensor = pil_frames_to_video_tensor(vae_recon_video)

        assert vae_video_tensor.shape == gt_video_tensor.shape, (
            "Eval VAE reconstruction/GT shape mismatch: "
            f"vae={tuple(vae_video_tensor.shape)} vs gt={tuple(gt_video_tensor.shape)}"
        )

        psnr_decode_vs_gt = video_psnr(pred=vae_video_tensor, target=gt_video_tensor)
        ssim_decode_vs_gt = video_ssim(pred=vae_video_tensor, target=gt_video_tensor)

        psnr_rollout_vs_decode = video_psnr(pred=pred_video_tensor, target=vae_video_tensor)
        ssim_rollout_vs_decode = video_ssim(pred=pred_video_tensor, target=vae_video_tensor)

        stitched_video_tensor = torch.cat(
            [pred_video_tensor, vae_video_tensor, gt_video_tensor],
            dim=2,
        ).contiguous()
        stitched_frames = []
        for t in range(stitched_video_tensor.shape[1]):
            frame = (stitched_video_tensor[:, t].permute(1, 2, 0).clamp(0.0, 1.0).numpy() * 255.0).astype(np.uint8)
            stitched_frames.append(Image.fromarray(frame))

        video_path = os.path.join(
            self.eval_dir,
            f"step_{self.global_step:06d}_rank_{self.accelerator.process_index:03d}.mp4",
        )
        save_mp4(stitched_frames, video_path, fps=8)

        local_metrics = torch.tensor(
            [
                float(val_loss),
                float(psnr_rollout_vs_gt),
                float(ssim_rollout_vs_gt),
                float(psnr_rollout_vs_decode),
                float(ssim_rollout_vs_decode),
                float(psnr_decode_vs_gt),
                float(ssim_decode_vs_gt),
                float(action_l2) if action_l2 is not None else -1.0,
                float(action_l1) if action_l1 is not None else -1.0,
            ],
            device=self.accelerator.device,
            dtype=torch.float32,
        ).unsqueeze(0)
        gathered_metrics = self.accelerator.gather_for_metrics(local_metrics)
        mean_metrics = gathered_metrics[:, :7].mean(dim=0)
        action_l2_mean = gathered_metrics[:, 7].mean().item() if action_l2 is not None else None
        action_l1_mean = gathered_metrics[:, 8].mean().item() if action_l1 is not None else None

        if was_dit_training:
            self._set_dit_only_train_mode()

        result = {
            "val_loss": float(mean_metrics[0].item()),
            "psnr_rg": float(mean_metrics[1].item()),
            "ssim_rg": float(mean_metrics[2].item()),
            "psnr_rd": float(mean_metrics[3].item()),
            "ssim_rd": float(mean_metrics[4].item()),
            "psnr_dg": float(mean_metrics[5].item()),
            "ssim_dg": float(mean_metrics[6].item()),
            "video_path": video_path,
        }
        if action_l2_mean is not None:
            result["action_l2"] = float(action_l2_mean)
        if action_l1_mean is not None:
            result["action_l1"] = float(action_l1_mean)
        return result

    def _save_weights_checkpoint(self, step_tag: str):
        model = self.accelerator.unwrap_model(self.model)
        ckpt_path = os.path.join(self.weights_dir, f"{step_tag}.pt")
        model.save_checkpoint(ckpt_path, optimizer=None, step=self.global_step)
        return ckpt_path

    def _save_trainable_checkpoint(self, step_tag: str):
        """Save only the explicitly trainable interface tensors.

        P027-C freezes the 6B backbone.  Serializing the full model and
        DeepSpeed state would turn a small learnability pilot into a roughly
        100 GB write, so the pilot stores the exact locked interface state.
        The default training/checkpoint behavior is unchanged unless
        ``save_trainable_final`` is enabled.
        """
        model = self.accelerator.unwrap_model(self.model)
        state = {
            name: parameter.detach().cpu().clone()
            for name, parameter in model.named_parameters()
            if parameter.requires_grad
        }
        if not state:
            raise RuntimeError("Refusing to save an empty trainable-only checkpoint.")
        if (
            self.expected_trainable_parameter_names is not None
            and set(state) != set(self.expected_trainable_parameter_names)
        ):
            raise RuntimeError(
                "Trainable-only checkpoint names differ from the locked set: "
                f"expected={sorted(self.expected_trainable_parameter_names)} actual={sorted(state)}"
            )
        payload = {
            "format": "fastwam_trainable_only_v1",
            "global_step": int(self.global_step),
            "trainable_numel": int(sum(tensor.numel() for tensor in state.values())),
            "state_dict": state,
        }
        ckpt_path = os.path.join(self.weights_dir, f"{step_tag}_trainable_only.pt")
        torch.save(payload, ckpt_path)
        return ckpt_path

    def _load_trainable_checkpoint(self, checkpoint_path: str):
        checkpoint_file = Path(checkpoint_path).resolve()
        if not checkpoint_file.is_file():
            raise FileNotFoundError(f"Trainable-only checkpoint not found: {checkpoint_file}")
        digest = hashlib.sha256()
        with open(checkpoint_file, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        checkpoint_sha256 = digest.hexdigest()
        if (
            self.expected_eval_checkpoint_sha256 is not None
            and checkpoint_sha256 != self.expected_eval_checkpoint_sha256
        ):
            raise RuntimeError(
                "Trainable-only checkpoint SHA256 mismatch: "
                f"expected={self.expected_eval_checkpoint_sha256} actual={checkpoint_sha256}"
            )
        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
        if checkpoint.get("format") != "fastwam_trainable_only_v1":
            raise RuntimeError(
                f"Unsupported trainable-only checkpoint format in {checkpoint_path}: "
                f"{checkpoint.get('format')}"
            )
        state = checkpoint.get("state_dict")
        if not isinstance(state, dict) or not state:
            raise RuntimeError(f"Trainable-only checkpoint has no state_dict: {checkpoint_path}")
        if (
            self.expected_trainable_parameter_names is not None
            and set(state) != set(self.expected_trainable_parameter_names)
        ):
            raise RuntimeError(
                "Trainable-only checkpoint names differ from the locked set: "
                f"expected={sorted(self.expected_trainable_parameter_names)} actual={sorted(state)}"
            )
        checkpoint_numel = sum(tensor.numel() for tensor in state.values())
        checkpoint_step = int(checkpoint.get("global_step", -1))
        if (
            self.expected_eval_checkpoint_step is not None
            and checkpoint_step != self.expected_eval_checkpoint_step
        ):
            raise RuntimeError(
                "Trainable-only checkpoint step mismatch: "
                f"expected={self.expected_eval_checkpoint_step} actual={checkpoint_step}"
            )
        if self.expected_trainable_numel is not None and checkpoint_numel != self.expected_trainable_numel:
            raise RuntimeError(
                f"Trainable-only checkpoint numel mismatch: expected={self.expected_trainable_numel} "
                f"actual={checkpoint_numel}"
            )

        model = self.accelerator.unwrap_model(self.model)
        named_parameters = dict(model.named_parameters())
        with torch.no_grad():
            for name, source in state.items():
                if name not in named_parameters:
                    raise RuntimeError(f"Checkpoint parameter is absent from model: {name}")
                target = named_parameters[name]
                if tuple(source.shape) != tuple(target.shape):
                    raise RuntimeError(
                        f"Checkpoint shape mismatch for {name}: source={tuple(source.shape)} "
                        f"target={tuple(target.shape)}"
                    )
                target.copy_(source.to(device=target.device, dtype=target.dtype))
        self.accelerator.wait_for_everyone()
        logger.info(
            "Loaded trainable-only checkpoint: path=%s sha256=%s step=%d tensors=%d numel=%d",
            checkpoint_file,
            checkpoint_sha256,
            checkpoint_step,
            len(state),
            checkpoint_numel,
        )
        return {
            "kind": "trainable_only_checkpoint",
            "path": str(checkpoint_file),
            "sha256": checkpoint_sha256,
            "format": checkpoint.get("format"),
            "global_step": checkpoint_step,
            "trainable_numel": int(checkpoint_numel),
        }

    @torch.no_grad()
    def evaluate_action_swap(self, tag: str, source: dict | None = None):
        """Measure whether future-video loss prefers its factual action.

        Each rank evaluates a distinct held-out episode window.  The negative
        action comes from the next rank, while video, language, proprioception,
        padding masks, diffusion timestep, and diffusion noise are held fixed.
        Positive ``margin = swapped_video_loss - matched_video_loss`` therefore
        means the WAM assigns the factual action a better future prediction.
        """
        if self.val_dataset is None:
            raise RuntimeError("Action-swap evaluation requires a validation dataset.")
        if self.accelerator.num_processes < 2:
            raise RuntimeError("Action-swap evaluation requires at least two distributed ranks.")
        if self.action_swap_eval_num_batches <= 0:
            raise RuntimeError("action_swap_eval_num_batches must be positive when swap evaluation is enabled.")

        model = self.accelerator.unwrap_model(self.model)
        was_dit_training = model.dit.training
        model.eval()
        cpu_rng_state = torch.get_rng_state()
        cuda_rng_state = None
        if torch.cuda.is_available():
            cuda_rng_state = torch.cuda.get_rng_state(self.accelerator.device)

        local_rows = []
        try:
            for batch_index in range(self.action_swap_eval_num_batches):
                eval_index = (
                    self.action_swap_eval_index_offset
                    + (
                        batch_index * self.accelerator.num_processes
                        + self.accelerator.process_index
                    )
                    * self.action_swap_eval_index_stride
                ) % len(self.val_dataset)
                sample = default_collate([self.val_dataset[eval_index]])
                factual_action = sample["action"].to(
                    device=self.accelerator.device,
                    dtype=torch.float32,
                    non_blocking=True,
                )
                gathered_actions = self.accelerator.gather(factual_action)
                negative_rank = (self.accelerator.process_index + 1) % self.accelerator.num_processes
                swapped_action = gathered_actions[negative_rank : negative_rank + 1].clone()
                action_mse = (factual_action - swapped_action).float().pow(2).mean()
                if not bool(torch.isfinite(action_mse).item()) or float(action_mse.item()) <= 0.0:
                    raise RuntimeError(
                        f"Invalid action-swap negative at eval_index={eval_index}: action_mse={action_mse.item()}"
                    )

                factual_sample = dict(sample)
                swapped_sample = dict(sample)
                factual_sample["action"] = factual_action
                swapped_sample["action"] = swapped_action
                pair_seed = self.seed + 100_000 + eval_index

                torch.manual_seed(pair_seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed_all(pair_seed)
                with self.accelerator.autocast():
                    _, factual_losses = model.training_loss(factual_sample)

                torch.manual_seed(pair_seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed_all(pair_seed)
                with self.accelerator.autocast():
                    _, swapped_losses = model.training_loss(swapped_sample)

                factual_video = float(factual_losses["loss_video"])
                swapped_video = float(swapped_losses["loss_video"])
                if not np.isfinite(factual_video) or not np.isfinite(swapped_video):
                    raise FloatingPointError(
                        "Non-finite action-swap video loss: "
                        f"factual={factual_video} swapped={swapped_video}"
                    )
                local_rows.append(
                    [
                        float(eval_index),
                        factual_video,
                        swapped_video,
                        swapped_video - factual_video,
                        float(action_mse.item()),
                    ]
                )
        finally:
            torch.set_rng_state(cpu_rng_state)
            if cuda_rng_state is not None:
                torch.cuda.set_rng_state(cuda_rng_state, self.accelerator.device)
            if was_dit_training:
                self._set_dit_only_train_mode()

        rows = torch.tensor(local_rows, device=self.accelerator.device, dtype=torch.float64)
        gathered_rows = self.accelerator.gather_for_metrics(rows).detach().cpu()
        margins = gathered_rows[:, 3]
        result = {
            "tag": str(tag),
            "global_step": int(source.get("global_step", self.global_step)) if source else int(self.global_step),
            "trainer_global_step": int(self.global_step),
            "source": source,
            "num_examples": int(gathered_rows.shape[0]),
            "factual_video_loss_mean": float(gathered_rows[:, 1].mean().item()),
            "swapped_video_loss_mean": float(gathered_rows[:, 2].mean().item()),
            "margin_mean": float(margins.mean().item()),
            "margin_std": float(margins.std(unbiased=True).item()) if margins.numel() > 1 else 0.0,
            "positive_margin_rate": float((margins > 0).to(torch.float64).mean().item()),
            "action_mse_mean": float(gathered_rows[:, 4].mean().item()),
            "rows": [
                {
                    "eval_index": int(row[0].item()),
                    "factual_video_loss": float(row[1].item()),
                    "swapped_video_loss": float(row[2].item()),
                    "margin": float(row[3].item()),
                    "action_mse": float(row[4].item()),
                }
                for row in gathered_rows
            ],
        }
        if self.accelerator.is_main_process:
            output_path = os.path.join(self.eval_dir, f"action_swap_{tag}.json")
            with open(output_path, "w", encoding="utf-8") as handle:
                json.dump(result, handle, ensure_ascii=True, indent=2)
            logger.info(
                "[action-swap] tag=%s step=%d n=%d factual=%.6f swapped=%.6f "
                "margin=%.6f positive_rate=%.4f action_mse=%.6f path=%s",
                tag,
                self.global_step,
                result["num_examples"],
                result["factual_video_loss_mean"],
                result["swapped_video_loss_mean"],
                result["margin_mean"],
                result["positive_margin_rate"],
                result["action_mse_mean"],
                output_path,
            )
        self.accelerator.wait_for_everyone()
        return result if self.accelerator.is_main_process else None

    def _save_trainer_state(self, state_path: str):
        state_file = os.path.join(state_path, "trainer_state.json")
        payload = {
            "global_step": int(self.global_step),
            "epoch": int(self.epoch),
            "batch_in_epoch": int(self.batch_in_epoch),
        }
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=True, indent=2)

    def save_checkpoint(self):
        step_tag = f"step_{self.global_step:06d}"

        self.accelerator.wait_for_everyone()
        ckpt_path = None
        if self.accelerator.is_main_process:
            ckpt_path = self._save_weights_checkpoint(step_tag=step_tag)
        self.accelerator.wait_for_everyone()

        state_path = os.path.join(self.state_dir, step_tag)
        ensure_dir(state_path)
        self.accelerator.save_state(output_dir=state_path)
        if self.accelerator.is_main_process:
            self._save_trainer_state(state_path)
        self.accelerator.wait_for_everyone()

        return {"weights_path": ckpt_path, "state_path": state_path}

    def load_training_state(self, state_dir: str):
        self.accelerator.load_state(input_dir=state_dir)
        state_file = Path(state_dir) / "trainer_state.json"
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
            self.global_step = int(payload["global_step"])

            if "epoch" in payload and "batch_in_epoch" in payload:
                self.epoch = int(payload["epoch"])
                self.batch_in_epoch = int(payload["batch_in_epoch"])
                self.train_sampler.set_epoch_offset(self.epoch)
                self.train_sampler.set_resume_batch_offset(self.batch_in_epoch)
                logger.info(
                    "Restored dataloader progress: epoch=%d batch_in_epoch=%d sample_offset=%d",
                    self.epoch,
                    self.batch_in_epoch,
                    self.batch_in_epoch * self.batch_size * self.accelerator.num_processes,
                )
            else:
                self.epoch = 0
                self.batch_in_epoch = 0
                self.train_sampler.clear_resume_batch_offset()
                logger.warning(
                    "State file does not contain `epoch`/`batch_in_epoch`; "
                    "optimizer/scheduler were restored, but dataloader progress resume is skipped."
                )
            self.accelerator.wait_for_everyone()
            return

        match = re.search(r"step[_-](\d+)$", str(state_dir).rstrip("/"))
        if match:
            self.global_step = int(match.group(1))
        else:
            self.global_step = 0
        self.epoch = 0
        self.batch_in_epoch = 0
        self.train_sampler.clear_resume_batch_offset()
        self.accelerator.wait_for_everyone()
        logger.info("Loaded accelerate training state from %s at step=%d", state_dir, self.global_step)
        logger.warning(
            "State file `%s` is missing; dataloader progress resume is skipped.",
            state_file,
        )

    def train(self):
        self._set_dit_only_train_mode()

        unwrapped_model = self.accelerator.unwrap_model(self.model)

        if self.max_steps is None:
            raise ValueError("`max_steps` must be set before entering the while-step training loop.")

        if self.eval_only:
            if self.action_swap_eval_num_batches <= 0:
                raise RuntimeError("eval_only requires action_swap_eval_num_batches > 0.")
            self.evaluate_action_swap(
                tag="base",
                source={
                    "kind": "random_interface_initialization",
                    "seed": int(self.seed),
                    "global_step": 0,
                },
            )
            if self.eval_only_trainable_checkpoint is not None:
                checkpoint_source = self._load_trainable_checkpoint(self.eval_only_trainable_checkpoint)
                self.evaluate_action_swap(tag="checkpoint", source=checkpoint_source)
            if self.accelerator.is_main_process:
                logger.info("[done] eval_only=true; no optimizer step or checkpoint write was performed.")
            return

        if self.action_swap_eval_at_start:
            self.evaluate_action_swap(tag="start")
        logger.info("Starting training with max_steps=%d.", self.max_steps)
        data_iter = iter(self.train_loader)
        self.run_start_step = self.global_step
        self.run_start_time = time.perf_counter()

        while self.global_step < self.max_steps:
            try:
                sample = next(data_iter)
                self.batch_in_epoch += 1
            except StopIteration:
                self.epoch += 1
                self.batch_in_epoch = 0
                self.train_sampler.clear_resume_batch_offset()
                data_iter = iter(self.train_loader)
                continue

            with self.accelerator.accumulate(self.model):
                train_model = self.model if hasattr(self.model, "training_loss") else self.accelerator.unwrap_model(self.model)

                with self.accelerator.autocast():
                    loss, loss_dict = train_model.training_loss(sample)
                if self.require_finite_train_step:
                    local_loss_finite = torch.isfinite(loss.detach().float()).all()
                    for value in loss_dict.values():
                        if torch.is_tensor(value):
                            component = value.detach().to(device=loss.device, dtype=torch.float32)
                        else:
                            component = torch.as_tensor(value, device=loss.device, dtype=torch.float32)
                        local_loss_finite = local_loss_finite & torch.isfinite(component).all()
                    loss_finite_by_rank = self.accelerator.gather(
                        local_loss_finite.to(dtype=torch.int32).reshape(1)
                    )
                    if not bool((loss_finite_by_rank == 1).all().item()):
                        self.optimizer.zero_grad(set_to_none=True)
                        raise FloatingPointError(
                            "Non-finite total/component training loss detected on at least one rank."
                        )
                self.accelerator.backward(loss)

                if self.accelerator.sync_gradients:
                    grad_norm = self.accelerator.clip_grad_norm_(self.model.parameters(), self.max_grad_norm)
                    grad_norm_tensor = torch.as_tensor(grad_norm, device=loss.device, dtype=torch.float32).reshape(1)
                    grad_norm_by_rank = self.accelerator.gather(grad_norm_tensor)
                    if self.require_finite_train_step and not bool(torch.isfinite(grad_norm_by_rank).all().item()):
                        self.optimizer.zero_grad(set_to_none=True)
                        raise FloatingPointError("Non-finite gradient norm detected on at least one rank.")
                    if self.require_positive_grad_norm and not bool((grad_norm_by_rank > 0).all().item()):
                        self.optimizer.zero_grad(set_to_none=True)
                        raise RuntimeError("Non-positive gradient norm detected on at least one rank.")
                    self.optimizer.step()
                    step_skipped = torch.tensor(
                        [int(bool(self.accelerator.optimizer_step_was_skipped))],
                        device=loss.device,
                        dtype=torch.int32,
                    )
                    step_skipped_by_rank = self.accelerator.gather(step_skipped)
                    any_step_skipped = bool((step_skipped_by_rank != 0).any().item())
                    if not any_step_skipped:
                        self.scheduler.step()
                    self.optimizer.zero_grad(set_to_none=True)
                    if self.require_optimizer_step and any_step_skipped:
                        raise RuntimeError("Optimizer step was skipped on at least one rank.")
                    self.global_step += 1
                    global_loss = float(
                        self.accelerator.gather(loss.detach().float().reshape(1)).mean().item()
                    )
                    global_loss_metrics = {}
                    for key, value in loss_dict.items():
                        metric_tensor = torch.tensor(float(value), device=loss.device, dtype=torch.float32).reshape(1)
                        global_loss_metrics[key] = float(
                            self.accelerator.gather(metric_tensor).mean().item()
                        )
                    global_grad_norm = float(grad_norm_by_rank.mean().item())

                    current_lr = float(self.optimizer.param_groups[0]["lr"])

                    if self.log_every > 0 and self.global_step % self.log_every == 0 and self.accelerator.is_main_process:
                        eta_str, steps_per_sec = self._estimate_eta()
                        description = "[train] epoch=%d step=%d/%d loss=%.4f " % (
                            self.epoch,
                            self.global_step,
                            self.max_steps,
                            global_loss,
                        )
                        if global_loss_metrics:
                            detail_str = " ".join([f"{k}={v:.4f}" for k, v in sorted(global_loss_metrics.items())])
                            description += detail_str + " "
                        description += "lr=%.2e speed=%.2f step/s, %.2f samples/s eta=%s" % (
                            current_lr,
                            steps_per_sec,
                            steps_per_sec * self.batch_size * self.accelerator.num_processes,
                            eta_str,
                        )
                        logger.info(description)

                        wandb_payload = {
                            "train/loss": global_loss,
                            "train/grad_norm": global_grad_norm,
                            "train/lr": current_lr,
                            "performance/steps_per_sec": steps_per_sec,
                            "performance/samples_per_sec": steps_per_sec * self.batch_size * self.accelerator.num_processes,
                        }
                        for key, value in global_loss_metrics.items():
                            wandb_payload[f"train/{key}"] = value
                        self._wandb_log(wandb_payload)

                    if (
                        self.eval_every > 0
                        and self.val_dataset is not None
                        and self.global_step % self.eval_every == 0
                    ):
                        metrics = self.evaluate()
                        self.accelerator.wait_for_everyone()
                        if metrics is not None and self.accelerator.is_main_process:
                            description = "[eval] step=%d val_loss=%.4f infer_psnr=%.4f infer_ssim=%.4f" % (
                                self.global_step,
                                metrics["val_loss"],
                                metrics["psnr_rd"],
                                metrics["ssim_rd"],
                            )
                            if "action_l2" in metrics:
                                description += " action_l2=%.4f" % metrics["action_l2"]
                            if "action_l1" in metrics:
                                description += " action_l1=%.4f" % metrics["action_l1"]
                            logger.info(description)
                            eval_payload = {
                                "eval/val_loss": float(metrics["val_loss"]),
                                "eval/psnr_rg": float(metrics["psnr_rg"]),
                                "eval/ssim_rg": float(metrics["ssim_rg"]),
                                "eval/psnr_rd": float(metrics["psnr_rd"]),
                                "eval/ssim_rd": float(metrics["ssim_rd"]),
                                "eval/psnr_dg": float(metrics["psnr_dg"]),
                                "eval/ssim_dg": float(metrics["ssim_dg"]),
                            }
                            if "action_l2" in metrics:
                                eval_payload["eval/action_l2"] = float(metrics["action_l2"])
                            if "action_l1" in metrics:
                                eval_payload["eval/action_l1"] = float(metrics["action_l1"])
                            self._wandb_log(eval_payload)

                    if self.save_every > 0 and self.global_step % self.save_every == 0:
                        ckpt_info = self.save_checkpoint()
                        if self.accelerator.is_main_process:
                            logger.info(
                                "[ckpt] step=%d weights=%s state=%s",
                                self.global_step,
                                ckpt_info["weights_path"],
                                ckpt_info["state_path"],
                            )

                    if self.global_step >= self.max_steps:
                        if self.action_swap_eval_at_end:
                            self.evaluate_action_swap(tag="end")
                        if self.save_trainable_final:
                            self.accelerator.wait_for_everyone()
                            if self.accelerator.is_main_process:
                                interface_path = self._save_trainable_checkpoint(
                                    step_tag=f"step_{self.global_step:06d}"
                                )
                                logger.info(
                                    "[interface-ckpt] step=%d path=%s",
                                    self.global_step,
                                    interface_path,
                                )
                            self.accelerator.wait_for_everyone()
                        if self.save_final:
                            ckpt_info = self.save_checkpoint()
                            if self.accelerator.is_main_process:
                                logger.info(
                                    "[done] max_steps reached step=%d weights=%s state=%s",
                                    self.global_step,
                                    ckpt_info["weights_path"],
                                    ckpt_info["state_path"],
                                )
                        elif self.accelerator.is_main_process:
                            logger.info(
                                "[done] max_steps reached step=%d save_final=false; "
                                "no final checkpoint was written.",
                                self.global_step,
                            )
                        return

        if self.save_final:
            ckpt_info = self.save_checkpoint()
            if self.accelerator.is_main_process:
                logger.info(
                    "[done] training finished step=%d weights=%s state=%s",
                    self.global_step,
                    ckpt_info["weights_path"],
                    ckpt_info["state_path"],
                )
        elif self.accelerator.is_main_process:
            logger.info(
                "[done] training finished step=%d save_final=false; "
                "no final checkpoint was written.",
                self.global_step,
            )
        
