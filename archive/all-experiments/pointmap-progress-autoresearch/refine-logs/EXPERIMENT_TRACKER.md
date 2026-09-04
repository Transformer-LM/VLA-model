# Experiment Tracker

Current repair cycle: E0/G0 v3 invariant-feature repair.

| Run | Block | Status | Evidence / next action |
|---|---|---|---|
| R010 | Full 360-sample collection | PASS | Dataset SHA-256 `ea15283b...` |
| R011 | Dataset/geometry audit | PASS | Exact audit SHA-256 `39f7bf51...` |
| R020–R023 v1 | Initial GPU launch | INVALID | RGB/Depth deterministic-pool failure; PointMap/Oracle obsolete code hash; excluded from evidence |
| R020–R023 v2 | Original four-modality grid | PASS (execution) | 60/60 fold-seed runs complete |
| R024 v2 | Original G0 aggregate | FAIL | Oracle sanity and both PointMap-vs-Depth performance gates failed |
| A001 | v2 independent integrity audit | WARN | No fabrication; replay/validation-trace provenance incomplete |
| C001 | v2 result-to-claim | NO → REPAIR | Main realized-trace novelty remained untested |
| R025 v3 | Deterministic invariant Oracle/PointMap probe | PASS | Oracle accuracy `0.9972`, macro-F1 `0.9965`; PointMap accuracy `0.9639`; 360 predictions stored |
| R026 v3 | Learned invariant Oracle 5×3 pilot | PASS | Macro-F1 `0.9532`; IMR `0.0278`; achieved FRR `0.0367` |
| R020–R023 v3 | Fresh matched four-modality rerun | PASS (execution) | 60/60 fold-seed runs, 4,320 test and 4,320 validation predictions, all jobs exit 0 |
| R024 v3 | Bootstrap aggregate | PRELIMINARY PASS | All five frozen G0 conditions pass; exact aggregate SHA-256 `7be5a00c...` |
| A002 | v3 independent integrity audit | WARN / G0 PASS | Exact 5/5 gate independently recomputed; three non-gate-changing provenance/protocol warnings retained |
| C002 | v3 result-to-claim | YES (narrow E0) | Conditional E1/B2 authorization; main realized-kinematic novelty remains untested |
| R100 | E1 environment/trace preflight | CODE REVIEW | CPU/OSMesa engineering check before physics outcome collection |
| R110 | E1 paired physics rollout pilot | BLOCKED | Starts only after R100 and fresh code review pass |

Repair changes remain frozen in `E0_REPAIR_PLAN_20260830_143000.md`; original positive G0 thresholds were not moved. The audited v3 pass supports controlled simulator-mask PointMap representation headroom only. E1/B2 is conditionally authorized after protocol repairs; no action-conditioned WAM, VLA improvement, runtime correction, closed-loop success, or real-robot benefit is yet supported.
