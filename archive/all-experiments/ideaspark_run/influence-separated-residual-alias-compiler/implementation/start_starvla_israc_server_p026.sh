#!/usr/bin/env bash
set -euo pipefail

BASE=<PERSONAL_RESEARCH_ROOT>
STAR="$BASE/workspace/cf-dynalign-starvla/source/starVLA"
CKPT="$BASE/checkpoints/cf-dynalign/cf_dynalign_baseline_libero_all_20260727_185501/final_model/pytorch_model.pt"
RUN_DIR="$BASE/results/israc/starvla_policy_support_p026_heldout"
LOG="$RUN_DIR/server.log"
GPU_INDEX=2

test -f "$CKPT"
mkdir -p "$RUN_DIR" "$BASE/tmp/israc" "$BASE/cache/israc-starvla"
if [[ -e "$LOG" ]]; then
  echo "Refusing to overwrite prior server log: $LOG" >&2
  exit 2
fi

IFS=, read -r gpu_uuid memory_used utilization < <(
  nvidia-smi -i "$GPU_INDEX" \
    --query-gpu=uuid,memory.used,utilization.gpu \
    --format=csv,noheader,nounits
)
gpu_uuid="${gpu_uuid// /}"
memory_used="${memory_used// /}"
utilization="${utilization// /}"
echo "GPU_PREFLIGHT index=$GPU_INDEX uuid=$gpu_uuid memory_mib=$memory_used utilization=$utilization"
if (( memory_used >= 500 || utilization > 5 )); then
  echo "GPU $GPU_INDEX is not eligible" >&2
  exit 3
fi
if nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory \
  --format=csv,noheader,nounits | grep -Fq "$gpu_uuid"; then
  echo "GPU $GPU_INDEX already has a compute process" >&2
  exit 3
fi

cd "$STAR"
export PYTHONDONTWRITEBYTECODE=1
export TOKENIZERS_PARALLELISM=false
export NO_ALBUMENTATIONS_UPDATE=1
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1
export HF_HOME="$BASE/cache/israc-starvla/huggingface"
export XDG_CACHE_HOME="$BASE/cache/israc-starvla/xdg"
export TMPDIR="$BASE/tmp/israc"
export PYTHONPATH="$STAR"
export CUDA_VISIBLE_DEVICES="$GPU_INDEX"

exec "$BASE/conda/envs/cf-dynalign/bin/python" \
  deployment/model_server/server_policy.py \
  --ckpt_path "$CKPT" \
  --port 17778 \
  --use_bf16 \
  --idle_timeout 7200 >"$LOG" 2>&1
