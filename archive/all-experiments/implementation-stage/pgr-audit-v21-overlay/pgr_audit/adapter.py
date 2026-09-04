"""The frozen rank-32 identity adapter at the VLA action interface."""

from __future__ import annotations

import math

import torch
from torch import nn

from .constants import ADAPTER_RANK, REPRESENTATION_DIM


class IdentityLowRankAdapter(nn.Module):
    """Apply ``h + U @ V @ LN0(h)`` tokenwise.

    ``LN0`` uses population variance, epsilon 1e-5, and no affine terms.
    U is exactly zero at construction, making the initial mapping identity.
    """

    def __init__(
        self,
        dimension: int = REPRESENTATION_DIM,
        rank: int = ADAPTER_RANK,
        eps: float = 1e-5,
        *,
        generator: torch.Generator | None = None,
    ) -> None:
        super().__init__()
        if dimension <= 0 or rank <= 0:
            raise ValueError("dimension and rank must be positive")
        self.dimension = dimension
        self.rank = rank
        self.eps = eps
        self.V = nn.Parameter(torch.empty(rank, dimension, dtype=torch.float32))
        self.U = nn.Parameter(torch.zeros(dimension, rank, dtype=torch.float32))
        self.reset_parameters(generator=generator)

    def reset_parameters(self, *, generator: torch.Generator | None = None) -> None:
        nn.init.kaiming_uniform_(self.V, a=math.sqrt(5), generator=generator)
        nn.init.zeros_(self.U)

    def ln0(self, hidden: torch.Tensor) -> torch.Tensor:
        if hidden.shape[-1] != self.dimension:
            raise ValueError(f"Expected final dimension {self.dimension}, got {hidden.shape[-1]}")
        source = hidden.float()
        mean = source.mean(dim=-1, keepdim=True)
        variance = (source - mean).square().mean(dim=-1, keepdim=True)
        return (source - mean) * torch.rsqrt(variance + self.eps)

    def delta(self, hidden: torch.Tensor) -> torch.Tensor:
        normalized = self.ln0(hidden)
        return (normalized @ self.V.t()) @ self.U.t()

    def forward(self, hidden: torch.Tensor) -> torch.Tensor:
        source = hidden.float()
        return source + self.delta(source)

    def assert_identity(self, hidden: torch.Tensor) -> None:
        output = self(hidden)
        if not torch.equal(output, hidden.float()):
            maximum = (output - hidden.float()).abs().max().item()
            raise AssertionError(f"Zero-U adapter is not exact identity; max_abs={maximum}")
