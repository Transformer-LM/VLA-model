# Research Contract: H1 / PGR-Audit v2

## Identity and scope

- **Run:** `20260806-vla-wam-expanded-field-map`
- **Selected direction:** H1 — predictive world objectives shape VLA representations.
- **Protocol:** `pgr-audit-v2-parallel-real`
- **Contribution:** one preregistered sequential identification protocol at a frozen VLA action interface.
- **Not contributions:** a new VLA, WAM, objective, adapter, predictor, planner, RL algorithm, or benchmark.
- **Paper writing:** prohibited in this run.

## Claim ladder

1. **C0:** held-out action-conditioned future association beyond locked controls.
2. **C1:** controlled algorithmic effect of valid future-gradient A relative to action-only B and fixed matched deranged-target C.
3. **C2:** task-local placebo-relative reliance, comparing predictive-subspace removal with matched nonpredictive Q removal.

Simulation and real-robot claim ladders are independent. A lane may advance only on its own evidence. Cross-domain replication requires both lanes to pass independently.

Forbidden language includes natural causal mediation, physical causality, SOTA, cross-architecture generality, and broad real-robot generality from one platform.

## Frozen simulation design

- **Suite:** all ten LIBERO-10 tasks.
- **Dataset:** full personal 379-episode, 101,469-frame tree.
- **Screen checkpoints:** steps 1k, 5k, 10k with frozen hashes.
- **Screen states:** 0..4 on every task; 150 total baseline rollouts.
- **Qualification:** pooled all-task SR in [0.2,0.8] and at least four tasks individually in [0.2,0.8].
- **Selection:** maximum eligible-task count; then pooled SR closest to 0.5; then earlier checkpoint.
- **Primary task set:** treatment-blind eligible tasks frozen before treatment.
- **Mandatory coverage:** all ten tasks remain in training, eligibility, rollout, and reporting.
- **Training seeds:** primary cohort [0,1,2,3,4,5,6,7,8,9]; replication cohort [10,11,12,13,14,15,16,17,18,19].
- **Final states:** 5..14 for every seed/condition/task.
- **Stage 1:** 6000 rollouts.
- **Conditional Stage 2:** 4000 rollouts.
- **Seed changes:** no drop, replacement, timing-based reduction, result-adaptive addition, or outcome-driven retry.

The exact split, target, preprocessing, decoder, controls, C matching, optimizer, dose, P/Q, fold4, statistical, sealing, and retry rules are normative only in `refine-logs/PGR_AUDIT_PROTOCOL.json`.

## Real-robot contract

Real-robot work is not simulation-first and is not gated by a simulation result. However, no live action is authorized until the following are supplied, frozen, and separately reviewed:

- reachable controller endpoint/SDK and authentication boundary;
- robot, arm, gripper, and camera identities, plus either a calibrated force/torque sensor or a controller joint-torque/force-estimate source; if neither telemetry source exists, robot motion is forbidden;
- action dimensions, units, frame, rate, chunk semantics, clipping/filtering, and actual-executed-action logs;
- calibration, time synchronization, latency and stale-command policy;
- workspace/joint/velocity/acceleration/force/torque/gripper limits;
- collision detection, watchdog/heartbeat, network-loss safe stop, E-stop owner, and on-site operator;
- task/reset/success definitions, frozen baseline, and personal data paths;
- randomized opaque experiment order, technical retry categories, trial count, and power rationale.

Required safety sequence: observe-only → hold/zero action → bounded low-speed no-object single-step → baseline closed-loop canary → separately authorized opaque experiment.

A policy-caused safety abort is both a task failure and a safety event and is never retried. Success and safety metrics remain separate.

## Personal-only infrastructure

- SSH user `liu_meng` only.
- Project/data/model/checkpoint/environment/cache/tmp/log/metric/video/W&B/result paths must be under logical `<PERSONAL_RESEARCH_ROOT>` and resolve under canonical `<PERSONAL_RESEARCH_ROOT_ALIAS>`.
- Team/shared datasets, models, projects, caches, and results have zero access.
- No root, sudo, su, `.bashrc` changes, global Conda changes, system CUDA/driver changes, or external process interference.
- Dirty source `<PERSONAL_RESEARCH_ROOT>/workspace/cf-dynalign-starvla/source/starVLA` is provenance-only.
- Isolated runtime target: `<PERSONAL_RESEARCH_ROOT>/workspace/h1-predictive-aux-starvla`.
- Existing CF-DynAlign predictor/cache/metric/result/checkpoint-sidecar/`lambda_cf` artifacts are forbidden.
- New output directories use UUID identity, `umask 077`, no overwrite, and canonical-parent checks.

## GPU contract

- Preferred physical GPUs: 2, then 3.
- Conditional physical GPUs: 0 and 1, each independently usable when that candidate is idle in a fresh snapshot for that launch.
- Four-card simultaneous idleness is not required.
- Idle: no compute process, memory ≤500 MiB, utilization ≤5%.
- Recheck physical index, hardware UUID, PIDs, memory, and utilization before every launch; post-bind verify the new CUDA PID/PGID.
- Never preempt/share/attach/kill an unrelated process.
- Race or mismatch stops only the current launch and preserves its artifact/time.
- Historical snapshots never authorize a launch.

There is no pilot, projected, or total GPU-hour cap. Actual GPU-hours are retained as deduplicated provenance and throughput telemetry, never as a scientific admission gate.

## Outcome isolation

- Screen artifacts remain sealed until checkpoint and primary-task manifests are atomically frozen.
- A/B/C and P/Q comparative outputs remain sealed until both fixed seed cohorts complete.
- Stage 1 remains sealed until all 6000 expected records and hashes exist.
- Stage 2 remains sealed until all 4000 expected records and hashes exist.
- Stdout/stderr, metrics, videos, trajectories, and offline W&B data inherit the same visibility class.
- Failed attempts are retained and never overwritten.

## Scientific and technical failure

- Scientific gate failure stops or narrows the corresponding lane and is never retried or tuned away.
- A preregistered infrastructure class permits at most one same-seed, unchanged-config retry with a new launch UUID; the prior attempt remains preserved.
- Nonfinite training invalidates that seed; no replacement.
- Ordinary task failure is not retried.
- After the one allowed unchanged technical retry, an incomplete sealed batch permanently fails the affected claim gate. An integrity audit may explain the missingness only; it cannot waive, impute, replace, or convert the incomplete batch into a claim.
- Negative, NO-RUN, ineligible, and safety-stop outcomes are legitimate results.

## Current authorization

- Local v2 protocol work: authorized.
- Remote read-only checks within the stated account and personal scope: authorized.
- Remote mutation or GPU launch: pending renewed execution jury and exact implementation review.
- Live robot commands: not authorized; connection/domain/interface/safety contract missing.
- Paper writing: not authorized.
