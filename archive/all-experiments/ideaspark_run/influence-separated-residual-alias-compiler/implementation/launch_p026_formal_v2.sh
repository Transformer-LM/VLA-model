#!/usr/bin/env bash
set -euo pipefail

exec <PERSONAL_RESEARCH_ROOT>/venvs/libero-eval-py310/bin/python \
  <PERSONAL_RESEARCH_ROOT>/workspace/israc/implementation/run_p026_compiler_matrix.py \
  --plan <PERSONAL_RESEARCH_ROOT>/results/israc/P026_BOUNDARY_PLAN.json \
  --plan-sha256 11ae175df05e7b8c1bec50f518732def512352ec9cd4de1efdabb79acff33f03 \
  --compiler-lock <PERSONAL_RESEARCH_ROOT>/results/israc/P026_COMPILER_LOCK_V2.json \
  --compiler-lock-sha256 1e9516d777e78b86ccbeb16c82eeeaa6c77c855c1895808c4ce2415d483f6aa0 \
  --matrix-run-lock <PERSONAL_RESEARCH_ROOT>/results/israc/P026_FORMAL_MATRIX_LOCK_V2.json \
  --matrix-run-lock-sha256 ba1b442383448d41679f40e24a838fb6e7be761d0297e4144832a2984b653ee2 \
  --launch-record <PERSONAL_RESEARCH_ROOT>/results/israc/P026_FORMAL_LAUNCH_RECORD_V2.json \
  --launch-record-sha256 d4df177818d98a7699a9919ca15d092c256c95daddf863ca8f17237bdc652a65 \
  --implementation-root <PERSONAL_RESEARCH_ROOT>/workspace/israc/implementation \
  --support-code <PERSONAL_RESEARCH_ROOT>/workspace/pointmap-progress-belief/implementation \
  --python <PERSONAL_RESEARCH_ROOT>/venvs/libero-eval-py310/bin/python \
  --workers 4 \
  >> <PERSONAL_RESEARCH_ROOT>/results/israc/P026_FORMAL_V2_RUNNER.log 2>&1
