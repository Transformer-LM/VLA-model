"""Task-invariant geometry utilities for the controlled relation-event pilot."""

from __future__ import annotations

import numpy as np


GEOMETRY_SCALE_M = 0.30
INVALIDATION_THRESHOLD_M = 0.09


def masked_world_points(
    depth_m: np.ndarray,
    segmentation: np.ndarray,
    instance_id: int,
    pixel_to_world: np.ndarray,
    max_points: int = 512,
) -> np.ndarray:
    """Back-project one instance into a sparse world-frame PointMap.

    LIBERO observations are vertically flipped relative to MuJoCo's camera
    projection convention, so image rows are reversed before applying the
    inverse projection matrix.
    """

    depth = np.asarray(depth_m).squeeze()
    seg = np.asarray(segmentation).squeeze()
    pixels = np.argwhere((seg == int(instance_id)) & np.isfinite(depth) & (depth > 0.0))
    if pixels.size == 0:
        return np.empty((0, 3), dtype=np.float32)
    if len(pixels) > max_points:
        # Deterministic coverage of the full mask, not a random sample.
        keep = np.linspace(0, len(pixels) - 1, max_points, dtype=np.int64)
        pixels = pixels[keep]
    rows = depth.shape[0] - 1 - pixels[:, 0]
    cols = pixels[:, 1]
    z = depth[pixels[:, 0], pixels[:, 1]]
    homogeneous = np.stack((cols * z, rows * z, z, np.ones_like(z)), axis=1)
    points = (np.asarray(pixel_to_world) @ homogeneous.T).T[:, :3]
    return points.astype(np.float32, copy=False)


def cloud_summary(points: np.ndarray) -> np.ndarray:
    """Return visibility, robust center, spread, and extent for one cloud."""

    if len(points) == 0:
        return np.zeros(10, dtype=np.float32)
    center = np.median(points, axis=0)
    spread = np.median(np.abs(points - center), axis=0)
    lo, hi = np.quantile(points, [0.1, 0.9], axis=0)
    visibility = np.array([min(len(points) / 128.0, 1.0)], dtype=np.float32)
    return np.concatenate((visibility, center, spread, hi - lo)).astype(np.float32)


def _scaled_motion(before: np.ndarray | None, after: np.ndarray | None) -> np.ndarray:
    """Return validity, scaled xyz motion, and scaled motion norm."""

    if before is None or after is None:
        return np.zeros(5, dtype=np.float32)
    delta = (np.asarray(after) - np.asarray(before)).astype(np.float32)
    scaled = delta / GEOMETRY_SCALE_M
    return np.concatenate(([1.0], scaled, [np.linalg.norm(delta) / GEOMETRY_SCALE_M])).astype(np.float32)


def relation_pointmap_features(
    depths: np.ndarray,
    segmentations: np.ndarray,
    pixel_to_world: np.ndarray,
    target_id: int,
    reference_id: int,
) -> np.ndarray:
    """Return task-invariant object-relative PointMap motion features.

    Absolute world coordinates, object extents, and raw pixel counts are
    intentionally omitted. Each camera contributes four visibility flags plus
    valid/scaled motion for the target, reference, and their relative center.
    Expected leading dimensions are [time=2, camera=2].
    """

    centers: dict[tuple[int, int, str], np.ndarray | None] = {}
    for time_idx in range(depths.shape[0]):
        for camera_idx in range(depths.shape[1]):
            target = masked_world_points(
                depths[time_idx, camera_idx],
                segmentations[time_idx, camera_idx],
                target_id,
                pixel_to_world[time_idx, camera_idx],
            )
            reference = masked_world_points(
                depths[time_idx, camera_idx],
                segmentations[time_idx, camera_idx],
                reference_id,
                pixel_to_world[time_idx, camera_idx],
            )
            target_center = None if len(target) == 0 else np.median(target, axis=0)
            reference_center = None if len(reference) == 0 else np.median(reference, axis=0)
            centers[(time_idx, camera_idx, "target")] = target_center
            centers[(time_idx, camera_idx, "reference")] = reference_center

    features: list[np.ndarray] = []
    for camera_idx in range(depths.shape[1]):
        target_before = centers[(0, camera_idx, "target")]
        target_after = centers[(1, camera_idx, "target")]
        reference_before = centers[(0, camera_idx, "reference")]
        reference_after = centers[(1, camera_idx, "reference")]
        visibility = np.asarray(
            [
                target_before is not None,
                target_after is not None,
                reference_before is not None,
                reference_after is not None,
            ],
            dtype=np.float32,
        )
        relative_before = (
            None if target_before is None or reference_before is None else target_before - reference_before
        )
        relative_after = (
            None if target_after is None or reference_after is None else target_after - reference_after
        )
        features.extend(
            (
                visibility,
                _scaled_motion(target_before, target_after),
                _scaled_motion(reference_before, reference_after),
                _scaled_motion(relative_before, relative_after),
            )
        )
    return np.concatenate(features).astype(np.float32)


def oracle_relative_features(
    target_pose: np.ndarray,
    reference_pose: np.ndarray,
    target_visible: np.ndarray,
    reference_visible: np.ndarray,
) -> np.ndarray:
    """Build a task-invariant Oracle vector from simulator relative motion.

    The repair deliberately removes absolute positions, quaternions, and raw
    visibility pixel counts that caused held-family normalization shift.
    """

    target_pose = np.asarray(target_pose, dtype=np.float32)
    reference_pose = np.asarray(reference_pose, dtype=np.float32)
    delta_target = target_pose[1, :3] - target_pose[0, :3]
    delta_reference = reference_pose[1, :3] - reference_pose[0, :3]
    relative = target_pose[:, :3] - reference_pose[:, :3]
    delta_relative = relative[1] - relative[0]
    target_visible = np.asarray(target_visible, dtype=np.float32) > 0
    reference_visible = np.asarray(reference_visible, dtype=np.float32) > 0

    def scaled(delta: np.ndarray) -> np.ndarray:
        return np.concatenate(
            (delta / GEOMETRY_SCALE_M, [np.linalg.norm(delta) / GEOMETRY_SCALE_M])
        ).astype(np.float32)

    return np.concatenate(
        (
            scaled(delta_target),
            scaled(delta_reference),
            scaled(delta_relative),
            target_visible.astype(np.float32).reshape(-1),
            reference_visible.astype(np.float32).reshape(-1),
            (target_visible[0] & ~target_visible[1]).astype(np.float32),
            (reference_visible[0] & ~reference_visible[1]).astype(np.float32),
        )
    ).astype(np.float32)


def invariant_oracle_decision(
    target_pose: np.ndarray,
    reference_pose: np.ndarray,
    target_visible: np.ndarray,
    threshold_m: float = INVALIDATION_THRESHOLD_M,
) -> int:
    """Frozen deterministic Oracle: continue=0, retract=1, reobserve=2."""

    target_pose = np.asarray(target_pose, dtype=np.float32)
    reference_pose = np.asarray(reference_pose, dtype=np.float32)
    relative = target_pose[:, :3] - reference_pose[:, :3]
    if float(np.linalg.norm(relative[1] - relative[0])) >= threshold_m:
        return 1
    visible = np.asarray(target_visible) > 0
    if bool(np.any(visible[0])) and not bool(np.any(visible[1])):
        return 2
    return 0


def invariant_pointmap_decision(
    features: np.ndarray,
    threshold_m: float = INVALIDATION_THRESHOLD_M,
) -> int:
    """Frozen PointMap diagnostic using only observed relative motion."""

    values = np.asarray(features, dtype=np.float32)
    if values.shape != (38,):
        raise ValueError(f"expected 38 invariant PointMap features, got {values.shape}")
    blocks = values.reshape(2, 19)
    valid_relative = blocks[:, 14] > 0.5
    relative_norm_m = blocks[:, 18] * GEOMETRY_SCALE_M
    if np.any(valid_relative & (relative_norm_m >= threshold_m)):
        return 1
    target_pre_visible = bool(np.any(blocks[:, 0] > 0.5))
    target_post_visible = bool(np.any(blocks[:, 1] > 0.5))
    if target_pre_visible and not target_post_visible:
        return 2
    return 0
