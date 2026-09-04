"""Matched A/B/C predictive-gradient routing with manual FP32 SGD."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import torch

from .adapter import IdentityLowRankAdapter

TensorPair = tuple[torch.Tensor, torch.Tensor]
LossFunction = Callable[[IdentityLowRankAdapter], torch.Tensor]


@dataclass(frozen=True)
class GradientDiagnostics:
    action_norm_a: float
    action_norm_b: float
    action_norm_c: float
    future_norm_a: float
    future_norm_b_discarded: float
    future_norm_c: float
    rho: float
    scale_a: float
    scale_c: float
    relative_error_a: float
    relative_error_c: float
    fallback: bool
    fallback_reasons: tuple[str, ...]
    final_norm_a_before_clip: float
    final_norm_b_before_clip: float
    final_norm_c_before_clip: float


def _parameters(adapter: IdentityLowRankAdapter) -> tuple[torch.nn.Parameter, torch.nn.Parameter]:
    return adapter.U, adapter.V


def _grad(loss_fn: LossFunction, adapter: IdentityLowRankAdapter) -> TensorPair:
    loss = loss_fn(adapter)
    if loss.ndim != 0 or not torch.isfinite(loss):
        raise FloatingPointError("Loss must be a finite scalar")
    gradients = torch.autograd.grad(loss, _parameters(adapter), create_graph=False, retain_graph=False)
    result = tuple(gradient.detach().float() for gradient in gradients)
    if not all(torch.isfinite(gradient).all() for gradient in result):
        raise FloatingPointError("Nonfinite adapter gradient")
    return result  # type: ignore[return-value]


def _norm(gradients: TensorPair) -> torch.Tensor:
    return torch.sqrt(sum(gradient.square().sum() for gradient in gradients))


def _add(left: TensorPair, right: TensorPair, scale: float) -> TensorPair:
    return tuple(a + scale * b for a, b in zip(left, right, strict=True))  # type: ignore[return-value]


def _clip(gradients: TensorPair, maximum: float = 1.0) -> tuple[TensorPair, float]:
    norm = _norm(gradients)
    norm_value = float(norm.item())
    factor = min(1.0, maximum / (norm_value + 1e-12))
    return tuple(gradient * factor for gradient in gradients), norm_value  # type: ignore[return-value]


def _dose(rho: float, future: TensorPair, label: str) -> tuple[float, float, tuple[str, ...]]:
    future_norm = float(_norm(future).item())
    reasons: list[str] = []
    raw_scale = rho / (future_norm + 1e-12)
    scale = min(1e3, max(1e-3, raw_scale))
    if future_norm <= 1e-12:
        reasons.append(f"{label}:future_norm<=1e-12")
    if rho <= 1e-12:
        reasons.append(f"{label}:rho<=1e-12")
    if scale in (1e-3, 1e3):
        reasons.append(f"{label}:scale_hit_cap")
    scaled_norm = future_norm * scale
    relative_error = abs(scaled_norm - rho) / max(rho, 1e-12)
    if relative_error > 0.01:
        reasons.append(f"{label}:relative_error>0.01")
    return scale, relative_error, tuple(reasons)


def _manual_update(adapter: IdentityLowRankAdapter, gradients: TensorPair, learning_rate: float) -> None:
    with torch.no_grad():
        for parameter, gradient in zip(_parameters(adapter), gradients, strict=True):
            parameter.add_(gradient.to(device=parameter.device, dtype=parameter.dtype), alpha=-learning_rate)


def matched_triplet_step(
    *,
    adapter_a: IdentityLowRankAdapter,
    adapter_b: IdentityLowRankAdapter,
    adapter_c: IdentityLowRankAdapter,
    action_loss_a: LossFunction,
    action_loss_b: LossFunction,
    action_loss_c: LossFunction,
    valid_future_loss_a: LossFunction,
    valid_future_loss_b: LossFunction,
    donor_future_loss_c: LossFunction,
    learning_rate: float = 1e-3,
) -> GradientDiagnostics:
    """Run one frozen matched-compute update.

    B's valid-target future forward/backward is fully evaluated, diagnosed, and
    discarded. Rho comes only from B's own action gradient. If either A or C
    fails dose matching, both omit the future component for this batch.
    """

    action_a = _grad(action_loss_a, adapter_a)
    action_b = _grad(action_loss_b, adapter_b)
    action_c = _grad(action_loss_c, adapter_c)
    future_a = _grad(valid_future_loss_a, adapter_a)
    future_b_discarded = _grad(valid_future_loss_b, adapter_b)
    future_c = _grad(donor_future_loss_c, adapter_c)

    action_norm_b = float(_norm(action_b).item())
    rho = 0.30 * action_norm_b
    scale_a, relative_a, reasons_a = _dose(rho, future_a, "A")
    scale_c, relative_c, reasons_c = _dose(rho, future_c, "C")
    reasons = (*reasons_a, *reasons_c)
    fallback = bool(reasons)

    combined_a = action_a if fallback else _add(action_a, future_a, scale_a)
    combined_c = action_c if fallback else _add(action_c, future_c, scale_c)
    clipped_a, preclip_a = _clip(combined_a)
    clipped_b, preclip_b = _clip(action_b)
    clipped_c, preclip_c = _clip(combined_c)

    _manual_update(adapter_a, clipped_a, learning_rate)
    _manual_update(adapter_b, clipped_b, learning_rate)
    _manual_update(adapter_c, clipped_c, learning_rate)

    return GradientDiagnostics(
        action_norm_a=float(_norm(action_a).item()),
        action_norm_b=action_norm_b,
        action_norm_c=float(_norm(action_c).item()),
        future_norm_a=float(_norm(future_a).item()),
        future_norm_b_discarded=float(_norm(future_b_discarded).item()),
        future_norm_c=float(_norm(future_c).item()),
        rho=rho,
        scale_a=scale_a,
        scale_c=scale_c,
        relative_error_a=relative_a,
        relative_error_c=relative_c,
        fallback=fallback,
        fallback_reasons=tuple(reasons),
        final_norm_a_before_clip=preclip_a,
        final_norm_b_before_clip=preclip_b,
        final_norm_c_before_clip=preclip_c,
    )


def adapters_identical(adapters: Iterable[IdentityLowRankAdapter]) -> bool:
    values = tuple(adapters)
    if not values:
        raise ValueError("At least one adapter is required")
    reference = values[0].state_dict()
    return all(
        all(torch.equal(reference[key], adapter.state_dict()[key]) for key in reference)
        for adapter in values[1:]
    )
