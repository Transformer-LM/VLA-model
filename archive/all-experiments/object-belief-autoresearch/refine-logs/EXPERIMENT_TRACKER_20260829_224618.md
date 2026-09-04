# Experiment Tracker

| Run ID | Milestone | Purpose | System / Variant | Split | Metrics | Priority | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| R000 | M0 | environment smoke | personal MuJoCo env | tiny | witness + assertions | MUST | TODO | no installs |
| R001 | M0 | generator sanity | spatial pusher, 2 objects | tiny | leakage/chance/oracle checks | MUST | TODO | CPU |
| R101 | M1 | oracle upper bound | pose/velocity/shared/oracle | heterogeneous hard | assignment, NLL, wrong-object | MUST | TODO | seed 11 |
| R102 | M1 | oracle upper bound | same | heterogeneous hard | same | MUST | TODO | seed 22 |
| R103 | M1 | oracle upper bound | same | heterogeneous hard | same | MUST | TODO | seed 33 |
| R104 | M1 | negative control | same | homogeneous hard | false gain | MUST | TODO | 3 data seeds |
| R201 | M2 | learned main | shared MLP | nominal/OOD | prediction + identity | MUST | BLOCKED | requires M1 pass |
| R202 | M2 | learned main | fingerprint MLP | nominal/OOD | prediction + identity | MUST | BLOCKED | requires M1 pass |
| R203 | M2 | capacity control | history/matched MLP | nominal/OOD | prediction + identity | MUST | BLOCKED | requires M1 pass |
| R301 | M3 | mechanism ablation | shuffled/no fingerprint | hard | delta metrics | MUST | BLOCKED | requires M2 pass |
| R401 | M4 | decision consequence | frozen scripted policy | multi-template | wrong-object/task success | MUST | BLOCKED | requires M2 pass |
| R501 | M5 | nuisance controls | concurrent controls | camera shift | false interventions | NICE | BLOCKED | requires main result |

