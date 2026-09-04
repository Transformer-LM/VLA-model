# Research Proposal: PGR-Audit v2

**Direction:** H1 — predictive world objectives shape VLA representations.  
**Protocol ID:** `pgr-audit-v2-parallel-real`.  
**Status:** frozen candidate pending renewed execution jury. The earlier budget-constrained plan and its NO-GO verdict remain historical evidence but are superseded by this v2 scope.  
**Machine source of truth:** `refine-logs/PGR_AUDIT_PROTOCOL.json`.  
**Input source of truth:** `refine-logs/INPUT_MANIFEST.json`.  
**Paper writing:** out of scope.

## Research question

Does a valid action-conditioned future-prediction gradient reshape the shared action-interface representation of a frozen VLA in a way that is useful for closed-loop control, rather than merely improving an auxiliary loss?

The bottleneck is identification. Existing future-objective results can confound:

- genuine held-out future association;
- arbitrary auxiliary-gradient regularization;
- action-output diversity or seed luck;
- and actual policy reliance on the learned representation.

PGR-Audit contributes one preregistered sequential identification contract, not a new VLA, WAM, adapter, predictive target, planner, or reinforcement-learning algorithm:

1. **C0:** establish held-out action-conditioned future association beyond strong state, action, nuisance, and derangement controls;
2. **C1:** compare valid-target training A against action-only B and a fixed matched deranged-target placebo C;
3. **C2:** only after C0 and C1 pass, compare removal of an offline predictive subspace with removal of an empirical-support and action-output-matched nonpredictive Q subspace.

The strongest allowed claims are behavioral-policy association, controlled algorithmic effect, and task-local placebo-relative reliance. Natural causal mediation, physical causality, SOTA, and cross-architecture generality are forbidden claims.

## Scope override and validation lanes

The user explicitly removed simulation/offline-first, the 2 GPU-hour pilot, the 7.2 GPU-hour projection gate, and the 8 GPU-hour total cap. Compute is therefore not an admission criterion. Actual GPU time is still logged for provenance, throughput, scheduling, and hung-job detection.

Validation has two independent lanes:

- **S-LIBERO10:** the fully specified simulation lane over all ten LIBERO-10 tasks;
- **R-REAL:** a real-robot lane that may proceed independently when its robot/domain/interface/safety contract is supplied and separately reviewed.

Simulation is not a prerequisite for robot interface or safety work, and a simulation failure does not automatically forbid a scientifically separate real-robot test. Conversely, real-robot availability does not weaken the simulation protocol. Results are analyzed separately; “cross-domain replication” is allowed only if both lanes independently pass.

No live robot action is authorized now. Missing items include the reachable endpoint or SDK, embodiment and sensor identities, action units/frame/frequency/chunk semantics, calibration and timestamps, hard limits, E-stop ownership, safe-stop behavior, task/reset/success definitions, a compatible executable frozen real-domain baseline, and all licensed personal training/demonstration data required by the method.

## Frozen host and personal-only boundary

- SSH identity: `liu_meng` only.
- Every project, dataset, checkpoint, environment, cache, temporary file, log, metric, video, offline W&B artifact, and result path must be specified under `<PERSONAL_RESEARCH_ROOT>` and resolve under canonical `<PERSONAL_RESEARCH_ROOT_ALIAS>`.
- Read-only OS/device/runtime access is the only exception. Team/shared project or data trees are forbidden.
- The dirty CF-DynAlign source is provenance-only and may never be the H1 runtime.
- The runtime must be created from the hashed personal StarVLA bundle at clean commit `3422b9f2387b6f682cf02802904a77b23ab13afd` in the isolated target `<PERSONAL_RESEARCH_ROOT>/workspace/h1-predictive-aux-starvla`.
- Existing CF-DynAlign predictors, caches, metrics, results, checkpoint sidecars, and `lambda_cf` artifacts are forbidden. Only independently verified frozen base VLA checkpoints/configuration and raw-data-derived action statistics may be used.
- All pinned inputs, byte counts, and digests are recorded in `INPUT_MANIFEST.json`; any runtime mismatch fails closed before scientific execution.

## Simulation data and treatment-blind checkpoint selection

The frozen personal dataset contains 379 episodes and 101,469 frames across all ten LIBERO-10 tasks. The full 3,430-file tree is pinned by SHA256. The protocol fixes the suite-task to dataset-task mapping and requires all ten tasks in every relevant partition.

Episodes are deterministically ordered within task from domain-separated SHA256 keys and allocated constraint-first. Every task first reserves D_head/D_adapter/D_post counts 11/3/15. D_head reserves train/validation/strict-test 5/3/3; D_post reserves three distinct episodes in each of folds0..4. Only episodes above the binding 29-task minimum are distributed by the locked largest-remainder proportions. Thus the five-fold nuisance CV contains every task, every projector selection/calibration/holdout fold has at least three episodes per task, and the three-episode D_adapter minimum remains protected by a fail-closed perfect-bijection feasibility test. Episodes may not be moved to repair a gate. A sample is `(dataset_task_index, episode_index, t)`; it is valid only when `t+8` remains in the same episode.

Before any selected-checkpoint cache, target/head fit, A/B/C training, P/Q fit, or treatment rollout, the screen evaluates checkpoints 1k, 5k, and 10k on all ten tasks and initial states 0..4: `3 × 10 × 5 = 150` baseline rollouts. A checkpoint qualifies when pooled all-task SR is in [0.2, 0.8] and at least four tasks individually have SR in [0.2, 0.8]. Selection maximizes eligible-task count, then chooses pooled SR closest to 0.5, then the earlier step. The selected checkpoint and treatment-blind primary eligible task set are atomically frozen before screen details are revealed. No qualifier gives S-LIBERO10 NO-RUN.

An engineering CUDA/model-load canary may precede the screen only if it cannot read a scientific target, fit a representation cache, produce task success, or expose a treatment outcome. The screen remains the first S-LIBERO10 scientific model/data outcome launch class; it creates no ordering edge for R-REAL.

## Future target and C0

The host is a frozen Qwen3-VL-4B-Instruct VLA with a frozen deterministic MLPResNet action head. Its eight gathered action-token states have shape `[B,8,2560]`. The only trainable policy component is a rank-32 identity-initialized residual adapter:

`m = h + U V LN0(h)`.

For each main and wrist RGB stream, a frozen local DINOv2 ViT-S/14 encodes `o_t` and `o_{t+8}`. Per-camera future differences are FP64-whitened from D_head-train only, then projected with two persisted 384×32 seeded orthonormal matrices. Concatenation gives a 64-D target.

The action-conditioned decoder has an explicit 256-D state branch, 128-D action branch, 384-D concatenation, 256-D fusion layer, and 64-D output. It is trained with MSE on D_head-train, selected by task-equal validation nMSE, and evaluated once on strict-test.

Controls are state-only, action-only, current-DINO+action, additive, nuisance ridge, task×progress mean, and zero. Both action and representation derangements are different-episode, same-task matched controls. For joint64 and main32 separately, the full model must improve by at least 5% over the strongest control and have a one-sided 10,000-replicate episode-block bootstrap LCB above zero; both derangements must degrade by at least 5% with LCB above zero. Any C0 failure stops adapter training in the simulation lane.

Action normalization is frozen: the first six action dimensions use the verified base statistics’ min/max map to [-1,1] without clipping; the gripper dimension is identity.

## A/B/C controlled training

All arms share the same identity initialization, exact batch-index arrays, 500 update steps, task-balanced batch size 256, manual FP32 SGD, learning rate 1e-3, zero momentum and weight decay, and global gradient clipping at 1. The Qwen backbone and action head remain frozen.

- **A:** action gradient plus valid future-target gradient.
- **B:** parameter updates use only its own action gradient, while B also computes the same valid-target future forward and full backward as A and discards that future gradient, keeping scheduled compute/exposure matched.
- **C:** action gradient plus a fixed matched deranged future target.

C is built once from D_adapter by a frozen global merge hierarchy and a float64 Hungarian bijection. Donors must be from another episode, have nonoverlapping windows, and contain no fixed point or duplicate. Matching uses target norm and identity-decoder Huber loss, with deterministic SHA-derived tie breaking. Its donor map is frozen before training. Target-dose, prediction-loss, and saturation matching gates must pass.

The auxiliary dose is locked to 30% of the common B action-gradient norm on every batch. Future-gradient scaling is detached and bounded; invalid/zero norms, cap hits, dose error over 1%, or excessive fallbacks invalidate the seed. Nonfinite values invalidate the seed. No seed may be dropped or replaced.

## Fixed seed cohorts and representation test

There is no timing-based seed choice:

- primary cohort: seeds 0..9;
- preregistered replication cohort: seeds 10..19;
- all twenty are mandatory and were fixed before any treatment outcome.

For each seed, P is learned from the mean-token A−B representation delta on D_post folds0–1 using task-aware nuisance cross-fitting, PCA/whitening, and a ridge-SVD predictive mapping. Hyperparameter and rank selection occur on fold2. Q is selected from 100 seeded Gaussian candidates on fold3 after removing nuisance and predictive bases. Q must match removed energy and all `10 × 8 = 80` task-token action-output perturbation ratios while remaining nonpredictive. Fold4 is opened exactly once after every model, basis, threshold, parity artifact, and hash is frozen.

Every seed must pass Stage-1 eligibility: A beats identity, B, and C future-prediction metrics by the locked margins/LCBs; dose, residual-size, nonfinite, and identity/direct-cache/hot-switch parity gates pass. Any one of twenty failures forbids simulation Stage 1.

Every seed must also pass the separately defined Stage-2 eligibility for Stage 2 to run: fold4 P R² and bootstrap gate, Q nonprediction UCB, energy/action-output matching, nuisance orthogonality, A→B cached parity on one frozen 16-window trace for every task, and exact empirical-support bounds. A Stage-2 eligibility failure does not erase a valid Stage-1 result, but globally forbids simulation Stage 2.

## Closed-loop outcomes

Simulation evaluation fixes seed 7, ten settle actions, a 520-action horizon, and open-loop execution of every eight-action chunk. Success is environment `done=true`; horizon exhaustion is failure. Infrastructure exceptions are not silently converted into task failures.

Final initial states are 5..14 for every condition and seed.

### Stage 1

`20 seeds × 3 arms × 10 tasks × 10 states = 6000` sealed rollouts.

The primary contrasts are A−B and A−C on the treatment-blind primary task set. Separately for each 10-seed cohort and each contrast:

- at least 9/10 seed-level primary-task-average differences are positive; ties are nonpositive;
- the pooled primary-task gain is at least 10 percentage points.

Both cohorts must pass. Their two 9/10 gates mechanically imply at least 18/20 positive seeds, so that combined count is reported only as derived consistency rather than a third gate. Every primary task’s combined mean must be nonnegative, no cohort×task reversal may be below −5 pp, and C may not trail B by more than 5 pp. All ten tasks are mandatory secondary coverage and may not be hidden.

### Stage 2

Only if Stage 1 and every Stage-2 eligibility row pass:

`20 seeds × 2 removal conditions × 10 tasks × 10 states = 4000` sealed rollouts.

The primary contrast is `SR(A_Q_removed) − SR(A_pred_removed)`. Each cohort again requires at least 9/10 positive seeds and at least 10 pp pooled primary-task gain. Every primary task’s combined mean must be nonnegative; Q-removed must remain within 5 pp of intact A; predictive removal must erase at least half of A−B and may not fall more than 10 pp below B.

Comparative training and rollout outputs remain sealed until both fixed cohorts complete. Failed attempts, stdout/stderr, videos, metrics, and offline W&B data are preserved with their visibility class.

## GPU and process safety

GPU 2 and 3 are preferred. GPU 0 or 1 may be used individually whenever that launch’s fresh snapshot shows the candidate GPU idle; all four cards do not need to be idle. Every launch rechecks within five seconds:

- physical index and hardware UUID;
- compute PIDs and owners when readable;
- memory usage and utilization;
- an atomic personal-root reservation keyed by hardware UUID, a second post-reservation snapshot, and post-CUDA-bind UUID/PID/PGID ownership.

Idle means no compute process, memory at most 500 MiB, and utilization at most 5%. A race or mismatch stops only this launch, preserves and charges its artifacts/time, and never touches another process. No preemption or sharing is allowed.

Actual GPU-hours are telemetry, not a cap. They are deduplicated as the union of this run’s launch intervals per physical GPU UUID. Each logical job has a conservative hung timeout; a timeout may stop only its own process group and is not a scientific budget stop.

## Immutable execution order

1. freeze/hash v2 protocol, inputs, seeds, task rules, lane independence, and personal-only contract;
2. obtain renewed execution-jury authorization;
3. create isolated personal source, locks, guards, sealing, science code, tests, and fresh-agent code review;
4. run a non-outcome engineering canary;
5. run and seal the all-ten-task checkpoint screen, then freeze checkpoint and primary tasks;
6. build all-task cache and C0; stop the simulation lane if C0 fails;
7. independently accept and review a real-robot contract when supplied;
8. build fixed C; run both twenty-seed A/B/C and folds0–3 P/Q cohorts with outcomes sealed;
9. freeze artifacts and open fold4 once;
10. run sealed simulation Stage 1;
11. conditionally run sealed simulation Stage 2;
12. run a separately reviewed real-domain sequence if its interface and safety gates pass;
13. perform per-lane integrity audit, result-to-claim, and cross-domain synthesis without paper writing.

Negative, NO-RUN, ineligible, or lane-specific failure is a legitimate result. Thresholds, tasks, seeds, controls, and claims may not be changed to rescue an outcome.

## Claim ceiling

If S-LIBERO10 fully passes, the strongest simulation statement is:

> In a treatment-blind-selected deterministic StarVLA checkpoint, across two fixed ten-seed cohorts and mandatory all-LIBERO-10 coverage, valid-target gradient training produced a seed-consistent task-local closed-loop gain over action-only and one fixed matched deranged-target placebo; removing one offline-learned nuisance-annihilated predictive subspace harmed performance more than removing an empirical-support and action-output-matched nonpredictive subspace.

If only C0 or C1 passes, the claim narrows accordingly. Real-robot and cross-domain language requires independent evidence from R-REAL and may never be inferred from simulation availability alone.
