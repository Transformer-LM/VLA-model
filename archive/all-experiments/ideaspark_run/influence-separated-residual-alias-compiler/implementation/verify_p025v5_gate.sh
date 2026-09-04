#!/usr/bin/env bash
set -euo pipefail

BASE=<PERSONAL_RESEARCH_ROOT>
IMPLEMENTATION="$BASE/workspace/israc/implementation"
RESULTS="$BASE/results/israc"
PYTHON="$BASE/venvs/libero-eval-py310/bin/python"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$IMPLEMENTATION:$BASE/workspace/third_party/LIBERO"
export LIBERO_CONFIG_PATH="$BASE/config/libero"

verify_one() {
  local manifest="$1"
  local log="${manifest%.json}.verify.log"
  "$PYTHON" "$IMPLEMENTATION/verify_p025_manifest.py" \
    --manifest "$manifest" \
    --allowed-root "$BASE" >"$log" 2>&1
  echo "VERIFIED $manifest"
}

pids=()
for manifest in "$RESULTS"/P025V5_GATE_goal_t[0-9]_c[0-9][0-9]_israc_seed0.json; do
  verify_one "$manifest" &
  pids+=("$!")
  if (( ${#pids[@]} == 4 )); then
    for pid in "${pids[@]}"; do wait "$pid"; done
    pids=()
  fi
done
for pid in "${pids[@]}"; do wait "$pid"; done

"$PYTHON" - "$RESULTS" <<'PY'
import glob
import json
import os
import sys

root = sys.argv[1]
logs = sorted(glob.glob(os.path.join(root, "P025V5_GATE_goal_t*_c*_israc_seed0.verify.log")))
rows = [json.loads(open(path, encoding="utf-8").read().splitlines()[-1]) for path in logs]
summary = {
    "kind": "p025_v5_gate_formal_verification",
    "verified_manifest_count": len(rows),
    "all_passed": len(rows) == 8 and all(row["passed"] for row in rows),
    "verified_blocks": sum(row["verified_blocks"] for row in rows),
    "verified_certificate_pairs": sum(row["verified_certificate_pairs"] for row in rows),
    "source_executed_steps_by_manifest": [row["verified_source_executed_steps"] for row in rows],
    "records": rows,
}
path = os.path.join(root, "P025V5_GATE_FORMAL_VERIFICATION.json")
with open(path, "w", encoding="utf-8") as handle:
    json.dump(summary, handle, indent=2, sort_keys=True)
    handle.write("\n")
print(json.dumps(summary, indent=2, sort_keys=True))
if not summary["all_passed"]:
    raise SystemExit(1)
PY
