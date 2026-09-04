"""Measure whether saved VLA chunk transitions replay from saved LIBERO states."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path("<PERSONAL_RESEARCH_ROOT>").resolve()


def checked(raw: str) -> Path:
    path = Path(raw).resolve()
    if path == ROOT or ROOT not in path.parents or not path.exists():
        raise ValueError(path)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rollout", required=True)
    parser.add_argument("--support-code", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rollout = checked(args.rollout)
    support = checked(args.support_code)
    output = Path(args.output).resolve()
    if output == ROOT or ROOT not in output.parents or output.exists():
        raise ValueError(output)
    manifest = json.loads(rollout.read_text(encoding="utf-8"))
    arrays = np.load(checked(manifest["arrays"]))
    states = np.asarray(arrays["boundary_states"], dtype=np.float64)
    chunks = np.asarray(arrays["action_chunks"], dtype=np.float32)
    sys.path.insert(0, str(support))
    from collect_e1_paired_rollouts import ObservableModes, restore_canonical
    from libero.libero.envs import SegmentationRenderEnv

    env = SegmentationRenderEnv(
        bddl_file_name=str(checked(manifest["bddl"])),
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
        for index in range(min(len(states) - 1, len(chunks))):
            restore_canonical(env, states[index], modes)
            for action in chunks[index]:
                modes.trace()
                env.step(action)
            end = np.asarray(env.sim.get_state().flatten(), dtype=np.float64)
            expected = states[index + 1]
            rows.append(
                {
                    "transition": index,
                    "state_max_abs": float(np.max(np.abs(end - expected))),
                    "state_l2": float(np.linalg.norm(end - expected)),
                }
            )
    finally:
        env.close()
    payload = {
        "kind": "israc_policy_transition_replay_probe",
        "claim_limit": "Controller-state/replay compatibility probe only; not alias evidence.",
        "rollout": str(rollout),
        "transition_count": len(rows),
        "max_state_max_abs": max((row["state_max_abs"] for row in rows), default=0.0),
        "rows": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, output)
    print(json.dumps({k: payload[k] for k in ("transition_count", "max_state_max_abs")}, sort_keys=True))


if __name__ == "__main__":
    main()
