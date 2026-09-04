# E0 experiment code review

Verdict: **CHANGES_REQUIRED**

Reviewed scope:

- `implementation/geometry.py`
- `implementation/collect_relation_events.py`
- `implementation/audit_e0_dataset.py`
- `implementation/train_representation_pilot.py`
- `implementation/aggregate_e0_results.py`
- `EXPERIMENT_PLAN_20260830_130200.md`
- `PREFLIGHT_REPORT_20260830_130200.md`

The reviewer found that the initial implementation parsed, but could still admit an incomplete or invalid B0 dataset and could aggregate incomplete, duplicated, unaudited, or mixed-code B1 runs. The following were classified as blocking:

1. Enforce the exact preregistered 5-task x 12-seed x 6-event grid, with no missing or rejected cell and all decision classes in every task family.
2. Require `unobservable` to mask a genuinely visible target, preserve the exact original target mask, and reject unrelated NaN or masking changes.
3. Test PointMap projection separately on target/reference translation strata and camera-shift world-coordinate invariance, with task-camera coverage.
4. Use LIBERO's authoritative instance-value mapping and audit target/reference masks against simulator-pose motion.
5. Bind training and aggregation to a passing audit and exact dataset/manifest hashes; require exactly 4 modalities x 5 folds x 3 seeds, correct fold rotation, and one code/config version.
6. Replace run-level confidence intervals with task-family-cluster summaries; the validated aggregator is the only claim-bearing G0 result.
7. Prohibit non-finite metrics and non-standard JSON; store finite no-retraction thresholds and validation operating-point metrics.

Important corrections requested:

- Name efficiency measurements as head-only latency and verifier-tensor bytes unless end-to-end sensing/projection is measured.
- Enforce deterministic PyTorch/cuBLAS behavior and record runtime versions.
- State that probabilities are uncalibrated and thresholds are fitted only on the validation task family.
- Remove fragile fixture fallbacks.
- Add BDDL, arguments, audit, manifest, code hashes, and explicit completion markers.
- Embed the `not_executed_vla_actions` claim guard in the archive and record controlled intervention actor/delta without calling them VLA actions.

Confirmed non-blocking properties included correct label/success semantics, exact simulator and camera restoration, coherent depth back-projection, train-only feature normalization, validation-only threshold selection, correct FRR/IMR formulas, no intervention-value leakage into the verifier, and explicit representation-only claim limits.

This file records the first review. A second review is required after all fixes and before the full registered launch.
