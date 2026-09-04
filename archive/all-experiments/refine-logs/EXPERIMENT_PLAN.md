# Experiment Plan: PGR-Audit v2

**Question:** does a valid action-conditioned future-latent gradient create a useful future-sensitive VLA action-interface representation?  
**Status:** pending renewed execution jury; no remote mutation or GPU launch is authorized by the current plan state.  
**Scientific source of truth:** `refine-logs/PGR_AUDIT_PROTOCOL.json`.  
**Input source of truth:** `refine-logs/INPUT_MANIFEST.json`.  
**Compute policy:** no pilot cap, projection cap, or total GPU-hour cap. GPU time remains auditable telemetry.  
**Validation order:** simulation and real robot are independent lanes; there is no simulation-first requirement.  
**Paper writing:** out of scope.

## Claim map

| Claim | Required evidence | Failure meaning |
|---|---|---|
| C0-S | selected-checkpoint strict-test full decoder beats all locked controls and both derangements for joint64/main32 | S-LIBERO10 NO-RUN before adapter training |
| C1-S | all twenty seed eligibility rows plus sealed 6000-rollout A−B and A−C gates in both cohorts | no simulation algorithmic-effect claim; Stage 2 forbidden |
| C2-S | every seed’s locked P/Q eligibility plus sealed 4000-rollout P-vs-Q removal gates in both cohorts | no simulation reliance claim; passed C1-S remains valid |
| C0/C1/C2-R | separately frozen real-domain data, intervention, randomization, and safety protocol | narrows R-REAL only; does not rewrite S-LIBERO10 |
| Cross-domain | S and R independently pass the same claim level | otherwise report lanes separately |

## Non-negotiable gates

1. A renewed fresh-agent execution jury must give GO or a precisely scoped CONDITIONAL-GO.
2. Protocol, input manifest, proposal, plan, tracker, research contract, and preregistration lock must parse where applicable, agree, and have recorded SHA256 hashes.
3. Every scientific/project/data/artifact path must be under logical `<PERSONAL_RESEARCH_ROOT>` and resolve under canonical `<PERSONAL_RESEARCH_ROOT_ALIAS>`. Team/shared project or data access is forbidden.
4. The isolated runtime must be created from the hashed clean personal bundle. The dirty CF-DynAlign source and all prior predictor/cache/metric/result/`lambda_cf` artifacts are forbidden runtime inputs.
5. CPU/static tests, sealed-output dry runs, and a fresh-agent code review must pass before a scientific GPU launch.
6. A non-outcome engineering CUDA/model-load canary may precede the screen. The all-ten-task checkpoint screen is the first S-LIBERO10 scientific model/data outcome GPU class; it does not gate the independent robot-contract branch.
7. Every GPU launch independently passes fresh filesystem, physical UUID, occupancy, and post-bind ownership checks. GPU 2/3 are preferred; GPU 0/1 may be used individually when that candidate is freshly idle. No preemption or sharing.
8. All twenty train seeds, all ten tasks, and both fixed cohorts are mandatory. There is no timing-based seed reduction or result-adaptive extra seed.
9. No live robot command occurs until R-REAL has a complete endpoint/domain/interface/safety contract and separate jury approval.

## Fixed experimental cardinalities

- Checkpoint screen: `3 checkpoints × 10 tasks × 5 states = 150` rollouts.
- Training seeds: primary 0..9; replication 10..19.
- Final states: 5..14.
- Stage 1: `20 × 3 × 10 × 10 = 6000` rollouts.
- Conditional Stage 2: `20 × 2 × 10 × 10 = 4000` rollouts.
- Fold4: one opening only, after all models, P/Q bases, thresholds, hashes, and parity artifacts are frozen.

## Common implementation milestones

### M0 — Freeze v2 and renewed jury (0 GPU)

Freeze and hash:

- all 20 seeds and role-separated RNG derivations;
- all checkpoint, task, state, split, preprocessing, control, matching, P/Q, threshold, sealing, retry, and reveal rules;
- full personal LIBERO-10 input tree and environment/source locks;
- simulation/real independence and the current real-robot live-action prohibition;
- personal-only filesystem and per-launch GPU rules.

Success: the renewed jury authorizes isolated implementation and specifies any remaining pre-GPU conditions.  
Failure: remain in method-plan and perform no remote mutation/GPU work.

### M1 — Isolated personal implementation and static review (0 GPU)

After M0 passes:

- create `<PERSONAL_RESEARCH_ROOT>/workspace/h1-predictive-aux-starvla` only from the pinned personal bundle;
- set `HOME`, `TMPDIR`, XDG/HF/Torch/CUDA caches, W&B offline directory, logs, and results to personal paths with `umask 077`;
- materialize the pinned Conda-explicit and evaluator pip-freeze locks;
- implement realpath/symlink-escape guard, launch UUID guard, GPU telemetry, outcome quarantine/reveal state machine, and infrastructure retry ledger;
- implement arbitrary LIBERO task/state evaluation;
- implement deterministic split/cache/target/head/controls/C/A-B-C/P-Q/fold4/Stage1/Stage2 artifact writers;
- implement an abstract RobotAdapter with no reachable live-command path by default;
- run CPU unit tests for split cardinality, task mapping, t+8 boundaries, normalization, decoder shapes, nMSE/R²/bootstrap, matching, projector algebra, output sealing, and path denial;
- obtain a fresh-agent code review and fix every blocking issue.

Forbidden at this milestone: scientific checkpoint scoring, representation caching, treatment training, treatment rollout, or live robot action.

### M2 — Engineering CUDA/model-load canary

Run only after M1 review. It may verify CUDA binding, exact frozen-model loading, deterministic kernels, memory envelope, logging, quarantine mechanics, and exit behavior. It may not read future targets, run a task-success evaluation, fit a scientific cache/head, or expose treatment outcomes.

Success: exact hashes load, the bound GPU UUID and launch PID/PGID pass post-bind verification, and the canary writes only allowed telemetry.  
Failure: stop this launch, preserve the attempt, repair, and repeat code review before retry.

## S-LIBERO10 lane

### S0 — Treatment-blind checkpoint screen

Evaluate checkpoints 1k, 5k, and 10k in fixed order on suite tasks 0..9 and states 0..4. All 150 raw rollouts, logs, metrics, and videos are sealed.

The selector alone reads sealed records and atomically writes:

- `selected_checkpoint.json`;
- `primary_task_set.json`;
- selector-rule and source-artifact hashes.

Qualification: pooled all-task SR in [0.2, 0.8] and at least four tasks individually in [0.2, 0.8]. Select maximal eligible-task count; tie by pooled SR closest to 0.5; tie by lower step. Only after both outputs are hashed may screen details be revealed.

No qualifier or fewer than four eligible tasks: S-LIBERO10 NO-RUN.

### S1 — Interface parity, full cache, and C0

- Verify direct, cache, identity-adapter, and hot-switch normalized actions agree within `1e-6`.
- Verify all ten suite↔dataset task mappings and deterministic episode allocations.
- Build the full selected-checkpoint Qwen/DINO cache for all valid t+8 windows, then hash its sample IDs, shapes, bytes, source digests, and task counts.
- Fit D_head whitening, projections, nuisance models, predictive decoder, and every frozen control.
- Open strict-test once and execute joint64/main32 full-vs-control and both derangement gates with the exact task-stratified episode bootstrap.

Any path, parity, leakage, split, or C0 failure stops scientific progression until an implementation correction passes fresh review. A valid scientific C0 failure gives S-LIBERO10 NO-RUN and may not be tuned away.

### S2 — Fixed C and sealed two-cohort offline training

- Build one deterministic C donor bijection on D_adapter and freeze its merge level, matching diagnostics, donor IDs, and hash.
- For seeds 0..19, run A/B/C with identical batch manifests and initialization roles.
- For every seed, fit folds0–3 P and Q using only the locked rules.
- Seal all comparative losses, nMSE, R², Q scores, and arm comparisons until both cohorts and their manifests complete.
- Expose only launch identity, exit/timing/peak memory, nonfinite and safety booleans, and artifact hashes.
- No seed drop, replacement, timing-based truncation, hyperparameter rescue, or outcome-triggered retry.

The fixed infrastructure retry rule is at most one unchanged-config same-seed retry per logical job for a preregistered technical error; it gets a new launch UUID and preserves the old attempt. Scientific failures are not retried.

### S3 — Freeze artifacts and open fold4 once

Before fold4:

- all twenty A/B/C models and cache/parity bundles are frozen;
- P/Q candidates, selected alpha/rank, nuisance bases, thresholds, support statistics, and hashes are frozen;
- A→B cached parity inputs are frozen on one treatment-blind hash-selected 16-window trace for each of all ten tasks.

Open fold4 exactly once for all seeds. Produce an immutable per-seed Stage-1/Stage-2 eligibility table. Any Stage-1 eligibility failure forbids S Stage 1. Any Stage-2 eligibility failure forbids S Stage 2 but does not erase a later valid Stage-1 result.

### S4 — Sealed Stage 1

Run all 6000 A/B/C rollouts over all ten tasks and states 5..14. The batch manifest enumerates every expected record before launch. Do not aggregate, inspect, or reveal comparative outcomes until all 6000 records and hashes are present.

After one reveal, apply only the preregistered gates:

- A−B and A−C each require at least 9/10 positive seeds in both cohorts;
- both contrasts require at least 10 pp pooled primary-task gain in both cohorts;
- report the mechanically implied combined ≥18/20 consistency descriptively, without treating it as a third gate;
- combined primary-task means nonnegative;
- cohort×task reversal floor −5 pp;
- C not below B by more than 5 pp;
- all-ten-task secondary table mandatory.

An ordinary horizon failure is a valid failure outcome and is never retried. A simulator/reset/camera failure before a valid outcome may use the single technical retry; a second technical failure leaves a permanently incomplete sealed record and permanently fails the affected stage claim gate. An audit may explain the missingness only; it cannot waive, impute, replace, or convert that record set into a claim.

### S5 — Conditional sealed Stage 2

Run only if S4 passes and all twenty Stage-2 eligibility rows pass. Execute all 4000 predictive-removed/Q-removed rollouts with the same task/state coverage and seal/reveal discipline.

Apply only the locked gates: 9/10 positive and ≥10 pp per cohort, nonnegative combined primary-task means, Q-removed within 5 pp of intact A, predictive removal erases at least half of A−B, and predictive-removed not more than 10 pp below B. Report all ten tasks.

## R-REAL lane

### R0 — Connection/domain/safety contract (independent, no live action)

This milestone may run in parallel with S0–S5 and is not gated by a simulation result. Gather and freeze:

- robot/arm/gripper/camera/force-torque identities and reachable controller endpoint;
- SDK, authentication, process boundary, command acknowledgement, and safe disconnect behavior;
- action dimension, physical units, coordinate frame, frequency, chunk execution, clipping/filtering, and actual-executed-action logging;
- camera calibration, time synchronization, latency/staleness limits, and observation schema;
- joint/workspace/velocity/acceleration/force/torque/gripper limits;
- collision detector, watchdog/heartbeat, network-loss safe stop, episode timeout, E-stop owner, and on-site operator;
- frozen task instructions, reset distributions, success detection, baseline checkpoint, and personal demonstration/data paths;
- opaque treatment labels, randomized complete blocks or Latin-square session order, and technical retry categories.

Success: a separate fresh-agent safety/scientific jury authorizes a bounded real-domain canary.  
Current status: waiting for user-supplied interface information; `live_action_authorized_now=false`.

### R1 — Staged safety canaries

In order: observe-only connectivity; hold/zero-action verification; bounded low-speed no-object single-step; baseline closed-loop canary. Any unexpected motion, stale command, missing actual-action log, safety-filter ambiguity, or limit/watchdog failure immediately stops R-REAL.

### R2 — Real-domain C0/C1/C2

Only after R0/R1 pass, freeze a robot-specific data split, target availability, A/B/C intervention, P/Q construction, tasks, trials, session blocks, success metrics, safety metrics, and power rationale. Re-jury that protocol before opaque randomized execution. A safety filter’s actually executed action, not merely the commanded action, defines the predictive target. Safety events are reported separately from success and never hidden inside a composite score.

## GPU launch contract

For every GPU job:

1. atomically create a UUIDv4 launch intent under the personal root with `umask 077`;
2. within five seconds query physical indices 0..3, hardware UUIDs, compute PIDs/owners when readable, memory, and utilization;
3. define idle as no compute PID, memory ≤500 MiB, and utilization ≤5%;
4. select idle physical GPU 2 then 3 first; GPU 0 or 1 may be selected individually if that candidate is idle in this fresh snapshot; all-four-idle is not required;
5. atomically reserve each selected hardware UUID under the personal root, then take a second passing snapshot while holding all reservations;
6. bind `CUDA_VISIBLE_DEVICES` by hardware UUID;
7. after CUDA context creation, verify bound UUIDs and that each new PID belongs to this launch PID/PGID;
8. on race/mismatch, stop only this launch, preserve artifacts/time, and never attach to or kill an external process;
9. set a conservative logical-job hung timeout that can terminate only this launch’s process group.

A historical GPU snapshot never authorizes a later launch.

## Telemetry, sealing, and audit

There is no GPU-hour admission gate. Actual GPU-hours are measured as the union of this run’s launch intervals per physical UUID and summed across UUIDs. Parent/child processes inside one envelope are not double counted; failed and retried attempts remain charged and preserved.

Outcome visibility classes are screen, cohort training, Stage 1, and Stage 2. Their stdout/stderr, metrics, videos, trajectories, and offline W&B artifacts are sealed together. Reveal programs validate the preregistered record set and manifest hash before exposing comparisons.

After each lane reaches a terminal scientific result:

1. parse structured JSON/CSV artifacts rather than prose;
2. compute exact locked tests and descriptive confidence intervals;
3. run experiment-integrity audit for lineage, leakage, fake ground truth, score manipulation, missing attempts, and phantom results;
4. run result-to-claim;
5. synthesize lanes without pooling away a failed lane;
6. stop before paper writing.

## Stop conditions

Stop or narrow only the affected lane when any of the following occurs:

- renewed jury or fresh code review does not authorize progression;
- personal-path, source, environment, dataset, checkpoint, or hash mismatch;
- GPU occupancy/UUID/post-bind guard failure;
- no qualifying simulation checkpoint;
- valid C0, C, dose, nonfinite, parity, support, P/Q, Stage-1, or Stage-2 gate failure;
- incomplete sealed record set after the one allowed technical retry, which permanently fails the affected claim gate; no missingness disposition can waive, impute, replace, or restore that claim;
- real-robot contract, canary, watchdog, limit, or operator-safety failure;
- integrity audit finds leakage, fabricated ground truth, score manipulation, missing failed attempts, or broken lineage.

No compute-budget stop exists in v2. Negative and NO-RUN outcomes are preserved as results, not repaired by changing controls, thresholds, tasks, seeds, or claims.
