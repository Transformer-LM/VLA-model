# Experiment Tracker

| Run ID | Milestone | Purpose | Variant | Split / task | Primary metric | Priority | Status | Stop note |
|---|---|---|---|---|---|---|---|---|
| R000 | M0 | remote preflight | read-only | personal paths/GPU/process | contract pass | MUST | TODO | any shared/root/process conflict |
| R001 | M1 | isolated clone | clean HEAD | source | commit/hash/tests | MUST | TODO | dirty base or wrong hash |
| R002 | M2 | cache tiny sanity | identity | 2 episodes | t+8/parity | MUST | TODO | padding/leak/parity fail |
| R003 | M2 | cache full | frozen Qwen+DINO | fixed tasks | manifest/hash | MUST | TODO | projected pilot>2h |
| R004 | M3 | nuisance/head train | full | D_head train/val | val nMSE | MUST | TODO | nonfinite |
| R005 | M3 | predictive controls | state/action/current/additive | D_head | strict gate | MUST | TODO | any C0 gate fails |
| R006 | M4 | C build | fixed derangement | D_adapter | match audit | MUST | TODO | C invalid |
| R007 | M4 | seed0 triplet | A/B/C | D_adapter | dose/stability | MUST | TODO | optimizer gate fail |
| R008 | M4 | seed0 P/Q calibration | P/Q | D_post folds0–3 | R²/matching | MUST | TODO | builder infeasible |
| R009 | M4 | wrapper timing | A+B+P/Q | cached 65 chunks | GPU-seconds | MUST | TODO | budget projection |
| R010 | M5 | 1k screen | baseline | task3/6 states0–4 | task SR/time | MUST | TODO | screen incomplete |
| R011 | M5 | 5k screen | baseline | task3/6 states0–4 | task SR/time | MUST | TODO | screen incomplete |
| R012 | M5 | 10k screen | baseline | task3/6 states0–4 | task SR/time | MUST | TODO | screen incomplete |
| R013 | M5 | seed/budget decision | 10→5→stop | ledger | H10/H5 | MUST | TODO | >7.2 GPUh |
| R014 | M6 | remaining triplets | A/B/C | selected seeds | training audit | MUST | TODO | any seed invalid |
| R015 | M6 | all P/Q + fold4 | per seed | D_post | eligibility table | MUST | TODO | Stage1/2 eligibility |
| R016 | M7 | Stage1 intact | A/B/C | fixed states | A−B/A−C | MUST | TODO | preregistered gate |
| R017 | M8 | Stage2 intervention | A_pred/A_Q | fixed states | Q−pred SR | CONDITIONAL | BLOCKED | requires R016 pass/all C2 eligible |
| R018 | M9 | result analysis | all planned | logs/results | stats/tables | MUST | BLOCKED | requires available results |
| R019 | M9 | integrity audit | all artifacts | full lineage | audit verdict | MUST | BLOCKED | required before claims |
| R020 | M9 | result-to-claim | passed stages | evidence | claim ceiling | MUST | BLOCKED | no paper writing |

