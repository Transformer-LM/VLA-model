"""Frozen deterministic 54-D object-relative PointMap geometry for E1.

This module is intentionally independent from ``geometry.py``. The latter is
the audited 38-D two-frame E0 diagnostic; this file implements the pre-action
transition input registered in the E1 proposal.
"""

from __future__ import annotations

import numpy as np


VOXEL_SIZE_M = 0.005
MAX_OBJECT_POINTS = 128


def masked_world_points(
    depth_m: np.ndarray,
    segmentation: np.ndarray,
    instance_id: int,
    pixel_to_world: np.ndarray,
) -> np.ndarray:
    """Back-project every finite instance pixel to MuJoCo world coordinates."""
    depth = np.asarray(depth_m).squeeze()
    segmentation = np.asarray(segmentation).squeeze()
    if depth.ndim != 2 or segmentation.shape != depth.shape:
        raise ValueError(f"invalid depth/seg shapes: {depth.shape}/{segmentation.shape}")
    pixels = np.argwhere(
        (segmentation == int(instance_id)) & np.isfinite(depth) & (depth > 0.0)
    )
    if len(pixels) == 0:
        return np.empty((0, 3), dtype=np.float32)
    # LIBERO image rows are flipped relative to MuJoCo's camera convention.
    rows = depth.shape[0] - 1 - pixels[:, 0]
    cols = pixels[:, 1]
    z = depth[pixels[:, 0], pixels[:, 1]]
    homogeneous = np.stack((cols * z, rows * z, z, np.ones_like(z)), axis=1)
    points = (np.asarray(pixel_to_world, dtype=np.float64) @ homogeneous.T).T[:, :3]
    return points.astype(np.float32, copy=False)


def world_to_robot_base(
    points: np.ndarray,
    base_position: np.ndarray,
    base_rotation: np.ndarray,
) -> np.ndarray:
    """Express row-vector world points in the robot-base coordinate frame."""
    points = np.asarray(points, dtype=np.float64)
    if len(points) == 0:
        return np.empty((0, 3), dtype=np.float32)
    base_position = np.asarray(base_position, dtype=np.float64).reshape(3)
    base_rotation = np.asarray(base_rotation, dtype=np.float64).reshape(3, 3)
    return ((points - base_position) @ base_rotation).astype(np.float32)


def deterministic_voxel_reduce(
    points: np.ndarray,
    voxel_size_m: float = VOXEL_SIZE_M,
    max_points: int = MAX_OBJECT_POINTS,
) -> np.ndarray:
    """Select one center-nearest point per lexicographically ordered voxel."""
    points = np.asarray(points, dtype=np.float64).reshape(-1, 3)
    points = points[np.isfinite(points).all(axis=1)]
    if len(points) == 0:
        return np.empty((0, 3), dtype=np.float32)
    voxels = np.floor(points / float(voxel_size_m)).astype(np.int64)
    order = np.lexsort((voxels[:, 2], voxels[:, 1], voxels[:, 0]))
    points = points[order]
    voxels = voxels[order]

    selected: list[np.ndarray] = []
    start = 0
    while start < len(points):
        stop = start + 1
        while stop < len(points) and np.array_equal(voxels[stop], voxels[start]):
            stop += 1
        center = (voxels[start].astype(np.float64) + 0.5) * float(voxel_size_m)
        distances = np.sum((points[start:stop] - center) ** 2, axis=1)
        selected.append(points[start + int(np.argmin(distances))])
        start = stop
    reduced = np.stack(selected)
    if len(reduced) > max_points:
        keep = np.linspace(0, len(reduced) - 1, max_points, dtype=np.int64)
        reduced = reduced[keep]
    return reduced.astype(np.float32)


def instance_cloud(
    depths: np.ndarray,
    segmentations: np.ndarray,
    pixel_to_world: np.ndarray,
    instance_id: int,
    base_position: np.ndarray,
    base_rotation: np.ndarray,
) -> tuple[np.ndarray, int]:
    """Fuse two camera PointMaps, align to robot base, and reduce deterministically."""
    clouds = [
        masked_world_points(depths[index], segmentations[index], instance_id, pixel_to_world[index])
        for index in range(depths.shape[0])
    ]
    raw_count = int(sum(len(cloud) for cloud in clouds))
    fused = np.concatenate(clouds, axis=0) if raw_count else np.empty((0, 3), dtype=np.float32)
    aligned = world_to_robot_base(fused, base_position, base_rotation)
    return deterministic_voxel_reduce(aligned), raw_count


def _object_block(
    points: np.ndarray,
    target_center: np.ndarray,
    geometry_allowed: bool,
) -> np.ndarray:
    block = np.zeros(20, dtype=np.float32)
    if len(points) == 0:
        return block
    block[0] = 1.0
    # The registered count is a property of the deterministic reduced
    # PointMap, not camera resolution or duplicate two-view pixels.
    block[1] = min(float(len(points)) / float(MAX_OBJECT_POINTS), 1.0)
    if not geometry_allowed:
        return block
    centered = np.asarray(points, dtype=np.float64) - np.asarray(target_center, dtype=np.float64)
    robust_center = np.median(centered, axis=0)
    quantiles = np.quantile(centered, (0.1, 0.5, 0.9), axis=0)
    if len(centered) <= 1:
        eigenvalues = np.zeros(3, dtype=np.float64)
    else:
        covariance = np.cov(centered, rowvar=False, bias=True)
        eigenvalues = np.linalg.eigvalsh(covariance)[::-1]
    extents = quantiles[2] - quantiles[0]
    block[2:5] = robust_center.astype(np.float32)
    block[5:14] = quantiles.reshape(-1).astype(np.float32)
    block[14:17] = eigenvalues.astype(np.float32)
    block[17:20] = extents.astype(np.float32)
    return block


def _robust_box(points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    quantiles = np.quantile(np.asarray(points, dtype=np.float64), (0.1, 0.9), axis=0)
    return quantiles[0], quantiles[1]


def _pair_block(target: np.ndarray, reference: np.ndarray, relation: str) -> np.ndarray:
    block = np.zeros(14, dtype=np.float32)
    if len(target) == 0 or len(reference) == 0:
        return block
    target_center = np.median(target, axis=0)
    reference_center = np.median(reference, axis=0)
    displacement = reference_center - target_center
    block[0:3] = displacement
    block[3:6] = np.abs(displacement)
    pairwise = target[:, None, :].astype(np.float64) - reference[None, :, :].astype(np.float64)
    block[6] = float(np.sqrt(np.min(np.sum(pairwise * pairwise, axis=2))))

    target_low, target_high = _robust_box(target)
    reference_low, reference_high = _robust_box(reference)
    intersection = np.maximum(0.0, np.minimum(target_high, reference_high) - np.maximum(target_low, reference_low))
    union = np.maximum(target_high, reference_high) - np.minimum(target_low, reference_low)
    overlap = np.divide(intersection, np.maximum(union, 1e-6))
    block[7:10] = overlap.astype(np.float32)

    if relation == "in":
        # Positive only when the target robust box lies inside the reference robust box.
        block[10] = float(np.min(np.concatenate((target_low - reference_low, reference_high - target_high))))
        block[11] = 1.0
    elif relation == "on":
        horizontal_intersection = intersection[:2]
        vertical_tolerance = 0.02 - abs(float(target_low[2] - reference_high[2]))
        block[12] = float(min(horizontal_intersection[0], horizontal_intersection[1], vertical_tolerance))
        block[13] = 1.0
    else:
        raise ValueError(f"unsupported E1 relation: {relation}")
    return block


def relation_geometry_54(
    depths: np.ndarray,
    segmentations: np.ndarray,
    pixel_to_world: np.ndarray,
    target_id: int,
    reference_id: int,
    base_position: np.ndarray,
    base_rotation: np.ndarray,
    relation: str,
) -> tuple[np.ndarray, dict[str, int]]:
    """Return the registered 54-D geometry and visibility counts."""
    target, target_raw_count = instance_cloud(
        depths, segmentations, pixel_to_world, target_id, base_position, base_rotation
    )
    reference, reference_raw_count = instance_cloud(
        depths, segmentations, pixel_to_world, reference_id, base_position, base_rotation
    )
    if len(target) == 0:
        target_center = np.zeros(3, dtype=np.float32)
        target_block = np.zeros(20, dtype=np.float32)
        reference_block = _object_block(
            reference, target_center, geometry_allowed=False
        )
    else:
        target_center = np.median(target, axis=0)
        target_block = _object_block(target, target_center, geometry_allowed=True)
        reference_block = _object_block(
            reference, target_center, geometry_allowed=len(reference) > 0
        )
    features = np.concatenate((target_block, reference_block, _pair_block(target, reference, relation)))
    if features.shape != (54,) or not np.isfinite(features).all():
        raise RuntimeError(f"invalid E1 geometry output: {features.shape}")
    return features.astype(np.float32), {
        "target_raw": target_raw_count,
        "reference_raw": reference_raw_count,
        "target_reduced": int(len(target)),
        "reference_reduced": int(len(reference)),
    }
