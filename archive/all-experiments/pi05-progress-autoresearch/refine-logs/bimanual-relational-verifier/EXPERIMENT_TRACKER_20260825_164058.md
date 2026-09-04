# Experiment Tracker

| Run ID | Milestone | Purpose | System / Variant | Split | Primary Metrics | Priority | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| R001 | M0 | label sanity | FK/object relative transform visualization | 20 trajectories | manual alignment pass | MUST | TODO | plot against action timestamps |
| R002 | M0 | interface | π0.5 action normalization/chunk timing | replay | max alignment error | MUST | TODO | no training |
| R003 | M0 | label QA | relation-event label audit | 100 events | precision/recall by human audit | MUST | TODO | contact is proxy only |
| R004 | M0 | split QA | episode-level leakage test | all data | duplicate/near-duplicate count | MUST | TODO | block frame leakage |
| R005 | M1 | headroom | π0.5 fixed chunk | left/right lag pilot | success | MUST | TODO | paired states |
| R006 | M1 | headroom | periodic re-query | same | success, calls | MUST | TODO | matched calls |
| R007 | M1 | headroom | oracle relation trigger | same | success, recovery | MUST | TODO | GO if +10pp |
| R008 | M1 | ceiling | oracle safe stop | same | prevented unsafe failures | MUST | TODO | not method result |
| R009 | M2 | overfit | privileged-state relational dynamics | tiny train | state/event error | MUST | TODO | one task |
| R010 | M2 | causality | correct action condition | toy test | action sensitivity | MUST | TODO | reference |
| R011 | M2 | negative control | shuffled action | toy test | degradation vs R010 | MUST | TODO | must degrade |
| R012 | M2 | intervention | left-only action change | toy test | edge localization | MUST | TODO | L-O/L-R should change |
| R013 | M2 | intervention | right-only action change | toy test | edge localization | MUST | TODO | R-O/L-R should change |
| R014 | M2 | invariance | visual nuisance/SE3 transform | toy test | false response/equivariance | MUST | TODO | no physical change |
| R015 | M3 | baseline | observation-only monitor | validation | timely recall@5% FI | MUST | TODO | same encoder |
| R016 | M3 | baseline | global action-conditioned WAM | validation | timely recall@5% FI | MUST | TODO | matched params |
| R017 | M3 | baseline | object absolute-pose WAM | validation | timely recall@5% FI | MUST | TODO | no relation graph |
| R018 | M3 | method | relational WAM | validation | timely recall@5% FI | MUST | TODO | target +10pp |
| R019 | M3 | upper bound | oracle relations | validation | timely recall@5% FI | MUST | TODO | ceiling |
| R020 | M3 | calibration | conformal/risk calibration | calibration split | coverage, Brier, risk-coverage | MUST | TODO | frozen threshold |
| R021 | M4 | closed loop | fixed chunk | perturbed episodes | success | MUST | TODO | paired |
| R022 | M4 | closed loop | periodic replanning | same | success, calls | MUST | TODO | matched calls |
| R023 | M4 | closed loop | global WAM verifier | same | success, FI | MUST | TODO | strongest baseline |
| R024 | M4 | closed loop | relational verifier | same | success, FI | MUST | TODO | target +5pp |
| R025 | M4 | ceiling | oracle verifier | same | success | MUST | TODO | headroom |
| R026-R040 | M5 | final | 3 seeds + held-out shifts | final splits | CIs, failure taxonomy | MUST after gate | BLOCKED | unlock only after M4 |

