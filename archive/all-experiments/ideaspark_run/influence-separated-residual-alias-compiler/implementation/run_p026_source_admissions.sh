#!/usr/bin/env bash
set -euo pipefail

BASE=<PERSONAL_RESEARCH_ROOT>
IMPLEMENTATION="$BASE/workspace/israc/implementation"
RESULTS="$BASE/results/israc"
PYTHON="$BASE/venvs/libero-eval-py310/bin/python"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$IMPLEMENTATION:$BASE/workspace/third_party/LIBERO"
export LIBERO_CONFIG_PATH="$BASE/config/libero"
export MUJOCO_GL=osmesa
export PYOPENGL_PLATFORM=osmesa
export LD_LIBRARY_PATH="$BASE/renderer-runtime/osmesa/prefix/usr/lib/x86_64-linux-gnu:$BASE/renderer-runtime/osmesa/prefix/lib/x86_64-linux-gnu"
export MESA_SHADER_CACHE_DIR="$BASE/renderer-runtime/osmesa/cache"
export XDG_CACHE_HOME="$BASE/renderer-runtime/osmesa/cache"

sources=(
  "$RESULTS/R020_strong_starvla_libero_goal_task0_ep0_seed11.json"
  "$RESULTS/R020_strong_starvla_libero_goal_task1_ep0_seed13.json"
  "$RESULTS/R020_strong_starvla_libero_goal_task2_ep0_seed17.json"
)
outputs=(
  "$RESULTS/P026_SOURCE_ADMISSION_goal_t0_ep0_seed11.json"
  "$RESULTS/P026_SOURCE_ADMISSION_goal_t1_ep0_seed13.json"
  "$RESULTS/P026_SOURCE_ADMISSION_goal_t2_ep0_seed17.json"
)

pids=()
for index in 0 1 2; do
  if [[ -e "${outputs[$index]}" ]]; then
    echo "SKIP_EXISTING ${outputs[$index]}"
    continue
  fi
  nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits
  nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits
  "$PYTHON" "$IMPLEMENTATION/verify_source_rollout_replay.py" \
    --source "${sources[$index]}" \
    --output "${outputs[$index]}" \
    >"${outputs[$index]%.json}.log" 2>&1 &
  pids+=("$!")
done
for pid in "${pids[@]}"; do wait "$pid"; done

"$PYTHON" - "$RESULTS" <<'PY'
import glob
import json
import os
import sys

root = sys.argv[1]
paths = sorted(glob.glob(os.path.join(root, "P026_SOURCE_ADMISSION_goal_*.json")))
rows = [json.load(open(path, encoding="utf-8")) for path in paths]
summary = {
    "kind": "israc_source_admission_replay_summary_v1",
    "source_count": len(rows),
    "all_passed": len(rows) == 3 and all(row["passed"] for row in rows),
    "total_replayed_action_steps": sum(row["replayed_action_steps"] for row in rows),
    "total_state_digest_mismatches": sum(row["state_digest_mismatches"] for row in rows),
    "total_rgb_digest_mismatches": sum(row["rgb_digest_mismatches"] for row in rows),
    "total_contact_mismatches": sum(row["contact_mismatches"] for row in rows),
    "maximum_boundary_state_abs": max(row["boundary_state_max_abs"] for row in rows),
    "records": paths,
}
path = os.path.join(root, "P026_SOURCE_ADMISSION_SUMMARY.json")
with open(path, "w", encoding="utf-8") as handle:
    json.dump(summary, handle, indent=2, sort_keys=True)
    handle.write("\n")
print(json.dumps(summary, indent=2, sort_keys=True))
if not summary["all_passed"]:
    raise SystemExit(1)
PY
