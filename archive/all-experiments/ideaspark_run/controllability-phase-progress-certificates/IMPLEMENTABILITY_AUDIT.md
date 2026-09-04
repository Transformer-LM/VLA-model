# CPPC Implementation Feasibility Red-Team Audit

**Concept:** Controllability-Phase Progress Certificates (CPPC)  
**Date:** 2026-08-31  
**Scope:** implementation feasibility under 4×A100, frozen/fine-tunable π0.5, RGB + proprioception, LIBERO/RoboTwin-like simulation, and no tactile sensing  
**Experiment status:** no experiment, rollout, training job, or GPU process was started

## Bottom line

**Verdict: conditional GO for an oracle kill test; not yet implementable as a frozen-WAM method claim.** The simulator-side test is cheap and worthwhile. The learned-WAM test requires a new matched-branch dataset producer, an object-conditioned metric effect head, and short observation history. Current π0.5/LIBERO assets do not already provide these pieces.

The strongest blocker is structural, not computational:

> Imagined finite differences cannot recover a contact fact that is absent from the WAM's conditioning observation. If two hidden physical states induce the same RGB/proprioceptive history, then a WAM receives the same `(history, candidate action)` inputs in both states and must produce the same conditional response distribution for every imagined perturbation. Counterfactual actions add no new information unless one is physically executed.

Consequently, CPPC is viable only for contact modes already inferable from a short visual/proprioceptive history—e.g., recent object/EEF co-motion and gripper closure. But this creates the second major risk: a same-capacity history classifier may solve the predicate without finite differences. CPPC is killed as a mechanism if action-intervention controls show that its signature is only a disguised contact classifier.

The smallest defensible scope is therefore **local physical contact-mode certification**, initially stable grasp/loss and one genuinely different constrained-contact family. It is not a general progress certificate for semantic placement, task completion, or long-horizon memory.

## 1. What is actually available

The official OpenPI LIBERO evaluation path supplies an agent-view RGB image, a wrist RGB image, EEF position and axis-angle orientation, gripper joint positions, and a language prompt. It queries π0.5 for an action chunk and executes the first five actions before replanning. The server response is an action chunk, not an action-conditioned future-state or object-effect prediction. Thus **π0.5 cannot itself serve as the CPPC WAM**. See the [official OpenPI LIBERO client](https://github.com/Physical-Intelligence/openpi/blob/main/examples/libero/main.py).

The default LIBERO data configuration is RGB/low-dimensional robot state and short sequences; depth is not part of the default observation contract. See the [official LIBERO data configuration](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/master/libero/configs/data/default.yaml).

A workspace inventory found proposal artifacts but no runnable OpenPI/LIBERO/RoboTwin checkout, same-domain WAM checkpoint, object tracker, or simulator branch producer. Therefore:

- **Existing data are sufficient only to choose nominal π0.5 actions**, once the external stacks are installed.
- **Existing demonstrations are not sufficient to identify local finite differences**, because they do not contain cloned states with matched ± perturbation branches.
- **No verified frozen WAM currently has the required output or sensitivity.** A generic video WAM is not an acceptable drop-in: small contact-conditioned image differences can be below its stochastic/video reconstruction noise.
- Four A100s are ample for a small object-effect model or π0.5 inference. They do not remove simulator cloning, object identity, or partial-observability problems.

Fine-tuning π0.5 is unnecessary for E0 and would confound the causal question. Keep the policy frozen. If a WAM must be trained, train only the smallest effect model needed to recover the oracle signature.

## 2. Minimum observable state and object feature

### 2.1 Conditioning state

A single RGB frame is inadequate. The minimum input should be a **3–5 frame history spanning roughly 0.3–0.5 s at 10 Hz**:

1. calibrated agent-view and wrist RGB;
2. EEF position and orientation; finite-difference EEF twist derived from the history;
3. gripper position, gripper velocity, and preceding gripper command;
4. the last 3–5 executed 7-D actions;
5. task prompt/target-object identifier;
6. joint position/velocity only if the simulator/controller interface already exposes it—useful for detecting saturation, but not a required conceptual input.

This history is required because stable grasp is primarily visible as object/EEF co-motion and persistent gripper configuration. It is not a convenience feature: without it, hidden-contact pairs can be observationally identical.

### 2.2 Minimum predicted feature

For E0, do not predict pixels, dense PointMaps, full scene state, or a semantic predicate. Predict only:

```text
μ_o = expected target-object translation Δp_obj ∈ R³ over a 2–5 step branch
μ_e = expected achieved EEF translation Δp_ee ∈ R³ over the same branch
q_vis = object visibility/tracking quality
Σ_o, Σ_e = optional heteroscedastic covariance used only to reject unresolved effects
```

Object rotation should be deferred until translational coupling passes. Millimetric 6-D pose estimation, object symmetry, and quaternion noise would otherwise dominate E0.

The visual object token should be pooled from frozen multiview image features under a target-object mask/slot, followed by a small temporal action/proprioception head. Simulator object pose can supervise `Δp_obj` during training, but privileged masks, object poses, contact forces, or depth cannot be inputs at evaluation. If target-object localization is not already available from task-conditioned vision, that is a required subsystem and must be counted in feasibility.

## 3. Perturbation basis and signature

### 3.1 Smallest basis

Use the nominal frozen-π0.5 prefix and six imagined central-difference branches:

```text
u⁰, u⁰ ± ε e_x, u⁰ ± ε e_y, u⁰ ± ε e_z
```

where the basis is base-frame translational OSC motion. Preserve nominal orientation and gripper command. Apply the perturbation to the first two steps of the deployed five-step prefix; execute/predict the rest nominally. Clip only after converting to the simulator's physical controller convention.

Do not define `ε` in raw normalized action units. Calibrate it so the median one-sided **achieved cumulative EEF displacement** is 4, 8, or 12 mm for the three stability settings. The central 8 mm setting is the primary condition. This is large enough to clear rendering/tracking noise but still intended to remain local. If the contact mode changes between the + and − branch, that state is a non-differentiable boundary case and must be flagged, not averaged into a rank.

Do not include gripper open/close as a derivative direction: it is discrete and deliberately changes contact mode. It can be a later discrete contrast. Add ±2° rotations only after translation succeeds and only for rigid tool attachment; they are not part of the minimum E0.

### 3.2 Use realized robot motion, not commanded motion

For each axis `j`, form

```text
J_o[:,j] = (Δp_obj(+j) − Δp_obj(−j)) / (2 ε_j)
J_e[:,j] = (Δp_ee (+j) − Δp_ee (−j)) / (2 ε_j)
C         = J_o J_eᵀ (J_e J_eᵀ + λI)⁻¹
```

`J_o` is the object effect, `J_e` exposes controller/environment constraints, and `C` measures object–EEF coupling. Keeping all three is necessary:

- stable grasp is primarily `C: near 0 → near I`;
- insertion or a rail constraint may primarily reduce the singular spectrum of `J_e`/`J_o`;
- normalizing only by achieved EEF motion can erase the constraint transition that insertion is supposed to reveal;
- using command deltas alone confounds contact with OSC saturation and collision response.

Never use raw numerical matrix rank. Define an active singular mode only if its normalized singular value is at least 0.25 **and** at least 5× the branch-repeat/tracker noise floor. Store the full singular spectrum and principal subspace; the thresholded rank is only a summary.

## 4. Oracle simulator producer

The missing critical component is a matched branch producer. At selected rollout states it must:

1. save the full simulator state—not just visible qpos—including qpos/qvel, object/articulation states and velocities, actuator/mocap state, controller goal/integrator state, renderer/camera state, and RNG;
2. restore that exact state for nominal and six ± branches under common randomness;
3. roll each branch for 2–5 control steps and record two-view RGB, robot state, commanded and achieved motion, privileged target-object pose, articulation coordinates, contact IDs/impulses, and semantic mode label;
4. rerun at least 5% of anchors twice to measure restoration determinism;
5. split data by episode lineage, object instance, and seed, never by individual branch frame.

The label producer must distinguish touch from a stable mode. For grasp, require bilateral finger/object contact plus persistent object–EEF co-motion for at least three steps or a small lift; a single contact bit is not enough. Contact impulses are privileged labels/diagnostics only and are never WAM inputs.

If restored identical branches differ by more than 5% in Frobenius signature norm, or controller/RNG state cannot be reproduced, CPPC is not measurable in that simulator until the producer is fixed.

## 5. WAM interface

The minimum interface is:

```python
predict_effect(
    rgb_history, proprio_history, executed_action_history,
    candidate_action_prefix, target_object_token
) -> {
    delta_object_xyz_mean,
    delta_eef_xyz_mean,
    covariance,
    visibility_quality,
}
```

It must batch all seven branches for the same observation. The downstream CPPC code constructs `J_o`, `J_e`, and `C`; the WAM must not output the predicate label or matrix rank directly.

The smallest credible WAM is an R4-style object-centric dynamics head: a frozen vision encoder, target-object pooling/slot, temporal proprio/action encoder, and a 10–30M parameter metric displacement head. A stochastic pixel/video generator is scientifically unnecessary and likely less sensitive to millimetric effects. A frozen video-WAM feature may be used only if it first passes an action-effect resolution test; otherwise fitting a small effect head is the honest E0.

### PointMap/depth decision

- **Oracle Stage 1:** neither PointMap nor depth is needed.
- **RGB Stage 2:** neither should be required. Calibrated two-view RGB plus simulator metric-pose supervision should be tried first.
- Depth or a PointMap may be used as a privileged diagnostic/upper bound, not as the primary evaluation input.
- If CPPC passes only with ground-truth depth, ground-truth masks, or simulator object pose at test time, it fails the stated RGB+proprioception contract.

Adding a monocular PointMap before the translational E0 passes introduces scale error, occlusion error, and another trainable component without solving hidden contact. It is not a remedy for the core observability blocker.

## 6. Which predicates can actually exhibit a phase transition?

| Predicate/event | Expected signature | Assessment |
|---|---|---|
| Stable rigid grasp acquired | `C≈0 → C≈I`; effective coupling rank 0→3 | **Strongest and first test.** Requires persistent co-motion, not contact bit. |
| Grasp lost/released | `C≈I → C≈0` | Strong inverse transition, but not an independent family; rank 0 alone cannot distinguish released from never grasped. |
| Rigid tool/object latch | coupling rank 0→3, possibly rotation too | Physically clean if the simulator has a true rigid attachment; not broadly present in LIBERO. |
| Drawer/slider handle engaged while held | one dominant rail direction; rank/subspace near 1 | **Conditional second family.** Sensitive to handle slip, controller compliance, and whether object output is drawer body or joint. |
| Peg/contact insertion while held | lateral modes may collapse; axial mode remains | Fragile. Usually continuous/hysteretic and amplitude-dependent; central differences may cross contact modes. Must be treated as a stress test, not assumed success. |
| One-sided pushing contact | asymmetric cone-like response, apparent rank 1–2 | Poor fit to a symmetric Jacobian; +/− branches often inhabit different modes. |
| Object correctly placed after release | generally `C≈0` both inside and outside target | **No identifiable local phase transition.** |
| Stack stable, task complete, door/drawer open vs closed, correct receptacle | semantic state can change while local rank is unchanged | **Not certifiable by CPPC.** Use other progress evidence. |

Only stable grasp has a near-guaranteed clean transition under the stated setup. The concept needs one distinct constrained-contact family to pass; otherwise the general mechanism collapses to “grasp detector through imagined motion,” too narrow to support the proposed progress-certification role.

## 7. Blocker ledger

### B1 — Hidden contact remains unobservable (**fundamental**)

Matched physical states with identical RGB/proprio history but different hidden contact induce identical WAM counterfactuals. More imagined actions do not resolve this. Required response: use history and quantify matched-pair observability. If the matched-pair ceiling is low, stop; do not blame training.

### B2 — WAM action-effect resolution is below the perturbation signal (**likely**)

Contact features may move only a few pixels over a short horizon, while a generative WAM has stochastic and reconstruction noise. Required response: metric object-displacement output and repeat-noise SNR gate. Full video quality is irrelevant.

### B3 — Contact dynamics are non-smooth (**fundamental at boundaries**)

Rank is undefined when ± perturbations enter different contact modes. Friction, sticking/sliding, backlash, and unilateral contact make the local response set-valued. Required response: amplitude/horizon stability gate and explicit “unresolved boundary” output; never force a certificate.

### B4 — Controller effects masquerade as physical phase (**high**)

OSC clipping, singularity, collision avoidance, and blocked EEF motion alter the matrix independently of progress. Required response: record `J_e`, normalize using realized motion, and include free-space controller controls at matched robot poses.

### B5 — Visual object identity and occlusion (**high**)

The object is often occluded by the gripper exactly at grasp/contact. Wrist motion and specular/texture-poor objects destabilize tracking. Required response: two-view temporal object token and visibility rejection; privileged masks at test are prohibited.

### B6 — Numerical rank instability (**high**)

Hard rank flips under tiny noise and choice of scale. Required response: singular-spectrum SNR, fixed physical units, three amplitudes, two horizons, and continuous subspace metrics.

### B7 — Ordinary-classifier equivalence (**fatal to mechanism claim**)

Gripper width, object height, and recent co-motion may directly identify grasp. If shuffling or zeroing imagined actions leaves predicate accuracy largely unchanged, the WAM is acting as a state classifier. Required response: equal-capacity current-frame and short-history baselines plus action-intervention controls.

### B8 — Nominal demonstrations lack local interventions (**certain**)

Standard policy demos cannot estimate matched finite differences. Required response: generate cloned branches. Do not estimate the Jacobian from unrelated transitions.

### B9 — Privileged leakage (**fatal to deployment claim**)

Simulator object pose, depth, contact IDs, or masks in the evaluation input turn E0 into an oracle. They are valid labels/upper bounds only.

## 8. Minimal two-stage E0

### Stage 1 — Oracle physical headroom and stability

**Question:** do the simulator/controller dynamics themselves contain a stable predicate-specific signature?

Use privileged object/EEF poses, no learned WAM. Test stable grasp/loss plus exactly one distinct constrained-contact family available in the simulator (prefer drawer/slider engagement; use insertion only as a harder alternative).

Minimum data:

- 100 independent anchor states per mode per family;
- at least 10 episode lineages and two object/scene instances per family;
- nominal + six translational branches;
- 4/8/12 mm achieved-displacement settings and 2/4-step horizons;
- lineage/object/seed-held-out evaluation.

This is roughly 400 primary anchors and 11,200 primary branch steps before the stability sweep; even a 3×2 sweep remains small.

**Pass all gates:**

1. restoration repeat error ≤5% in matrix Frobenius norm;
2. true-vs-false event AUROC ≥0.90 in-distribution and ≥0.85 on held-out lineage/object;
3. rank-state agreement across amplitudes/horizons ≥85%; median constrained-subspace principal angle ≤20°;
4. every retained active singular mode has SNR ≥5;
5. the second physical family—not release as the inverse of grasp—reaches held-out AUROC ≥0.85;
6. matched free-space robot-pose controls do not produce the same signature (false-positive rate ≤10%).

**Immediate kill:** oracle AUROC <0.85 for grasp, no second family passes, or rank/subspace changes under the perturbation scale more than they change across predicate state. In that case a learned WAM cannot rescue the mechanism.

### Stage 2 — RGB-WAM recoverability and non-classifier test

**Question:** can RGB+proprio history recover the oracle action-effect signature, and is the action dependence essential?

Generate 3,000–5,000 independent branch anchors after Stage 1 passes, yielding about 105k–175k short branch transitions at seven branches × five steps. Train/freeze a vision encoder and fit the small object-effect head. Use unseen object/scene/episode lineages for the primary test.

Required baselines and controls:

- equal-capacity current-frame predicate classifier;
- equal-capacity 3–5 frame history classifier;
- action-shuffled columns within each state;
- zero/nominal-action replacement;
- unseen perturbation amplitude and rotated translation basis;
- optional privileged-depth upper bound, never the main result.

**Pass all gates:**

1. object displacement MAE ≤3 mm on branches with median 8 mm robot displacement;
2. relative Frobenius error of the oracle effect matrix ≤0.35;
3. median oracle/WAM principal-subspace angle ≤20° and rank-state agreement ≥80%;
4. held-out predicate AUROC ≥0.85 on both physical families;
5. at least +0.05 absolute AUROC over the same-capacity short-history classifier;
6. action shuffling lowers oracle-subspace alignment by ≥0.20 and predicate AUROC by ≥0.10;
7. unseen-amplitude/basis AUROC decreases by no more than 0.05;
8. at least 80% of evaluated states exceed the singular-mode SNR gate; the rest must abstain.

**Immediate kill or scope reduction:**

- If the history classifier matches within 0.05 AUROC, CPPC has not demonstrated value beyond classification.
- If action shuffling causes <0.10 AUROC loss, the “finite-difference controllability” mechanism is not being used.
- If only stable grasp passes, rename the method as a grasp-coupling diagnostic; do not claim general progress certification.
- If privileged depth passes but RGB does not, report an RGB observability failure rather than adding PointMap machinery to the main method.

No policy-level recovery experiment is needed before these two gates. They are sufficient to decide whether the core physical certificate exists and is observable.

## 9. Estimated time on four A100s

These are run-time estimates **after** the simulator/policy stack and branch producer are integrated; engineering time is separate.

| Work | Wall time | GPU use |
|---|---:|---:|
| Branch-producer integration and state-clone validation | 1–2 engineer-days | negligible |
| Stage 1 nominal π0.5 snapshot collection + oracle branches | 3–6 h | about 1–2 A100-h for policy inference; simulation is CPU/render-bound |
| Stage 1 analysis | <1 h | negligible |
| Stage 2 3k–5k anchor branch generation | 6–12 h | mostly CPU/render-bound |
| Frozen visual-feature cache | 1–2 h | 1–2 A100-h |
| Four effect-head seeds in parallel | 2–4 h wall | 8–16 A100-h total |
| Stage 2 controls and evaluation | 1–2 h | 2–4 A100-h |

Expected post-integration end-to-end wall time is approximately **12–24 hours**, with **12–24 A100-hours** and more CPU simulator time than GPU time. Four cards mainly allow seed/control parallelism. Full video-WAM fine-tuning would likely expand this to multiple days and is outside the minimum E0; it should not be authorized unless the small metric-effect head first passes.

## 10. Final implementation decision

Proceed only with Stage 1. Do not yet describe CPPC as a frozen-WAM-ready method.

The concept earns a Stage 2 implementation only if the oracle simulator shows a reproducible signature for stable grasp **and** one distinct constrained-contact family. It earns the mechanism claim only if the RGB WAM recovers that signature on held-out instances, exceeds the equal-capacity history classifier by at least five AUROC points, and fails decisively when counterfactual actions are shuffled.

The likely outcome is narrower than the original idea: stable grasp/loss may work, while insertion/pushing and semantic placement may not possess a stable local rank transition. That is a bounded E0 risk, not a compute blocker. The actual blockers are hidden-state observability, millimetric WAM sensitivity, simulator clone fidelity, and classifier equivalence.
