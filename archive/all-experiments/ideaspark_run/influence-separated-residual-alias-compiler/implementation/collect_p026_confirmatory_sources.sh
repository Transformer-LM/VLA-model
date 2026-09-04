#!/usr/bin/env bash
set -euo pipefail

BASE=<PERSONAL_RESEARCH_ROOT>
STAR="$BASE/workspace/cf-dynalign-starvla/source/starVLA"
LIBERO="$BASE/workspace/third_party/LIBERO"
IMPLEMENTATION="$BASE/workspace/israc/implementation"
RESULTS="$BASE/results/israc"
PYTHON="$BASE/venvs/libero-eval-py310/bin/python"
POLICY_LOCK="$RESULTS/P026_POLICY_LOCK.json"
tasks=(3 4 5 6 7 8 9)
seeds=(47 53 59 61 67 71 73)

test -f "$POLICY_LOCK"
export CUDA_VISIBLE_DEVICES=""
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$IMPLEMENTATION:$STAR:$LIBERO"
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
  source="$RESULTS/P026_CONFIRM_SOURCE_libero_goal_task${task}_ep1_seed${seed}.json"
  source_log="${source%.json}.log"
  admission="$RESULTS/P026_CONFIRM_ADMISSION_libero_goal_task${task}_ep1_seed${seed}.json"
  admission_log="${admission%.json}.log"
  if [[ ! -e "$source" ]]; then
    {
      echo "GPU_CHECK_BEFORE_CPU_COLLECTOR task=$task episode=1 seed=$seed"
      nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits
      nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits
      "$PYTHON" "$IMPLEMENTATION/collect_starvla_natural_rollout.py" \
        --suite-name libero_goal \
        --task-id "$task" \
        --episode-index 1 \
        --num-steps-wait 10 \
        --output "$source" \
        --host 127.0.0.1 \
        --port 17778 \
        --seed "$seed" \
        --max-steps 400
      echo "SOURCE_RESULT task=$task episode=1 seed=$seed exit=$? output=$source"
    } >"$source_log" 2>&1
  fi
  if [[ ! -e "$admission" ]]; then
    set +e
    "$PYTHON" "$IMPLEMENTATION/verify_source_rollout_replay.py" \
      --source "$source" \
      --policy-lock "$POLICY_LOCK" \
      --output "$admission" >"$admission_log" 2>&1
    admission_status=$?
    set -e
    echo "ADMISSION_RESULT task=$task episode=1 seed=$seed exit=$admission_status output=$admission"
  fi
done

"$PYTHON" - "$RESULTS" <<'PY'
import glob
import json
import os
import sys

root = sys.argv[1]
sources = sorted(glob.glob(os.path.join(root, "P026_CONFIRM_SOURCE_*.json")))
admissions = sorted(glob.glob(os.path.join(root, "P026_CONFIRM_ADMISSION_*.json")))
admission_rows = [json.load(open(path, encoding="utf-8")) for path in admissions]
summary = {
    "kind": "p026_confirmatory_source_admission_summary",
    "policy_lock": os.path.join(root, "P026_POLICY_LOCK.json"),
    "attempt_count": len(sources),
    "admission_count": len(admissions),
    "admitted_count": sum(row["passed"] for row in admission_rows),
    "all_policy_identities_verified": all(
        row["policy_identity_verified"] for row in admission_rows
    ),
    "all_policy_locks_verified": all(row["policy_lock_verified"] for row in admission_rows),
    "admissions": admissions,
}
path = os.path.join(root, "P026_CONFIRM_SOURCE_ADMISSION_SUMMARY.json")
with open(path, "w", encoding="utf-8") as handle:
    json.dump(summary, handle, indent=2, sort_keys=True)
    handle.write("\n")
print(json.dumps(summary, indent=2, sort_keys=True))
if len(sources) != 7 or len(admissions) != 7:
    raise SystemExit(1)
PY
