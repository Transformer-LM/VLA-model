"""P025: leakage-free, continuous factual-to-candidate contact-support audit.

This protocol differs from the earlier P022/P024 diagnostics in four ways:

1. blocks are individual simulator geom parameter addresses, not body groups;
2. every selector receives a fixed per-boundary simulator-step cap and never receives
   ISRAC's selected-block count;
3. candidate actions continue directly from each factual twin endpoint;
4. the compiler manifest contains no WAM residual, embedding, ranking, or ID.

The first version covers contact-local compliance or friction only. It is an
E0 protocol witness, not yet a paper-level multi-simulator result.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Iterable, Sequence

import numpy as np

from certify_policy_boundary_alias import (
    FAMILY_VALUES,
    contacts,
    dynamic_nonrobot_vector,
    existing,
    is_robot_body,
    new_output,
    parameter,
)
from israc.certificate import (
    AliasCertificate,
    FrameTrace,
    NoiseEnvelope,
    RolloutTrace,
    certify_alias_pair,
)
from libero_m0_alias import repeat_envelope


BLOCK_SELECTORS = ("israc-contact-subtraction", "candidate-contact", "random-scene")
CONTINUOUS_EXECUTIONS_PER_BLOCK = 4
NOMINAL_CONTINUOUS_EXECUTIONS = 2
ENDPOINT_REPEAT_ABSOLUTE_CAP = 1e-2
SAVED_ENDPOINT_ABSOLUTE_CAP = 1e-2
STATIC_PHYSICS_SCHEMA_VERSION = "mujoco-static-v1"


class SimulatorStepCounter:
    """Count actual simulator transitions instead of inferring them post hoc."""

    def __init__(self) -> None:
        self.count = 0

    def step(self, env: Any, action: np.ndarray) -> Any:
        self.count += 1
        return env.step(action)


def array_digest_probe(array: np.ndarray) -> str:
    """Represent a complete array by an exact deterministic SHA-256 digest."""

    contiguous = np.ascontiguousarray(array)
    payload = (
        str(contiguous.dtype).encode("ascii")
        + b"|"
        + json.dumps(list(contiguous.shape), separators=(",", ":")).encode("ascii")
        + b"|"
        + contiguous.tobytes()
    )
    return hashlib.sha256(payload).hexdigest()


def canonical_array_sha256(array: np.ndarray) -> str:
    contiguous = np.ascontiguousarray(array)
    digest = hashlib.sha256()
    digest.update(str(contiguous.dtype).encode("ascii"))
    digest.update(str(tuple(contiguous.shape)).encode("ascii"))
    digest.update(contiguous.tobytes())
    return digest.hexdigest()


def geom_blocks(
    model: Any,
    pairs: Iterable[tuple[int, int]] | None = None,
) -> dict[str, tuple[int, ...]]:
    """Map realized contacts to exact non-robot geom parameter addresses."""

    if pairs is None:
        ids = range(int(model.ngeom))
    else:
        ids = sorted({geom_id for pair in pairs for geom_id in pair})
    blocks: dict[str, tuple[int, ...]] = {}
    for geom_id in ids:
        body_id = int(model.geom_bodyid[geom_id])
        body_name = model.body_id2name(body_id)
        if is_robot_body(body_name):
            continue
        geom_name = model.geom_id2name(geom_id) or f"geom_{geom_id}"
        key = f"geom:{geom_id}:{geom_name}"
        blocks[key] = (int(geom_id),)
    return blocks


def contact_topology(model: Any) -> list[dict[str, Any]]:
    """Serialize the exact geom/body names used by selector reconstruction."""

    return [
        {
            "geom_id": int(geom_id),
            "geom_name": str(model.geom_id2name(geom_id) or ""),
            "body_id": int(model.geom_bodyid[geom_id]),
            "body_name": str(
                model.body_id2name(int(model.geom_bodyid[geom_id])) or ""
            ),
        }
        for geom_id in range(int(model.ngeom))
    ]


def subtract_blocks(
    candidate: dict[str, tuple[int, ...]],
    factual: dict[str, tuple[int, ...]],
) -> dict[str, tuple[int, ...]]:
    factual_geom_ids = {geom_id for ids in factual.values() for geom_id in ids}
    return {
        key: ids
        for key, ids in candidate.items()
        if all(geom_id not in factual_geom_ids for geom_id in ids)
    }


def select_blocks(
    pool: dict[str, tuple[int, ...]],
    *,
    selector: str,
    max_blocks: int,
    seed: int,
) -> list[tuple[str, tuple[int, ...]]]:
    """Choose blocks without access to another selector's pool size."""

    del selector
    def priority(item: tuple[str, tuple[int, ...]]) -> tuple[str, str]:
        address = item[0]
        digest = hashlib.sha256(f"{seed}|{address}".encode("utf-8")).hexdigest()
        return digest, address

    return sorted(pool.items(), key=priority)[:max_blocks]


def execute_nominal_contacts(
    env: Any,
    modes: Any,
    initialize_episode: Any,
    factual_actions: np.ndarray,
    candidate_actions: np.ndarray,
    step_counter: SimulatorStepCounter,
) -> tuple[set[tuple[int, int]], set[tuple[int, int]], np.ndarray]:
    """Run one continuous nominal factual->candidate trajectory."""

    initialize_episode()
    factual_pairs: set[tuple[int, int]] = set()
    for action in factual_actions:
        modes.trace()
        step_counter.step(env, np.asarray(action, dtype=np.float32))
        factual_pairs.update(contacts(env))
    factual_endpoint = np.asarray(env.sim.get_state().flatten(), dtype=np.float64).copy()
    candidate_pairs: set[tuple[int, int]] = set()
    for action in candidate_actions:
        modes.trace()
        step_counter.step(env, np.asarray(action, dtype=np.float32))
        candidate_pairs.update(contacts(env))
    return factual_pairs, candidate_pairs, factual_endpoint


def boundary_eligibility(
    replay_endpoint_error: float | None,
    repeat_endpoint_error: float | None,
    factual_pairs: set[tuple[int, int]],
    factual_pairs_repeat: set[tuple[int, int]],
    candidate_pairs: set[tuple[int, int]],
    candidate_pairs_repeat: set[tuple[int, int]],
) -> tuple[bool, list[str], float]:
    tolerance = max(
        1e-10,
        1.05 * float(repeat_endpoint_error or 0.0) + 1e-12,
    )
    tolerance = min(tolerance, SAVED_ENDPOINT_ABSOLUTE_CAP)
    reasons: list[str] = []
    if (
        replay_endpoint_error is None
        or not np.isfinite(replay_endpoint_error)
        or replay_endpoint_error > tolerance
    ):
        reasons.append("replayed_factual_endpoint_mismatches_saved_boundary")
    if (
        repeat_endpoint_error is None
        or not np.isfinite(repeat_endpoint_error)
    ):
        reasons.append("nominal_endpoint_repeat_invalid")
    elif repeat_endpoint_error > ENDPOINT_REPEAT_ABSOLUTE_CAP:
        reasons.append("nominal_endpoint_repeat_exceeds_absolute_cap")
    if factual_pairs != factual_pairs_repeat or candidate_pairs != candidate_pairs_repeat:
        reasons.append("nominal_contact_support_not_repeatable")
    return not reasons, reasons, tolerance


def fixed_budget_accounting(
    *,
    factual_steps: int,
    candidate_steps: int,
    selected_blocks: int,
    max_blocks: int,
    boundary_eligible: bool,
    measured_actual_steps: int,
    charge_invalid: bool = False,
) -> dict[str, int]:
    segment_steps = factual_steps + candidate_steps
    actual_executions = (
        NOMINAL_CONTINUOUS_EXECUTIONS
        + CONTINUOUS_EXECUTIONS_PER_BLOCK * selected_blocks
    )
    expected_actual_steps = actual_executions * segment_steps
    if measured_actual_steps != expected_actual_steps:
        raise RuntimeError(
            f"simulator step counter mismatch: measured={measured_actual_steps} "
            f"expected={expected_actual_steps}"
        )
    charged_executions = (
        NOMINAL_CONTINUOUS_EXECUTIONS
        + CONTINUOUS_EXECUTIONS_PER_BLOCK * max_blocks
    ) if (boundary_eligible or charge_invalid) else 0
    charged_steps = charged_executions * segment_steps
    return {
        "actual_continuous_executions": actual_executions,
        "charged_continuous_execution_cap": charged_executions,
        "actual_simulator_steps": measured_actual_steps,
        "expected_actual_simulator_steps": expected_actual_steps,
        "charged_simulator_step_cap": charged_steps,
        "unused_simulator_step_budget": (
            charged_steps - measured_actual_steps
            if (boundary_eligible or charge_invalid) else 0
        ),
    }


def trace_contact_union(trace: RolloutTrace) -> set[tuple[int, int]]:
    """Match the legacy nominal counter: contacts after actions, excluding t0."""

    return {
        pair
        for frame_value in trace.frames[1:]
        for pair in frame_value.contact_geom_pairs
    }


def trace_observation_digest_equal(left: RolloutTrace, right: RolloutTrace) -> bool:
    if len(left.frames) != len(right.frames):
        return False
    return all(
        a.rgb_sha256 == b.rgb_sha256 and a.depth_sha256 == b.depth_sha256
        for a, b in zip(left.frames, right.frames)
    )


def trace_matches_unedited_reference(
    trace: RolloutTrace,
    nominal: RolloutTrace,
    nominal_repeat: RolloutTrace,
) -> bool:
    """Require a claimed factual twin to match the raw unedited transcript."""

    if not (len(trace.frames) == len(nominal.frames) == len(nominal_repeat.frames)):
        return False
    envelope = repeat_envelope((nominal, nominal_repeat))
    for actual, reference, repeated in zip(
        trace.frames, nominal.frames, nominal_repeat.frames
    ):
        for field_name in ("state", "proprio", "physical_effect_probe", "task_effect"):
            actual_values = np.asarray(getattr(actual, field_name), dtype=np.float64)
            reference_values = np.asarray(getattr(reference, field_name), dtype=np.float64)
            repeated_values = np.asarray(getattr(repeated, field_name), dtype=np.float64)
            if actual_values.shape != reference_values.shape or (
                repeated_values.shape != reference_values.shape
            ):
                return False
            tolerance = float(getattr(envelope, field_name))
            if (
                float(np.max(np.abs(actual_values - reference_values), initial=0.0)) > tolerance
                or float(np.max(np.abs(actual_values - repeated_values), initial=0.0)) > tolerance
            ):
                return False
        if (
            actual.rgb_sha256 != reference.rgb_sha256
            or reference.rgb_sha256 != repeated.rgb_sha256
            or actual.depth_sha256 != reference.depth_sha256
            or reference.depth_sha256 != repeated.depth_sha256
            or actual.contact_geom_pairs != reference.contact_geom_pairs
            or reference.contact_geom_pairs != repeated.contact_geom_pairs
        ):
            return False
    return True


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def trace_arrays(prefix: str, trace: RolloutTrace) -> dict[str, np.ndarray]:
    contact_pairs = [frame.contact_geom_pairs for frame in trace.frames]
    offsets = [0]
    flattened: list[tuple[int, int]] = []
    for pairs in contact_pairs:
        flattened.extend(pairs)
        offsets.append(len(flattened))
    return {
        f"{prefix}_state": np.asarray([frame.state for frame in trace.frames], dtype=np.float64),
        f"{prefix}_proprio": np.asarray([frame.proprio for frame in trace.frames], dtype=np.float64),
        f"{prefix}_rgb_sha256": np.asarray(
            [frame.rgb_sha256 for frame in trace.frames], dtype="U64"
        ),
        f"{prefix}_depth_sha256": np.asarray(
            [frame.depth_sha256 for frame in trace.frames], dtype="U64"
        ),
        f"{prefix}_physical_effect_probe": np.asarray(
            [frame.physical_effect_probe for frame in trace.frames], dtype=np.float64
        ),
        f"{prefix}_task_effect": np.asarray(
            [frame.task_effect for frame in trace.frames], dtype=np.float64
        ),
        f"{prefix}_active": np.asarray(
            [bool(frame.active_parameter_blocks) for frame in trace.frames], dtype=np.bool_
        ),
        f"{prefix}_contact_pairs": np.asarray(flattened, dtype=np.int32).reshape(-1, 2),
        f"{prefix}_contact_offsets": np.asarray(offsets, dtype=np.int64),
    }


def write_endpoint_evidence(
    path: Path,
    factual: RolloutTrace,
    candidate: RolloutTrace,
    raw_images: dict[str, np.ndarray],
    live_static_arrays: dict[str, np.ndarray],
    factual_actions: np.ndarray,
    candidate_actions: np.ndarray,
    metadata: dict[str, Any],
) -> str:
    arrays: dict[str, np.ndarray] = {}
    arrays.update(trace_arrays("factual", factual))
    arrays.update(trace_arrays("candidate", candidate))
    expected_image_keys = {
        "factual_rgb", "factual_depth", "candidate_rgb", "candidate_depth",
        "factual_t0_rgb", "factual_t0_depth", "factual_t0_state", "factual_t0_proprio",
        "candidate_t0_rgb", "candidate_t0_depth", "candidate_t0_state", "candidate_t0_proprio",
    }
    if set(raw_images) != expected_image_keys:
        raise ValueError("raw image evidence schema mismatch")
    for prefix, trace in (("factual", factual), ("candidate", candidate)):
        rgb = np.asarray(raw_images[f"{prefix}_rgb"])
        depth = np.asarray(raw_images[f"{prefix}_depth"])
        if len(rgb) != len(trace.frames) or len(depth) != len(trace.frames):
            raise ValueError("raw image evidence length mismatch")
        for index, frame_value in enumerate(trace.frames):
            if array_digest_probe(rgb[index]) != frame_value.rgb_sha256:
                raise ValueError("RGB digest does not bind raw evidence")
            if array_digest_probe(depth[index]) != frame_value.depth_sha256:
                raise ValueError("depth digest does not bind raw evidence")
        arrays[f"{prefix}_rgb"] = np.ascontiguousarray(rgb)
        arrays[f"{prefix}_depth"] = np.ascontiguousarray(depth)
    for key in sorted(expected_image_keys - {
        "factual_rgb", "factual_depth", "candidate_rgb", "candidate_depth"
    }):
        arrays[key] = np.ascontiguousarray(raw_images[key])
    if factual.frames:
        if not np.array_equal(
            np.asarray(factual.frames[-1].state, dtype=np.float64),
            arrays["candidate_t0_state"],
        ):
            raise ValueError("candidate pre-action state is not factual endpoint")
        if not np.array_equal(
            np.asarray(factual.frames[-1].proprio, dtype=np.float64),
            arrays["candidate_t0_proprio"],
        ):
            raise ValueError("candidate pre-action proprio is not factual endpoint")
        if array_digest_probe(arrays["candidate_t0_rgb"]) != factual.frames[-1].rgb_sha256:
            raise ValueError("candidate pre-action RGB is not factual endpoint RGB")
        if array_digest_probe(arrays["candidate_t0_depth"]) != factual.frames[-1].depth_sha256:
            raise ValueError("candidate pre-action depth is not factual endpoint depth")
    arrays["factual_actions"] = np.asarray(factual_actions, dtype=np.float32)
    arrays["candidate_actions"] = np.asarray(candidate_actions, dtype=np.float32)
    static_names = sorted(live_static_arrays)
    arrays["static_field_names"] = np.asarray(static_names, dtype="U")
    for index, name in enumerate(static_names):
        arrays[f"static_field_{index:05d}"] = np.ascontiguousarray(
            live_static_arrays[name]
        )
    arrays["metadata_json"] = np.asarray(
        json.dumps(metadata, sort_keys=True, separators=(",", ":")), dtype="U"
    )
    np.savez_compressed(path, **arrays)
    return sha256_file(path)


def write_static_baseline_evidence(
    path: Path,
    arrays: dict[str, np.ndarray],
) -> str:
    names = sorted(arrays)
    payload: dict[str, np.ndarray] = {
        "schema_version": np.asarray(STATIC_PHYSICS_SCHEMA_VERSION, dtype="U"),
        "static_field_names": np.asarray(names, dtype="U"),
    }
    for index, name in enumerate(names):
        payload[f"static_field_{index:05d}"] = np.ascontiguousarray(arrays[name])
    np.savez_compressed(path, **payload)
    return sha256_file(path)


def frame(
    env: Any,
    obs: dict[str, Any],
    image: dict[str, np.ndarray],
    robot_vector: Any,
    initial_world: np.ndarray,
    initial_robot: np.ndarray,
    block_id: str,
    geom_ids: tuple[int, ...],
) -> FrameTrace:
    state = np.asarray(env.sim.get_state().flatten(), dtype=np.float64)
    proprio = np.asarray(robot_vector(obs), dtype=np.float64)
    world_effect = dynamic_nonrobot_vector(env) - initial_world
    robot_effect = proprio[:3] - initial_robot[:3]
    realized_contacts = tuple(sorted(contacts(env)))
    active = any(
        left in geom_ids or right in geom_ids
        for left, right in realized_contacts
    )
    return FrameTrace(
        state=tuple(float(value) for value in state),
        proprio=tuple(float(value) for value in proprio),
        rgb_sha256=array_digest_probe(image["rgb"]),
        depth_sha256=array_digest_probe(image["depth"]),
        physical_effect_probe=tuple(
            float(value) for value in np.concatenate((world_effect, robot_effect))
        ),
        task_effect=tuple(float(value) for value in world_effect),
        active_parameter_blocks=(block_id,) if active else (),
        contact_geom_pairs=realized_contacts,
    )


def continuous_rollout(
    env: Any,
    modes: Any,
    initialize_episode: Any,
    capture: Any,
    robot_vector: Any,
    original_solref: np.ndarray,
    original_friction: np.ndarray,
    factual_actions: np.ndarray,
    candidate_actions: np.ndarray,
    block_id: str,
    geom_ids: tuple[int, ...],
    value: float,
    family: str,
    values: Sequence[float],
    factual_action_id: str,
    candidate_action_id: str,
    height: int,
    width: int,
    step_counter: SimulatorStepCounter,
    baseline_static_arrays: dict[str, np.ndarray],
    unedited: bool = False,
) -> tuple[
    RolloutTrace,
    RolloutTrace,
    dict[str, np.ndarray],
    dict[str, Any],
    dict[str, np.ndarray],
]:
    """Return traces whose candidate segment directly follows factual replay."""

    env.sim.model.geom_solref[:] = original_solref
    env.sim.model.geom_friction[:] = original_friction
    env.sim.forward()
    obs = initialize_episode()
    indices = np.asarray(geom_ids, dtype=np.int64)
    if not unedited:
        if family == "compliance":
            env.sim.model.geom_solref[indices, 0] = float(value)
            env.sim.model.geom_solref[indices, 1] = 1.0
        else:
            env.sim.model.geom_friction[indices, 0] = float(value)
            env.sim.model.geom_friction[indices, 1] = float(value) * 0.05
            env.sim.model.geom_friction[indices, 2] = float(value) * 0.001
    env.sim.forward()
    live_static_arrays = capture_model_static_arrays(env.sim.model)
    static_diff = [] if unedited else validate_live_static_edit(
        baseline_static_arrays, live_static_arrays, geom_ids, family
    )
    live_static_sha256 = hash_static_arrays(live_static_arrays)
    expected_static_sha256 = (
        hash_static_arrays(baseline_static_arrays)
        if unedited
        else static_contact_config_hash(baseline_static_arrays, geom_ids, family, value)
    )
    if live_static_sha256 != expected_static_sha256:
        raise RuntimeError("live static physics hash differs from precomputed target edit")

    factual_t0_image = capture(env, modes, height, width)
    factual_t0_state = np.asarray(env.sim.get_state().flatten(), dtype=np.float64).copy()
    factual_t0_proprio = np.asarray(robot_vector(obs), dtype=np.float64).copy()

    factual_initial_world = dynamic_nonrobot_vector(env)
    factual_initial_robot = np.asarray(robot_vector(obs), dtype=np.float64)
    factual_frames: list[FrameTrace] = [
        frame(
            env, obs, factual_t0_image, robot_vector,
            factual_initial_world, factual_initial_robot,
            block_id, geom_ids,
        )
    ]
    factual_rgb: list[np.ndarray] = [np.asarray(factual_t0_image["rgb"]).copy()]
    factual_depth: list[np.ndarray] = [np.asarray(factual_t0_image["depth"]).copy()]
    for action in factual_actions:
        modes.trace()
        obs, _, _, _ = step_counter.step(env, np.asarray(action, dtype=np.float32))
        image = capture(env, modes, height, width)
        factual_rgb.append(np.asarray(image["rgb"]).copy())
        factual_depth.append(np.asarray(image["depth"]).copy())
        factual_frames.append(
            frame(
                env, obs, image, robot_vector,
                factual_initial_world, factual_initial_robot,
                block_id, geom_ids,
            )
        )

    candidate_initial_world = dynamic_nonrobot_vector(env)
    candidate_initial_robot = np.asarray(robot_vector(obs), dtype=np.float64)
    candidate_t0_image = capture(env, modes, height, width)
    candidate_t0_state = np.asarray(env.sim.get_state().flatten(), dtype=np.float64).copy()
    candidate_t0_proprio = np.asarray(robot_vector(obs), dtype=np.float64).copy()
    candidate_frames: list[FrameTrace] = [
        frame(
            env, obs, candidate_t0_image, robot_vector,
            candidate_initial_world, candidate_initial_robot,
            block_id, geom_ids,
        )
    ]
    candidate_rgb: list[np.ndarray] = [np.asarray(candidate_t0_image["rgb"]).copy()]
    candidate_depth: list[np.ndarray] = [np.asarray(candidate_t0_image["depth"]).copy()]
    for action in candidate_actions:
        modes.trace()
        obs, _, _, _ = step_counter.step(env, np.asarray(action, dtype=np.float32))
        image = capture(env, modes, height, width)
        candidate_rgb.append(np.asarray(image["rgb"]).copy())
        candidate_depth.append(np.asarray(image["depth"]).copy())
        candidate_frames.append(
            frame(
                env, obs, image, robot_vector,
                candidate_initial_world, candidate_initial_robot,
                block_id, geom_ids,
            )
        )

    token = str(value).replace(".", "p")
    world_id = f"{block_id}@{token}"
    physical_parameters = () if unedited else (
        parameter(block_id, geom_ids, value, family, values),
    )
    factual = RolloutTrace(
        world_id=world_id,
        action_id=factual_action_id,
        action_rank=1,
        frames=tuple(factual_frames),
        parameters=physical_parameters,
    )
    candidate = RolloutTrace(
        world_id=world_id,
        action_id=candidate_action_id,
        action_rank=1,
        frames=tuple(candidate_frames),
        parameters=physical_parameters,
    )
    raw_images = {
        "factual_rgb": np.stack(factual_rgb, axis=0),
        "factual_depth": np.stack(factual_depth, axis=0),
        "candidate_rgb": np.stack(candidate_rgb, axis=0),
        "candidate_depth": np.stack(candidate_depth, axis=0),
        "factual_t0_rgb": np.asarray(factual_t0_image["rgb"]).copy(),
        "factual_t0_depth": np.asarray(factual_t0_image["depth"]).copy(),
        "factual_t0_state": factual_t0_state,
        "factual_t0_proprio": factual_t0_proprio,
        "candidate_t0_rgb": np.asarray(candidate_t0_image["rgb"]).copy(),
        "candidate_t0_depth": np.asarray(candidate_t0_image["depth"]).copy(),
        "candidate_t0_state": candidate_t0_state,
        "candidate_t0_proprio": candidate_t0_proprio,
    }
    static_runtime = {
        "schema_version": STATIC_PHYSICS_SCHEMA_VERSION,
        "live_static_sha256": live_static_sha256,
        "expected_static_sha256": expected_static_sha256,
        "live_field_sha256": static_field_hashes(live_static_arrays),
        "structured_diff": static_diff,
    }
    return factual, candidate, raw_images, static_runtime, live_static_arrays


def capture_model_static_arrays(model: Any) -> dict[str, np.ndarray]:
    """Capture a versioned, replay-relevant MuJoCo static-physics schema."""

    arrays: dict[str, np.ndarray] = {}
    for name in sorted(dir(model)):
        if name.startswith("_"):
            continue
        try:
            value = getattr(model, name)
        except Exception:
            continue
        if isinstance(value, np.ndarray) and value.dtype.kind in "biufc":
            arrays[f"model.{name}"] = np.asarray(value).copy()
        elif isinstance(value, (bool, int, float, np.number)):
            arrays[f"model.{name}"] = np.asarray(value).copy()
    option = getattr(model, "opt", None)
    if option is not None:
        for name in sorted(dir(option)):
            if name.startswith("_"):
                continue
            try:
                value = getattr(option, name)
            except Exception:
                continue
            array = np.asarray(value)
            if array.dtype.kind in "biufc" and array.size <= 1024:
                arrays[f"model.opt.{name}"] = array.copy()
    if "model.geom_solref" not in arrays or "model.geom_friction" not in arrays:
        raise RuntimeError("static model array capture missed contact parameters")
    return arrays


def hash_static_arrays(arrays: dict[str, np.ndarray]) -> str:
    digest = hashlib.sha256()
    digest.update(STATIC_PHYSICS_SCHEMA_VERSION.encode("ascii"))
    for name, array in sorted(arrays.items()):
        contiguous = np.ascontiguousarray(array)
        digest.update(name.encode("utf-8"))
        digest.update(str(contiguous.dtype).encode("ascii"))
        digest.update(str(tuple(contiguous.shape)).encode("ascii"))
        digest.update(contiguous.tobytes())
    return digest.hexdigest()


def static_field_hashes(arrays: dict[str, np.ndarray]) -> dict[str, str]:
    return {
        name: canonical_array_sha256(np.asarray(array))
        for name, array in sorted(arrays.items())
    }


def validate_live_static_edit(
    baseline: dict[str, np.ndarray],
    live: dict[str, np.ndarray],
    geom_ids: tuple[int, ...],
    family: str,
) -> list[dict[str, Any]]:
    if set(baseline) != set(live):
        raise RuntimeError("live static physics schema changed")
    target_name = "model.geom_solref" if family == "compliance" else "model.geom_friction"
    columns = (0, 1) if family == "compliance" else (0, 1, 2)
    allowed = {(int(geom_id), int(column)) for geom_id in geom_ids for column in columns}
    differences: list[dict[str, Any]] = []
    for name in sorted(baseline):
        left = np.asarray(baseline[name])
        right = np.asarray(live[name])
        if left.shape != right.shape or left.dtype != right.dtype:
            raise RuntimeError(f"static field schema changed: {name}")
        unequal = np.argwhere(left != right)
        if unequal.size and name != target_name:
            raise RuntimeError(f"non-target static field changed: {name}")
        for index_array in unequal:
            index = tuple(int(value) for value in index_array)
            if index not in allowed:
                raise RuntimeError(f"non-target static address changed: {name}{index}")
            differences.append({
                "field": name,
                "index": list(index),
                "before": float(left[index]),
                "after": float(right[index]),
            })
    return differences


def static_contact_config_hash(
    static_model_arrays: dict[str, np.ndarray],
    geom_ids: tuple[int, ...],
    family: str,
    value: float,
) -> str:
    """Hash all exposed numeric MjModel arrays after one contact edit."""

    arrays = {name: np.asarray(array).copy() for name, array in static_model_arrays.items()}
    solref = np.asarray(arrays["model.geom_solref"]).copy()
    friction = np.asarray(arrays["model.geom_friction"]).copy()
    indices = np.asarray(geom_ids, dtype=np.int64)
    if family == "compliance":
        solref[indices, 0] = float(value)
        solref[indices, 1] = 1.0
    else:
        friction[indices, 0] = float(value)
        friction[indices, 1] = float(value) * 0.05
        friction[indices, 2] = float(value) * 0.001
    arrays["model.geom_solref"] = solref
    arrays["model.geom_friction"] = friction
    return hash_static_arrays(arrays)


def contact_topology_schema_hash(
    static_model_arrays: dict[str, np.ndarray],
    topology: list[dict[str, Any]],
) -> str:
    """Hash the static model and selector-visible geom/body topology."""

    digest = hashlib.sha256()
    digest.update(STATIC_PHYSICS_SCHEMA_VERSION.encode("ascii"))
    digest.update(hash_static_arrays(static_model_arrays).encode("ascii"))
    digest.update(
        json.dumps(
            topology, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    )
    return digest.hexdigest()


def model_contact_schema_hash(model: Any, static_model_arrays: dict[str, np.ndarray]) -> str:
    """Hash the structural contact-parameter schema used by the compiler."""

    return contact_topology_schema_hash(static_model_arrays, contact_topology(model))


def assert_no_audit_payload_fields(value: Any) -> None:
    """Reject target-model payload fields while allowing provenance booleans."""

    forbidden_keys = {
        "wam_residual",
        "wam_embedding",
        "wam_ranking",
        "wam_id",
        "posthoc_wam_scores",
    }
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).casefold() in forbidden_keys:
                raise RuntimeError(f"target-model audit field leaked into compiler manifest: {key}")
            assert_no_audit_payload_fields(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            assert_no_audit_payload_fields(item)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rollout", required=True)
    parser.add_argument(
        "--source-admission-report",
        help="Required for P026; binds independently replayed success and policy lock",
    )
    parser.add_argument(
        "--compiler-lock",
        help="Required for P026; immutable hash manifest for compiler and verifier code",
    )
    parser.add_argument(
        "--matrix-run-lock",
        help="Required for P026; freezes this cell's unique output path before execution",
    )
    parser.add_argument("--support-code", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--candidate-index", type=int, required=True)
    parser.add_argument("--candidate-chunks", type=int, default=4)
    parser.add_argument("--family", choices=sorted(FAMILY_VALUES), default="compliance")
    parser.add_argument("--block-selector", choices=BLOCK_SELECTORS, required=True)
    parser.add_argument("--selector-seed", type=int, default=0)
    parser.add_argument("--max-selected-blocks", type=int, default=3)
    parser.add_argument("--height", type=int, default=64)
    parser.add_argument("--width", type=int, default=64)
    args = parser.parse_args()
    if args.candidate_chunks < 1 or args.max_selected_blocks < 1:
        raise ValueError("candidate-chunks and max-selected-blocks must be positive")

    rollout_path = existing(args.rollout)
    protocol_version = "P026-v1" if args.source_admission_report else "P025-v5"
    source_admission_path = (
        existing(args.source_admission_report) if args.source_admission_report else None
    )
    compiler_lock_path = existing(args.compiler_lock) if args.compiler_lock else None
    matrix_run_lock_path = existing(args.matrix_run_lock) if args.matrix_run_lock else None
    if protocol_version == "P026-v1" and compiler_lock_path is None:
        raise ValueError("P026 requires a frozen compiler lock")
    if protocol_version == "P026-v1" and matrix_run_lock_path is None:
        raise ValueError("P026 requires a frozen matrix-run lock")
    if protocol_version != "P026-v1" and compiler_lock_path is not None:
        raise ValueError("compiler lock is only defined for P026")
    if protocol_version != "P026-v1" and matrix_run_lock_path is not None:
        raise ValueError("matrix-run lock is only defined for P026")
    support = existing(args.support_code)
    output = new_output(args.output)
    evidence_dir = output.with_suffix(output.suffix + ".evidence")
    evidence_temp = output.with_suffix(output.suffix + f".evidence.tmp.{os.getpid()}")
    if evidence_dir.exists() or evidence_temp.exists():
        raise ValueError(f"evidence path already exists: {evidence_dir}")
    manifest = json.loads(rollout_path.read_text(encoding="utf-8"))
    arrays_path = existing(manifest["arrays"])
    arrays = np.load(arrays_path)
    source_admission_reference: dict[str, str] | None = None
    compiler_lock_reference: dict[str, str] | None = None
    compiler_lock: dict[str, Any] | None = None
    matrix_run_lock_reference: dict[str, str] | None = None
    matrix_run_lock: dict[str, Any] | None = None
    if source_admission_path is not None:
        admission = json.loads(source_admission_path.read_text(encoding="utf-8"))
        if (
            admission.get("kind") != "israc_source_admission_replay_v1"
            or admission.get("passed") is not True
            or admission.get("policy_identity_verified") is not True
            or admission.get("policy_lock_verified") is not True
        ):
            raise ValueError("P026 source admission did not pass identity/lock replay")
        if manifest.get("source_schema_version") != "P026-source-v1":
            raise ValueError("P026 requires a provenance-bearing source")
        if admission.get("source_rollout_sha256") != sha256_file(rollout_path):
            raise ValueError("source admission is bound to another rollout")
        if admission.get("source_arrays_sha256") != sha256_file(arrays_path):
            raise ValueError("source admission is bound to another array archive")
        source_admission_reference = {
            "path": str(source_admission_path),
            "sha256": sha256_file(source_admission_path),
        }
    if compiler_lock_path is not None:
        compiler_lock = json.loads(compiler_lock_path.read_text(encoding="utf-8"))
        if (
            compiler_lock.get("kind") != "p026_compiler_code_lock"
            or compiler_lock.get("frozen") is not True
        ):
            raise ValueError("P026 compiler lock is invalid")
        locked_files = compiler_lock.get("files")
        if not isinstance(locked_files, list) or not locked_files:
            raise ValueError("P026 compiler lock has no code files")
        for reference in locked_files:
            path = existing(reference["path"])
            if sha256_file(path) != str(reference["sha256"]):
                raise ValueError(f"P026 compiler code drift: {path}")
        compiler_lock_reference = {
            "path": str(compiler_lock_path),
            "sha256": sha256_file(compiler_lock_path),
        }
    if matrix_run_lock_path is not None:
        matrix_run_lock = json.loads(matrix_run_lock_path.read_text(encoding="utf-8"))
        if (
            matrix_run_lock.get("kind") != "p026_matrix_run_lock"
            or matrix_run_lock.get("frozen") is not True
            or matrix_run_lock.get("compiler_lock") != compiler_lock_reference
            or compiler_lock is None
            or matrix_run_lock.get("boundary_plan") != compiler_lock.get("boundary_plan")
        ):
            raise ValueError("P026 matrix-run lock is invalid or bound to another compiler")
        matrix_run_lock_reference = {
            "path": str(matrix_run_lock_path),
            "sha256": sha256_file(matrix_run_lock_path),
        }
    states = np.asarray(arrays["boundary_states"], dtype=np.float64)
    chunks = np.asarray(arrays["action_chunks"], dtype=np.float32)
    index = args.candidate_index
    if not 1 <= index < min(len(states), len(chunks)):
        raise IndexError(index)

    sys.path.insert(0, str(support))
    from collect_e1_paired_rollouts import ObservableModes, capture, robot_vector
    from libero.libero.envs import SegmentationRenderEnv

    evidence_temp.mkdir(parents=False)
    env = SegmentationRenderEnv(
        bddl_file_name=str(existing(manifest["bddl"])),
        camera_heights=args.height,
        camera_widths=args.width,
        camera_depths=True,
        camera_segmentations="instance",
    )
    accepted: list[dict[str, Any]] = []
    block_rows: list[dict[str, Any]] = []
    try:
        env.seed(int(manifest["seed"]))
        env.reset()
        initialization = manifest.get("initialization", {})
        if initialization.get("source") != "libero_benchmark_initial_state":
            raise RuntimeError(
                "P025-v5 fails closed unless the source rollout names a LIBERO "
                "benchmark initial state; direct-BDDL/intermediate-state restore is forbidden"
            )
        from libero.libero import benchmark

        suite = benchmark.get_benchmark_dict()[str(initialization["suite_name"])]()
        initial_states = suite.get_task_init_states(int(initialization["task_id"]))
        episode_index = int(initialization["episode_index"])
        if not 0 <= episode_index < len(initial_states):
            raise IndexError("rollout benchmark episode index is invalid")
        benchmark_initial_state = np.asarray(
            initial_states[episode_index], dtype=np.float64
        ).copy()
        env.set_init_state(benchmark_initial_state)
        episode_start_state = np.asarray(
            env.sim.get_state().flatten(), dtype=np.float64
        ).copy()
        modes = ObservableModes(env.env)
        def initialize_episode() -> dict[str, np.ndarray]:
            modes.capture()
            env.seed(int(manifest["seed"]))
            env.reset()
            return env.set_init_state(benchmark_initial_state)

        original_solref = np.asarray(env.sim.model.geom_solref, dtype=np.float64).copy()
        original_friction = np.asarray(env.sim.model.geom_friction, dtype=np.float64).copy()
        static_model_arrays = capture_model_static_arrays(env.sim.model)
        baseline_static_field_sha256 = static_field_hashes(static_model_arrays)
        baseline_static_sha256 = hash_static_arrays(static_model_arrays)
        baseline_static_name = "baseline_static_physics.npz"
        baseline_static_evidence_sha256 = write_static_baseline_evidence(
            evidence_temp / baseline_static_name, static_model_arrays
        )
        baseline_static_evidence = {
            "path": str(evidence_dir / baseline_static_name),
            "sha256": baseline_static_evidence_sha256,
        }
        step_counter = SimulatorStepCounter()
        contact_topology_rows = contact_topology(env.sim.model)
        simulator_model_sha256 = contact_topology_schema_hash(
            static_model_arrays, contact_topology_rows
        )
        bddl_sha256 = sha256_file(existing(manifest["bddl"]))
        try:
            import mujoco_py
            mujoco_version = str(getattr(mujoco_py, "__version__", "unknown"))
        except Exception:
            mujoco_version = "unknown"
        try:
            import robosuite
            robosuite_version = str(getattr(robosuite, "__version__", "unknown"))
        except Exception:
            robosuite_version = "unknown"
        engine_identity = (
            f"mujoco_py={mujoco_version};robosuite={robosuite_version};"
            f"protocol={protocol_version}"
        )
        values = FAMILY_VALUES[args.family]
        # Rebuild both the benchmark warmup and every policy chunk.  P025-v3
        # started at boundary_states[0], which is already after warmup and thus
        # still omitted ten low-level controller transitions.
        start_state = episode_start_state
        wait_steps = int(manifest.get("num_steps_wait", 0))
        wait_action = np.asarray([0.0] * 6 + [-1.0], dtype=np.float32)
        warmup_actions = np.repeat(wait_action[None, :], wait_steps, axis=0)
        factual_actions = np.concatenate((warmup_actions, *chunks[:index]), axis=0)
        suffix_end = min(index + args.candidate_chunks, len(chunks))
        candidate_actions = np.concatenate(chunks[index:suffix_end], axis=0)
        arrays_sha256 = sha256_file(arrays_path)
        snapshot_sha256 = canonical_array_sha256(start_state)
        factual_action_sha256 = canonical_array_sha256(factual_actions)
        candidate_hash = canonical_array_sha256(candidate_actions)
        rollout_hash = hashlib.sha256(rollout_path.read_bytes()).hexdigest()
        factual_action_id = f"warmup_{wait_steps}_policy_prefix_0_to_{index - 1}"
        candidate_action_id = f"policy_suffix_{index}_to_{suffix_end - 1}"
        if matrix_run_lock is not None:
            matching_jobs = [
                row for row in matrix_run_lock.get("jobs", [])
                if str(Path(str(row.get("output"))).resolve()) == str(output.resolve())
                and str(row.get("source_rollout_sha256")) == rollout_hash
                and int(row.get("candidate_index", -1)) == index
                and row.get("selector") == args.block_selector
                and int(row.get("selector_seed", -1)) == args.selector_seed
            ]
            if len(matching_jobs) != 1:
                raise ValueError("P026 invocation is absent or duplicated in matrix-run lock")
            locked_job = matching_jobs[0]
            if (
                str(Path(str(locked_job["source_admission"])).resolve())
                != str(source_admission_path.resolve())
                or locked_job.get("source_admission_sha256")
                != source_admission_reference["sha256"]
            ):
                raise ValueError("P026 invocation admission differs from matrix-run lock")

        nominal_unedited_evidence: dict[str, str] | None = None
        nominal_unedited_repeat_evidence: dict[str, str] | None = None
        nominal_factual: RolloutTrace | None = None
        nominal_factual_repeat: RolloutTrace | None = None
        if protocol_version == "P026-v1":
            (
                nominal_factual,
                nominal_candidate,
                nominal_raw,
                nominal_static_runtime,
                nominal_static_arrays,
            ) = continuous_rollout(
                env, modes, initialize_episode, capture, robot_vector,
                original_solref, original_friction,
                factual_actions, candidate_actions, "nominal_unedited", (),
                0.0, args.family, values, factual_action_id,
                candidate_action_id, args.height, args.width,
                step_counter, static_model_arrays, unedited=True,
            )
            (
                nominal_factual_repeat,
                nominal_candidate_repeat,
                nominal_raw_repeat,
                nominal_static_runtime_repeat,
                nominal_static_arrays_repeat,
            ) = continuous_rollout(
                env, modes, initialize_episode, capture, robot_vector,
                original_solref, original_friction,
                factual_actions, candidate_actions, "nominal_unedited", (),
                0.0, args.family, values, factual_action_id,
                candidate_action_id, args.height, args.width,
                step_counter, static_model_arrays, unedited=True,
            )
            nominal_metadata = {
                "kind": "nominal_unedited_evidence",
                "block_id": "nominal_unedited",
                "geom_ids": [],
                "parameter_family": args.family,
                "parameter_value": 0.0,
                "source_rollout_sha256": rollout_hash,
                "arrays_sha256": arrays_sha256,
                "snapshot_sha256": snapshot_sha256,
                "factual_action_sha256": factual_action_sha256,
                "candidate_action_sha256": candidate_hash,
                "simulator_model_sha256": simulator_model_sha256,
                "bddl_sha256": bddl_sha256,
                "engine_identity": engine_identity,
                "static_runtime": nominal_static_runtime,
            }
            nominal_name = "nominal_unedited.npz"
            nominal_sha256 = write_endpoint_evidence(
                evidence_temp / nominal_name,
                nominal_factual,
                nominal_candidate,
                nominal_raw,
                nominal_static_arrays,
                factual_actions,
                candidate_actions,
                nominal_metadata,
            )
            nominal_unedited_evidence = {
                "path": str(evidence_dir / nominal_name),
                "sha256": nominal_sha256,
            }
            nominal_repeat_metadata = {
                **nominal_metadata,
                "kind": "nominal_unedited_repeat_evidence",
                "static_runtime": nominal_static_runtime_repeat,
            }
            nominal_repeat_name = "nominal_unedited_repeat.npz"
            nominal_repeat_sha256 = write_endpoint_evidence(
                evidence_temp / nominal_repeat_name,
                nominal_factual_repeat,
                nominal_candidate_repeat,
                nominal_raw_repeat,
                nominal_static_arrays_repeat,
                factual_actions,
                candidate_actions,
                nominal_repeat_metadata,
            )
            nominal_unedited_repeat_evidence = {
                "path": str(evidence_dir / nominal_repeat_name),
                "sha256": nominal_repeat_sha256,
            }
            factual_pairs = trace_contact_union(nominal_factual)
            candidate_pairs = trace_contact_union(nominal_candidate)
            factual_pairs_repeat = trace_contact_union(nominal_factual_repeat)
            candidate_pairs_repeat = trace_contact_union(nominal_candidate_repeat)
            nominal_factual_endpoint = np.asarray(
                nominal_factual.frames[-1].state, dtype=np.float64
            )
            nominal_factual_endpoint_repeat = np.asarray(
                nominal_factual_repeat.frames[-1].state, dtype=np.float64
            )
        else:
            factual_pairs, candidate_pairs, nominal_factual_endpoint = execute_nominal_contacts(
                env, modes, initialize_episode, factual_actions, candidate_actions, step_counter,
            )
            factual_pairs_repeat, candidate_pairs_repeat, nominal_factual_endpoint_repeat = (
                execute_nominal_contacts(
                    env, modes, initialize_episode, factual_actions, candidate_actions, step_counter
                )
            )

        replay_endpoint_error: float | None = float(
            np.max(np.abs(nominal_factual_endpoint - states[index]))
        ) if nominal_factual_endpoint.shape == states[index].shape else None
        nominal_endpoint_repeat_error: float | None = float(
            np.max(np.abs(nominal_factual_endpoint - nominal_factual_endpoint_repeat))
        ) if nominal_factual_endpoint.shape == nominal_factual_endpoint_repeat.shape else None
        boundary_eligible, invalid_boundary_reasons, endpoint_tolerance = boundary_eligibility(
            replay_endpoint_error,
            nominal_endpoint_repeat_error,
            factual_pairs,
            factual_pairs_repeat,
            candidate_pairs,
            candidate_pairs_repeat,
        )

        factual_pool = geom_blocks(env.sim.model, factual_pairs) if boundary_eligible else {}
        candidate_pool = geom_blocks(env.sim.model, candidate_pairs) if boundary_eligible else {}
        if not boundary_eligible:
            pool = {}
        elif args.block_selector == "israc-contact-subtraction":
            pool = subtract_blocks(candidate_pool, factual_pool)
        elif args.block_selector == "candidate-contact":
            pool = candidate_pool
        else:
            pool = geom_blocks(env.sim.model)
        selected = select_blocks(
            pool,
            selector=args.block_selector,
            max_blocks=args.max_selected_blocks,
            seed=int(manifest["seed"]) + args.selector_seed,
        ) if boundary_eligible else []

        for address, geom_ids in selected:
            block_id = f"{args.block_selector}_{args.family}:{address}"
            factual: dict[float, RolloutTrace] = {}
            candidate: dict[float, RolloutTrace] = {}
            raw_images: dict[float, dict[str, np.ndarray]] = {}
            static_runtime: dict[float, dict[str, Any]] = {}
            live_static_arrays: dict[float, dict[str, np.ndarray]] = {}
            for value in values:
                (
                    factual[value], candidate[value], raw_images[value], static_runtime[value],
                    live_static_arrays[value],
                ) = continuous_rollout(
                    env, modes, initialize_episode, capture, robot_vector,
                    original_solref, original_friction,
                    factual_actions, candidate_actions, block_id, geom_ids,
                    value, args.family, values, factual_action_id,
                    candidate_action_id, args.height, args.width,
                    step_counter, static_model_arrays,
                )
            (
                factual_repeat, candidate_repeat, raw_images_repeat, static_runtime_repeat,
                live_static_arrays_repeat,
            ) = continuous_rollout(
                env, modes, initialize_episode, capture, robot_vector,
                original_solref, original_friction,
                factual_actions, candidate_actions, block_id, geom_ids,
                values[0], args.family, values, factual_action_id,
                candidate_action_id, args.height, args.width,
                step_counter, static_model_arrays,
            )
            factual_envelope = repeat_envelope((factual[values[0]], factual_repeat))
            candidate_envelope = repeat_envelope((candidate[values[0]], candidate_repeat))
            factual_observation_repeat_stable = trace_observation_digest_equal(
                factual[values[0]], factual_repeat
            )
            evidence_by_value: dict[float, dict[str, str]] = {}
            for value in values:
                token = str(value).replace(".", "p")
                evidence_name = (
                    f"b{int(arrays['boundary_steps'][index])}_g{geom_ids[0]}_"
                    f"{args.family}_{token}.npz"
                )
                evidence_path = evidence_temp / evidence_name
                evidence_sha256 = write_endpoint_evidence(
                    evidence_path,
                    factual[value],
                    candidate[value],
                    raw_images[value],
                    live_static_arrays[value],
                    factual_actions,
                    candidate_actions,
                    {
                        "block_id": block_id,
                        "geom_ids": list(geom_ids),
                        "parameter_family": args.family,
                        "parameter_value": value,
                        "source_rollout_sha256": rollout_hash,
                        "arrays_sha256": arrays_sha256,
                        "snapshot_sha256": snapshot_sha256,
                        "factual_action_sha256": factual_action_sha256,
                        "candidate_action_sha256": candidate_hash,
                        "simulator_model_sha256": simulator_model_sha256,
                        "bddl_sha256": bddl_sha256,
                        "engine_identity": engine_identity,
                        "static_runtime": static_runtime[value],
                    },
                )
                evidence_by_value[value] = {
                    "path": str(evidence_dir / evidence_name),
                    "sha256": evidence_sha256,
                }
            repeat_evidence_name = (
                f"b{int(arrays['boundary_steps'][index])}_g{geom_ids[0]}_"
                f"{args.family}_repeat_{str(values[0]).replace('.', 'p')}.npz"
            )
            repeat_evidence_path = evidence_temp / repeat_evidence_name
            repeat_evidence_sha256 = write_endpoint_evidence(
                repeat_evidence_path,
                factual_repeat,
                candidate_repeat,
                raw_images_repeat,
                live_static_arrays_repeat,
                factual_actions,
                candidate_actions,
                {
                    "kind": "repeat_evidence",
                    "block_id": block_id,
                    "geom_ids": list(geom_ids),
                    "parameter_family": args.family,
                    "parameter_value": values[0],
                    "source_rollout_sha256": rollout_hash,
                    "arrays_sha256": arrays_sha256,
                    "snapshot_sha256": snapshot_sha256,
                    "factual_action_sha256": factual_action_sha256,
                    "candidate_action_sha256": candidate_hash,
                    "simulator_model_sha256": simulator_model_sha256,
                    "bddl_sha256": bddl_sha256,
                    "engine_identity": engine_identity,
                    "static_runtime": static_runtime_repeat,
                },
            )
            repeat_evidence = {
                "path": str(evidence_dir / repeat_evidence_name),
                "sha256": repeat_evidence_sha256,
            }
            attempts = 0
            passes: list[dict[str, Any]] = []
            failures: dict[str, int] = {}
            for left_pos, left_value in enumerate(values):
                for right_value in values[left_pos + 1:]:
                    attempts += 1
                    certificate = AliasCertificate(
                        factual_action_id=factual_action_id,
                        candidate_action_id=candidate_action_id,
                        top_k=1,
                        search_objective_terms=(
                            f"block_selector:{args.block_selector}",
                            "realized_contact_support",
                            "fixed_endpoint_sweep",
                            "factual_transcript_constraint",
                            "candidate_physical_effect_separation",
                        ),
                        compiler_seed=int(manifest["seed"]) + args.selector_seed,
                        simulator="LIBERO-MuJoCo",
                        task_id=str(manifest["task"]),
                        snapshot_id=snapshot_sha256,
                        allowed_activation_lag=1,
                        factual_action_sha256=factual_action_sha256,
                        candidate_action_sha256=candidate_hash,
                        evidence_sha256=(
                            evidence_by_value[left_value]["sha256"],
                            evidence_by_value[right_value]["sha256"],
                            repeat_evidence_sha256,
                            *(
                                (
                                    nominal_unedited_evidence["sha256"],
                                    nominal_unedited_repeat_evidence["sha256"],
                                )
                                if protocol_version == "P026-v1" else ()
                            ),
                        ),
                        static_config_sha256=(
                            static_runtime[left_value]["live_static_sha256"],
                            static_runtime[right_value]["live_static_sha256"],
                        ),
                        simulator_model_sha256=simulator_model_sha256,
                        task_asset_sha256=bddl_sha256,
                        engine_identity=engine_identity,
                        parameter_addresses=(
                            str(parameter(
                                block_id, geom_ids, left_value, args.family, values
                            ).engine_field),
                        ),
                        factual_observation_repeat_stable=factual_observation_repeat_stable,
                    )
                    result = certify_alias_pair(
                        factual[left_value], factual[right_value],
                        candidate[left_value], candidate[right_value],
                        certificate, factual_envelope, candidate_envelope,
                    )
                    source_factual_match = True
                    if protocol_version == "P026-v1":
                        if nominal_factual is None or nominal_factual_repeat is None:
                            raise RuntimeError("P026 nominal factual traces are missing")
                        source_factual_match = (
                            trace_matches_unedited_reference(
                                factual[left_value], nominal_factual, nominal_factual_repeat
                            )
                            and trace_matches_unedited_reference(
                                factual[right_value], nominal_factual, nominal_factual_repeat
                            )
                        )
                    if result.passed and source_factual_match:
                        passes.append({
                            "left_value": left_value,
                            "right_value": right_value,
                            "left_static_contact_config_sha256": static_contact_config_hash(
                                static_model_arrays, geom_ids, args.family, left_value
                            ),
                            "right_static_contact_config_sha256": static_contact_config_hash(
                                static_model_arrays,
                                geom_ids, args.family, right_value
                            ),
                            "measurements": dict(result.measurements),
                            "certificate_sha256": result.certificate_sha256,
                            "certificate_payload": json.loads(result.canonical_payload),
                            "left_evidence": evidence_by_value[left_value],
                            "right_evidence": evidence_by_value[right_value],
                        })
                    else:
                        for failure in result.failures:
                            failures[failure] = failures.get(failure, 0) + 1
                        if not source_factual_match:
                            key = "factual_deviates_from_unedited_nominal"
                            failures[key] = failures.get(key, 0) + 1
            witness_key_payload = {
                "source_trajectory_sha256": rollout_hash,
                "arrays_sha256": arrays_sha256,
                "snapshot_sha256": snapshot_sha256,
                "factual_action_sha256": factual_action_sha256,
                "boundary_step": int(arrays["boundary_steps"][index]),
                "candidate_sha256": candidate_hash,
                "geom_ids": list(geom_ids),
                "parameter_family": args.family,
            }
            witness_key = hashlib.sha256(
                json.dumps(
                    witness_key_payload, sort_keys=True, separators=(",", ":")
                ).encode("utf-8")
            ).hexdigest()
            row = {
                "parameter_address": address,
                "geom_ids": list(geom_ids),
                "parameter_metadata": asdict(
                    parameter(block_id, geom_ids, values[0], args.family, values)
                ),
                "static_diff_schema": {
                    "array": "model.geom_solref" if args.family == "compliance" else "model.geom_friction",
                    "geom_ids": list(geom_ids),
                    "columns": [0, 1] if args.family == "compliance" else [0, 1, 2],
                    "legal_endpoints": list(values),
                    "all_other_exposed_numeric_model_arrays_must_hash_equal": True,
                },
                "witness_key": witness_key,
                "witness_key_fields": witness_key_payload,
                "attempted_endpoint_pairs": attempts,
                "certified_endpoint_pairs": len(passes),
                "unique_witness": int(bool(passes)),
                "endpoint_strength_curve": passes,
                "endpoint_evidence": {
                    str(value): evidence_by_value[value] for value in values
                },
                "repeat_evidence": repeat_evidence,
                "failure_reason_counts": dict(sorted(failures.items())),
                "factual_repeat_noise_envelope": asdict(factual_envelope),
                "candidate_repeat_noise_envelope": asdict(candidate_envelope),
                "factual_observation_repeat_stable": factual_observation_repeat_stable,
            }
            block_rows.append(row)
            if passes:
                accepted.append(row)
    finally:
        env.close()

    accounting = fixed_budget_accounting(
        factual_steps=len(factual_actions),
        candidate_steps=len(candidate_actions),
        selected_blocks=len(selected),
        max_blocks=args.max_selected_blocks,
        boundary_eligible=boundary_eligible,
        measured_actual_steps=step_counter.count,
        charge_invalid=(protocol_version == "P026-v1"),
    )
    payload = {
        "kind": "israc_continuous_geom_contact_support_e0",
        "protocol_version": protocol_version,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "claim_limit": (
            "Confirmatory compiler evidence only. Sources and boundaries are preregistered, "
            "policy identity is locked, every selected boundary retains two raw unedited-world "
            "rollouts, and invalid boundaries remain charged zero-yield observations. No WAM "
            "audit, second physical mechanism, or second simulator is included."
            if protocol_version == "P026-v1" else
            "Protocol-debug evidence only. The fixed budget and continuous replay close two "
            "P024 confounds, but these boundaries were already inspected and no strong optimizer, "
            "second mechanism, second simulator, or WAM audit is included."
        ),
        "passed": bool(accepted),
        "boundary_eligible": boundary_eligible,
        "invalid_boundary_reasons": invalid_boundary_reasons,
        "compiler_target_wam_blind": True,
        "rollout": str(rollout_path),
        "rollout_sha256": hashlib.sha256(rollout_path.read_bytes()).hexdigest(),
        "arrays_sha256": arrays_sha256,
        "source_admission_report": source_admission_reference,
        "compiler_lock": compiler_lock_reference,
        "matrix_run_lock": matrix_run_lock_reference,
        "artifact_output_path": str(output.resolve()),
        "simulator_model_contact_schema_sha256": simulator_model_sha256,
        "contact_topology": contact_topology_rows,
        "static_physics_schema_version": STATIC_PHYSICS_SCHEMA_VERSION,
        "baseline_static_physics_sha256": baseline_static_sha256,
        "baseline_static_field_sha256": baseline_static_field_sha256,
        "baseline_static_evidence": baseline_static_evidence,
        "nominal_unedited_evidence": nominal_unedited_evidence,
        "nominal_unedited_repeat_evidence": nominal_unedited_repeat_evidence,
        "task_asset_bddl_sha256": bddl_sha256,
        "engine_identity": engine_identity,
        "environment_seed": int(manifest["seed"]),
        "snapshot_sha256": snapshot_sha256,
        "factual_action_sha256": factual_action_sha256,
        "factual_action_id": factual_action_id,
        "candidate_action_id": candidate_action_id,
        "factual_prefix_start_chunk_index": 0,
        "factual_prefix_end_chunk_index": index - 1,
        "warmup_action_steps": wait_steps,
        "candidate_chunk_index": index,
        "candidate_suffix_end_index": suffix_end - 1,
        "factual_action_steps": len(factual_actions),
        "candidate_action_steps": len(candidate_actions),
        "candidate_sha256": candidate_hash,
        "candidate_boundary_step": int(arrays["boundary_steps"][index]),
        "block_selector": args.block_selector,
        "selector_seed": args.selector_seed,
        "selector_visible_pool_count": len(pool),
        "selected_block_count": len(selected),
        "max_selected_blocks": args.max_selected_blocks,
        **accounting,
        "continuous_executions_per_selected_block": CONTINUOUS_EXECUTIONS_PER_BLOCK,
        "nominal_continuous_executions": NOMINAL_CONTINUOUS_EXECUTIONS,
        "continuous_factual_to_candidate": True,
        "controller_reset_mode": "fresh_seeded_reset_set_benchmark_init_then_replay_warmup_full_prefix_candidate",
        "replay_endpoint_vs_saved_boundary_max_abs": replay_endpoint_error,
        "nominal_endpoint_repeat_max_abs": nominal_endpoint_repeat_error,
        "replay_endpoint_tolerance": endpoint_tolerance,
        "endpoint_repeat_absolute_cap": ENDPOINT_REPEAT_ABSOLUTE_CAP,
        "saved_endpoint_absolute_cap": SAVED_ENDPOINT_ABSOLUTE_CAP,
        "dynamic_state_schema": {
            "mujoco_flat_state_dim": int(start_state.size),
            "fields": "MjSimState.flatten plus full proprio; full RGB/depth arrays represented by SHA-256 digests; movable nonrobot body poses are task-effect evidence",
            "unobserved": "solver warm-start/contact cache and external controller caches not exposed by saved trajectory",
        },
        "primary_witness_key": (
            "source trajectory hash + boundary step + candidate hash + geom id + parameter family"
        ),
        "raw_endpoint_pair_count": sum(
            int(row["certified_endpoint_pairs"]) for row in block_rows
        ),
        "unique_witness_count": len(accepted),
        "blocks": block_rows,
        "arguments": vars(args),
    }
    assert_no_audit_payload_fields(payload)
    serialized = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(serialized, encoding="utf-8")
    os.replace(evidence_temp, evidence_dir)
    os.replace(temporary, output)
    print(json.dumps({
        "passed": payload["passed"],
        "unique_witness_count": payload["unique_witness_count"],
        "raw_endpoint_pair_count": payload["raw_endpoint_pair_count"],
        "charged_simulator_step_cap": accounting["charged_simulator_step_cap"],
        "endpoint_replay_error": replay_endpoint_error,
    }, sort_keys=True))
    raise SystemExit(0)


if __name__ == "__main__":
    main()
