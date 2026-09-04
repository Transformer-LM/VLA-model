"""Geometry utilities for the controlled PointMap relation-event pilot."""

from __future__ import annotations

import numpy as np


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


def relation_pointmap_features(
    depths: np.ndarray,
    segmentations: np.ndarray,
    pixel_to_world: np.ndarray,
    target_id: int,
    reference_id: int,
) -> np.ndarray:
    """Summarize target/reference PointMaps and their metric relation.

    Expected leading dimensions are [time=2, camera=2]. The same object
    association masks are available to all object-addressed baselines.
    """

    features: list[np.ndarray] = []
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
            target_summary = cloud_summary(target)
            reference_summary = cloud_summary(reference)
            features.extend((target_summary, reference_summary))
            target_center = None if len(target) == 0 else np.median(target, axis=0)
            reference_center = None if len(reference) == 0 else np.median(reference, axis=0)
            centers[(time_idx, camera_idx, "target")] = target_center
            centers[(time_idx, camera_idx, "reference")] = reference_center
            if target_center is None or reference_center is None:
                features.append(np.zeros(4, dtype=np.float32))
            else:
                relative = target_center - reference_center
                features.append(np.concatenate(([1.0], relative)).astype(np.float32))

    # Explicit temporal deltas are useful to both the no-action PointMap model
    # and the direct predicate baseline; no action is smuggled into this pilot.
    for camera_idx in range(depths.shape[1]):
        for role in ("target", "reference"):
            before = centers[(0, camera_idx, role)]
            after = centers[(1, camera_idx, role)]
            if before is None or after is None:
                features.append(np.zeros(4, dtype=np.float32))
            else:
                features.append(np.concatenate(([1.0], after - before)).astype(np.float32))
    return np.concatenate(features).astype(np.float32)


def oracle_relative_features(
    target_pose: np.ndarray,
    reference_pose: np.ndarray,
    target_visible: np.ndarray,
    reference_visible: np.ndarray,
) -> np.ndarray:
    """Build an oracle upper-bound vector from simulator poses."""

    target_pose = np.asarray(target_pose, dtype=np.float32)
    reference_pose = np.asarray(reference_pose, dtype=np.float32)
    relative = target_pose[:, :3] - reference_pose[:, :3]
    delta_target = target_pose[1, :3] - target_pose[0, :3]
    delta_reference = reference_pose[1, :3] - reference_pose[0, :3]
    return np.concatenate(
        (
            target_pose.reshape(-1),
            reference_pose.reshape(-1),
            relative.reshape(-1),
            delta_target,
            delta_reference,
            np.asarray(target_visible, dtype=np.float32).reshape(-1),
            np.asarray(reference_visible, dtype=np.float32).reshape(-1),
        )
    )

