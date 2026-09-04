#!/usr/bin/env bash
set -u

BASE=<PERSONAL_RESEARCH_ROOT>
IMPLEMENTATION="$BASE/workspace/israc/implementation"
SUPPORT="$BASE/workspace/pointmap-progress-belief/implementation"
RESULTS="$BASE/results/israc"

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$IMPLEMENTATION:$BASE/workspace/third_party/LIBERO"
export LIBERO_CONFIG_PATH="$BASE/config/libero"
export MUJOCO_GL=osmesa
export PYOPENGL_PLATFORM=osmesa
export LD_LIBRARY_PATH="$BASE/renderer-runtime/osmesa/prefix/usr/lib/x86_64-linux-gnu:$BASE/renderer-runtime/osmesa/prefix/lib/x86_64-linux-gnu"
export MESA_SHADER_CACHE_DIR="$BASE/renderer-runtime/osmesa/cache"
export XDG_CACHE_HOME="$BASE/renderer-runtime/osmesa/cache"

rollouts=(
  "$RESULTS/R020_strong_starvla_libero_goal_task0_ep0_seed11.json"
  "$RESULTS/R020_strong_starvla_libero_goal_task1_ep0_seed13.json"
  "$RESULTS/R020_strong_starvla_libero_goal_task1_ep0_seed13.json"
  "$RESULTS/R020_strong_starvla_libero_goal_task1_ep0_seed13.json"
  "$RESULTS/R020_strong_starvla_libero_goal_task2_ep0_seed17.json"
  "$RESULTS/R020_strong_starvla_libero_goal_task2_ep0_seed17.json"
  "$RESULTS/R020_strong_starvla_libero_goal_task2_ep0_seed17.json"
  "$RESULTS/R020_strong_starvla_libero_goal_task2_ep0_seed17.json"
)
tags=(goal_t0 goal_t1 goal_t1 goal_t1 goal_t2 goal_t2 goal_t2 goal_t2)
indices=(11 4 5 10 3 6 8 9)

for selector in candidate-contact random-scene; do
  for selector_seed in 0 1 2; do
    for row in "${!indices[@]}"; do
      rollout="${rollouts[$row]}"
      tag="${tags[$row]}"
      index="${indices[$row]}"
      output="$RESULTS/P024_${tag}_c$(printf '%02d' "$index")_${selector}_seed${selector_seed}.json"
      if [[ -e "$output" ]]; then
        echo "SKIP_EXISTING selector=$selector seed=$selector_seed tag=$tag index=$index output=$output"
        continue
      fi
      "$BASE/venvs/libero-eval-py310/bin/python" \
        "$IMPLEMENTATION/certify_policy_boundary_alias.py" \
        --rollout "$rollout" \
        --support-code "$SUPPORT" \
        --output "$output" \
        --candidate-index "$index" \
        --candidate-chunks 4 \
        --family compliance \
        --block-selector "$selector" \
        --match-israc-block-count \
        --selector-seed "$selector_seed"
      status=$?
      echo "BASELINE_RESULT selector=$selector seed=$selector_seed tag=$tag index=$index exit=$status output=$output"
    done
  done
done

"$BASE/venvs/libero-eval-py310/bin/python" - <<'PY'
from collections import Counter, defaultdict
import glob
import json
import os

root = "<PERSONAL_RESEARCH_ROOT>/results/israc"
rows = []
for path in sorted(glob.glob(os.path.join(root, "P024_*.json"))):
    with open(path, encoding="utf-8") as stream:
        payload = json.load(stream)
    rows.append({
        "file": os.path.basename(path),
        "selector": payload["block_selector"],
        "seed": payload["selector_seed"],
        "selected_blocks": payload["selected_block_count"],
        "attempted_pairs": sum(block["attempted_pairs"] for block in payload["blocks"]),
        "certified_pairs": payload["compiled_pair_count"],
        "passing_blocks": sum(block["certified_pairs"] > 0 for block in payload["blocks"]),
        "simulator_rollouts": payload["total_rollouts_including_selection"],
        "failure_counts": dict(Counter(
            reason
            for block in payload["blocks"]
            for reason, count in block["failure_reason_counts"].items()
            for _ in range(count)
        )),
    })

summary = {}
for selector in sorted({row["selector"] for row in rows}):
    chosen = [row for row in rows if row["selector"] == selector]
    summary[selector] = {
        "runs": len(chosen),
        "selected_blocks": sum(row["selected_blocks"] for row in chosen),
        "attempted_pairs": sum(row["attempted_pairs"] for row in chosen),
        "certified_pairs": sum(row["certified_pairs"] for row in chosen),
        "passing_blocks": sum(row["passing_blocks"] for row in chosen),
        "simulator_rollouts": sum(row["simulator_rollouts"] for row in chosen),
    }
print(json.dumps({"rows": rows, "summary": summary}, indent=2, sort_keys=True))
PY
