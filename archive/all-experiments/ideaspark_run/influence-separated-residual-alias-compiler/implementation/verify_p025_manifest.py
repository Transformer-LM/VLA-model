#!/usr/bin/env python3
"""Independently replay P025 certificates from immutable NPZ evidence.

The certificate path does not execute MuJoCo.  It checks every file hash,
recomputes image digests from stored raw frames, reconstructs the four rollout
traces, reruns the target-WAM-blind certifier, and requires the exact canonical
certificate hash to match the manifest.  It additionally authenticates the
natural-success source rollout and binds the action prefix/suffix and initial
state to that source and to the named LIBERO benchmark episode.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from certify_continuous_contact_support import (
    FAMILY_VALUES,
    STATIC_PHYSICS_SCHEMA_VERSION,
    array_digest_probe,
    boundary_eligibility,
    canonical_array_sha256,
    contact_topology_schema_hash,
    geom_blocks,
    hash_static_arrays,
    parameter,
    select_blocks,
    static_contact_config_hash,
    static_field_hashes,
    subtract_blocks,
    trace_observation_digest_equal,
    validate_live_static_edit,
)
from israc.certificate import (
    AliasCertificate,
    FrameTrace,
    NoiseEnvelope,
    PhysicalParameter,
    RolloutTrace,
    certify_alias_pair,
)
from libero_m0_alias import repeat_envelope


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: str) -> dict[str, Any]:
    def reject(value: str) -> None:
        raise ValueError(f"non-finite JSON constant: {value}")

    with open(path, "r", encoding="utf-8") as handle:
        value = json.load(handle, parse_constant=reject)
    if not isinstance(value, dict):
        raise ValueError("manifest must be an object")
    return value


def confined_file(value: Any, allowed_root: Path, label: str) -> Path:
    path = Path(str(value)).resolve()
    if path == allowed_root or allowed_root not in path.parents:
        raise ValueError(f"{label} outside allowed personal root: {path}")
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    return path


def verify_protocol_amendments(
    payload: dict[str, Any], allowed_root: Path
) -> int:
    amendments = payload.get("protocol_amendments")
    if not isinstance(amendments, list) or [row.get("version") for row in amendments] != [
        "v1", "v2"
    ]:
        raise ValueError("P026 compiler lock lacks the exact v1/v2 amendment chain")
    paths: list[Path] = []
    for reference in amendments:
        frozen_path = confined_file(
            reference.get("path"),
            allowed_root,
            f"locked protocol amendment {reference.get('version')}",
        )
        if sha256_file(frozen_path) != str(reference.get("sha256")):
            raise ValueError(
                f"P026 locked protocol amendment {reference.get('version')} changed"
            )
        paths.append(frozen_path)
    if (
        [path.name for path in paths]
        != ["P026_PROTOCOL_AMENDMENT.md", "P026_PROTOCOL_AMENDMENT_V2.md"]
        or len(set(paths)) != 2
        or len({str(row.get("sha256")) for row in amendments}) != 2
        or amendments[1].get("predecessor_sha256") != amendments[0].get("sha256")
        or str(amendments[0].get("sha256"))
        not in paths[1].read_text(encoding="utf-8")
    ):
        raise ValueError("P026 protocol amendment chain is aliased or not predecessor-pinned")
    return len(amendments)


def verify_source_rollout(record: dict[str, Any], allowed_root: Path) -> dict[str, int]:
    """Authenticate the successful frozen-policy transcript used by P025."""

    rollout_path = confined_file(record["rollout"], allowed_root, "source rollout")
    if sha256_file(rollout_path) != str(record["rollout_sha256"]):
        raise ValueError("source rollout JSON hash mismatch")
    source = read_json(str(rollout_path))
    if source.get("kind") != "israc_frozen_starvla_natural_policy_support_rollout":
        raise ValueError("unexpected source rollout kind")
    if source.get("done") is not True or float(source.get("reward_max", 0.0)) < 1.0:
        raise ValueError("source rollout is not a declared natural success")
    frames = source.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError("source rollout has no frame transcript")
    rewards = [float(frame.get("reward", 0.0)) for frame in frames]
    if (
        frames[-1].get("done") is not True
        or max(rewards) != float(source["reward_max"])
        or float(frames[-1].get("reward", 0.0)) < 1.0
    ):
        raise ValueError("source success flags disagree with frame transcript")

    initialization = source.get("initialization")
    if not isinstance(initialization, dict) or initialization.get("source") != (
        "libero_benchmark_initial_state"
    ):
        raise ValueError("source does not use a benchmark initial state")
    required_init = {"suite_name", "task_id", "episode_index"}
    if not required_init.issubset(initialization):
        raise ValueError("source benchmark initialization is incomplete")
    if int(source["seed"]) != int(record["environment_seed"]):
        raise ValueError("source seed differs from certified environment seed")

    bddl_path = confined_file(source["bddl"], allowed_root, "source BDDL")
    if sha256_file(bddl_path) != str(record["task_asset_bddl_sha256"]):
        raise ValueError("source BDDL differs from certified task asset")
    if Path(str(source.get("task", ""))).name != bddl_path.name:
        raise ValueError("source task name differs from BDDL asset")

    arrays_path = confined_file(source["arrays"], allowed_root, "source arrays")
    if sha256_file(arrays_path) != str(record["arrays_sha256"]):
        raise ValueError("source array archive hash mismatch")
    with np.load(arrays_path, allow_pickle=False) as archive:
        required_arrays = {
            "boundary_steps", "boundary_states", "action_chunks", "executed_actions"
        }
        if not required_arrays.issubset(archive.files):
            raise ValueError("source array archive lacks required transcript arrays")
        boundary_steps = np.asarray(archive["boundary_steps"], dtype=np.int64)
        boundary_states = np.asarray(archive["boundary_states"], dtype=np.float64)
        chunks = np.asarray(archive["action_chunks"], dtype=np.float32)
        executed = np.asarray(archive["executed_actions"], dtype=np.float32)
    if (
        boundary_steps.ndim != 1
        or boundary_states.ndim != 2
        or chunks.ndim != 3
        or executed.ndim != 2
        or len(boundary_steps) != len(boundary_states)
        or len(boundary_steps) != len(chunks)
        or chunks.shape[1:] != (int(source["action_chunk_size"]), 7)
        or executed.shape[1:] != (7,)
        or not np.isfinite(boundary_states).all()
        or not np.isfinite(chunks).all()
        or not np.isfinite(executed).all()
    ):
        raise ValueError("invalid source transcript array schema")
    json_boundary_steps = [int(value) for value in source.get("boundary_steps", [])]
    if json_boundary_steps != boundary_steps.tolist():
        raise ValueError("source JSON/NPZ boundary steps disagree")
    if int(source["chunk_count"]) != len(chunks):
        raise ValueError("source chunk count disagrees with arrays")
    if int(source["executed_steps"]) != len(executed) or len(frames) != len(executed):
        raise ValueError("source executed-step count disagrees with transcript")
    if int(frames[-1].get("step", -1)) != len(executed) - 1:
        raise ValueError("source final frame step is inconsistent")

    index = int(record["candidate_chunk_index"])
    suffix_end = int(record["candidate_suffix_end_index"]) + 1
    if not (1 <= index < suffix_end <= len(chunks)):
        raise ValueError("certified source chunk indices are invalid")
    if int(boundary_steps[index]) != int(record["candidate_boundary_step"]):
        raise ValueError("certified boundary step differs from source transcript")
    if int(record["factual_prefix_start_chunk_index"]) != 0 or int(
        record["factual_prefix_end_chunk_index"]
    ) != index - 1:
        raise ValueError("certified factual prefix indices are inconsistent")
    chunk_size = int(source["action_chunk_size"])
    policy_prefix = chunks[:index].reshape(-1, chunks.shape[-1])
    if len(executed) < len(policy_prefix) or not np.array_equal(
        policy_prefix, executed[: len(policy_prefix)]
    ):
        raise ValueError("source executed actions do not match saved policy chunks")
    wait_steps = int(source.get("num_steps_wait", -1))
    if wait_steps < 0 or wait_steps != int(record["warmup_action_steps"]):
        raise ValueError("source/certificate warmup lengths disagree")
    wait_action = np.asarray([0.0] * 6 + [-1.0], dtype=np.float32)
    warmup = np.repeat(wait_action[None, :], wait_steps, axis=0)
    factual_actions = np.concatenate((warmup, policy_prefix), axis=0)
    candidate_actions = chunks[index:suffix_end].reshape(-1, chunks.shape[-1])
    if len(factual_actions) != int(record["factual_action_steps"]) or (
        canonical_array_sha256(factual_actions) != record["factual_action_sha256"]
    ):
        raise ValueError("certified factual actions do not reconstruct from source")
    if len(candidate_actions) != int(record["candidate_action_steps"]) or (
        canonical_array_sha256(candidate_actions) != record["candidate_sha256"]
    ):
        raise ValueError("certified candidate actions do not reconstruct from source")
    expected_factual_id = f"warmup_{wait_steps}_policy_prefix_0_to_{index - 1}"
    expected_candidate_id = f"policy_suffix_{index}_to_{suffix_end - 1}"
    if record["factual_action_id"] != expected_factual_id or (
        record["candidate_action_id"] != expected_candidate_id
    ):
        raise ValueError("certified action IDs do not match source indices")

    # Bind the certificate's t=0 snapshot to the actual benchmark episode.  No
    # simulator is stepped here; the benchmark state vector is the state passed
    # to env.set_init_state by both source collection and the compiler.
    from libero.libero import benchmark

    suite_name = str(initialization["suite_name"])
    suite_dict = benchmark.get_benchmark_dict()
    if suite_name not in suite_dict:
        raise ValueError("unknown benchmark suite in source initialization")
    suite = suite_dict[suite_name]()
    task_id = int(initialization["task_id"])
    episode_index = int(initialization["episode_index"])
    initial_states = suite.get_task_init_states(task_id)
    if not 0 <= episode_index < len(initial_states):
        raise ValueError("source benchmark episode index is invalid")
    initial_state = np.asarray(initial_states[episode_index], dtype=np.float64)
    if canonical_array_sha256(initial_state) != record["snapshot_sha256"]:
        raise ValueError("certified t=0 snapshot differs from benchmark initial state")
    return {
        "verified_source_chunks": len(chunks),
        "verified_source_executed_steps": len(executed),
    }


def load_metadata(archive: Any) -> dict[str, Any]:
    raw = archive["metadata_json"]
    if np.asarray(raw).shape != ():
        raise ValueError("metadata_json must be scalar")
    value = json.loads(str(np.asarray(raw).item()))
    if not isinstance(value, dict):
        raise ValueError("evidence metadata must be an object")
    return value


def load_static_arrays(archive: Any) -> dict[str, np.ndarray]:
    names = [str(value) for value in np.asarray(archive["static_field_names"]).tolist()]
    if not names or len(names) != len(set(names)) or names != sorted(names):
        raise ValueError("invalid static field-name table")
    arrays: dict[str, np.ndarray] = {}
    for index, name in enumerate(names):
        arrays[name] = np.asarray(archive[f"static_field_{index:05d}"]).copy()
    return arrays


def load_baseline_static(record: dict[str, Any]) -> dict[str, np.ndarray]:
    reference = record["baseline_static_evidence"]
    path = Path(str(reference["path"])).resolve()
    if sha256_file(path) != str(reference["sha256"]):
        raise ValueError("baseline static evidence hash mismatch")
    with np.load(path, allow_pickle=False) as archive:
        if str(np.asarray(archive["schema_version"]).item()) != STATIC_PHYSICS_SCHEMA_VERSION:
            raise ValueError("baseline static schema mismatch")
        arrays = load_static_arrays(archive)
    if hash_static_arrays(arrays) != record["baseline_static_physics_sha256"]:
        raise ValueError("baseline static full hash mismatch")
    if static_field_hashes(arrays) != record["baseline_static_field_sha256"]:
        raise ValueError("baseline static field hashes mismatch")
    return arrays


def verify_raw_reference(
    reference: dict[str, Any],
    block: dict[str, Any],
    value: float,
    record: dict[str, Any],
    *,
    unedited: bool = False,
) -> None:
    path = Path(str(reference["path"])).resolve()
    if sha256_file(path) != str(reference["sha256"]):
        raise ValueError("raw endpoint evidence file hash mismatch")
    with np.load(path, allow_pickle=False) as archive:
        metadata = load_metadata(archive)
        expected = {
            "block_id": block["parameter_metadata"]["block_id"],
            "geom_ids": block["geom_ids"],
            "parameter_family": record["arguments"]["family"],
            "parameter_value": float(value),
            "source_rollout_sha256": record["rollout_sha256"],
            "arrays_sha256": record["arrays_sha256"],
            "snapshot_sha256": record["snapshot_sha256"],
            "factual_action_sha256": record["factual_action_sha256"],
            "candidate_action_sha256": record["candidate_sha256"],
            "simulator_model_sha256": record["simulator_model_contact_schema_sha256"],
            "bddl_sha256": record["task_asset_bddl_sha256"],
            "engine_identity": record["engine_identity"],
        }
        for key, expected_value in expected.items():
            if metadata.get(key) != expected_value:
                raise ValueError(f"raw endpoint metadata mismatch: {key}")
        if canonical_array_sha256(np.asarray(archive["factual_actions"], dtype=np.float32)) != record[
            "factual_action_sha256"
        ]:
            raise ValueError("raw factual action mismatch")
        if canonical_array_sha256(np.asarray(archive["candidate_actions"], dtype=np.float32)) != record[
            "candidate_sha256"
        ]:
            raise ValueError("raw candidate action mismatch")
        live_static_arrays = load_static_arrays(archive)
        for prefix in ("factual", "candidate"):
            rgb = np.asarray(archive[f"{prefix}_rgb"])
            depth = np.asarray(archive[f"{prefix}_depth"])
            rgb_hashes = np.asarray(archive[f"{prefix}_rgb_sha256"])
            depth_hashes = np.asarray(archive[f"{prefix}_depth_sha256"])
            if not (len(rgb) == len(depth) == len(rgb_hashes) == len(depth_hashes)):
                raise ValueError("raw image evidence length mismatch")
            expected_trace_length = 1 + int(
                record[f"{prefix}_action_steps"]
            )
            if len(rgb) != expected_trace_length:
                raise ValueError(f"{prefix} trace does not contain t=0 plus every action step")
            for index in range(len(rgb)):
                if array_digest_probe(rgb[index]) != str(rgb_hashes[index]):
                    raise ValueError("raw RGB digest mismatch")
                if array_digest_probe(depth[index]) != str(depth_hashes[index]):
                    raise ValueError("raw depth digest mismatch")
            for suffix in ("state", "proprio", "physical_effect_probe", "task_effect"):
                values = np.asarray(archive[f"{prefix}_{suffix}"], dtype=np.float64)
                if len(values) != len(rgb) or not np.isfinite(values).all():
                    raise ValueError(f"invalid raw numeric evidence: {prefix}_{suffix}")
            active = np.asarray(archive[f"{prefix}_active"], dtype=np.bool_)
            if active.shape != (len(rgb),):
                raise ValueError("raw activation evidence length mismatch")
            if unedited and np.any(active):
                raise ValueError("unedited nominal evidence declares an active parameter block")
            pairs = np.asarray(archive[f"{prefix}_contact_pairs"], dtype=np.int32)
            offsets = np.asarray(archive[f"{prefix}_contact_offsets"], dtype=np.int64)
            if (
                pairs.ndim != 2
                or pairs.shape[1:] != (2,)
                or offsets.shape != (len(rgb) + 1,)
                or int(offsets[0]) != 0
                or int(offsets[-1]) != len(pairs)
                or np.any(np.diff(offsets) < 0)
            ):
                raise ValueError("raw contact evidence schema mismatch")
        factual_actions = np.asarray(archive["factual_actions"], dtype=np.float32)
        candidate_actions = np.asarray(archive["candidate_actions"], dtype=np.float32)
        if len(factual_actions) != int(record["factual_action_steps"]):
            raise ValueError("factual action length mismatch")
        if len(candidate_actions) != int(record["candidate_action_steps"]):
            raise ValueError("candidate action length mismatch")
        factual_t0_state = np.asarray(archive["factual_t0_state"], dtype=np.float64)
        factual_t0_proprio = np.asarray(archive["factual_t0_proprio"], dtype=np.float64)
        candidate_t0_state = np.asarray(archive["candidate_t0_state"], dtype=np.float64)
        candidate_t0_proprio = np.asarray(archive["candidate_t0_proprio"], dtype=np.float64)
        if canonical_array_sha256(factual_t0_state) != record["snapshot_sha256"]:
            raise ValueError("restored factual t=0 state differs from snapshot")
        factual_state = np.asarray(archive["factual_state"], dtype=np.float64)
        factual_proprio = np.asarray(archive["factual_proprio"], dtype=np.float64)
        candidate_state = np.asarray(archive["candidate_state"], dtype=np.float64)
        candidate_proprio = np.asarray(archive["candidate_proprio"], dtype=np.float64)
        if not np.array_equal(factual_t0_state, factual_state[0]) or not np.array_equal(
            factual_t0_proprio, factual_proprio[0]
        ):
            raise ValueError("factual t=0 state/proprio is outside certified transcript")
        if array_digest_probe(np.asarray(archive["factual_t0_rgb"])) != str(
            np.asarray(archive["factual_rgb_sha256"])[0]
        ) or array_digest_probe(np.asarray(archive["factual_t0_depth"])) != str(
            np.asarray(archive["factual_depth_sha256"])[0]
        ):
            raise ValueError("factual t=0 image is outside certified transcript")
        if not np.array_equal(candidate_t0_state, candidate_state[0]) or not np.array_equal(
            candidate_t0_proprio, candidate_proprio[0]
        ):
            raise ValueError("candidate t=0 state/proprio is outside certified transcript")
        if array_digest_probe(np.asarray(archive["candidate_t0_rgb"])) != str(
            np.asarray(archive["candidate_rgb_sha256"])[0]
        ) or array_digest_probe(np.asarray(archive["candidate_t0_depth"])) != str(
            np.asarray(archive["candidate_depth_sha256"])[0]
        ):
            raise ValueError("candidate t=0 image is outside certified transcript")
        if not len(factual_state) or not np.array_equal(candidate_t0_state, factual_state[-1]):
            raise ValueError("candidate pre-action state is not factual endpoint")
        if not np.array_equal(candidate_t0_proprio, factual_proprio[-1]):
            raise ValueError("candidate pre-action proprio is not factual endpoint")
        if array_digest_probe(np.asarray(archive["candidate_t0_rgb"])) != str(
            np.asarray(archive["factual_rgb_sha256"])[-1]
        ):
            raise ValueError("candidate pre-action RGB is not factual endpoint")
        if array_digest_probe(np.asarray(archive["candidate_t0_depth"])) != str(
            np.asarray(archive["factual_depth_sha256"])[-1]
        ):
            raise ValueError("candidate pre-action depth is not factual endpoint")
        runtime = metadata.get("static_runtime")
        if not isinstance(runtime, dict):
            raise ValueError("runtime static-physics manifest missing")
        if runtime.get("schema_version") != record["static_physics_schema_version"]:
            raise ValueError("static-physics schema version mismatch")
        if runtime.get("live_static_sha256") != runtime.get("expected_static_sha256"):
            raise ValueError("live static physics differs from target edit")
        baseline_static_arrays = load_baseline_static(record)
        actual_live_sha256 = hash_static_arrays(live_static_arrays)
        if actual_live_sha256 != runtime.get("live_static_sha256"):
            raise ValueError("live static full hash does not match raw arrays")
        expected_live_sha256 = (
            hash_static_arrays(baseline_static_arrays)
            if unedited else
            static_contact_config_hash(
                baseline_static_arrays,
                tuple(int(item) for item in block["geom_ids"]),
                str(record["arguments"]["family"]),
                float(value),
            )
        )
        if actual_live_sha256 != expected_live_sha256:
            raise ValueError(
                "raw live static arrays are not the baseline"
                if unedited else
                "raw live static arrays are not the registered endpoint edit"
            )
        field_hashes = runtime.get("live_field_sha256")
        baseline_hashes = record["baseline_static_field_sha256"]
        if not isinstance(field_hashes, dict) or set(field_hashes) != set(baseline_hashes):
            raise ValueError("live static field manifest is incomplete")
        if field_hashes != static_field_hashes(live_static_arrays):
            raise ValueError("live static field hashes do not match raw arrays")
        if unedited:
            if field_hashes != baseline_hashes:
                raise ValueError("unedited evidence changes a static physics field")
            if runtime.get("structured_diff") != []:
                raise ValueError("unedited evidence declares a static physics edit")
            return
        target_field = block["static_diff_schema"]["array"]
        for field, digest in field_hashes.items():
            if field != target_field and digest != baseline_hashes[field]:
                raise ValueError(f"non-target live static field changed: {field}")
        allowed_indices = {
            (int(geom_id), int(column))
            for geom_id in block["geom_ids"]
            for column in block["static_diff_schema"]["columns"]
        }
        actual_diff = validate_live_static_edit(
            baseline_static_arrays,
            live_static_arrays,
            tuple(int(item) for item in block["geom_ids"]),
            str(record["arguments"]["family"]),
        )
        if runtime.get("structured_diff") != actual_diff:
            raise ValueError("declared static diff is incomplete or incorrect")
        for change in actual_diff:
            if (
                change.get("field") != target_field
                or tuple(change.get("index", [])) not in allowed_indices
            ):
                raise ValueError("runtime static diff escapes registered geom address")
            if not math.isfinite(float(change["before"])) or not math.isfinite(float(change["after"])):
                raise ValueError("runtime static diff contains non-finite value")


def load_trace(
    archive: Any,
    prefix: str,
    *,
    world_id: str,
    action_id: str,
    block_id: str,
    geom_ids: tuple[int, ...],
    parameter: PhysicalParameter,
) -> RolloutTrace:
    state = np.asarray(archive[f"{prefix}_state"], dtype=np.float64)
    proprio = np.asarray(archive[f"{prefix}_proprio"], dtype=np.float64)
    rgb_hashes = np.asarray(archive[f"{prefix}_rgb_sha256"])
    depth_hashes = np.asarray(archive[f"{prefix}_depth_sha256"])
    physical = np.asarray(archive[f"{prefix}_physical_effect_probe"], dtype=np.float64)
    task = np.asarray(archive[f"{prefix}_task_effect"], dtype=np.float64)
    active = np.asarray(archive[f"{prefix}_active"], dtype=np.bool_)
    contact_pairs = np.asarray(archive[f"{prefix}_contact_pairs"], dtype=np.int32)
    contact_offsets = np.asarray(archive[f"{prefix}_contact_offsets"], dtype=np.int64)
    rgb = np.asarray(archive[f"{prefix}_rgb"])
    depth = np.asarray(archive[f"{prefix}_depth"])
    lengths = {
        len(value)
        for value in (state, proprio, rgb_hashes, depth_hashes, physical, task, active, rgb, depth)
    }
    if len(lengths) != 1:
        raise ValueError("evidence trace arrays have inconsistent lengths")
    if not all(np.isfinite(value).all() for value in (state, proprio, physical, task)):
        raise ValueError("evidence contains non-finite numeric trace")
    if (
        contact_pairs.ndim != 2
        or contact_pairs.shape[1:] != (2,)
        or contact_offsets.shape != (len(state) + 1,)
        or int(contact_offsets[0]) != 0
        or int(contact_offsets[-1]) != len(contact_pairs)
        or np.any(np.diff(contact_offsets) < 0)
    ):
        raise ValueError("invalid contact-pair encoding")
    target_geoms = set(geom_ids)
    frames: list[FrameTrace] = []
    for index in range(len(state)):
        rgb_digest = array_digest_probe(rgb[index])
        depth_digest = array_digest_probe(depth[index])
        if rgb_digest != str(rgb_hashes[index]):
            raise ValueError("stored RGB frame does not match digest")
        if depth_digest != str(depth_hashes[index]):
            raise ValueError("stored depth frame does not match digest")
        frame_pairs = tuple(
            tuple(int(value) for value in pair)
            for pair in contact_pairs[
                int(contact_offsets[index]):int(contact_offsets[index + 1])
            ]
        )
        derived_active = any(
            left in target_geoms or right in target_geoms for left, right in frame_pairs
        )
        if derived_active != bool(active[index]):
            raise ValueError("declared activation differs from raw contact geom pairs")
        frames.append(
            FrameTrace(
                state=tuple(float(value) for value in state[index]),
                proprio=tuple(float(value) for value in proprio[index]),
                rgb_sha256=rgb_digest,
                depth_sha256=depth_digest,
                physical_effect_probe=tuple(float(value) for value in physical[index]),
                task_effect=tuple(float(value) for value in task[index]),
                active_parameter_blocks=(block_id,) if derived_active else (),
                contact_geom_pairs=frame_pairs,
            )
        )
    return RolloutTrace(
        world_id=world_id,
        action_id=action_id,
        action_rank=1,
        frames=tuple(frames),
        parameters=(parameter,),
    )


def physical_parameter(block: dict[str, Any], value: float) -> PhysicalParameter:
    metadata = dict(block["parameter_metadata"])
    metadata["value"] = float(value)
    return PhysicalParameter(**metadata)


def load_endpoint(
    reference: dict[str, Any],
    block: dict[str, Any],
    value: float,
    certificate: dict[str, Any],
    record: dict[str, Any],
) -> tuple[RolloutTrace, RolloutTrace, dict[str, Any]]:
    path = Path(str(reference["path"])).resolve()
    if sha256_file(path) != str(reference["sha256"]):
        raise ValueError("endpoint evidence file hash mismatch")
    with np.load(path, allow_pickle=False) as archive:
        metadata = load_metadata(archive)
        if float(metadata["parameter_value"]) != float(value):
            raise ValueError("endpoint value differs from evidence metadata")
        expected = {
            "block_id": block["parameter_metadata"]["block_id"],
            "source_rollout_sha256": record["rollout_sha256"],
            "arrays_sha256": record["arrays_sha256"],
            "snapshot_sha256": certificate["snapshot_id"],
            "factual_action_sha256": certificate["factual_action_sha256"],
            "candidate_action_sha256": certificate["candidate_action_sha256"],
            "simulator_model_sha256": certificate["simulator_model_sha256"],
            "bddl_sha256": certificate["task_asset_sha256"],
            "engine_identity": certificate["engine_identity"],
        }
        for key, expected_value in expected.items():
            if metadata.get(key) != expected_value:
                raise ValueError(f"endpoint metadata binding mismatch: {key}")
        if canonical_array_sha256(np.asarray(archive["factual_actions"], dtype=np.float32)) != certificate[
            "factual_action_sha256"
        ]:
            raise ValueError("factual action bytes do not match certificate")
        if canonical_array_sha256(np.asarray(archive["candidate_actions"], dtype=np.float32)) != certificate[
            "candidate_action_sha256"
        ]:
            raise ValueError("candidate action bytes do not match certificate")
        parameter = physical_parameter(block, value)
        token = str(value).replace(".", "p")
        world_id = f"{parameter.block_id}@{token}"
        factual = load_trace(
            archive,
            "factual",
            world_id=world_id,
            action_id=str(certificate["factual_action_id"]),
            block_id=parameter.block_id,
            geom_ids=tuple(int(value) for value in block["geom_ids"]),
            parameter=parameter,
        )
        candidate = load_trace(
            archive,
            "candidate",
            world_id=world_id,
            action_id=str(certificate["candidate_action_id"]),
            block_id=parameter.block_id,
            geom_ids=tuple(int(value) for value in block["geom_ids"]),
            parameter=parameter,
        )
    return factual, candidate, metadata


def alias_certificate(payload: dict[str, Any]) -> AliasCertificate:
    values = dict(payload)
    for key in ("search_objective_terms", "evidence_sha256", "parameter_addresses"):
        values[key] = tuple(values[key])
    values["static_config_sha256"] = tuple(values["static_config_sha256"])
    return AliasCertificate(**values)


def noise_envelope(payload: dict[str, Any]) -> NoiseEnvelope:
    values = {key: float(value) for key, value in payload.items()}
    if not all(math.isfinite(value) and value >= 0.0 for value in values.values()):
        raise ValueError("certificate noise envelope is invalid")
    return NoiseEnvelope(**values)


def verify_pair(
    pair: dict[str, Any],
    block: dict[str, Any],
    record: dict[str, Any],
) -> None:
    payload = pair["certificate_payload"]
    certificate_values = payload["certificate"]
    left_value = float(pair["left_value"])
    right_value = float(pair["right_value"])
    factual_left, candidate_left, left_metadata = load_endpoint(
        pair["left_evidence"], block, left_value, certificate_values, record
    )
    factual_right, candidate_right, right_metadata = load_endpoint(
        pair["right_evidence"], block, right_value, certificate_values, record
    )
    expected_static = certificate_values["static_config_sha256"]
    if left_metadata["static_runtime"]["live_static_sha256"] != expected_static[0]:
        raise ValueError("left certificate static hash differs from live evidence")
    if right_metadata["static_runtime"]["live_static_sha256"] != expected_static[1]:
        raise ValueError("right certificate static hash differs from live evidence")
    result = certify_alias_pair(
        factual_left,
        factual_right,
        candidate_left,
        candidate_right,
        alias_certificate(certificate_values),
        noise_envelope(payload["factual_envelope"]),
        noise_envelope(payload["candidate_envelope"]),
    )
    if not result.passed:
        raise ValueError(f"recomputed certificate failed: {result.failures}")
    if result.certificate_sha256 != pair["certificate_sha256"]:
        raise ValueError("recomputed certificate hash differs from manifest")
    if json.loads(result.canonical_payload) != payload:
        raise ValueError("recomputed canonical certificate differs from manifest")


def verify_repeat(block: dict[str, Any], record: dict[str, Any]) -> None:
    endpoints = block["endpoint_evidence"]
    nominal_value = float(block["static_diff_schema"]["legal_endpoints"][0])
    nominal_reference = endpoints[str(nominal_value)]
    certificate_values = None
    for pair in block["endpoint_strength_curve"]:
        certificate_values = pair["certificate_payload"]["certificate"]
        break
    if certificate_values is None:
        certificate_values = {
            "snapshot_id": record["snapshot_sha256"],
            "factual_action_id": record["factual_action_id"],
            "candidate_action_id": record["candidate_action_id"],
            "factual_action_sha256": record["factual_action_sha256"],
            "candidate_action_sha256": record["candidate_sha256"],
            "simulator_model_sha256": record["simulator_model_contact_schema_sha256"],
            "task_asset_sha256": record["task_asset_bddl_sha256"],
            "engine_identity": record["engine_identity"],
        }
    factual, candidate, _ = load_endpoint(
        nominal_reference, block, nominal_value, certificate_values, record
    )
    repeat_factual, repeat_candidate, _ = load_endpoint(
        block["repeat_evidence"], block, nominal_value, certificate_values, record
    )
    measured_factual = repeat_envelope((factual, repeat_factual))
    measured_candidate = repeat_envelope((candidate, repeat_candidate))
    declared_factual = NoiseEnvelope(**block["factual_repeat_noise_envelope"])
    declared_candidate = NoiseEnvelope(**block["candidate_repeat_noise_envelope"])
    if measured_factual != declared_factual or measured_candidate != declared_candidate:
        raise ValueError("repeat-noise envelope does not match raw evidence")


def source_boundary_state(record: dict[str, Any], allowed_root: Path) -> np.ndarray:
    rollout_path = confined_file(record["rollout"], allowed_root, "source rollout")
    source = read_json(str(rollout_path))
    arrays_path = confined_file(source["arrays"], allowed_root, "source arrays")
    if sha256_file(arrays_path) != str(record["arrays_sha256"]):
        raise ValueError("source arrays changed before boundary-fidelity verification")
    with np.load(arrays_path, allow_pickle=False) as archive:
        states = np.asarray(archive["boundary_states"], dtype=np.float64)
    index = int(record["candidate_chunk_index"])
    if not 0 <= index < len(states):
        raise ValueError("candidate boundary index outside source states")
    return states[index].copy()


def verify_source_admission(
    record: dict[str, Any], allowed_root: Path
) -> dict[str, int]:
    reference = record.get("source_admission_report")
    if not isinstance(reference, dict):
        raise ValueError("P026 source admission reference is missing")
    path = confined_file(reference.get("path"), allowed_root, "source admission report")
    if sha256_file(path) != str(reference.get("sha256")):
        raise ValueError("source admission report hash mismatch")
    report = read_json(str(path))
    required_true = (
        report.get("kind") == "israc_source_admission_replay_v1"
        and report.get("passed") is True
        and report.get("policy_identity_verified") is True
        and report.get("policy_lock_verified") is True
    )
    if not required_true:
        raise ValueError("P026 source admission did not pass replay/identity/lock")
    bindings = {
        "source_rollout": str(Path(str(record["rollout"])).resolve()),
        "source_rollout_sha256": record["rollout_sha256"],
        "source_arrays_sha256": record["arrays_sha256"],
        "task_asset_bddl_sha256": record["task_asset_bddl_sha256"],
        "environment_seed": int(record["environment_seed"]),
    }
    for key, expected in bindings.items():
        actual = report.get(key)
        if key == "source_rollout":
            actual = str(Path(str(actual)).resolve())
        if actual != expected:
            raise ValueError(f"P026 source admission binding mismatch: {key}")
    source_arrays = confined_file(report.get("source_arrays"), allowed_root, "admitted arrays")
    if sha256_file(source_arrays) != str(report["source_arrays_sha256"]):
        raise ValueError("admitted source arrays changed")
    if int(report.get("state_digest_mismatches", -1)) != 0 or int(
        report.get("rgb_digest_mismatches", -1)
    ) != 0 or int(report.get("wrist_rgb_digest_mismatches", -1)) != 0 or int(
        report.get("contact_mismatches", -1)
    ) != 0 or int(report.get("reward_or_done_mismatches", -1)) != 0 or int(
        report.get("boundary_state_mismatches", -1)
    ) != 0 or float(report.get("boundary_state_max_abs", math.inf)) != 0.0:
        raise ValueError("P026 source admission contains replay mismatches")
    return {"verified_source_admission_reports": 1}


def verify_compiler_lock(
    record: dict[str, Any], allowed_root: Path
) -> dict[str, int]:
    reference = record.get("compiler_lock")
    if not isinstance(reference, dict):
        raise ValueError("P026 compiler lock reference is missing")
    path = confined_file(reference.get("path"), allowed_root, "compiler lock")
    if sha256_file(path) != str(reference.get("sha256")):
        raise ValueError("P026 compiler lock hash mismatch")
    payload = read_json(str(path))
    if payload.get("kind") != "p026_compiler_code_lock" or payload.get("frozen") is not True:
        raise ValueError("P026 compiler lock is not frozen")
    files = payload.get("files")
    required_roles = {
        "compiler",
        "manifest_verifier",
        "p025_schema_validator",
        "p026_analyzer",
        "matrix_runner",
        "matrix_lock_builder",
        "launch_record_builder",
        "selector_support",
        "certificate_core",
        "repeat_envelope",
        "observation_support",
    }
    if not isinstance(files, list) or len(files) != len(required_roles) or (
        {str(item.get("role")) for item in files} != required_roles
    ):
        raise ValueError("P026 compiler lock role set is incomplete")
    for item in files:
        code_path = confined_file(item.get("path"), allowed_root, "locked compiler code")
        if sha256_file(code_path) != str(item.get("sha256")):
            raise ValueError(f"P026 locked code drift: {item.get('role')}")
    for label in ("preregistration", "policy_lock"):
        frozen_reference = payload.get(label)
        if not isinstance(frozen_reference, dict):
            raise ValueError(f"P026 compiler lock lacks {label}")
        frozen_path = confined_file(
            frozen_reference.get("path"), allowed_root, f"locked {label}"
        )
        if sha256_file(frozen_path) != str(frozen_reference.get("sha256")):
            raise ValueError(f"P026 locked {label} changed")
    verify_protocol_amendments(payload, allowed_root)
    plan_reference = payload.get("boundary_plan")
    if not isinstance(plan_reference, dict):
        raise ValueError("P026 compiler lock lacks boundary plan")
    plan_path = confined_file(
        plan_reference.get("path"), allowed_root, "locked boundary plan"
    )
    if sha256_file(plan_path) != str(plan_reference.get("sha256")):
        raise ValueError("P026 locked boundary plan changed")
    plan = read_json(str(plan_path))
    if (
        plan.get("kind") != "p026_outcome_blind_boundary_plan"
        or plan.get("frozen_before_compiler_execution") is not True
    ):
        raise ValueError("P026 boundary plan is not outcome-blind frozen")
    for label in ("preregistration", "policy_lock"):
        plan_reference = plan.get(label)
        lock_reference = payload.get(label)
        if not isinstance(plan_reference, dict) or not isinstance(lock_reference, dict):
            raise ValueError(f"P026 plan/lock lacks {label} reference")
        normalized_plan = {
            "path": str(Path(str(plan_reference.get("path"))).resolve()),
            "sha256": str(plan_reference.get("sha256")),
        }
        normalized_lock = {
            "path": str(Path(str(lock_reference.get("path"))).resolve()),
            "sha256": str(lock_reference.get("sha256")),
        }
        if normalized_plan != normalized_lock:
            raise ValueError(f"P026 compiler lock {label} differs from boundary plan")
    admission_path = confined_file(
        record["source_admission_report"]["path"], allowed_root, "source admission"
    )
    admission = read_json(str(admission_path))
    admission_policy = admission.get("policy_lock")
    plan_policy = plan.get("policy_lock")
    if not isinstance(admission_policy, dict) or not isinstance(plan_policy, dict):
        raise ValueError("P026 admission/plan policy lock reference missing")
    if {
        "path": str(Path(str(admission_policy.get("path"))).resolve()),
        "sha256": str(admission_policy.get("sha256")),
    } != {
        "path": str(Path(str(plan_policy.get("path"))).resolve()),
        "sha256": str(plan_policy.get("sha256")),
    }:
        raise ValueError("P026 admission policy lock differs from frozen boundary plan")
    matching = [
        row for row in plan.get("boundaries", [])
        if str(row.get("source_rollout_sha256")) == str(record["rollout_sha256"])
        and int(row.get("candidate_index", -1)) == int(record["candidate_chunk_index"])
    ]
    if len(matching) != 1:
        raise ValueError("P026 manifest boundary is absent or duplicated in frozen plan")
    frozen_boundary = matching[0]
    frozen_admission = {
        "path": str(Path(str(frozen_boundary["source_admission"])).resolve()),
        "sha256": str(frozen_boundary["source_admission_sha256"]),
    }
    actual_admission = dict(record["source_admission_report"])
    actual_admission["path"] = str(Path(str(actual_admission["path"])).resolve())
    if actual_admission != frozen_admission or int(
        frozen_boundary["candidate_boundary_step"]
    ) != int(record["candidate_boundary_step"]):
        raise ValueError("P026 manifest differs from its frozen boundary row")
    if (
        record["block_selector"] not in plan.get("selectors", [])
        or int(record["selector_seed"]) not in {
            int(value) for value in plan.get("selector_seeds", [])
        }
        or record["arguments"]["family"] != plan.get("physical_family")
        or int(record["arguments"]["candidate_chunks"]) != int(plan["candidate_chunks"])
        or int(record["max_selected_blocks"]) != int(plan["max_selected_blocks"])
    ):
        raise ValueError("P026 compiler arguments escape the frozen plan")
    arguments_path = str(Path(str(record.get("arguments", {}).get("compiler_lock"))).resolve())
    if arguments_path != str(path):
        raise ValueError("P026 compiler argument does not match embedded lock")
    return {"verified_compiler_lock_files": len(files)}


def verify_matrix_run_lock(
    record: dict[str, Any], allowed_root: Path
) -> dict[str, int]:
    reference = record.get("matrix_run_lock")
    if not isinstance(reference, dict):
        raise ValueError("P026 matrix-run lock reference is missing")
    path = confined_file(reference.get("path"), allowed_root, "matrix-run lock")
    if sha256_file(path) != str(reference.get("sha256")):
        raise ValueError("P026 matrix-run lock hash mismatch")
    lock = read_json(str(path))
    if lock.get("kind") != "p026_matrix_run_lock" or lock.get("frozen") is not True:
        raise ValueError("P026 matrix-run lock is not frozen")
    if lock.get("compiler_lock") != record.get("compiler_lock"):
        raise ValueError("P026 matrix-run lock is bound to another compiler lock")
    compiler_path = confined_file(
        record["compiler_lock"]["path"], allowed_root, "compiler lock for matrix"
    )
    compiler = read_json(str(compiler_path))
    if lock.get("boundary_plan") != compiler.get("boundary_plan"):
        raise ValueError("P026 matrix-run lock is bound to another boundary plan")
    output_path = Path(str(record.get("artifact_output_path"))).resolve()
    confined_file(output_path, allowed_root, "locked matrix artifact")
    jobs = lock.get("jobs")
    matching = [
        row for row in jobs if Path(str(row.get("output"))).resolve() == output_path
    ] if isinstance(jobs, list) else []
    if len(matching) != 1:
        raise ValueError("P026 artifact path is absent or duplicated in matrix-run lock")
    row = matching[0]
    bindings = {
        "source_rollout_sha256": record["rollout_sha256"],
        "candidate_index": int(record["candidate_chunk_index"]),
        "selector": record["block_selector"],
        "selector_seed": int(record["selector_seed"]),
        "source_admission_sha256": record["source_admission_report"]["sha256"],
    }
    for key, expected in bindings.items():
        if row.get(key) != expected:
            raise ValueError(f"P026 matrix-run job binding mismatch: {key}")
    if str(Path(str(row.get("source_admission"))).resolve()) != str(
        Path(str(record["source_admission_report"]["path"])).resolve()
    ):
        raise ValueError("P026 matrix-run admission path mismatch")
    if int(lock.get("job_count", -1)) != len(jobs):
        raise ValueError("P026 matrix-run job count mismatch")
    return {"verified_matrix_run_lock_jobs": len(jobs)}


def evidence_contact_union(reference: dict[str, Any], prefix: str) -> set[tuple[int, int]]:
    path = Path(str(reference["path"])).resolve()
    with np.load(path, allow_pickle=False) as archive:
        pairs = np.asarray(archive[f"{prefix}_contact_pairs"], dtype=np.int32)
        offsets = np.asarray(archive[f"{prefix}_contact_offsets"], dtype=np.int64)
    if offsets.ndim != 1 or len(offsets) < 2 or int(offsets[-1]) != len(pairs):
        raise ValueError("nominal contact evidence encoding is invalid")
    # The compiler's contact gate observes contacts after actions, not the t=0 frame.
    start = int(offsets[1])
    return {
        (int(left), int(right)) for left, right in pairs[start:]
    }


class ContactTopologyModel:
    """Minimal authenticated model view required by the frozen selector code."""

    def __init__(self, rows: list[dict[str, Any]], geom_bodyid: np.ndarray):
        self.ngeom = len(rows)
        self.geom_bodyid = np.asarray(geom_bodyid, dtype=np.int64)
        self._geom_names = [str(row["geom_name"]) for row in rows]
        self._body_names: dict[int, str] = {}
        for row in rows:
            body_id = int(row["body_id"])
            body_name = str(row["body_name"])
            if body_id in self._body_names and self._body_names[body_id] != body_name:
                raise ValueError("contact topology gives one body id multiple names")
            self._body_names[body_id] = body_name

    def geom_id2name(self, geom_id: int) -> str | None:
        return self._geom_names[geom_id] or None

    def body_id2name(self, body_id: int) -> str | None:
        return self._body_names.get(body_id) or None


def authenticated_contact_topology(record: dict[str, Any]) -> ContactTopologyModel:
    rows = record.get("contact_topology")
    if not isinstance(rows, list) or not rows:
        raise ValueError("P026 contact topology is missing")
    expected_keys = {"geom_id", "geom_name", "body_id", "body_name"}
    if any(not isinstance(row, dict) or set(row) != expected_keys for row in rows):
        raise ValueError("P026 contact topology schema is invalid")
    geom_ids = [int(row["geom_id"]) for row in rows]
    if geom_ids != list(range(len(rows))):
        raise ValueError("P026 contact topology geom ids are not complete and ordered")
    static = load_baseline_static(record)
    if "model.geom_bodyid" not in static:
        raise ValueError("baseline static evidence lacks geom_bodyid topology")
    geom_bodyid = np.asarray(static["model.geom_bodyid"], dtype=np.int64).reshape(-1)
    if len(geom_bodyid) != len(rows) or any(
        int(row["body_id"]) != int(geom_bodyid[index])
        for index, row in enumerate(rows)
    ):
        raise ValueError("P026 contact topology disagrees with hashed geom_bodyid")
    if contact_topology_schema_hash(static, rows) != str(
        record["simulator_model_contact_schema_sha256"]
    ):
        raise ValueError("P026 contact topology/model schema hash mismatch")
    return ContactTopologyModel(rows, geom_bodyid)


def validate_selected_block_rows(
    record: dict[str, Any],
    selected: list[tuple[str, tuple[int, ...]]],
    visible_pool_count: int,
) -> None:
    if int(record.get("selector_visible_pool_count", -1)) != visible_pool_count:
        raise ValueError("selector visible pool count differs from raw reconstruction")
    if int(record.get("selected_block_count", -1)) != len(selected):
        raise ValueError("selected block count differs from raw reconstruction")
    family = str(record["arguments"]["family"])
    legal = tuple(float(value) for value in FAMILY_VALUES[family])
    expected_rows = []
    for address, geom_ids in selected:
        block_id = f"{record['block_selector']}_{family}:{address}"
        expected_rows.append({
            "parameter_address": address,
            "geom_ids": [int(value) for value in geom_ids],
            "parameter_metadata": asdict(
                parameter(block_id, geom_ids, legal[0], family, legal)
            ),
        })
    actual_rows = [
        {
            "parameter_address": block.get("parameter_address"),
            "geom_ids": block.get("geom_ids"),
            "parameter_metadata": block.get("parameter_metadata"),
        }
        for block in record["blocks"]
    ]
    if actual_rows != expected_rows:
        raise ValueError("manifest block list/order differs from raw selector reconstruction")


def verify_selector_block_reconstruction(record: dict[str, Any]) -> int:
    model = authenticated_contact_topology(record)
    nominal = record["nominal_unedited_evidence"]
    factual_pairs = evidence_contact_union(nominal, "factual")
    candidate_pairs = evidence_contact_union(nominal, "candidate")
    if any(
        geom_id < 0 or geom_id >= model.ngeom
        for pair in factual_pairs | candidate_pairs
        for geom_id in pair
    ):
        raise ValueError("raw selector contact contains an out-of-range geom id")
    factual_pool = geom_blocks(model, factual_pairs)
    candidate_pool = geom_blocks(model, candidate_pairs)
    if not bool(record["boundary_eligible"]):
        pool: dict[str, tuple[int, ...]] = {}
    elif record["block_selector"] == "israc-contact-subtraction":
        pool = subtract_blocks(candidate_pool, factual_pool)
    elif record["block_selector"] == "candidate-contact":
        pool = candidate_pool
    elif record["block_selector"] == "random-scene":
        pool = geom_blocks(model)
    else:
        raise ValueError("unknown block selector during raw reconstruction")
    selected = select_blocks(
        pool,
        selector=str(record["block_selector"]),
        max_blocks=int(record["max_selected_blocks"]),
        seed=int(record["environment_seed"]) + int(record["selector_seed"]),
    ) if bool(record["boundary_eligible"]) else []
    validate_selected_block_rows(record, selected, len(pool))
    return len(selected)


def verify_p026_nominal_gate(
    record: dict[str, Any], allowed_root: Path
) -> dict[str, int]:
    nominal = record.get("nominal_unedited_evidence")
    repeat = record.get("nominal_unedited_repeat_evidence")
    if not isinstance(nominal, dict) or not isinstance(repeat, dict):
        raise ValueError("P026 raw unedited nominal evidence is missing")
    for label, reference in (("nominal", nominal), ("nominal repeat", repeat)):
        path = confined_file(reference.get("path"), allowed_root, label)
        if sha256_file(path) != str(reference.get("sha256")):
            raise ValueError(f"{label} evidence hash mismatch")
    if nominal == repeat or nominal.get("sha256") == repeat.get("sha256"):
        raise ValueError("P026 nominal and repeat evidence are not distinct artifacts")
    for reference, expected_kind in (
        (nominal, "nominal_unedited_evidence"),
        (repeat, "nominal_unedited_repeat_evidence"),
    ):
        with np.load(Path(str(reference["path"])).resolve(), allow_pickle=False) as archive:
            if load_metadata(archive).get("kind") != expected_kind:
                raise ValueError(f"P026 nominal evidence kind mismatch: {expected_kind}")
    fake_block = {
        "parameter_metadata": {"block_id": "nominal_unedited"},
        "geom_ids": [],
    }
    verify_raw_reference(nominal, fake_block, 0.0, record, unedited=True)
    verify_raw_reference(repeat, fake_block, 0.0, record, unedited=True)

    expected = source_boundary_state(record, allowed_root)
    nominal_endpoint, nominal_candidate_t0 = evidence_factual_endpoint(nominal)
    repeat_endpoint, repeat_candidate_t0 = evidence_factual_endpoint(repeat)
    for endpoint in (
        nominal_endpoint, nominal_candidate_t0, repeat_endpoint, repeat_candidate_t0
    ):
        if endpoint.shape != expected.shape:
            raise ValueError("P026 source boundary/raw nominal state shape mismatch")
    replay_error = float(np.max(np.abs(nominal_endpoint - expected)))
    repeat_error = float(np.max(np.abs(nominal_endpoint - repeat_endpoint)))
    factual_pairs = evidence_contact_union(nominal, "factual")
    candidate_pairs = evidence_contact_union(nominal, "candidate")
    factual_pairs_repeat = evidence_contact_union(repeat, "factual")
    candidate_pairs_repeat = evidence_contact_union(repeat, "candidate")
    eligible, reasons, tolerance = boundary_eligibility(
        replay_error,
        repeat_error,
        factual_pairs,
        factual_pairs_repeat,
        candidate_pairs,
        candidate_pairs_repeat,
    )
    if not isinstance(record.get("boundary_eligible"), bool) or (
        eligible != record["boundary_eligible"]
    ):
        raise ValueError("P026 boundary eligibility was not recomputed from raw nominal evidence")
    if reasons != record.get("invalid_boundary_reasons"):
        raise ValueError("P026 invalid-boundary reasons differ from raw nominal evidence")
    exact_values = {
        "replay_endpoint_vs_saved_boundary_max_abs": replay_error,
        "nominal_endpoint_repeat_max_abs": repeat_error,
        "replay_endpoint_tolerance": tolerance,
    }
    for key, expected_value in exact_values.items():
        if float(record[key]) != expected_value:
            raise ValueError(f"P026 nominal gate scalar mismatch: {key}")
    return {
        "verified_nominal_unedited_references": 2,
        "verified_boundary_endpoint_references": 0,
    }


def evidence_factual_endpoint(reference: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    path = Path(str(reference["path"])).resolve()
    with np.load(path, allow_pickle=False) as archive:
        factual = np.asarray(archive["factual_state"], dtype=np.float64)
        candidate_t0 = np.asarray(archive["candidate_t0_state"], dtype=np.float64)
    if factual.ndim != 2 or not len(factual):
        raise ValueError("raw factual state trace is empty")
    return factual[-1].copy(), candidate_t0.copy()


def raw_factual_matches_unedited(
    reference: dict[str, Any],
    nominal_reference: dict[str, Any],
    repeat_reference: dict[str, Any],
) -> bool:
    paths = [
        Path(str(item["path"])).resolve()
        for item in (reference, nominal_reference, repeat_reference)
    ]
    archives = [np.load(path, allow_pickle=False) for path in paths]
    try:
        actual, nominal, repeated = archives
        for field in ("state", "proprio", "physical_effect_probe", "task_effect"):
            actual_values = np.asarray(actual[f"factual_{field}"], dtype=np.float64)
            nominal_values = np.asarray(nominal[f"factual_{field}"], dtype=np.float64)
            repeat_values = np.asarray(repeated[f"factual_{field}"], dtype=np.float64)
            if not (
                actual_values.shape == nominal_values.shape == repeat_values.shape
            ):
                return False
            observed_repeat = float(
                np.max(np.abs(nominal_values - repeat_values), initial=0.0)
            )
            guarded = (
                0.0 if observed_repeat == 0.0 else observed_repeat * 1.05 + 1e-12
            )
            floor = 1e-6 if field == "task_effect" else 1e-10
            envelope = max(guarded, floor)
            if (
                float(np.max(np.abs(actual_values - nominal_values), initial=0.0)) > envelope
                or float(np.max(np.abs(actual_values - repeat_values), initial=0.0)) > envelope
            ):
                return False
        for field in ("rgb_sha256", "depth_sha256", "contact_pairs", "contact_offsets"):
            actual_values = np.asarray(actual[f"factual_{field}"])
            nominal_values = np.asarray(nominal[f"factual_{field}"])
            repeat_values = np.asarray(repeated[f"factual_{field}"])
            if not (
                np.array_equal(actual_values, nominal_values)
                and np.array_equal(nominal_values, repeat_values)
            ):
                return False
        return True
    finally:
        for archive in archives:
            archive.close()


def verify_saved_boundary_fidelity(
    manifest: dict[str, Any], allowed_root: Path
) -> dict[str, int]:
    """Independently recompute the source-boundary endpoint gate from raw NPZs."""

    if manifest.get("protocol_version") == "P026-v1":
        verified = verify_p026_nominal_gate(manifest, allowed_root)
        expected = source_boundary_state(manifest, allowed_root)
        checked = 0
        passing_references: dict[str, dict[str, Any]] = {}
        for block in manifest["blocks"]:
            for reference in [
                *block["endpoint_evidence"].values(), block["repeat_evidence"]
            ]:
                factual_endpoint, candidate_t0 = evidence_factual_endpoint(reference)
                for endpoint in (factual_endpoint, candidate_t0):
                    if endpoint.shape != expected.shape:
                        raise ValueError("P026 edited endpoint state shape mismatch")
                checked += 1
            for pair in block["endpoint_strength_curve"]:
                for label in ("left_evidence", "right_evidence"):
                    reference = pair[label]
                    passing_references[str(reference["sha256"])] = reference
        for reference in passing_references.values():
            if not raw_factual_matches_unedited(
                reference,
                manifest["nominal_unedited_evidence"],
                manifest["nominal_unedited_repeat_evidence"],
            ):
                raise ValueError(
                    "P026 certified witness factual trace differs from raw unedited nominal"
                )
        verified["verified_boundary_endpoint_references"] = checked
        verified["verified_source_faithful_passing_endpoint_references"] = len(
            passing_references
        )
        return verified

    expected = source_boundary_state(manifest, allowed_root)
    all_errors: list[float] = []
    repeat_errors: list[float] = []
    checked = 0
    for block in manifest["blocks"]:
        legal = [float(value) for value in block["static_diff_schema"]["legal_endpoints"]]
        nominal_reference = block["endpoint_evidence"][str(legal[0])]
        nominal_endpoint, nominal_candidate_t0 = evidence_factual_endpoint(nominal_reference)
        repeat_endpoint, repeat_candidate_t0 = evidence_factual_endpoint(
            block["repeat_evidence"]
        )
        for endpoint in (nominal_endpoint, nominal_candidate_t0):
            if endpoint.shape != expected.shape:
                raise ValueError("source boundary/raw endpoint state shape mismatch")
            all_errors.append(float(np.max(np.abs(endpoint - expected))))
        for endpoint in (repeat_endpoint, repeat_candidate_t0):
            if endpoint.shape != expected.shape:
                raise ValueError("source boundary/repeat endpoint state shape mismatch")
            all_errors.append(float(np.max(np.abs(endpoint - expected))))
        repeat_errors.extend([
            float(np.max(np.abs(nominal_endpoint - repeat_endpoint))),
            float(np.max(np.abs(nominal_candidate_t0 - repeat_candidate_t0))),
        ])
        for reference in block["endpoint_evidence"].values():
            factual_endpoint, candidate_t0 = evidence_factual_endpoint(reference)
            if factual_endpoint.shape != expected.shape or candidate_t0.shape != expected.shape:
                raise ValueError("source boundary/endpoint sweep state shape mismatch")
            all_errors.extend([
                float(np.max(np.abs(factual_endpoint - expected))),
                float(np.max(np.abs(candidate_t0 - expected))),
            ])
            checked += 1
    observed_replay = max(all_errors, default=0.0)
    observed_repeat = max(repeat_errors, default=0.0)
    declared_replay = float(manifest["replay_endpoint_vs_saved_boundary_max_abs"])
    declared_repeat = float(manifest["nominal_endpoint_repeat_max_abs"])
    # The generator's declared values come from the unedited nominal runs.  All
    # certified endpoint factual prefixes must be equal as well, so the raw
    # evidence maximum cannot exceed the declared gate tolerance.
    if observed_replay > float(manifest["replay_endpoint_tolerance"]):
        raise ValueError("raw factual endpoint exceeds saved-boundary tolerance")
    if observed_repeat > float(manifest["endpoint_repeat_absolute_cap"]):
        raise ValueError("raw endpoint repeat exceeds absolute cap")
    if declared_replay > float(manifest["replay_endpoint_tolerance"]):
        raise ValueError("declared replay endpoint error fails its own gate")
    if declared_repeat > float(manifest["endpoint_repeat_absolute_cap"]):
        raise ValueError("declared nominal repeat error fails its own gate")
    expected_tolerance = min(
        max(1e-10, 1.05 * declared_repeat + 1e-12),
        float(manifest["saved_endpoint_absolute_cap"]),
    )
    if expected_tolerance != float(manifest["replay_endpoint_tolerance"]):
        raise ValueError("declared replay tolerance was not recomputed from repeat error")
    return {"verified_boundary_endpoint_references": checked}


def validate_derived_pair_accounting(
    block: dict[str, Any],
    derived_passing_keys: list[tuple[float, float]],
    derived_failure_counts: dict[str, int],
) -> None:
    """Require the manifest to report the complete raw-derived endpoint sweep."""

    declared_keys = [
        (float(pair["left_value"]), float(pair["right_value"]))
        for pair in block["endpoint_strength_curve"]
    ]
    if declared_keys != derived_passing_keys:
        raise ValueError(
            "manifest passing endpoint set differs from complete raw recomputation"
        )
    expected_pairs = len(derived_passing_keys)
    if int(block["certified_endpoint_pairs"]) != expected_pairs:
        raise ValueError("certified endpoint count differs from raw recomputation")
    if int(block["unique_witness"]) != int(expected_pairs > 0):
        raise ValueError("unique witness flag differs from raw recomputation")
    expected_failures = dict(sorted(derived_failure_counts.items()))
    if block.get("failure_reason_counts") != expected_failures:
        raise ValueError("failure reason counts differ from complete raw recomputation")


def verify_complete_endpoint_pair_sweep(
    block: dict[str, Any], record: dict[str, Any]
) -> int:
    """Recompute every legal endpoint pair, including all reported negatives.

    This closes an asymmetric-verification loophole: validating only declared
    passing pairs would let a producer delete a true-positive baseline witness
    and relabel the block as all-failed.
    """

    legal = [float(value) for value in block["static_diff_schema"]["legal_endpoints"]]
    bindings = {
        "snapshot_id": record["snapshot_sha256"],
        "factual_action_id": record["factual_action_id"],
        "candidate_action_id": record["candidate_action_id"],
        "factual_action_sha256": record["factual_action_sha256"],
        "candidate_action_sha256": record["candidate_sha256"],
        "simulator_model_sha256": record["simulator_model_contact_schema_sha256"],
        "task_asset_sha256": record["task_asset_bddl_sha256"],
        "engine_identity": record["engine_identity"],
    }
    traces: dict[float, tuple[RolloutTrace, RolloutTrace, dict[str, Any]]] = {}
    for value in legal:
        traces[value] = load_endpoint(
            block["endpoint_evidence"][str(value)], block, value, bindings, record
        )
    repeat_factual, repeat_candidate, _ = load_endpoint(
        block["repeat_evidence"], block, legal[0], bindings, record
    )
    factual_envelope = repeat_envelope((traces[legal[0]][0], repeat_factual))
    candidate_envelope = repeat_envelope((traces[legal[0]][1], repeat_candidate))
    factual_stable = trace_observation_digest_equal(
        traces[legal[0]][0], repeat_factual
    )
    if factual_stable != bool(block["factual_observation_repeat_stable"]):
        raise ValueError("factual observation repeat flag differs from raw evidence")

    source = read_json(str(Path(str(record["rollout"])).resolve()))
    task_id = str(source["task"])
    passing_keys: list[tuple[float, float]] = []
    failure_counts: dict[str, int] = {}
    derived_results: dict[tuple[float, float], Any] = {}
    for left_pos, left_value in enumerate(legal):
        for right_value in legal[left_pos + 1:]:
            certificate = AliasCertificate(
                factual_action_id=str(record["factual_action_id"]),
                candidate_action_id=str(record["candidate_action_id"]),
                top_k=1,
                search_objective_terms=(
                    f"block_selector:{record['block_selector']}",
                    "realized_contact_support",
                    "fixed_endpoint_sweep",
                    "factual_transcript_constraint",
                    "candidate_physical_effect_separation",
                ),
                compiler_seed=int(record["environment_seed"]) + int(record["selector_seed"]),
                simulator="LIBERO-MuJoCo",
                task_id=task_id,
                snapshot_id=str(record["snapshot_sha256"]),
                allowed_activation_lag=1,
                factual_action_sha256=str(record["factual_action_sha256"]),
                candidate_action_sha256=str(record["candidate_sha256"]),
                evidence_sha256=(
                    str(block["endpoint_evidence"][str(left_value)]["sha256"]),
                    str(block["endpoint_evidence"][str(right_value)]["sha256"]),
                    str(block["repeat_evidence"]["sha256"]),
                    str(record["nominal_unedited_evidence"]["sha256"]),
                    str(record["nominal_unedited_repeat_evidence"]["sha256"]),
                ),
                static_config_sha256=(
                    str(traces[left_value][2]["static_runtime"]["live_static_sha256"]),
                    str(traces[right_value][2]["static_runtime"]["live_static_sha256"]),
                ),
                simulator_model_sha256=str(record["simulator_model_contact_schema_sha256"]),
                task_asset_sha256=str(record["task_asset_bddl_sha256"]),
                engine_identity=str(record["engine_identity"]),
                parameter_addresses=(str(block["parameter_metadata"]["engine_field"]),),
                factual_observation_repeat_stable=factual_stable,
            )
            result = certify_alias_pair(
                traces[left_value][0],
                traces[right_value][0],
                traces[left_value][1],
                traces[right_value][1],
                certificate,
                factual_envelope,
                candidate_envelope,
            )
            source_factual_match = raw_factual_matches_unedited(
                block["endpoint_evidence"][str(left_value)],
                record["nominal_unedited_evidence"],
                record["nominal_unedited_repeat_evidence"],
            ) and raw_factual_matches_unedited(
                block["endpoint_evidence"][str(right_value)],
                record["nominal_unedited_evidence"],
                record["nominal_unedited_repeat_evidence"],
            )
            key = (left_value, right_value)
            if result.passed and source_factual_match:
                passing_keys.append(key)
                derived_results[key] = result
            else:
                for failure in result.failures:
                    failure_counts[failure] = failure_counts.get(failure, 0) + 1
                if not source_factual_match:
                    failure = "factual_deviates_from_unedited_nominal"
                    failure_counts[failure] = failure_counts.get(failure, 0) + 1

    validate_derived_pair_accounting(block, passing_keys, failure_counts)
    declared = {
        (float(pair["left_value"]), float(pair["right_value"])): pair
        for pair in block["endpoint_strength_curve"]
    }
    for key in passing_keys:
        pair = declared[key]
        result = derived_results[key]
        if pair.get("measurements") != dict(result.measurements):
            raise ValueError("passing pair measurements differ from raw recomputation")
        if pair.get("certificate_sha256") != result.certificate_sha256:
            raise ValueError("passing pair certificate differs from raw recomputation")
        if pair.get("certificate_payload") != json.loads(result.canonical_payload):
            raise ValueError("passing pair canonical payload differs from raw recomputation")
        verify_pair(pair, block, record)
    return len(passing_keys)


def verify_manifest_record(manifest: dict[str, Any], allowed_root: Path) -> dict[str, int]:
    source_verified = verify_source_rollout(manifest, allowed_root)
    admission_verified = (
        verify_source_admission(manifest, allowed_root)
        if manifest.get("protocol_version") == "P026-v1" else {}
    )
    compiler_verified = (
        verify_compiler_lock(manifest, allowed_root)
        if manifest.get("protocol_version") == "P026-v1" else {}
    )
    matrix_run_verified = (
        verify_matrix_run_lock(manifest, allowed_root)
        if manifest.get("protocol_version") == "P026-v1" else {}
    )
    boundary_verified = verify_saved_boundary_fidelity(manifest, allowed_root)
    load_baseline_static(manifest)
    selector_verified = (
        verify_selector_block_reconstruction(manifest)
        if manifest.get("protocol_version") == "P026-v1" else len(manifest["blocks"])
    )
    verified_pairs = 0
    for block in manifest["blocks"]:
        legal = [float(value) for value in block["static_diff_schema"]["legal_endpoints"]]
        for value in legal:
            verify_raw_reference(
                block["endpoint_evidence"][str(value)], block, value, manifest
            )
        verify_raw_reference(block["repeat_evidence"], block, legal[0], manifest)
        verify_repeat(block, manifest)
        if manifest.get("protocol_version") == "P026-v1":
            verified_pairs += verify_complete_endpoint_pair_sweep(block, manifest)
        else:
            for pair in block["endpoint_strength_curve"]:
                verify_pair(pair, block, manifest)
                verified_pairs += 1
    return {
        **source_verified,
        **admission_verified,
        **compiler_verified,
        **matrix_run_verified,
        **boundary_verified,
        "verified_selected_blocks": selector_verified,
        "verified_blocks": len(manifest["blocks"]),
        "verified_certificate_pairs": verified_pairs,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--allowed-root", required=True)
    args = parser.parse_args()
    root = Path(args.allowed_root).resolve()
    if root != Path("<PERSONAL_RESEARCH_ROOT>").resolve():
        raise ValueError("allowed root must be the configured personal data root")
    manifest_path = Path(args.manifest).resolve()
    if manifest_path == root or root not in manifest_path.parents:
        raise ValueError("manifest outside allowed root")
    manifest = read_json(str(manifest_path))
    from analyze_p025_fixed_budget import validate_record

    protocol = str(manifest.get("protocol_version"))
    if protocol not in {"P025-v5", "P026-v1"}:
        raise ValueError(f"unsupported protocol: {protocol}")
    validate_record(
        manifest, root, verify_evidence=True, expected_protocol=protocol
    )
    verified = verify_manifest_record(manifest, root)
    print(json.dumps({
        "manifest_sha256": sha256_file(manifest_path),
        **verified,
        "passed": True,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
