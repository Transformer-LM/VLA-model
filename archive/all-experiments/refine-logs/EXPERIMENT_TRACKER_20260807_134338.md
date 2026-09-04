# Experiment Tracker: PGR-Audit v2.1 implementation

| ID | Lane | Milestone | Fixed scope / artifact | GPU | Status | Dependency / stop |
|---|---|---|---|---:|---|---|
| V2-000 | common | freeze v2.1 protocol and full input manifest | all10, seeds0..19, S/R independence, no GPU cap | 0 | DONE | freeze manifest `21267bf7...` |
| V2-001 | common | renewed execution jury + receipt | exact reviewed bundle | 0 | DONE-CONDITIONAL | A–E stage-local gates; F NO-GO |
| V2-002 | common | remote preflight | personal root, source/input/GPU inventory | 0 | DONE | every launch still needs fresh snapshot |
| V2-003 | common | isolated runtime creation | clean bundle → personal workspace | 0 | DONE | HEAD `3422b9f...` |
| V2-004 | common | guards, sealing, foundation, RobotAdapter-off | personal overlay | 0 | DONE-FOUNDATION | source hashes recorded |
| V2-005 | common | CPU/static suite | foundation + launcher pure tests | 0 | PASS-23/23 | 0.462 s |
| V2-006 | common | fresh-agent code review | overlay + raw plan/protocol/jury/audit | 0 | IN-REVIEW | blocks canary until no blocker |
| V2-007 | common | engineering CUDA/model-load canary | synthetic input; no science outcome | 1 idle | BLOCKED | V2-006 + fresh launch guard |
| S-000 | sim | 1k checkpoint screen | tasks0..9 × states0..4 = 50 | 1+ idle | BLOCKED | V2-007 |
| S-001 | sim | 5k checkpoint screen | tasks0..9 × states0..4 = 50 | 1+ idle | BLOCKED | contiguous screen class |
| S-002 | sim | 10k checkpoint screen | tasks0..9 × states0..4 = 50 | 1+ idle | BLOCKED | contiguous screen class |
| S-003 | sim | selector lock/reveal | 150 sealed records | 0 | BLOCKED | complete atomic selector only |
| S-004 | sim | interface/cache science contract | exact dtype/roundtrip | 0 | PROTOCOL-REPAIR | issue22 + new jury |
| S-005 | sim | full all-task Qwen+DINO cache | 379 episodes, valid t+8 windows | 1+ idle | BLOCKED | S-004 + manifest parity |
| S-006 | sim | D_head target/head/controls | train/val only | 1+ idle | PROTOCOL-REPAIR | issues9/10/12/20/22 |
| S-007 | sim | one-time strict C0 | controls+derangements | 1+ idle | PROTOCOL-REPAIR | issues9/10/11/12/20/22 |
| S-008 | sim | fixed C map | D_adapter derangement | 0/CPU | PROTOCOL-REPAIR | issues11/12 |
| S-009 | sim | primary A/B/C | seeds0..9, 500 steps/arm | idle cards | BLOCKED | C0 + repaired protocol |
| S-010 | sim | replication A/B/C | seeds10..19, 500 steps/arm | idle cards | BLOCKED | C0 + repaired protocol |
| S-011 | sim | primary P/Q folds0–3 | seeds0..9 | idle cards | PROTOCOL-REPAIR | issues16–18 |
| S-012 | sim | replication P/Q folds0–3 | seeds10..19 | idle cards | PROTOCOL-REPAIR | issues16–18 |
| S-013 | sim | all parity/support bundles | 20 seeds | idle cards | BLOCKED | no seed drop/replacement |
| S-014 | sim | one-time fold4 | all 20 frozen artifacts | idle cards | BLOCKED | immutable eligibility table |
| S-015 | sim | sealed Stage 1 | 6000 rollouts | idle cards | BLOCKED | every Stage-1 row passes |
| S-016 | sim | Stage-1 reveal/gate | both cohorts + all10 | 0 | BLOCKED | failure forbids S-017 |
| S-017 | sim | conditional sealed Stage 2 | 4000 rollouts | idle cards | BLOCKED | S-016 + repaired P/Q |
| S-018 | sim | simulation audit/claim | exact prereg tests | 0 | BLOCKED | no paper writing |
| R-000 | robot | exact endpoint/interface contract | embodiment, SDK, actions, sensors, tasks | 0 | WAITING-USER-INTERFACE | independent of simulation |
| R-001 | robot | safety/scientific jury | limits, E-stop, watchdog, operator | 0 | BLOCKED | R-000 |
| R-002 | robot | observe-only connectivity | no command path | 0 | BLOCKED | R-001 GO |
| R-003 | robot | hold/zero + no-object canaries | safety logs | n/a | BLOCKED | operator + E-stop |
| R-004 | robot | baseline closed-loop canary | frozen task/reset/success | n/a | BLOCKED | R-003 |
| R-005 | robot | freeze robot protocol | randomized complete blocks only | 0 | BLOCKED | separate jury |
| R-006 | robot | opaque randomized execution | fixed cardinality | n/a | BLOCKED | no simulation gate |
| R-007 | robot | robot audit/claim | success + safety table | 0 | BLOCKED | no paper writing |
| X-000 | synthesis | cross-domain result-to-claim | never pool away failed lane | 0 | BLOCKED | terminal S and/or R evidence |

## Current ledger

- H1 GPU hours used: **0.0**
- H1 GPU jobs launched/completed: **0 / 0**
- H1 scientific jobs / robot trials: **0 / 0**
- Paid cost: **$0.00**
- Preset GPU-hour cap: **none**; compute is telemetry only
- Personal-root mutations: isolated clone, prereg bundle, overlay, tests, runtime directories
- Team/shared writes: **0**
- GPU assignment: physical 2/3 preferred; 0/1 individually allowed only after fresh per-launch proof
- 05:43:38Z snapshot showed all four idle; it is expired and gives no later launch authority
- Live robot authorized now: **false**
- Paper writing: **out of scope**

## Status semantics

- `DONE-CONDITIONAL`: stage-local prerequisites still apply.
- `PROTOCOL-REPAIR`: freeze, rehash, and re-jury required.
- `BLOCKED`: listed dependency unsatisfied.
- `WAITING-USER-INTERFACE`: other lanes continue; live robot remains unavailable.
