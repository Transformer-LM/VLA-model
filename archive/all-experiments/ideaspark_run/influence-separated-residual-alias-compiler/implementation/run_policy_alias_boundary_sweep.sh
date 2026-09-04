#!/usr/bin/env bash
set -u

BASE=<PERSONAL_RESEARCH_ROOT>
IMPLEMENTATION="$BASE/workspace/israc/implementation"
ROLLOUT="$BASE/results/israc/R010_strong_starvla_libero_goal_task6_ep0.json"
SUPPORT="$BASE/workspace/pointmap-progress-belief/implementation"

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$IMPLEMENTATION:$BASE/workspace/third_party/LIBERO"
export LIBERO_CONFIG_PATH="$BASE/config/libero"
export MUJOCO_GL=osmesa
export PYOPENGL_PLATFORM=osmesa
export LD_LIBRARY_PATH="$BASE/renderer-runtime/osmesa/prefix/usr/lib/x86_64-linux-gnu:$BASE/renderer-runtime/osmesa/prefix/lib/x86_64-linux-gnu"
export MESA_SHADER_CACHE_DIR="$BASE/renderer-runtime/osmesa/cache"
export XDG_CACHE_HOME="$BASE/renderer-runtime/osmesa/cache"

for index in 4 5 6 9 10 11 14 16; do
  output="$BASE/results/israc/P016_strong_starvla_alias_c$(printf '%02d' "$index").json"
  if [[ -e "$output" ]]; then
    echo "SKIP_EXISTING candidate_index=$index output=$output"
    continue
  fi
  "$BASE/venvs/libero-eval-py310/bin/python" \
    "$IMPLEMENTATION/certify_policy_boundary_alias.py" \
    --rollout "$ROLLOUT" \
    --support-code "$SUPPORT" \
    --output "$output" \
    --candidate-index "$index"
  status=$?
  echo "BOUNDARY_RESULT candidate_index=$index exit=$status output=$output"
done
