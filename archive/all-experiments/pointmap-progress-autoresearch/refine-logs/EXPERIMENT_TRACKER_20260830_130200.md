# Experiment Tracker

| Run ID | Milestone | Purpose | Variant | Split | Priority | Status | Notes |
|---|---|---|---|---|---|---|---|
| R000 | M0 | OSMesa RGB-D/seg/state restore | LIBERO scene1 | sanity | MUST | PASS | restore max error 0; dual-view RGB-D/instance available |
| R001 | M0 | one-task event collector | 6 controlled events | sanity | MUST | PASS | 6 samples; all arrays and manifest written |
| R002 | M0 | training runtime smoke | PointMap + oracle, 3 tasks | sanity | MUST | PASS | code path only; 18 samples/2 epochs are not science evidence |
| R003 | M0 | movable-reference replacement task | Scene6, 1 seed x 6 events | sanity | MUST | PASS | 6/6; fixture fallback removed |
| R004 | M0 | five explicit-family collector/audit | 5 families x 1 seed x 6 events | sanity | MUST | PASS | 30/30; unique scenes/family IDs; integrity checks zero-error; not science evidence |
| R010 | M0 | full E0 collection | 5 families ×12 seeds ×6 events | full | MUST | PASS | 360/360; 971 s; personal CPU OSMesa |
| R011 | M0 | dataset/geometry audit | deterministic checks | full | MUST | PASS | no failures; rigid-cloud medians 2.4–4.9 mm |
| R020 | M1 | RGB baseline | 5 folds ×3 seeds | task-heldout | MUST | INVALID | v1 deterministic adaptive-pool backward failure; rerun required |
| R021 | M1 | complete Depth baseline | 5 folds ×3 seeds | task-heldout | MUST | INVALID | v1 deterministic adaptive-pool backward failure; rerun required |
| R022 | M1 | PointMap diagnostic | 5 folds ×3 seeds | task-heldout | MUST | INVALID | v1 completed under superseded trainer hash; non-evidence |
| R023 | M1 | simulator pose oracle | 5 folds ×3 seeds | task-heldout | MUST | INVALID | v1 completed under superseded trainer hash; non-evidence |
| R020v2 | M1 | RGB baseline rerun | 5 folds ×3 seeds | task-heldout | MUST | PASS | 15/15 rows; trainer c2992f68 |
| R021v2 | M1 | complete Depth rerun | 5 folds ×3 seeds | task-heldout | MUST | PASS | 15/15 rows; trainer c2992f68 |
| R022v2 | M1 | PointMap rerun | 5 folds ×3 seeds | task-heldout | MUST | PASS | 15/15 rows; trainer c2992f68 |
| R023v2 | M1 | simulator pose oracle rerun | 5 folds ×3 seeds | task-heldout | MUST | PASS | 15/15 rows; trainer c2992f68 |
| R024 | M1 | aggregate/G0 gate | all B1 outputs | task-cluster | MUST | FAIL | oracle sanity failed; no representation conclusion; audit/claim review running |
| R100 | M2 | paired action-effect dataset | scripted physics | held actions/tasks | MUST | BLOCKED | only if G0 passes |
| R110 | M2 | transition variants | obs/no-trace/cmd/kin/shuffle/RGB | aliasing set | MUST | BLOCKED | only if R100 audit passes |
| R200 | M3 | VLA exact-state/on-policy dataset | StarVLA | held actions/tasks | MUST | BLOCKED | only if C1 E1 passes |
| R210 | M3 | VLA-distribution gate | transition variants | aliasing set | MUST | BLOCKED | only if R200 passes |
| R300 | M4 | oracle recovery gate | GT typed retract | closed loop | MUST | BLOCKED | only if E2 passes |
| R310 | M4 | learned typed rollback | frozen VLA | closed loop | MUST | BLOCKED | only if R300 passes |
