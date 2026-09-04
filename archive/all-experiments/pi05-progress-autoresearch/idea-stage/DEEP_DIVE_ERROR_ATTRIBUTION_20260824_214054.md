# Deep Dive A: Attribution-Conditioned VLA Intervention

**Date:** 2026-08-24  
**Status:** candidate; novelty review pending final cross-check; no experiment run

## 1. One-sentence idea

When an action-conditioned world model disagrees with reality, do not immediately equate disagreement with robot failure. Infer whether the evidence supports an execution failure, world-model misspecification, observation ambiguity, or several causes at once, then route each case to a different intervention.

## 2. Why the original formulation is insufficient

A scalar residual

`predicted future != observed future`

is not causally identifiable. The same residual magnitude can arise from:

- an actuator fault, slip, collision, or missed grasp;
- a correct task transition that the WAM cannot predict under a new object, view, texture, or dynamics regime;
- occlusion, blur, dropped frames, or a temporarily ambiguous viewpoint;
- a mixture, such as a real slip under a novel object.

A three-way softmax over the residual alone would therefore learn dataset shortcuts. The defensible research question is not generic failure classification, but whether independent, deployable evidence can reduce the downstream cost of wrong interventions.

## 3. Narrow claim that may remain defensible

> Under matched prediction-error magnitude, action-conditioned physical evidence, model-support evidence, and observation-consistency evidence can distinguish execution failures from verifier failures sufficiently well to reduce unnecessary recovery and missed failures at a fixed intervention budget.

This is narrower than claiming the first robot failure detector or the first uncertainty-aware world model.

## 4. Proposed system: TriCause Router

### Inputs

- observation/history before execution `o_<=t`;
- committed VLA action chunk `a_t:t+h`;
- WAM predictive distribution over future task latents or object effects;
- actual post-execution RGB and proprioception;
- optional second view or one delayed re-observation.

### Evidence channels

1. **Action-effect residual:** mismatch between predicted and observed object/robot effects.
2. **Model-support evidence:** ensemble disagreement, density/support score, or held-out WAM disagreement.
3. **Physical consistency:** gripper state, end-effector motion, object displacement/contact, and action reachability or inverse consistency.
4. **Observation consistency:** agreement across views or adjacent frames; sensitivity to re-observation.

### Output

Use multi-label probabilities rather than a forced exclusive class:

- `E_exec`: physical execution failed;
- `E_model`: WAM is unsupported or misspecified;
- `E_obs`: current observation is unreliable or ambiguous;
- `nominal`.

Set-valued calibrated output is preferable when two causes cannot be separated.

### Routing policy

| Attribution | System response | Memory update |
|---|---|---|
| execution failure | stop chunk; invoke recovery/replan | correct or invalidate affected progress |
| WAM error/OOD | reduce WAM authority; re-predict, recalibrate, or adapt | do not overwrite task progress from the residual alone |
| observation ambiguity | wait, change view, or request another sensor | keep relevant state pending |
| mixed/uncertain | conservative stop plus evidence acquisition | abstain from irreversible write |

The contribution is the attribution-conditioned intervention and its evaluation, not merely a new classifier head.

## 5. How to construct identifiable data

Use simulator interventions with privileged labels only for training/evaluation.

### Cause family A: execution failure

- gripper command drop or force reduction;
- action scaling/delay;
- object slip after grasp;
- collision/blocked motion;
- unexpected object displacement.

### Cause family B: WAM error while task execution remains correct

- unseen texture, lighting, camera extrinsics, background, or object instance;
- held-out mass/friction/tool regime where the intended postcondition is still achieved;
- WAM checkpoint corruption or restricted training support.

Operationally, the physical task postcondition must be true while the WAM prediction is wrong. A domain shift alone is not automatically a WAM error.

### Cause family C: observation ambiguity

- transient occlusion;
- blur or exposure shift;
- dropped/frozen frame;
- single-view aliasing resolved by a second view.

### Critical control

Match examples across cause families by residual magnitude, task stage, and visible motion. Otherwise a threshold or task-stage shortcut can solve the benchmark.

Include mixed-cause examples only after the single-cause pilot passes.

## 6. Training objective

Freeze the VLA and initially freeze the WAM. Train a lightweight router with:

- multi-label attribution loss;
- class-conditional or set-valued calibration;
- a cost-sensitive term derived from the downstream routing cost matrix;
- optional invariance across matched-residual pairs.

The router should be small enough that gains cannot be explained by replacing the WAM with a second large policy model.

## 7. Baselines required to prove the claim

1. scalar prediction-error threshold;
2. CheckVLA-style binary intervention monitor;
3. WAM uncertainty/ensemble disagreement alone;
4. observation-only anomaly detector;
5. direct discriminative cause classifier with the same data and parameter budget but no WAM prediction;
6. proprioception/geometric postcondition verifier;
7. oracle cause labels and oracle routing.

Baseline 5 is mandatory. If it matches the proposed system, WAM is not necessary for the claimed mechanism.

## 8. Minimal experiment

### Phase A0: identifiability audit

- 3 manipulation tasks with grasp, transport, and placement/contact phases;
- 3 cause families plus nominal;
- at least 100 matched events per family for an initial pilot;
- task-held-out and perturbation-held-out splits;
- frozen pi0.5 or another action-chunk VLA.

Report:

- macro-F1 and E-vs-M confusion under matched residual bins;
- set coverage and average set size if calibrated set output is used;
- unnecessary intervention rate at fixed execution-failure recall;
- missed-failure rate at fixed intervention budget.

### Phase A1: closed-loop routing

Compare all systems with the same recovery policy, memory mechanism, and number of interventions. Report:

- task success;
- recovery success;
- false recovery/false rollback rate;
- incorrect progress-memory edits;
- extra observation and latency cost.

### Phase A2: real robot

Only after the simulator result passes: 3 tasks, controlled actuator/slip faults, camera/appearance shifts, and transient occlusions. Do not claim general physical fault isolation from three tasks.

## 9. Kill criteria

Stop or reframe the idea if any of the following holds:

- matched-cause attribution improves macro-F1 by less than 10 percentage points over uncertainty-only and direct-classifier baselines;
- false recovery is not reduced by at least 30% at matched execution-failure recall;
- closed-loop task success improves by less than 5 absolute points over binary discrepancy routing;
- deployable sensors cannot identify the causes without privileged state;
- WAM features do not beat the direct discriminative classifier;
- most examples are intrinsically mixed and calibrated abstention dominates explicit attribution.

## 10. Nearest work and remaining gap

- **CheckVLA (2607.26789):** action-conditioned frozen WM, conformal intervention, suffix rewrite, and progress keyframes. It verifies that execution deviated; the abstract does not establish robot-vs-WM-vs-sensor cause attribution.
- **When to Trust Imagination (2605.06222):** future-reality verification controls action chunk length. It estimates whether rollout remains trustworthy, not why trust failed.
- **Foresight (2606.23085):** action-conditioned WM latents and functional conformal prediction for long-horizon failure detection. It strengthens the detection baseline but does not expose the attribution gap.
- **Foundational World Models Accurately Detect Bimanual Manipulator Failures (2603.06987):** probabilistic WM uncertainty as a failure monitor. This makes uncertainty-only a strong baseline and illustrates the potential conflation.
- **World Action Verifier (2604.01985):** separates state plausibility and action reachability to detect and repair WM prediction errors. It is the closest model-self-verification neighbor, but its target is improving the WM in underexplored regimes rather than routing a real execution mismatch among robot/model/observation causes.
- **Pre-VLA (2605.22446):** pre-execution safety and advantage scoring for action chunks. It addresses bad proposed actions before execution, not post-execution attribution.

## 11. Current score

| Dimension | Score | Reason |
|---|---:|---|
| problem importance | 8.5/10 | wrong interventions directly harm long-horizon reliability and memory |
| WAM necessity | 7/10 | action-conditioned expected effects are useful, but must beat a direct classifier |
| novelty | 6.0/10 | independent review: medium overlap; only matched-cause attribution and routing remain defensible |
| feasibility | 7/10 | frozen pi0.5 plus lightweight router is tractable, but deployable identifiability is unresolved |
| publication risk | medium-high | causal identifiability and classical fault diagnosis can absorb an overly broad claim |

## 12. Verdict

**Proceed only as a benchmark-first, attribution-conditioned intervention study.** Do not begin by training a large WAM or modifying pi0.5. The first scientific result must be that equal-sized residuals require different responses and that deployable evidence can distinguish them.
