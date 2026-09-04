# Experiment Tracker: PGR-Audit screen-first revision

| Run ID | Milestone | Purpose | Variant / atom | Split / task | Primary gate | GPU | Status | Stop / dependency |
|---|---|---|---|---|---|---:|---|---|
| R000 | M0 | freeze repaired protocol and inputs | protocol+manifest | local artifacts | parse/hash/consistency | 0 | DONE | renewed jury still required |
| R001 | M0 | renewed experiment-plan jury | fresh xhigh read-only | full plan | GO or pilot-authorizing CONDITIONAL-GO | 0 | TODO | blocks every remote write/GPU |
| R002 | M0 | historical remote read-only preflight | identity/path/GPU/process | personal root | liu_meng; personal target; no interference | 0 | DONE | snapshot never reusable for launch |
| R003 | M1 | isolated clone and lock materialization | clean bundle HEAD | personal workspace | source/env hashes | 0 | BLOCKED | requires R001 pass |
| R004 | M1 | implement guards, sealed evaluator, science code | all modules | CPU fixtures | unit tests | 0 | BLOCKED | requires R003 |
| R005 | M1 | fresh-agent code review | xhigh | exact implementation | no blocking issue | 0 | BLOCKED | requires R004 |
| R006 | M2 | first GPU envelope + 1k screen | baseline 1k | task3/6 states0..4 | witness + 10 sealed records | 1 | BLOCKED | requires R005 and fresh guards |
| R007 | M2 | 5k screen | baseline 5k | task3/6 states0..4 | 10 sealed records | 1 | BLOCKED | contiguous with screen class |
| R008 | M2 | 10k screen | baseline 10k | task3/6 states0..4 | 10 sealed records | 1 | BLOCKED | contiguous with screen class |
| R009 | M2 | checkpoint selector lock | automatic | 30 sealed records | qualifying selected SHA | 0 | BLOCKED | no qualifier = NO-RUN |
| R010 | M3 | conditional horizon timing | timing-only | one fixed task/state | real/forced 520-step time | 1 | BLOCKED | only if screen has no horizon fail |
| R011 | M4 | selected-checkpoint interface sanity | identity/direct/cache/hot | 2 episodes | max action error<1e-6 | 1 | BLOCKED | requires R009 |
| R012 | M4 | selected-task full cache | Qwen+DINO | frozen episodes | manifest/hash/no t+8 leak | 1 | BLOCKED | pilot admission |
| R013 | M5 | target, nuisance, head and controls | full+controls | D_head train/val | stable best-val artifacts | 1 | BLOCKED | requires R012 |
| R014 | M5 | strict predictive gate | full/control/derangements | D_head strict-test | C0 exact gates | 1 | BLOCKED | failure = H1 NO-RUN |
| R015 | M6 | fixed C donor map | Hungarian | D_adapter | feasibility/matching/hash | 0 | BLOCKED | requires R014 |
| R016 | M6 | sealed formal seed0 triplet | A/B/C seed0 | D_adapter | timing+safety visible only | 1 | BLOCKED | pilot admission |
| R017 | M6 | sealed formal seed0 PQ03 | P/Q seed0 | D_post folds0..3 | timing+safety visible only | 1 | BLOCKED | pilot admission |
| R018 | M6 | wrapper/fold3-shadow/parity timing | timing atoms | frozen traces | unit upper bounds | 1 | BLOCKED | pilot admission |
| R019 | M7 | automatic seed-count lock | 10→5→STOP | timing ledger | projection≤7.2 | 0 | BLOCKED | scientific fields denied |
| R020 | M8 | remaining triplets | A/B/C fixed seed prefix | D_adapter | all Stage1 seed rows | 1/launch | BLOCKED | requires R019 and fresh guard |
| R021 | M8 | remaining PQ03 | per fixed seed | folds0..3 | frozen P/Q artifacts | 1/launch | BLOCKED | no seed replacement |
| R022 | M8 | all per-seed parity bundles | cache+A→B+2 traces | frozen traces | <1e-6 | 1/launch | BLOCKED | all cost charged |
| R023 | M9 | one-time fold4 | P/Q eligibility | three episodes/task | immutable seed table | 1/launch | BLOCKED | all folds0..3/PQ/parity frozen |
| R024 | M10 | sealed Stage1 | A/B/C | fixed tasks/states | exact C1 gates | 1/launch | BLOCKED | requires every Stage1 row pass |
| R025 | M11 | sealed Stage2 | A_pred/A_Q removed | fixed tasks/states | exact C2 gates | 1/launch | BLOCKED | conditional on R024+all C2 rows |
| R026 | M12 | result analysis | parse-only | available artifacts | exact tables/stats | 0 | BLOCKED | requires completed/terminated path |
| R027 | M12 | experiment integrity audit | full lineage | all artifacts | audit verdict | 0 | BLOCKED | required before claims |
| R028 | M12 | result-to-claim | passed evidence only | claims | supported/partial/no | 0 | BLOCKED | no paper writing |

## Ledger status

- GPU hours spent：0.0
- GPU jobs launched：0
- Remote mutations：0
- Last read-only GPU snapshot：physical 0 busy by personal CF-DynAlign process；1/2/3 idle
- Permitted cards at that snapshot：2/3 only；snapshot 已过期，不具备 launch authority
- Pilot cap：2.0 GPUh
- Complete-path projection cap：7.2 GPUh
- Hard actual cap：8.0 GPUh

