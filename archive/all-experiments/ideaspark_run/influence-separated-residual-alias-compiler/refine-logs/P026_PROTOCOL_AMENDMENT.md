# P026 protocol amendment and contamination disclosure

This amendment is frozen before the formal P026 matrix. It does not replace or
rewrite `P026_HELDOUT_PREREGISTRATION.md` or `P026_BOUNDARY_PLAN.json`.

## What was exposed before the final compiler-code lock

- One end-to-end sanity execution for task 3, candidate index 7, ISRAC seed 0
  was inspected. It was boundary-eligible and produced zero witnesses.
- A first matrix launcher then completed two unique cells before it was stopped:
  task 3 candidate indices 6 and 7, ISRAC seed 0. Their files were moved, with
  interrupted temporary evidence, into the personal
  `P026_PRE_FREEZE_DEBUG_20260901` archive. No baseline cell completed.
- The candidate-6 outcome was not inspected before the stop; nevertheless both
  cells are treated as exposed because their artifacts existed.

## Why execution was stopped

The stop was triggered by evidence-integrity review, not by a comparative gate:

1. manifests did not yet bind the exact compiler/verifier/analyzer code hashes;
2. nominal and nominal-repeat evidence kinds were not independently checked;
3. semantic evidence reverification was optional in the final analyzer;
4. cross-cell nominal invariants, zero-denominator bootstrap behavior, and
   cross-seed witness-key deduplication were not fail-closed.

These issues are repaired before the new lock and formal matrix.

## What remains unchanged

- the seven source trajectories and their policy/source-admission locks;
- all 21 outcome-blind boundary indices and their order;
- the three selectors and selector seeds 0, 1, 2;
- compliance endpoint values, three-block cap, candidate horizon, fresh-reset
  replay, certificate criteria, and the 2x plus CI-lower-above-1 decision rule;
- the rule that no source or boundary is removed after observing yield.

## Formal-run label

The new run starts from an empty, new `P026_FORMAL_V1` directory and re-executes
all 189 cells under one immutable compiler-code lock. It must be reported as:

`amended confirmatory with disclosed two-cell pre-freeze contamination`

It must not be described as a pristine outcome-locked experiment. A new episode-2
roster is required later if a pristine confirmatory claim is needed.
