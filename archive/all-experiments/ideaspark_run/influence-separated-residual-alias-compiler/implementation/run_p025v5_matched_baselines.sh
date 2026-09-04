#!/usr/bin/env bash
set -euo pipefail

BASE=<PERSONAL_RESEARCH_ROOT>
IMPLEMENTATION="$BASE/workspace/israc/implementation"
SUPPORT="$BASE/workspace/pointmap-progress-belief/implementation"
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
selectors=(candidate-contact random-scene)
short_names=(candidate random)

gpu_snapshot() {
  nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits
  nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits
}

run_one() {
  local selector_row="$1"
  local boundary_row="$2"
  local selector="${selectors[$selector_row]}"
  local short="${short_names[$selector_row]}"
  local rollout="${rollouts[$boundary_row]}"
  local tag="${tags[$boundary_row]}"
  local index="${indices[$boundary_row]}"
  local output="$RESULTS/P025V5_MATCHED_${tag}_c$(printf '%02d' "$index")_${short}_seed0.json"
  local log="${output%.json}.log"
  if [[ -e "$output" ]]; then
    echo "SKIP_EXISTING selector=$selector tag=$tag index=$index output=$output"
    return 0
  fi
  {
    echo "GPU_CHECK_BEFORE_LAUNCH selector=$selector tag=$tag index=$index"
    gpu_snapshot
    "$PYTHON" "$IMPLEMENTATION/certify_continuous_contact_support.py" \
      --rollout "$rollout" \
      --support-code "$SUPPORT" \
      --output "$output" \
      --candidate-index "$index" \
      --candidate-chunks 4 \
      --family compliance \
      --block-selector "$selector" \
      --selector-seed 0 \
      --max-selected-blocks 3 \
      --height 64 \
      --width 64
    echo "BASELINE_RESULT selector=$selector tag=$tag index=$index exit=$? output=$output"
  } >"$log" 2>&1
}

# Four-way CPU waves; the jobs render MuJoCo evidence but do not reserve GPUs.
jobs=()
for selector_row in 0 1; do
  for boundary_row in 0 1 2 3 4 5 6 7; do
    jobs+=("$selector_row:$boundary_row")
  done
done
for wave_start in 0 4 8 12; do
  pids=()
  for offset in 0 1 2 3; do
    IFS=: read -r selector_row boundary_row <<<"${jobs[$((wave_start + offset))]}"
    run_one "$selector_row" "$boundary_row" &
    pids+=("$!")
  done
  for pid in "${pids[@]}"; do wait "$pid"; done
done

# Copy only the small immutable manifests into the matched-set namespace; all
# raw evidence remains singly stored under each original GATE manifest.
for row in 0 1 2 3 4 5 6 7; do
  tag="${tags[$row]}"
  index="${indices[$row]}"
  source="$RESULTS/P025V5_GATE_${tag}_c$(printf '%02d' "$index")_israc_seed0.json"
  target="$RESULTS/P025V5_MATCHED_${tag}_c$(printf '%02d' "$index")_israc_seed0.json"
  if [[ ! -e "$target" ]]; then cp "$source" "$target"; fi
done

echo "MATCHED_MANIFEST_COUNT $(find "$RESULTS" -maxdepth 1 -type f -name 'P025V5_MATCHED_*.json' | wc -l)"
