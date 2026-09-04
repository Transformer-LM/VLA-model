#!/usr/bin/env bash
set -euo pipefail

ROOT="<PERSONAL_RESEARCH_ROOT>/workspace/object-belief-fingerprints"
CANONICAL="<PERSONAL_RESEARCH_ROOT_ALIAS>"
PYTHON="<PERSONAL_RESEARCH_ROOT>/workspace/openpi/.venv/bin/python"
SCRIPT="$ROOT/code/ifb_pilot.py"
DATA="$ROOT/data/ifb_main_v5_12000.npz"
RUN_TAG="20260829_ifb_v5"
RESULTS="$ROOT/results/$RUN_TAG"
LOGS="$ROOT/logs/$RUN_TAG"

parent_real="$(readlink -f <PERSONAL_RESEARCH_ROOT>)"
if [[ "$parent_real" != "$CANONICAL" ]]; then
  echo "AUTHORIZED_ROOT_MISMATCH $parent_real" >&2
  exit 90
fi

mkdir -p "$ROOT/code" "$ROOT/data" "$RESULTS" "$LOGS" "$ROOT/tmp" "$ROOT/cache/xdg" "$ROOT/cache/torch" "$ROOT/cache/cuda" "$ROOT/cache/matplotlib" "$ROOT/cache/numba"
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=4
export TMPDIR="$ROOT/tmp"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TORCH_HOME="$ROOT/cache/torch"
export CUDA_CACHE_PATH="$ROOT/cache/cuda"
export MPLCONFIGDIR="$ROOT/cache/matplotlib"
export NUMBA_CACHE_DIR="$ROOT/cache/numba"

"$PYTHON" "$SCRIPT" smoke --seed 7 --num-objects 3 | tee "$LOGS/R000_smoke.log"

SMALL="$ROOT/data/ifb_sanity_v5_2000.npz"
if [[ ! -s "$SMALL" ]]; then
  "$PYTHON" "$SCRIPT" generate --output "$SMALL" --episodes 2000 --num-objects 3 --context-steps 3 --seed 20260829 \
    > "$LOGS/R001_generate_sanity.log" 2>&1
fi
"$PYTHON" "$SCRIPT" audit --data "$SMALL" --output "$RESULTS/R001_dataset_audit.json" \
  --min-hard 10 \
  > "$LOGS/R001_dataset_audit.log" 2>&1

if [[ ! -s "$DATA" ]]; then
  "$PYTHON" "$SCRIPT" generate --output "$DATA" --episodes 12000 --num-objects 3 --context-steps 3 --seed 20260830 \
    > "$LOGS/R100_generate_main.log" 2>&1
fi
"$PYTHON" "$SCRIPT" audit --data "$DATA" --output "$RESULTS/R100_dataset_audit.json" \
  > "$LOGS/R100_dataset_audit.log" 2>&1

gpu_idle() {
  local gpu="$1"
  local mem util uuid app_count
  read -r mem util < <(nvidia-smi --id="$gpu" --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits | tr -d ' ' | tr ',' ' ')
  uuid="$(nvidia-smi --id="$gpu" --query-gpu=uuid --format=csv,noheader,nounits | tr -d ' ')"
  app_count="$(nvidia-smi --query-compute-apps=gpu_uuid --format=csv,noheader,nounits 2>/dev/null | grep -Fxc "$uuid" || true)"
  [[ "$mem" -le 500 && "$util" -le 5 && "$app_count" -eq 0 ]]
}

discover_gpus() {
  local attempt
  for attempt in {1..12}; do
    AVAILABLE=()
    for gpu in 2 3 0 1; do
      if gpu_idle "$gpu"; then
        AVAILABLE+=("$gpu")
      fi
    done
    if [[ "${#AVAILABLE[@]}" -gt 0 ]]; then
      break
    fi
    sleep 5
  done
  if [[ "${#AVAILABLE[@]}" -eq 0 ]]; then
    echo "NO_IDLE_GPU_AFTER_RECHECKS" >&2
    exit 91
  fi
  printf 'AVAILABLE_GPUS %s\n' "${AVAILABLE[*]}" | tee -a "$LOGS/orchestrator.log"
}

train_job() {
  local variant="$1" seed="$2" gpu="$3" run_id="$4"
  if ! gpu_idle "$gpu"; then
    echo "GPU_NOT_IDLE_AT_LAUNCH gpu=$gpu run=$run_id" >&2
    return 92
  fi
  echo "LAUNCH run=$run_id variant=$variant seed=$seed physical_gpu=$gpu" | tee -a "$LOGS/orchestrator.log"
  CUDA_VISIBLE_DEVICES="$gpu" "$PYTHON" "$SCRIPT" train \
    --data "$DATA" \
    --output "$RESULTS/${run_id}_${variant}_seed${seed}.json" \
    --variant "$variant" --seed "$seed" --epochs 80 --batch-size 1024 --hidden 256 --patience 12 --fixed-epochs \
    > "$LOGS/${run_id}_${variant}_seed${seed}.log" 2>&1
}

run_specs() {
  local specs=("$@")
  local cursor=0
  while [[ "$cursor" -lt "${#specs[@]}" ]]; do
    discover_gpus
    pids=()
    labels=()
    for gpu in "${AVAILABLE[@]}"; do
      if [[ "$cursor" -ge "${#specs[@]}" ]]; then
        break
      fi
      IFS=: read -r variant seed run_id <<< "${specs[$cursor]}"
      train_job "$variant" "$seed" "$gpu" "$run_id" &
      pids+=("$!")
      labels+=("$run_id")
      cursor=$((cursor + 1))
      # Give nvidia-smi time to observe the reservation before another check.
      sleep 2
    done
    for i in "${!pids[@]}"; do
      if ! wait "${pids[$i]}"; then
        echo "JOB_FAILED ${labels[$i]}" >&2
        exit 93
      fi
    done
  done
}

# M1a: privileged headroom only.  This cannot support the method claim.
run_specs \
  "shared:11:R101" "oracle:11:R111" \
  "shared:22:R102" "oracle:22:R112" \
  "shared:33:R103" "oracle:33:R113"

"$PYTHON" "$SCRIPT" summarize --stage headroom --split hard_id --results-dir "$RESULTS" --output "$RESULTS/M1a_headroom_summary.json" \
  > "$LOGS/M1a_summarize.log" 2>&1
"$PYTHON" "$SCRIPT" summarize --stage headroom --split heterogeneous_id --results-dir "$RESULTS" --output "$RESULTS/M1a_heterogeneous_report.json" \
  > "$LOGS/M1a_heterogeneous_report.log" 2>&1
headroom_status="$("$PYTHON" -c 'import json,sys; print(json.load(open(sys.argv[1]))["gate"]["status"])' "$RESULTS/M1a_headroom_summary.json")"
echo "M1A_GATE $headroom_status" | tee -a "$LOGS/orchestrator.log"
if [[ "$headroom_status" != "pass" ]]; then
  echo "KILL_NO_PRIVILEGED_HEADROOM" | tee "$RESULTS/FINAL_STATUS.txt"
  exit 0
fi

# M1b: the actual method gate.  Both systems receive the same allowed history.
run_specs \
  "system_id:11:R121" "full_history:11:R131" "full_history_aux:11:R141" \
  "system_id:22:R122" "full_history:22:R132" "full_history_aux:22:R142" \
  "system_id:33:R123" "full_history:33:R133" "full_history_aux:33:R143"

"$PYTHON" "$SCRIPT" summarize --stage method --split hard_id --results-dir "$RESULTS" --output "$RESULTS/M1b_method_summary.json" \
  > "$LOGS/M1b_summarize.log" 2>&1
"$PYTHON" "$SCRIPT" summarize --stage method --split heterogeneous_id --results-dir "$RESULTS" --output "$RESULTS/M1b_heterogeneous_report.json" \
  > "$LOGS/M1b_heterogeneous_report.log" 2>&1
method_status="$("$PYTHON" -c 'import json,sys; print(json.load(open(sys.argv[1]))["gate"]["status"])' "$RESULTS/M1b_method_summary.json")"
echo "M1B_GATE $method_status" | tee -a "$LOGS/orchestrator.log"
if [[ "$method_status" != "pass" ]]; then
  echo "KILL_METHOD_NOT_BETTER_THAN_FULL_HISTORY" | tee "$RESULTS/FINAL_STATUS.txt"
  exit 0
fi

echo "PASS_TO_NEXT_ABLATION_STAGE" | tee "$RESULTS/FINAL_STATUS.txt"
