"""Strict QwenOFT host construction and the PGR action-interface facade."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import torch

from .checkpoint import CheckpointAudit, load_audited_state_dict, strict_load_host_state
from .constants import ACTION_HORIZON, REPRESENTATION_DIM


BASE_QWEN_PATH = Path("<PERSONAL_RESEARCH_ROOT>/checkpoints/qwen/Qwen3-VL-4B-Instruct")

SANITIZED_HOST_CONFIG_PAYLOAD = {
    "framework": {
        "name": "QwenOFT",
        "qwenvl": {"base_vlm": str(BASE_QWEN_PATH), "attn_implementation": "sdpa"},
        "action_model": {
            "action_model_type": "MLP",
            "action_dim": 7,
            "action_hidden_dim": REPRESENTATION_DIM,
            "future_action_window_size": 7,
            "past_action_window_size": 0,
            "action_horizon": ACTION_HORIZON,
        },
    },
    "datasets": {"vla_data": {"include_state": False, "obs_image_size": None}},
    "trainer": {"pretrained_checkpoint": None, "freeze_modules": "qwen_vl_interface,action_model"},
}


@dataclass(frozen=True)
class HostLoadAudit:
    checkpoint: CheckpointAudit
    hidden_size: int
    action_horizon: int
    action_head_dtype: str
    frozen_parameter_count: int
    trainable_parameter_count: int


def sanitized_host_config() -> Any:
    """Construct the approved host config without following historical paths."""

    from omegaconf import OmegaConf

    return OmegaConf.create(SANITIZED_HOST_CONFIG_PAYLOAD)


def move_tensor_inputs_to_device(inputs: Any, device: torch.device) -> Any:
    """Move processor outputs to one verified model device and assert the result."""

    moved = inputs.to(device) if hasattr(inputs, "to") else {
        key: value.to(device) if isinstance(value, torch.Tensor) else value for key, value in inputs.items()
    }
    for key, value in moved.items():
        if isinstance(value, torch.Tensor) and value.device != device:
            raise RuntimeError(f"Processor tensor {key} remained on {value.device}, expected {device}")
    return moved


def build_strict_frozen_host(step: int) -> tuple[torch.nn.Module, HostLoadAudit]:
    from starVLA.model.framework.base_framework import build_framework

    state_dict, checkpoint_audit = load_audited_state_dict(step)
    host = build_framework(sanitized_host_config())
    strict_load_host_state(host, state_dict)
    del state_dict
    hidden_size = int(host.qwen_vl_interface.model.config.hidden_size)
    if hidden_size != REPRESENTATION_DIM:
        raise RuntimeError(f"Host hidden size mismatch: {hidden_size} != {REPRESENTATION_DIM}")
    if int(host.action_horizon) != ACTION_HORIZON:
        raise RuntimeError(f"Host action horizon mismatch: {host.action_horizon} != {ACTION_HORIZON}")
    action_head_dtype = str(next(host.action_model.parameters()).dtype)
    frozen = sum(parameter.numel() for parameter in host.parameters() if not parameter.requires_grad)
    trainable = sum(parameter.numel() for parameter in host.parameters() if parameter.requires_grad)
    if trainable != 0:
        raise RuntimeError(f"Strict host unexpectedly has {trainable} trainable parameters")
    return host, HostLoadAudit(
        checkpoint=checkpoint_audit,
        hidden_size=hidden_size,
        action_horizon=int(host.action_horizon),
        action_head_dtype=action_head_dtype,
        frozen_parameter_count=frozen,
        trainable_parameter_count=trainable,
    )


class QwenOFTActionInterface:
    """Expose frozen action tokens and frozen action decoding without upstream edits."""

    def __init__(self, host: torch.nn.Module) -> None:
        self.host = host
        if int(host.chunk_len) != ACTION_HORIZON:
            raise ValueError("Host chunk length is not the frozen eight-token interface")

    def _prepare(self, examples: Sequence[dict[str, Any]]) -> dict[str, torch.Tensor]:
        from deployment.model_server.tools.image_tools import to_pil_preserve
        from starVLA.training.trainer_utils.trainer_tools import resize_images

        values = list(examples)
        if not values:
            raise ValueError("At least one example is required")
        images = [to_pil_preserve(example["image"]) for example in values]
        instructions = [str(example["lang"]) for example in values]
        states = [example["state"] for example in values] if "state" in values[0] else None
        if states is not None:
            instructions = self.host.add_discretized_state_to_instruction(instructions, states)
        image_size = getattr(self.host.config.datasets.vla_data, "obs_image_size", None)
        if image_size:
            images = resize_images(images, target_size=image_size)
        action_tokens = self.host.action_token * ACTION_HORIZON
        suffix = f" Please predict the next {ACTION_HORIZON} robot actions: <action>{action_tokens}<action>."
        instructions = [instruction + suffix for instruction in instructions]
        inputs = self.host.qwen_vl_interface.build_qwenvl_inputs(images=images, instructions=instructions)
        model_device = next(self.host.qwen_vl_interface.parameters()).device
        inputs = move_tensor_inputs_to_device(inputs, model_device)
        if inputs["input_ids"].ndim != 2 or inputs["input_ids"].shape[0] != len(values):
            raise RuntimeError(f"Processor input_ids batch mismatch: {tuple(inputs['input_ids'].shape)}")
        counts = (inputs["input_ids"] == self.host.action_token_id).sum(dim=1)
        if not torch.equal(counts, torch.full_like(counts, ACTION_HORIZON)):
            raise RuntimeError(f"Expected exactly eight action tokens per sample, got {counts.tolist()}")
        return inputs

    def encode_action_tokens(self, examples: Sequence[dict[str, Any]]) -> torch.Tensor:
        inputs = self._prepare(examples)
        device_type = next(self.host.qwen_vl_interface.parameters()).device.type
        with torch.inference_mode(), torch.autocast(
            device_type=device_type,
            dtype=torch.bfloat16,
            enabled=device_type == "cuda",
        ):
            outputs = self.host.qwen_vl_interface(
                **inputs,
                output_attentions=False,
                output_hidden_states=True,
                return_dict=True,
            )
        hidden = outputs.hidden_states[-1]
        action_tokens = self.host._gather_action_token_embeddings(
            hidden,
            inputs["input_ids"],
            action_token_id=self.host.action_token_id,
        )
        if tuple(action_tokens.shape[1:]) != (ACTION_HORIZON, REPRESENTATION_DIM):
            raise RuntimeError(f"Action-interface shape mismatch: {tuple(action_tokens.shape)}")
        if not torch.isfinite(action_tokens).all():
            raise RuntimeError("Action-interface tokens contain nonfinite values")
        return action_tokens.float()

    def decode_action_tokens(self, action_tokens: torch.Tensor) -> torch.Tensor:
        if tuple(action_tokens.shape[1:]) != (ACTION_HORIZON, REPRESENTATION_DIM):
            raise ValueError(f"Expected [B,8,2560] tokens, got {tuple(action_tokens.shape)}")
        parameter = next(self.host.action_model.parameters())
        values = action_tokens.to(device=parameter.device, dtype=parameter.dtype)
        decoded = self.host.action_model.predict_action(values).float()
        if tuple(decoded.shape[1:]) != (ACTION_HORIZON, 7) or not torch.isfinite(decoded).all():
            raise RuntimeError(f"Decoded action contract failed: shape={tuple(decoded.shape)}")
        return decoded

    def predict_via_interface(self, examples: Sequence[dict[str, Any]]) -> torch.Tensor:
        return self.decode_action_tokens(self.encode_action_tokens(examples))

    def predict_direct(self, examples: Sequence[dict[str, Any]]) -> torch.Tensor:
        result = self.host.predict_action(examples=list(examples))["normalized_actions"]
        return torch.from_numpy(np.asarray(result)).float()


@dataclass(frozen=True)
class InterfaceParity:
    direct_vs_interface_max_abs: float
    interface_repeat_max_abs: float
    in_memory_cache_roundtrip_max_abs: float
    threshold: float

    @property
    def passed(self) -> bool:
        return max(
            self.direct_vs_interface_max_abs,
            self.interface_repeat_max_abs,
            self.in_memory_cache_roundtrip_max_abs,
        ) <= self.threshold


def measure_engineering_parity(
    interface: QwenOFTActionInterface,
    examples: Sequence[dict[str, Any]],
    threshold: float = 1e-6,
) -> InterfaceParity:
    direct = interface.predict_direct(examples)
    tokens_first = interface.encode_action_tokens(examples)
    via_first = interface.decode_action_tokens(tokens_first).detach().cpu()
    tokens_second = interface.encode_action_tokens(examples)
    via_second = interface.decode_action_tokens(tokens_second).detach().cpu()
    cached_clone = tokens_first.detach().clone()
    via_cache = interface.decode_action_tokens(cached_clone).detach().cpu()
    return InterfaceParity(
        direct_vs_interface_max_abs=float((direct.cpu() - via_first).abs().max().item()),
        interface_repeat_max_abs=float((via_first - via_second).abs().max().item()),
        in_memory_cache_roundtrip_max_abs=float((via_first - via_cache).abs().max().item()),
        threshold=threshold,
    )
