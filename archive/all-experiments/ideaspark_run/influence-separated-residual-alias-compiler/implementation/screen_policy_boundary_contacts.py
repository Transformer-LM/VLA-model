"""Screen adjacent saved VLA chunks for candidate-only native contacts."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path("<PERSONAL_RESEARCH_ROOT>").resolve()


def existing(raw: str) -> Path:
    path = Path(raw).resolve()
    if path == ROOT or ROOT not in path.parents or not path.exists():
        raise ValueError(path)
    return path


def output_path(raw: str) -> Path:
    path = Path(raw).resolve()
    if path == ROOT or ROOT not in path.parents or path.exists():
        raise ValueError(path)
    return path


def pair_rows(env: Any) -> set[tuple[int, int]]:
    pairs = set()
    for index in range(int(env.sim.data.ncon)):
        contact = env.sim.data.contact[index]
        pairs.add(tuple(sorted((int(contact.geom1), int(contact.geom2)))))
    return pairs


def execute(env: Any, modes: Any, restore: Any, state: np.ndarray, actions: np.ndarray) -> set[tuple[int, int]]:
    restore(env, state, modes)
    pairs: set[tuple[int, int]] = set()
    for action in actions:
        modes.trace()
        env.step(np.asarray(action, dtype=np.float32))
        pairs.update(pair_rows(env))
    return pairs


def is_robot_body(name: str | None) -> bool:
    lowered = (name or "").casefold()
    return any(token in lowered for token in ("robot", "gripper", "panda"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rollout", required=True)
    parser.add_argument("--support-code", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rollout = existing(args.rollout)
    support = existing(args.support_code)
    output = output_path(args.output)
    manifest = json.loads(rollout.read_text(encoding="utf-8"))
    arrays = np.load(existing(manifest["arrays"]))
    states = np.asarray(arrays["boundary_states"], dtype=np.float64)
    chunks = np.asarray(arrays["action_chunks"], dtype=np.float32)

    sys.path.insert(0, str(support))
    from collect_e1_paired_rollouts import ObservableModes, restore_canonical
    from libero.libero.envs import SegmentationRenderEnv

    env = SegmentationRenderEnv(
        bddl_file_name=str(existing(manifest["bddl"])),
        camera_heights=64,
        camera_widths=64,
        camera_depths=True,
        camera_segmentations="instance",
    )
    rows = []
    try:
        env.seed(int(manifest["seed"]))
        env.reset()
        modes = ObservableModes(env.env)
        model = env.sim.model
        for candidate_index in range(1, min(len(states), len(chunks))):
            factual_pairs = execute(
                env, modes, restore_canonical, states[candidate_index - 1], chunks[candidate_index - 1]
            )
            candidate_pairs = execute(
                env, modes, restore_canonical, states[candidate_index], chunks[candidate_index]
            )
            new_pairs = candidate_pairs - factual_pairs
            factual_geoms = {geom_id for pair in factual_pairs for geom_id in pair}
            candidate_geoms = {geom_id for pair in candidate_pairs for geom_id in pair}
            candidate_only_geoms = candidate_geoms - factual_geoms
            body_groups: dict[str, set[int]] = {}
            named_pairs = []
            for left, right in sorted(new_pairs):
                pair_payload = []
                for geom_id in (left, right):
                    body_id = int(model.geom_bodyid[geom_id])
                    body_name = model.body_id2name(body_id)
                    geom_name = model.geom_id2name(geom_id)
                    pair_payload.append({"geom_id": geom_id, "geom_name": geom_name, "body_name": body_name})
                    if geom_id in candidate_only_geoms and not is_robot_body(body_name):
                        body_groups.setdefault(body_name or f"body_{body_id}", set()).add(geom_id)
                named_pairs.append(pair_payload)
            rows.append(
                {
                    "factual_chunk_index": candidate_index - 1,
                    "candidate_chunk_index": candidate_index,
                    "candidate_boundary_step": int(arrays["boundary_steps"][candidate_index]),
                    "factual_contact_pair_count": len(factual_pairs),
                    "candidate_contact_pair_count": len(candidate_pairs),
                    "candidate_only_pair_count": len(new_pairs),
                    "candidate_only_geom_count": len(candidate_only_geoms),
                    "candidate_only_pairs": named_pairs,
                    "nonrobot_body_groups": {
                        name: sorted(ids) for name, ids in sorted(body_groups.items())
                    },
                }
            )
    finally:
        env.close()
    payload = {
        "kind": "israc_policy_boundary_contact_screen",
        "claim_limit": (
            "Contact-graph screening at saved boundaries from one successful VLA trajectory; "
            "not a continuous-controller replay or alias certificate."
        ),
        "rollout": str(rollout),
        "transition_count": len(rows),
        "transitions_with_candidate_only_pairs": sum(row["candidate_only_pair_count"] > 0 for row in rows),
        "rows": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, output)
    print(json.dumps({
        "transition_count": payload["transition_count"],
        "transitions_with_candidate_only_pairs": payload["transitions_with_candidate_only_pairs"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
