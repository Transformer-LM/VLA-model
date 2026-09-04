#!/usr/bin/env bash
set -euo pipefail

GPU_INDEX=2
SESSION=israc-starvla-r004

IFS=, read -r memory_used utilization <<EOF
$(nvidia-smi -i "$GPU_INDEX" --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits)
EOF
memory_used="${memory_used// /}"
utilization="${utilization// /}"
compute_pids="$(nvidia-smi -i "$GPU_INDEX" --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^$/d' || true)"
printf 'PRELAUNCH_GPU2 mem=%s util=%s procs=%s\n' \
  "$memory_used" "$utilization" "${compute_pids:-none}"
test "$memory_used" -lt 500
test "$utilization" -le 5
test -z "$compute_pids"

if screen -ls 2>/dev/null | grep -q "$SESSION"; then
  echo "Refusing to replace existing personal session: $SESSION" >&2
  exit 2
fi
screen -dmS "$SESSION" bash -lc \
  'exec <PERSONAL_RESEARCH_ROOT>/workspace/israc/implementation/start_starvla_israc_server_r004.sh'
sleep 2
screen -ls | grep "$SESSION"
echo SERVER_R004_LAUNCHED
