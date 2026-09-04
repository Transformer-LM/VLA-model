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

run_one() {
  local row="$1"
  local rollout="${rollouts[$row]}"
  local tag="${tags[$row]}"
  local index="${indices[$row]}"
  local output="$RESULTS/P025V5_GATE_${tag}_c$(printf '%02d' "$index")_israc_seed0.json"
  local log="$RESULTS/P025V5_GATE_${tag}_c$(printf '%02d' "$index")_israc_seed0.log"
  if [[ -e "$output" ]]; then
    echo "SKIP_EXISTING tag=$tag index=$index output=$output"
    return 0
  fi
  {
    echo "GPU_CHECK_BEFORE_LAUNCH tag=$tag index=$index"
    nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits
    nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits
    "$BASE/venvs/libero-eval-py310/bin/python" \
      "$IMPLEMENTATION/certify_continuous_contact_support.py" \
      --rollout "$rollout" \
      --support-code "$SUPPORT" \
      --output "$output" \
      --candidate-index "$index" \
      --candidate-chunks 4 \
      --family compliance \
      --block-selector israc-contact-subtraction \
      --selector-seed 0 \
      --max-selected-blocks 3 \
      --height 64 \
      --width 64
    echo "GATE_RESULT tag=$tag index=$index exit=$? output=$output"
  } >"$log" 2>&1
}

for wave_start in 0 4; do
  pids=()
  for offset in 0 1 2 3; do
    row=$((wave_start + offset))
    run_one "$row" &
    pids+=("$!")
  done
  for pid in "${pids[@]}"; do
    wait "$pid"
  done
done

"$BASE/venvs/libero-eval-py310/bin/python" - <<'PY'
import glob
import json
import os

rows = []
for path in sorted(glob.glob("<PERSONAL_RESEARCH_ROOT>/results/israc/P025V5_GATE_*.json")):
    with open(path, encoding="utf-8") as stream:
        payload = json.load(stream)
    rows.append({
        "file": os.path.basename(path),
        "eligible": payload["boundary_eligible"],
        "replay_error": payload["replay_endpoint_vs_saved_boundary_max_abs"],
        "repeat_error": payload["nominal_endpoint_repeat_max_abs"],
        "pool": payload["selector_visible_pool_count"],
        "selected_blocks": payload["selected_block_count"],
        "unique_witnesses": payload["unique_witness_count"],
        "raw_pairs": payload["raw_endpoint_pair_count"],
    })
summary = {
    "rows": rows,
    "eligible": sum(row["eligible"] for row in rows),
    "unique_witnesses": sum(row["unique_witnesses"] for row in rows),
    "raw_pairs": sum(row["raw_pairs"] for row in rows),
}
path = "<PERSONAL_RESEARCH_ROOT>/results/israc/P025V5_GATE_SUMMARY.json"
with open(path + ".tmp", "w", encoding="utf-8") as stream:
    json.dump(summary, stream, indent=2, sort_keys=True)
    stream.write("\n")
os.replace(path + ".tmp", path)
print(json.dumps(summary, indent=2, sort_keys=True))
PY
