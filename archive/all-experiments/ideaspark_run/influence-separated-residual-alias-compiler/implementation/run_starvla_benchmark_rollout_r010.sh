#!/usr/bin/env bash
set -euo pipefail

BASE=<PERSONAL_RESEARCH_ROOT>
STAR="$BASE/workspace/cf-dynalign-starvla/source/starVLA"
LIBERO="$BASE/workspace/third_party/LIBERO"
IMPLEMENTATION="$BASE/workspace/israc/implementation"
RESULT="$BASE/results/israc/R010_strong_starvla_libero_goal_task6_ep0.json"

test -f "$IMPLEMENTATION/collect_starvla_natural_rollout.py"
ss -ltn 2>/dev/null | grep -q ':17778 '

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

exec "$BASE/venvs/libero-eval-py310/bin/python" \
  "$IMPLEMENTATION/collect_starvla_natural_rollout.py" \
  --suite-name libero_goal \
  --task-id 6 \
  --episode-index 0 \
  --num-steps-wait 10 \
  --output "$RESULT" \
  --host 127.0.0.1 \
  --port 17778 \
  --seed 7 \
  --max-steps 300
