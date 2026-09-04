"""Discover candidate-only native MuJoCo contact geoms at one LIBERO snapshot."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np

from libero_m0_alias import require_personal, target_geom_ids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bddl", required=True)
    parser.add_argument("--support-code", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=20260831)
    parser.add_argument("--steps", type=int, default=32)
    parser.add_argument("--margin-m", type=float, default=0.010)
    parser.add_argument("--push-magnitude", type=float, default=0.8)
    return parser.parse_args()


def contact_pairs(env: Any, relevant: set[int]) -> set[tuple[int, int]]:
    pairs: set[tuple[int, int]] = set()
    for index in range(int(env.sim.data.ncon)):
        contact = env.sim.data.contact[index]
        a, b = int(contact.geom1), int(contact.geom2)
        if a in relevant or b in relevant:
            pairs.add(tuple(sorted((a, b))))
    return pairs


def execute_contacts(
    env: Any,
    modes: Any,
    restore_canonical: Any,
    start_state: np.ndarray,
    commands: np.ndarray,
    relevant: set[int],
) -> tuple[set[tuple[int, int]], list[list[tuple[int, int]]]]:
    restore_canonical(env, start_state, modes)
    union: set[tuple[int, int]] = set()
    per_frame: list[list[tuple[int, int]]] = []
    for command in commands:
        modes.trace()
        env.step(command)
        current = contact_pairs(env, relevant)
        union.update(current)
        per_frame.append(sorted(current))
    return union, per_frame


def main() -> None:
    args = parse_args()
    if os.environ.get("MUJOCO_GL", "").casefold() != "osmesa":
        raise RuntimeError("registered OSMesa environment is required")
    bddl = require_personal(Path(args.bddl), must_exist=True)
    support = require_personal(Path(args.support_code), must_exist=True)
    output = require_personal(Path(args.output), must_exist=False)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    sys.path.insert(0, str(support))
    from collect_e1_paired_rollouts import (  # type: ignore
        ObservableModes,
        construct_prestate,
        discover_valid_placement_template,
        goal_spec,
        restore_canonical,
    )
    from libero.libero.envs import SegmentationRenderEnv

    env = SegmentationRenderEnv(
        bddl_file_name=str(bddl),
        camera_heights=32,
        camera_widths=32,
        camera_depths=True,
        camera_segmentations="instance",
    )
    try:
        env.seed(args.seed)
        env.reset()
        modes = ObservableModes(env.env)
        relation, target, reference, argument = goal_spec(env)
        base = env.sim.get_state().flatten().copy()
        template = discover_valid_placement_template(
            env, modes, base, relation, target, reference, argument, 12
        )
        start, construction = construct_prestate(
            env, modes, base, target, reference, argument,
            np.asarray((1.0, 0.0), dtype=np.float64), args.margin_m,
            template, 12, 80,
        )
        if start is None:
            raise RuntimeError(f"prestate construction failed: {construction}")
        target_geoms = set(target_geom_ids(env, target))
        reference_geoms = set(target_geom_ids(env, reference))
        relevant = target_geoms | reference_geoms
        hold = np.zeros((args.steps, 7), dtype=np.float32)
        push = np.zeros((args.steps, 7), dtype=np.float32)
        push[: args.steps // 2, 0] = float(args.push_magnitude)
        factual, factual_frames = execute_contacts(env, modes, restore_canonical, start, hold, relevant)
        candidate, candidate_frames = execute_contacts(env, modes, restore_canonical, start, push, relevant)
        candidate_only = candidate - factual
        factual_geoms = {value for pair in factual for value in pair}
        candidate_geoms = {value for pair in candidate for value in pair}
        candidate_only_reference = sorted((candidate_geoms - factual_geoms) & reference_geoms)

        def named(pair: tuple[int, int]) -> dict[str, Any]:
            return {
                "geom_ids": list(pair),
                "geom_names": [env.sim.model.geom_id2name(value) for value in pair],
            }

        payload = {
            "kind": "israc_libero_candidate_contact_graph_probe",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "claim_limit": "Contact-graph discovery only; no certified alias or policy/WAM claim.",
            "task": bddl.name,
            "target": target,
            "reference": reference,
            "factual_pairs": [named(pair) for pair in sorted(factual)],
            "candidate_pairs": [named(pair) for pair in sorted(candidate)],
            "candidate_only_pairs": [named(pair) for pair in sorted(candidate_only)],
            "candidate_only_reference_geoms": [
                {"geom_id": value, "geom_name": env.sim.model.geom_id2name(value)}
                for value in candidate_only_reference
            ],
            "candidate_only_reference_geom_count": len(candidate_only_reference),
            "factual_per_frame_pair_counts": [len(value) for value in factual_frames],
            "candidate_per_frame_pair_counts": [len(value) for value in candidate_frames],
            "prestate_construction": construction,
            "arguments": vars(args),
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(temporary, output)
        print(json.dumps(payload, indent=2, sort_keys=True))
        raise SystemExit(0 if candidate_only_reference else 2)
    finally:
        env.close()


if __name__ == "__main__":
    main()
