# Experiment Tracker: PGR-Audit v2.1 implementation

| ID | Lane | Milestone | Fixed scope / artifact | GPU | Status | Dependency / stop |
|---|---|---|---|---:|---|---|
| V2-000 | common | freeze v2.1 protocol and full input manifest | all10, seeds0..19, S/R independence, no GPU cap | 0 | DONE | freeze manifest `21267bf7...` |
| V2-001 | common | renewed execution jury + receipt | exact reviewed bundle | 0 | DONE-CONDITIONAL | A–E stage-local gates; F NO-GO |
| V2-002 | common | historical remote preflight | liu_meng, personal root, source/input/GPU inventory | 0 | DONE | historical snapshot has no launch authority |
| V2-003 | common | isolated runtime creation | clean personal bundle → personal workspace | 0 | DONE | HEAD `3422b9f...` |
| V2-004 | common | guards, sealing, science modules, RobotAdapter-off | CPU fixtures | 0 | DONE-FOUNDATION | source hashes recorded |
| V2-005 | common | CPU/static suite | foundation + launcher pure tests | 0 | PASS-23/23 | 0.462 s |
| V2-006 | common | fresh-agent code review | exact isolated implementation | 0 | IN-REVIEW | no blocking issue |
| V2-007 | common | engineering CUDA/model-load canary | no scientific target/outcome | 1+ idle | BLOCKED | V2-006 + fresh launch guard |
| S-000 | sim | 1k checkpoint screen | tasks0..9 × states0..4 = 50 | 1+ idle | BLOCKED | V2-007 |
| S-001 | sim | 5k checkpoint screen | tasks0..9 × states0..4 = 50 | 1+ idle | BLOCKED | contiguous scientific screen class |
| S-002 | sim | 10k checkpoint screen | tasks0..9 × states0..4 = 50 | 1+ idle | BLOCKED | contiguous scientific screen class |
| S-003 | sim | selector lock/reveal | 150 sealed records; checkpoint + eligible tasks | 0 | BLOCKED | no qualifier / <4 tasks = S NO-RUN |
| S-004 | sim | interface and cache parity | identity/direct/cache/hot; all10 mappings | 1+ idle | BLOCKED | max action error <1e-6 |
| S-005 | sim | full all-task Qwen+DINO cache | 379 episodes, valid t+8 windows | 1+ idle | BLOCKED | manifest/hash/cardinality |
| S-006 | sim | D_head target/head/controls | train/val only | 1+ idle | BLOCKED | S-005 |
| S-007 | sim | one-time strict C0 | joint64/main32 controls+derangements | 1+ idle | BLOCKED | failure = S NO-RUN |
| S-008 | sim | fixed C map | D_adapter global derangement | 0/CPU | BLOCKED | matching/dose pre-gates |
| S-009 | sim | primary cohort A/B/C | seeds0..9, 500 steps each arm | idle cards | BLOCKED | comparative outputs sealed |
| S-010 | sim | replication cohort A/B/C | seeds10..19, 500 steps each arm | idle cards | BLOCKED | comparative outputs sealed |
| S-011 | sim | primary cohort P/Q folds0–3 | seeds0..9 | idle cards | BLOCKED | locked P/Q artifacts |
| S-012 | sim | replication cohort P/Q folds0–3 | seeds10..19 | idle cards | BLOCKED | locked P/Q artifacts |
| S-013 | sim | all parity/support bundles | 20 seeds; cache/A→B/two traces | idle cards | BLOCKED | no seed drop/replacement |
| S-014 | sim | one-time fold4 | all 20 frozen seed artifacts | idle cards | BLOCKED | immutable eligibility table |
| S-015 | sim | sealed Stage 1 | 20×3×10×10 = 6000 | idle cards | BLOCKED | every Stage-1 row passes |
| S-016 | sim | Stage-1 reveal/gate | both cohorts, primary + all10 coverage | 0 | BLOCKED | failure permanently forbids S-017 |
| S-017 | sim | conditional sealed Stage 2 | 20×2×10×10 = 4000 | idle cards | BLOCKED | S-016 + all Stage-2 rows pass |
| S-018 | sim | simulation audit/claim | lineage + exact preregistered tests | 0 | BLOCKED | no paper writing |
| R-000 | robot | collect endpoint/domain/interface contract | embodiment, SDK, actions, sensors, tasks | 0 | WAITING-USER-INTERFACE | independent of simulation result |
| R-001 | robot | safety-contract jury | limits, E-stop, watchdog, operator | 0 | BLOCKED | R-000 complete |
| R-002 | robot | observe-only connectivity | no command path | 0 | BLOCKED | R-001 GO |
| R-003 | robot | hold/zero and bounded no-object canaries | actual-action + safety logs | n/a | BLOCKED | on-site operator and E-stop |
| R-004 | robot | baseline closed-loop canary | frozen task/reset/success | n/a | BLOCKED | R-003 pass |
| R-005 | robot | freeze robot C0/C1/C2 protocol | tasks/trials/blocks/power/PQ | 0 | BLOCKED | separate renewed jury |
| R-006 | robot | opaque randomized execution | separately fixed cardinality | n/a | BLOCKED | no simulation gate |
| R-007 | robot | robot audit/claim | task success + separate safety table | 0 | BLOCKED | no paper writing |
| X-000 | synthesis | cross-domain result-to-claim | never pool away a failed lane | 0 | BLOCKED | terminal S and/or R evidence |

## Current ledger

- H1 GPU hours used: **0.0**
- H1 GPU jobs launched/completed: **0 / 0**
- H1 scientific jobs / robot trials: **0 / 0**
- Paid cost: **$0.00**
- Preset GPU-hour cap: **none**
- GPU assignment: physical 2/3 preferred; physical 0/1 individually allowed only when that candidate is idle in a fresh per-launch snapshot; all four need not be idle
- Never preempt, share with, attach to, or terminate an unrelated process
- Personal-root engineering mutations: isolated clone, prereg bundle, overlay, tests, runtime directories
- Team/shared writes: **0**
- 05:43:38Z snapshot showed all four idle; it is expired and cannot authorize a later launch.
- Live robot action authorized now: **false**
- Paper writing: **out of scope**

## Status semantics

- `DONE-CANDIDATE`: locally frozen but awaiting renewed jury.
- `BLOCKED`: a listed scientific, implementation, safety, or review dependency is not satisfied.
- `WAITING-USER-INTERFACE`: interface facts are absent; read-only protocol work may continue, but no live command is permitted.
- `NO-RUN`: a valid preregistered scientific gate failed; preserve the negative outcome.
