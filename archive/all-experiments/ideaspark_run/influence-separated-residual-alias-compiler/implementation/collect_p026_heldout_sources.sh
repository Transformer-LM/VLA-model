#!/usr/bin/env bash
set -euo pipefail

BASE=<PERSONAL_RESEARCH_ROOT>
STAR="$BASE/workspace/cf-dynalign-starvla/source/starVLA"
LIBERO="$BASE/workspace/third_party/LIBERO"
IMPLEMENTATION="$BASE/workspace/israc/implementation"
RESULTS="$BASE/results/israc"
PYTHON="$BASE/venvs/libero-eval-py310/bin/python"
tasks=(3 4 5 6 7 8 9)
seeds=(19 23 29 31 37 41 43)

export CUDA_VISIBLE_DEVICES=""
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$STAR:$LIBERO"
export LIBERO_CONFIG_PATH="$BASE/config/libero"
export MUJOCO_GL=osmesa
export PYOPENGL_PLATFORM=osmesa
export LD_LIBRARY_PATH="$BASE/renderer-runtime/osmesa/prefix/usr/lib/x86_64-linux-gnu:$BASE/renderer-runtime/osmesa/prefix/lib/x86_64-linux-gnu"
export MESA_SHADER_CACHE_DIR="$BASE/renderer-runtime/osmesa/cache"
export XDG_CACHE_HOME="$BASE/renderer-runtime/osmesa/cache"
export MPLCONFIGDIR="$BASE/renderer-runtime/osmesa/cache/matplotlib"

for attempt in $(seq 1 120); do
  if ss -ltn 2>/dev/null | grep -q ':17778 '; then break; fi
  if (( attempt == 120 )); then
    echo "StarVLA server did not open port 17778" >&2
    exit 2
  fi
  sleep 1
done

for row in 0 1 2 3 4 5 6; do
  task="${tasks[$row]}"
  seed="${seeds[$row]}"
  output="$RESULTS/P026_HELDOUT_SOURCE_libero_goal_task${task}_ep0_seed${seed}.json"
  log="${output%.json}.log"
  if [[ -e "$output" ]]; then
    echo "SKIP_EXISTING task=$task seed=$seed"
    continue
  fi
  {
    echo "GPU_CHECK_BEFORE_CPU_COLLECTOR task=$task seed=$seed"
    nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits
    nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits
    "$PYTHON" "$IMPLEMENTATION/collect_starvla_natural_rollout.py" \
      --suite-name libero_goal \
      --task-id "$task" \
      --episode-index 0 \
      --num-steps-wait 10 \
      --output "$output" \
      --host 127.0.0.1 \
      --port 17778 \
      --seed "$seed" \
      --max-steps 400
    echo "SOURCE_RESULT task=$task seed=$seed exit=$? output=$output"
  } >"$log" 2>&1
done

"$PYTHON" - "$RESULTS" <<'PY'
import glob
import json
import os
import sys

root = sys.argv[1]
paths = sorted(glob.glob(os.path.join(root, "P026_HELDOUT_SOURCE_*.json")))
rows = [json.load(open(path, encoding="utf-8")) for path in paths]
summary = {
    "kind": "p026_heldout_source_collection_summary",
    "attempt_count": len(rows),
    "natural_success_count": sum(bool(row["done"]) and row["reward_max"] >= 1 for row in rows),
    "all_have_policy_provenance": all(
        row.get("source_schema_version") == "P026-source-v1"
        and "policy_provenance" in row for row in rows
    ),
    "records": [
        {
            "path": path,
            "task": row["task"],
            "seed": row["seed"],
            "steps": row["executed_steps"],
            "chunks": row["chunk_count"],
            "done": row["done"],
            "reward_max": row["reward_max"],
            "checkpoint_sha256": row.get("policy_provenance", {}).get("checkpoint_sha256"),
        }
        for path, row in zip(paths, rows)
    ],
}
path = os.path.join(root, "P026_HELDOUT_SOURCE_COLLECTION_SUMMARY.json")
with open(path, "w", encoding="utf-8") as handle:
    json.dump(summary, handle, indent=2, sort_keys=True)
    handle.write("\n")
print(json.dumps(summary, indent=2, sort_keys=True))
if len(rows) != 7 or not summary["all_have_policy_provenance"]:
    raise SystemExit(1)
PY
