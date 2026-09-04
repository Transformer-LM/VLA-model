"""Aggregate paired raw WAM/VLA pilot outputs without selecting scenes post hoc."""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Any


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    files = sorted(glob.glob(str(Path(args.root) / "anchored_*.json")))
    scenes: dict[tuple[str, str], dict[str, Any]] = {}
    for filename in files:
        payload = json.loads(Path(filename).read_text(encoding="utf-8"))
        for row in payload.get("records", []):
            key = (Path(filename).name, str(row["key"]))
            scenes.setdefault(key, {})[str(row["mode"])] = row

    complete = []
    for (filename, key), rows in scenes.items():
        required = {"baseline", "raw", "anchored", "oracle"}
        if set(rows) != required:
            continue
        b, r, a, o = (rows[name] for name in ("baseline", "raw", "anchored", "oracle"))
        complete.append({
            "file": filename,
            "key": key,
            "baseline_success": bool(b["done"]),
            "raw_success": bool(r["done"]),
            "anchored_success": bool(a["done"]),
            "oracle_success": bool(o["done"]),
            "baseline_steps": int(b["steps"]),
            "raw_steps": int(r["steps"]),
            "anchored_steps": int(a["steps"]),
            "oracle_steps": int(o["steps"]),
            "raw_action_l2": float(r["raw_vs_oracle_next_action_l2"]),
            "anchored_action_l2": float(r["anchored_vs_oracle_next_action_l2"]),
        })

    def count(name: str) -> int:
        return sum(int(row[name]) for row in complete)

    harmful = [
        row for row in complete
        if row["baseline_success"] and not row["raw_success"]
    ]
    rescued = [
        row for row in harmful if row["anchored_success"]
    ]
    output = {
        "schema": "state-repair-e1-aggregate-v1",
        "source_files": [Path(path).name for path in files],
        "n_complete_scenes": len(complete),
        "success_counts": {
            "baseline": count("baseline_success"),
            "raw": count("raw_success"),
            "anchored": count("anchored_success"),
            "oracle": count("oracle_success"),
        },
        "harmful_pairs": harmful,
        "n_harmful_pairs": len(harmful),
        "n_harmful_pairs_rescued_by_anchored": len(rescued),
        "mean_action_l2": {
            "raw": sum(row["raw_action_l2"] for row in complete) / max(len(complete), 1),
            "anchored": sum(row["anchored_action_l2"] for row in complete) / max(len(complete), 1),
        },
        "scenes": complete,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({
        "out": str(out),
        "n_complete_scenes": len(complete),
        "success_counts": output["success_counts"],
        "n_harmful_pairs": len(harmful),
        "n_rescued": len(rescued),
    }, indent=2))


if __name__ == "__main__":
    main()
