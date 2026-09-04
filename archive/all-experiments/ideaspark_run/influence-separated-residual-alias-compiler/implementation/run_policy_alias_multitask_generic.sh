#!/usr/bin/env bash
set -u

if [[ "$#" -ne 3 ]]; then
  echo "Usage: $0 <rollout_json> <tag> <candidate_chunks>" >&2
  exit 2
fi

ROLLOUT="$1"
TAG="$2"
CANDIDATE_CHUNKS="$3"

BASE=<PERSONAL_RESEARCH_ROOT>
IMPLEMENTATION="$BASE/workspace/israc/implementation"
SUPPORT="$BASE/workspace/pointmap-progress-belief/implementation"
SCREEN_OUTPUT="$BASE/results/israc/P021_${TAG}_geom_screen.json"

test -f "$ROLLOUT"

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$IMPLEMENTATION:$BASE/workspace/third_party/LIBERO"
export LIBERO_CONFIG_PATH="$BASE/config/libero"
export MUJOCO_GL=osmesa
export PYOPENGL_PLATFORM=osmesa
export LD_LIBRARY_PATH="$BASE/renderer-runtime/osmesa/prefix/usr/lib/x86_64-linux-gnu:$BASE/renderer-runtime/osmesa/prefix/lib/x86_64-linux-gnu"
export MESA_SHADER_CACHE_DIR="$BASE/renderer-runtime/osmesa/cache"
export XDG_CACHE_HOME="$BASE/renderer-runtime/osmesa/cache"

if [[ -e "$SCREEN_OUTPUT" ]]; then
  echo "REUSE_SCREEN output=$SCREEN_OUTPUT"
else
  "$BASE/venvs/libero-eval-py310/bin/python" \
    "$IMPLEMENTATION/screen_policy_boundary_contacts.py" \
    --rollout "$ROLLOUT" \
    --support-code "$SUPPORT" \
    --output "$SCREEN_OUTPUT"
fi

mapfile -t indices < <(
  "$BASE/venvs/libero-eval-py310/bin/python" -c \
    'import json,sys; p=json.load(open(sys.argv[1])); print("\n".join(str(r["candidate_chunk_index"]) for r in p["rows"] if r["nonrobot_body_groups"]))' \
    "$SCREEN_OUTPUT"
)

printf 'ELIGIBLE tag=%s count=%s indices=%s\n' \
  "$TAG" "${#indices[@]}" "${indices[*]:-none}"

for index in "${indices[@]}"; do
  output="$BASE/results/israc/P022_${TAG}_c$(printf '%02d' "$index")_suffix${CANDIDATE_CHUNKS}_compliance.json"
  if [[ -e "$output" ]]; then
    echo "SKIP_EXISTING candidate_index=$index output=$output"
    continue
  fi
  "$BASE/venvs/libero-eval-py310/bin/python" \
    "$IMPLEMENTATION/certify_policy_boundary_alias.py" \
    --rollout "$ROLLOUT" \
    --support-code "$SUPPORT" \
    --output "$output" \
    --candidate-index "$index" \
    --candidate-chunks "$CANDIDATE_CHUNKS" \
    --family compliance
  status=$?
  echo "BOUNDARY_RESULT tag=$TAG candidate_index=$index exit=$status output=$output"
done
