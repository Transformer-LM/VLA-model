#!/usr/bin/env python3
"""Target-WAM-blind mixed categorical/continuous CEM search for P027.

This script is a search-stage sanity implementation.  It never reads a WAM,
policy score, certificate outcome, or another selector's pool.  It searches
over one exact MuJoCo geom address and one log-scaled physical value, using
only factual feasibility and candidate physical-effect divergence.  The
result is a frozen selection plan consumed by a separate certifier wrapper.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Sequence

import numpy as np

from certify_continuous_contact_support import (
    SimulatorStepCounter,
    boundary_eligibility,
    canonical_array_sha256,
    capture_model_static_arrays,
    continuous_rollout,
    geom_blocks,
    hash_static_arrays,
    repeat_envelope,
    sha256_file,
    static_field_hashes,
    trace_contact_union,
    trace_matches_unedited_reference,
)
from certify_policy_boundary_alias import FAMILY_VALUES, existing, new_output


SEARCH_SELECTORS = ("candidate-contact-cem", "scene-cem")


def trace_max_abs(left: Any, right: Any, field: str) -> float:
    """Maximum aligned absolute trace difference for one FrameTrace field."""

    if len(left.frames) != len(right.frames):
        return math.inf
    maximum = 0.0
    for left_frame, right_frame in zip(left.frames, right.frames):
        lhs = np.asarray(getattr(left_frame, field), dtype=np.float64)
        rhs = np.asarray(getattr(right_frame, field), dtype=np.float64)
        if lhs.shape != rhs.shape or not np.all(np.isfinite(lhs)) or not np.all(np.isfinite(rhs)):
            return math.inf
        maximum = max(maximum, float(np.max(np.abs(lhs - rhs), initial=0.0)))
    return maximum


def trace_digest(trace: Any) -> str:
    """Compact exact digest for audit/replay without persisting another video copy."""

    digest = hashlib.sha256()
    for frame in trace.frames:
        for field in ("state", "proprio", "physical_effect_probe", "task_effect"):
            values = np.ascontiguousarray(np.asarray(getattr(frame, field), dtype=np.float64))
            digest.update(field.encode("ascii"))
            digest.update(str(values.shape).encode("ascii"))
            digest.update(values.tobytes())
        digest.update(frame.rgb_sha256.encode("ascii"))
        digest.update(frame.depth_sha256.encode("ascii"))
        digest.update(json.dumps(frame.contact_geom_pairs, separators=(",", ":")).encode("ascii"))
    return digest.hexdigest()


def categorical_update(
    count: int,
    elite_indices: Sequence[int],
    smoothing: float,
) -> np.ndarray:
    """Smoothed categorical MLE with a uniform floor."""

    if count < 1:
        raise ValueError("categorical support must be nonempty")
    if not 0.0 < smoothing <= 1.0:
        raise ValueError("smoothing must be in (0, 1]")
    prior = np.full(count, 1.0 / count, dtype=np.float64)
    if not elite_indices:
        return prior
    empirical = np.bincount(np.asarray(elite_indices, dtype=np.int64), minlength=count)
    empirical = empirical.astype(np.float64) / len(elite_indices)
    probabilities = smoothing * prior + (1.0 - smoothing) * empirical
    probabilities /= probabilities.sum()
    return probabilities


def truncated_log_sample(
    rng: np.random.Generator,
    mean: float,
    std: float,
    lower: float,
    upper: float,
) -> float:
    if not lower < upper or std <= 0:
        raise ValueError("invalid log-space sampling interval")
    for _ in range(64):
        value = float(rng.normal(mean, std))
        if lower <= value <= upper:
            return value
    return float(np.clip(mean, lower, upper))


def choose_distinct_blocks(
    evaluations: Sequence[dict[str, Any]],
    maximum: int,
) -> list[dict[str, Any]]:
    """Choose best feasible activated proposal per address with stable ties."""

    best: dict[str, dict[str, Any]] = {}
    for row in evaluations:
        if not row["feasible"] or not row["candidate_activated"] or not row.get(
            "certifiable_proxy", False
        ):
            continue
        address = str(row["parameter_address"])
        incumbent = best.get(address)
        key = (
            float(row["score"]),
            float(row["candidate_task_effect_max_abs_between_values"]),
            float(row["candidate_physical_effect_max_abs_between_values"]),
            -int(row["evaluation_index"]),
        )
        incumbent_key = (
            (
                float(incumbent["score"]),
                float(incumbent["candidate_task_effect_max_abs_between_values"]),
                float(incumbent["candidate_physical_effect_max_abs_between_values"]),
                -int(incumbent["evaluation_index"]),
            )
            if incumbent is not None else None
        )
        if incumbent_key is None or key > incumbent_key:
            best[address] = row
    return sorted(
        best.values(),
        key=lambda row: (
            -float(row["score"]),
            -float(row["candidate_task_effect_max_abs_between_values"]),
            -float(row["candidate_physical_effect_max_abs_between_values"]),
            str(row["parameter_address"]),
        ),
    )[:maximum]


def evaluation_rank_key(row: dict[str, Any]) -> tuple[float, float, float, int]:
    """Deterministic descending physics-oracle ranking key."""

    return (
        -float(row["score"]),
        -float(row["candidate_task_effect_max_abs_between_values"]),
        -float(row["candidate_physical_effect_max_abs_between_values"]),
        int(row["evaluation_index"]),
    )


def sample_distinct_log_pair(
    rng: np.random.Generator,
    mean: float,
    std: float,
    lower: float,
    upper: float,
) -> tuple[float, float]:
    """Sample an ordered, non-degenerate pair from the continuous domain."""

    minimum_gap = max(1e-6, 0.01 * (upper - lower))
    first = truncated_log_sample(rng, mean, std, lower, upper)
    second = first
    for _ in range(64):
        second = truncated_log_sample(rng, mean, std, lower, upper)
        if abs(second - first) >= minimum_gap:
            break
    if abs(second - first) < minimum_gap:
        second = lower if abs(first - lower) >= minimum_gap else upper
    return tuple(sorted((float(first), float(second))))


def verify_source_admission(
    rollout_path: Path,
    arrays_path: Path,
    admission_path: Path,
) -> dict[str, str]:
    payload = json.loads(admission_path.read_text(encoding="utf-8"))
    if (
        payload.get("kind") != "israc_source_admission_replay_v1"
        or payload.get("passed") is not True
        or payload.get("policy_identity_verified") is not True
        or payload.get("policy_lock_verified") is not True
        or payload.get("source_rollout_sha256") != sha256_file(rollout_path)
        or payload.get("source_arrays_sha256") != sha256_file(arrays_path)
    ):
        raise ValueError("source admission is invalid or bound to another source")
    return {"path": str(admission_path), "sha256": sha256_file(admission_path)}


def verify_search_run_lock(
    args: argparse.Namespace,
    *,
    rollout_path: Path,
    admission_path: Path,
    support_path: Path,
    output_path: Path,
) -> dict[str, str]:
    lock_path = existing(args.search_run_lock)
    payload = json.loads(lock_path.read_text(encoding="utf-8"))
    expected_invocation = {
        "rollout": str(rollout_path),
        "source_admission_report": str(admission_path),
        "support_code": str(support_path),
        "output": str(output_path),
        "candidate_index": args.candidate_index,
        "candidate_chunks": args.candidate_chunks,
        "family": args.family,
        "selector": args.selector,
        "search_seed": args.search_seed,
        "generations": args.generations,
        "population": args.population,
        "elite_count": args.elite_count,
        "smoothing": args.smoothing,
        "min_log_std_fraction": args.min_log_std_fraction,
        "max_selected_blocks": args.max_selected_blocks,
        "height": args.height,
        "width": args.width,
    }
    expected_executions = 2 + 2 * args.generations * args.population
    references = {
        "search_script": Path(__file__).resolve(),
        "compiler_dependency": Path(__file__).resolve().parent
        / "certify_continuous_contact_support.py",
        "selector_support": Path(__file__).resolve().parent
        / "certify_policy_boundary_alias.py",
        "repeat_envelope_support": Path(__file__).resolve().parent
        / "libero_m0_alias.py",
        "certificate_core": Path(__file__).resolve().parent
        / "israc"
        / "certificate.py",
        "rollout": rollout_path,
        "source_admission_report": admission_path,
        "support_entrypoint": support_path / "collect_e1_paired_rollouts.py",
    }
    manifest = json.loads(rollout_path.read_text(encoding="utf-8"))
    references["source_arrays"] = Path(str(manifest["arrays"])).resolve()
    references["task_asset_bddl"] = Path(str(manifest["bddl"])).resolve()
    if (
        payload.get("kind") != "p027_search_run_lock"
        or payload.get("protocol_version") != "P027-search-sanity-v1"
        or payload.get("frozen") is not True
        or payload.get("compiler_target_wam_blind") is not True
        or payload.get("invocation") != expected_invocation
        or int(payload.get("precommitted_search_continuous_executions", -1))
        != expected_executions
    ):
        raise ValueError("search run lock does not match the invocation")
    for key, path in references.items():
        reference = payload.get(key)
        if reference != {"path": str(path), "sha256": sha256_file(path)}:
            raise ValueError(f"search run lock reference drift: {key}")
    return {"path": str(lock_path), "sha256": sha256_file(lock_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rollout", required=True)
    parser.add_argument("--source-admission-report", required=True)
    parser.add_argument("--search-run-lock", required=True)
    parser.add_argument("--support-code", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--candidate-index", type=int, required=True)
    parser.add_argument("--candidate-chunks", type=int, default=4)
    parser.add_argument("--family", choices=sorted(FAMILY_VALUES), default="compliance")
    parser.add_argument("--selector", choices=SEARCH_SELECTORS, required=True)
    parser.add_argument("--search-seed", type=int, default=0)
    parser.add_argument("--generations", type=int, default=2)
    parser.add_argument("--population", type=int, default=6)
    parser.add_argument("--elite-count", type=int, default=2)
    parser.add_argument("--smoothing", type=float, default=0.20)
    parser.add_argument("--min-log-std-fraction", type=float, default=0.08)
    parser.add_argument("--max-selected-blocks", type=int, default=1)
    parser.add_argument("--height", type=int, default=64)
    parser.add_argument("--width", type=int, default=64)
    args = parser.parse_args()
    if (
        args.generations < 1
        or args.population < 2
        or not 1 <= args.elite_count <= args.population
        or args.max_selected_blocks != 1
        or args.candidate_chunks < 1
        or not 0.0 < args.min_log_std_fraction <= 1.0
    ):
        raise ValueError("invalid CEM or rollout arguments")

    rollout_path = existing(args.rollout)
    admission_path = existing(args.source_admission_report)
    support_path = existing(args.support_code)
    output = new_output(args.output)
    search_run_lock_reference = verify_search_run_lock(
        args,
        rollout_path=rollout_path,
        admission_path=admission_path,
        support_path=support_path,
        output_path=output,
    )
    manifest = json.loads(rollout_path.read_text(encoding="utf-8"))
    if manifest.get("source_schema_version") != "P026-source-v1":
        raise ValueError("P027 search requires a provenance-bearing P026 source")
    arrays_path = existing(manifest["arrays"])
    admission_reference = verify_source_admission(rollout_path, arrays_path, admission_path)
    with np.load(arrays_path) as archive:
        states = np.asarray(archive["boundary_states"], dtype=np.float64)
        chunks = np.asarray(archive["action_chunks"], dtype=np.float32)
        boundary_steps = np.asarray(archive["boundary_steps"], dtype=np.int64)
    index = int(args.candidate_index)
    if not 1 <= index < min(len(states), len(chunks)):
        raise IndexError(index)

    sys.path.insert(0, str(support_path))
    from collect_e1_paired_rollouts import ObservableModes, capture, robot_vector
    from libero.libero.envs import SegmentationRenderEnv
    from libero.libero import benchmark

    env = SegmentationRenderEnv(
        bddl_file_name=str(existing(manifest["bddl"])),
        camera_heights=args.height,
        camera_widths=args.width,
        camera_depths=True,
        camera_segmentations="instance",
    )
    evaluations: list[dict[str, Any]] = []
    selected_rows: list[dict[str, Any]] = []
    try:
        env.seed(int(manifest["seed"]))
        env.reset()
        initialization = manifest.get("initialization", {})
        if initialization.get("source") != "libero_benchmark_initial_state":
            raise ValueError("P027 search requires benchmark-initialized full-prefix replay")
        suite = benchmark.get_benchmark_dict()[str(initialization["suite_name"])]()
        initial_states = suite.get_task_init_states(int(initialization["task_id"]))
        benchmark_initial_state = np.asarray(
            initial_states[int(initialization["episode_index"])], dtype=np.float64
        ).copy()
        env.set_init_state(benchmark_initial_state)
        episode_start_state = np.asarray(env.sim.get_state().flatten(), dtype=np.float64).copy()
        modes = ObservableModes(env.env)

        def initialize_episode() -> dict[str, np.ndarray]:
            modes.capture()
            env.seed(int(manifest["seed"]))
            env.reset()
            return env.set_init_state(benchmark_initial_state)

        original_solref = np.asarray(env.sim.model.geom_solref, dtype=np.float64).copy()
        original_friction = np.asarray(env.sim.model.geom_friction, dtype=np.float64).copy()
        static_arrays = capture_model_static_arrays(env.sim.model)
        static_sha256 = hash_static_arrays(static_arrays)
        static_fields = static_field_hashes(static_arrays)
        wait_steps = int(manifest.get("num_steps_wait", 0))
        wait_action = np.asarray([0.0] * 6 + [-1.0], dtype=np.float32)
        warmup = np.repeat(wait_action[None, :], wait_steps, axis=0)
        factual_actions = np.concatenate((warmup, *chunks[:index]), axis=0)
        suffix_end = min(index + args.candidate_chunks, len(chunks))
        candidate_actions = np.concatenate(chunks[index:suffix_end], axis=0)
        factual_action_id = f"warmup_{wait_steps}_policy_prefix_0_to_{index - 1}"
        candidate_action_id = f"policy_suffix_{index}_to_{suffix_end - 1}"
        values = tuple(float(value) for value in FAMILY_VALUES[args.family])
        counter = SimulatorStepCounter()

        nominal_factual, nominal_candidate, _, _, _ = continuous_rollout(
            env, modes, initialize_episode, capture, robot_vector,
            original_solref, original_friction, factual_actions, candidate_actions,
            "nominal_unedited", (), 0.0, args.family, values,
            factual_action_id, candidate_action_id, args.height, args.width,
            counter, static_arrays, unedited=True,
        )
        nominal_factual_repeat, nominal_candidate_repeat, _, _, _ = continuous_rollout(
            env, modes, initialize_episode, capture, robot_vector,
            original_solref, original_friction, factual_actions, candidate_actions,
            "nominal_unedited", (), 0.0, args.family, values,
            factual_action_id, candidate_action_id, args.height, args.width,
            counter, static_arrays, unedited=True,
        )
        factual_pairs = trace_contact_union(nominal_factual)
        factual_pairs_repeat = trace_contact_union(nominal_factual_repeat)
        candidate_pairs = trace_contact_union(nominal_candidate)
        candidate_pairs_repeat = trace_contact_union(nominal_candidate_repeat)
        replay_error = float(np.max(np.abs(
            np.asarray(nominal_factual.frames[-1].state) - states[index]
        )))
        repeat_error = trace_max_abs(nominal_factual, nominal_factual_repeat, "state")
        eligible, reasons, tolerance = boundary_eligibility(
            replay_error, repeat_error, factual_pairs, factual_pairs_repeat,
            candidate_pairs, candidate_pairs_repeat,
        )
        factual_pool = geom_blocks(env.sim.model, factual_pairs) if eligible else {}
        if args.selector == "candidate-contact-cem":
            pool = geom_blocks(env.sim.model, candidate_pairs) if eligible else {}
            certifier_selector = "candidate-contact"
        else:
            pool = geom_blocks(env.sim.model) if eligible else {}
            certifier_selector = "random-scene"

        addresses = sorted(pool)
        if eligible and addresses:
            lower = math.log(min(values))
            upper = math.log(max(values))
            log_mean = 0.5 * (lower + upper)
            log_std = 0.5 * (upper - lower)
            minimum_std = args.min_log_std_fraction * (upper - lower)
            probabilities = np.full(len(addresses), 1.0 / len(addresses), dtype=np.float64)
            rng = np.random.default_rng(
                int(manifest["seed"]) * 1_000_003 + args.search_seed * 97 + 27
            )
            for generation in range(args.generations):
                generation_rows: list[dict[str, Any]] = []
                for population_index in range(args.population):
                    address_index = int(rng.choice(len(addresses), p=probabilities))
                    address = addresses[address_index]
                    geom_ids = tuple(int(value) for value in pool[address])
                    log_left, log_right = sample_distinct_log_pair(
                        rng, log_mean, max(log_std, minimum_std), lower, upper
                    )
                    parameter_values = (
                        float(math.exp(log_left)),
                        float(math.exp(log_right)),
                    )
                    block_id = f"{args.selector}_{args.family}:{address}"
                    traces = [
                        continuous_rollout(
                            env, modes, initialize_episode, capture, robot_vector,
                            original_solref, original_friction, factual_actions,
                            candidate_actions, block_id, geom_ids, value, args.family,
                            values, factual_action_id, candidate_action_id,
                            args.height, args.width, counter, static_arrays,
                        )
                        for value in parameter_values
                    ]
                    factual_left, candidate_left = traces[0][0], traces[0][1]
                    factual_right, candidate_right = traces[1][0], traces[1][1]
                    feasible = all(
                        trace_matches_unedited_reference(
                            factual_trace, nominal_factual, nominal_factual_repeat
                        )
                        for factual_trace in (factual_left, factual_right)
                    )
                    activated = all(
                        any(block_id in frame.active_parameter_blocks for frame in trace.frames)
                        for trace in (candidate_left, candidate_right)
                    )
                    task_effect = trace_max_abs(
                        candidate_left, candidate_right, "task_effect"
                    )
                    physical_effect = trace_max_abs(
                        candidate_left, candidate_right, "physical_effect_probe"
                    )
                    state_effect = trace_max_abs(
                        candidate_left, candidate_right, "state"
                    )
                    candidate_noise = repeat_envelope(
                        (nominal_candidate, nominal_candidate_repeat)
                    )
                    score = (
                        max(0.0, state_effect - float(candidate_noise.state))
                        if feasible and activated and math.isfinite(state_effect)
                        else -1.0
                    )
                    certifiable_proxy = bool(
                        score > 0.0
                        and task_effect > float(candidate_noise.task_effect)
                    )
                    row = {
                        "evaluation_index": len(evaluations),
                        "generation": generation,
                        "population_index": population_index,
                        "parameter_address": address,
                        "geom_ids": list(geom_ids),
                        "parameter_values": list(parameter_values),
                        "log_parameter_values": [log_left, log_right],
                        "feasible": bool(feasible),
                        "candidate_activated": bool(activated),
                        "certifiable_proxy": certifiable_proxy,
                        "score": score,
                        "candidate_repeat_state_envelope": float(candidate_noise.state),
                        "candidate_repeat_task_effect_envelope": float(
                            candidate_noise.task_effect
                        ),
                        "candidate_task_effect_max_abs_between_values": task_effect,
                        "candidate_physical_effect_max_abs_between_values": physical_effect,
                        "candidate_state_max_abs_between_values": state_effect,
                        "factual_trace_sha256": [
                            trace_digest(factual_left), trace_digest(factual_right)
                        ],
                        "candidate_trace_sha256": [
                            trace_digest(candidate_left), trace_digest(candidate_right)
                        ],
                    }
                    evaluations.append(row)
                    generation_rows.append(row)
                ranked = sorted(generation_rows, key=evaluation_rank_key)
                elites = [row for row in ranked if row["certifiable_proxy"]][
                    :args.elite_count
                ]
                elite_indices = [addresses.index(str(row["parameter_address"])) for row in elites]
                probabilities = categorical_update(len(addresses), elite_indices, args.smoothing)
                if elites:
                    elite_logs = np.asarray(
                        [
                            float(value)
                            for row in elites
                            for value in row["log_parameter_values"]
                        ],
                        dtype=np.float64,
                    )
                    log_mean = float(np.mean(elite_logs))
                    log_std = max(float(np.std(elite_logs)), minimum_std)
            selected_rows = choose_distinct_blocks(evaluations, args.max_selected_blocks)

        segment_steps = len(factual_actions) + len(candidate_actions)
        payload = {
            "kind": "p027_blackbox_mixed_cem_selection_plan",
            "protocol_version": "P027-search-sanity-v1",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "compiler_target_wam_blind": True,
            "target_wam_used_in_search": False,
            "search_objective_terms": [
                "factual_transcript_constraint",
                "candidate_state_divergence_above_repeat_noise",
                "candidate_task_effect_separation_above_repeat_noise",
                "mixed_categorical_continuous_cem",
            ],
            "rollout": str(rollout_path),
            "rollout_sha256": sha256_file(rollout_path),
            "arrays_sha256": sha256_file(arrays_path),
            "source_admission_report": admission_reference,
            "search_run_lock": search_run_lock_reference,
            "task_id": str(manifest["task"]),
            "environment_seed": int(manifest["seed"]),
            "candidate_chunk_index": index,
            "candidate_boundary_step": int(boundary_steps[index]),
            "candidate_suffix_end_index": suffix_end - 1,
            "candidate_sha256": canonical_array_sha256(candidate_actions),
            "factual_action_sha256": canonical_array_sha256(factual_actions),
            "parameter_family": args.family,
            "legal_domain": [min(values), max(values)],
            "selector": args.selector,
            "certifier_selector": certifier_selector,
            "search_seed": args.search_seed,
            "boundary_eligible": bool(eligible),
            "invalid_boundary_reasons": reasons,
            "replay_endpoint_vs_saved_boundary_max_abs": replay_error,
            "nominal_endpoint_repeat_max_abs": repeat_error,
            "replay_endpoint_tolerance": tolerance,
            "factual_contact_block_count": len(factual_pool),
            "visible_pool_count": len(addresses),
            "visible_pool_addresses": addresses,
            "baseline_static_physics_sha256": static_sha256,
            "baseline_static_field_sha256": static_fields,
            "nominal_factual_trace_sha256": trace_digest(nominal_factual),
            "nominal_factual_repeat_trace_sha256": trace_digest(nominal_factual_repeat),
            "nominal_candidate_trace_sha256": trace_digest(nominal_candidate),
            "nominal_candidate_repeat_trace_sha256": trace_digest(nominal_candidate_repeat),
            "actual_search_continuous_executions": 2 + 2 * len(evaluations),
            "actual_search_simulator_steps": counter.count,
            "expected_search_simulator_steps": (
                2 + 2 * len(evaluations)
            ) * segment_steps,
            "charged_search_simulator_step_cap": (
                2 + 2 * args.generations * args.population
            ) * segment_steps,
            "evaluations": evaluations,
            "selected_blocks": [
                {
                    "parameter_address": row["parameter_address"],
                    "geom_ids": row["geom_ids"],
                    "parameter_values": row["parameter_values"],
                    "search_score": row["score"],
                    "source_evaluation_index": row["evaluation_index"],
                }
                for row in selected_rows
            ],
            "arguments": vars(args),
            "claim_limit": (
                "Search-stage sanity only. The plan is target-WAM-blind and charges every "
                "search rollout, but publication evidence additionally requires a frozen code "
                "lock, immutable empty-directory launch record, matched certification, and "
                "independent reconstruction."
            ),
        }
        if counter.count != payload["expected_search_simulator_steps"]:
            raise RuntimeError("search simulator-step accounting mismatch")
    finally:
        env.close()

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + f".tmp.{os.getpid()}")
    encoded = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with temporary.open("x", encoding="utf-8") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.link(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    print(json.dumps({
        "boundary_eligible": payload["boundary_eligible"],
        "visible_pool_count": payload["visible_pool_count"],
        "evaluation_count": len(payload["evaluations"]),
        "selected_block_count": len(payload["selected_blocks"]),
        "actual_search_simulator_steps": payload["actual_search_simulator_steps"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
