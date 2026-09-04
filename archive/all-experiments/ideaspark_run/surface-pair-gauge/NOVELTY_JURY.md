# Strict Novelty Jury — Surface-Pair Gauge Action Representation

**Date:** 2026-08-31  
**Decision:** **FAIL / NO-GO**  
**Strict novelty score:** **6.55 / 10**  
**Gate:** novelty must be strictly greater than 7.0; 7.0 itself fails.  
**Naturalness:** **6.25 / 10**  
**Implementation feasibility:** **5.8 / 10** under the stated RGB-at-test constraint.  
**Oracle non-GPU E0:** **Not authorized for the current candidate.**

## 1. Exact claim audited

The candidate proposes that an **ordered pair of interacting functional surfaces**—one object-side and one environment/tool-side—defines a local relational gauge from surface centroids, normals, principal tangents, gap, and relative curvature. A complete relation-event trajectory is represented by gauge-covariant twist-spline coefficients plus gripper events. A VLA predicts both the surface pair and the coefficients, which are instantiated under unseen geometry. Simulator mesh or PointMap teachers may supervise training, but the surface pair must be inferred from RGB at deployment. There is no WAM, candidate search, test-time reranking, or tactile sensing.

The novelty judgment is about this **joint mechanism**, not merely the use of surface geometry, a task frame, a twist, a spline, or a VLA individually.

## 2. Four-axis novelty decomposition

| Axis | Judgment | Reason |
|---|---:|---|
| Problem framing | Moderate overlap | Transferring manipulation trajectories to unseen functional geometry is already a well-established problem. |
| Core mechanism | High partial overlap | Prior work already uses pairs of task-relevant local frames, local surface frame fields, surface constraints, and frame-parameterized motion primitives. |
| Key insight | High overlap | “Encode the skill relative to task-relevant geometry rather than the world/end-effector frame” is established. |
| Domain/evaluation | High overlap | The target domain—contact-rich manipulation and unseen-object geometry—is shared with the closest prior work. |

**Scoop level:** **Level 2 — high overlap.** I did not verify one paper containing every proposed component simultaneously. That absence is not evidence that the combination is novel enough, and the remaining delta must be judged by its mechanistic substance.

## 3. Closest primary-source prior art

| Prior work | Exact occupied mechanism | Residual difference from this candidate | Threat |
|---|---|---|---:|
| [R-NDF: SE(3)-Equivariant Relational Rearrangement with Neural Descriptor Fields](https://arxiv.org/abs/2211.09786) ([PMLR full text](https://proceedings.mlr.press/v205/simeonov23a/simeonov23a.pdf)) | Assigns consistent local coordinate frames to task-relevant parts on **two unseen objects** and executes the action by aligning those frames. It directly treats manipulation as a relation between object parts. | Primarily predicts/refines a terminal relational configuration rather than a full relation-event trajectory; it is point-cloud based rather than an RGB VLA head. | **Closest exact representation-level neighbor.** |
| [Object-centric Task Representation and Transfer using Diffused Orientation Fields](https://arxiv.org/abs/2511.18563) | Builds smooth, spatially varying local orientation frames on curved objects from raw point clouds and expresses continuous physical-interaction trajectories in those frames for transfer across object geometries. | Uses a surface orientation field rather than an ordered pair of interacting surfaces; not an RGB VLA. | **Closest trajectory-transfer neighbor.** |
| [Surface Constraint Policy](https://arxiv.org/abs/2605.31321) | Combines learned free-form surface constraints, a diffusion policy for task-level intention, and surface-constrained DMPs for smooth, dynamically feasible execution. | Does not define the proposed two-surface relational gauge or the exact twist-spline coefficient head. | **Closest end-to-end surface-policy neighbor.** |
| [Automatic Derivation of an Optimal Task Frame for Learning and Controlling Contact-Rich Tasks](https://arxiv.org/abs/2404.01900) | Learns task frames for contact-rich manipulation using screw-theoretic motion/wrench signals and executes the task in the derived frame. | The frame is inferred from demonstrations rather than explicitly constructed from two functional surfaces; it uses force/wrench observations. | Strong prior for task-frame plus screw/twist encoding. |
| [Learning from Few Demonstrations with Frame-Weighted Motion Generation](https://arxiv.org/abs/2303.14188) | Uses multiple reference frames to encode environmental context and synthesize motion under changed task geometry. | No ordered surface-pair gauge and no VLA. | Strong prior for task-parameterized trajectory transfer. |
| [GEAR-VLA](https://arxiv.org/abs/2606.08530) | A geometry-aware VLA action representation with 3D geometry features and action canonicalization for object, scene, and embodiment generalization. | Does not use a two-surface gauge or twist-spline relation-event representation. | Strong VLA-level neighbor; weakens claims that geometry-aware action representation in a VLA is itself new. |
| [ET-SEED](https://arxiv.org/abs/2411.03990) | Trajectory-level SE(3)-equivariant diffusion policy for generalizable manipulation. | No explicit functional-surface pair. | Occupies trajectory-level covariance/equivariance. |
| [EquiBot](https://arxiv.org/abs/2407.01479) | SIM(3)-equivariant diffusion policy for rotation, translation, and scale generalization to new objects/scenes. | No surface-pair gauge. | Weakens broad equivariant-generalization claims. |
| [RPDiff](https://arxiv.org/abs/2307.04751) | Geometry-conditioned diffusion over multimodal object–scene relational poses for unseen geometries. | Terminal pose rather than a full event trajectory; no explicit surface-pair coefficient representation. | Strong terminal-relational-pose baseline. |
| [NDF](https://arxiv.org/abs/2112.05124) and [Local NDF](https://arxiv.org/abs/2302.03573) | Category/local-geometry descriptors transfer object–target relations and manipulation demonstrations to novel instances and shapes. | No complete two-surface trajectory gauge. | Establish the local-functional-geometry lineage behind R-NDF. |

The strongest adversarial reading is not “one paper already did the entire candidate.” It is:

> **R-NDF's paired task-relevant frames + Diffused Orientation Fields' local surface trajectory transfer + Surface Constraint Policy/task-parameterized movement primitives' structured trajectory decoder + a modern geometry-aware VLA interface.**

This composition leaves a coherent residual, but it does not create an obviously new learning principle.

## 4. Component overlap versus joint difference

### Components already substantially occupied

1. **Two task-relevant entities/parts define a relation frame:** R-NDF.
2. **Local surface frames transfer trajectories across shape changes:** Diffused Orientation Fields.
3. **Surface geometry constrains a structured motion primitive:** Surface Constraint Policy and task-parameterized movement-primitive work.
4. **Twist/screw coordinates in a learned task frame:** automatic task-frame and invariant motion-descriptor literature.
5. **Trajectory-level equivariance:** ET-SEED and related equivariant diffusion policies.
6. **Geometry-aware VLA action representations:** GEAR-VLA.
7. **Unseen relational geometry and multimodal target poses:** RPDiff/R-NDF/NDF.

### Residual joint delta

The defensible residual is narrower:

> A VLA predicts an **ordered object-surface/environment-surface pair** and a **full relation-event trajectory** in the pair-derived gauge, rather than predicting only a terminal relation or conditioning a generic trajectory decoder on one surface.

That delta is coherent. However, its interaction is presently mostly representational: select two known kinds of functional parts, compute a task frame from familiar differential-geometric quantities, and predict a familiar spline/twist trajectory in that frame. The proposal does not yet identify a learning-theoretic or control property that emerges specifically from the ordered pair and cannot be achieved by R-NDF-style paired frames, a learned surface frame field, or a task-parameterized diffusion/DMP baseline.

Therefore, “no single paper contains the same list of modules” is insufficient for a score above 7.

## 5. Naturalness and the strongest fatal objection

The representation is natural for a restricted family of tasks—such as insertion, surface following, hanging, wiping, or placement—where two visibly identifiable functional surfaces determine a local interaction geometry.

It is not yet a natural **general** action representation because the proposed deterministic gauge is not well-defined on many common surfaces.

### Fatal issue: gauge singularity and discontinuity

- A principal tangent is undefined or unstable when principal curvatures are equal or nearly equal: planar patches, spherical patches, and locally isotropic regions.
- Cylindrical or axially symmetric geometry retains ambiguity along symmetry directions.
- Estimated normals have sign ambiguity; tangents have sign and possible axis-permutation ambiguity.
- Small RGB/PointMap noise, partial occlusion, or a slightly different surface crop can flip the tangent or move the centroid, creating a discontinuous coordinate system even when the physical task changes smoothly.
- Ordering the two surfaces does not remove each surface's internal tangent gauge ambiguity.

Consequently, the phrase **“gauge-covariant coefficients”** is not enough. The method must specify how coefficients transform under sign flips, tangent permutations, and locally undefined frames, and how the learned predictor marginalizes or remains equivariant to those alternatives. Without that machinery, this is a brittle hand-engineered task frame rather than a principled gauge representation.

### Additional conceptual objections

1. **Two surfaces do not determine the whole skill.** The same pair can support several approach sides, grasp schedules, obstacle-avoidance paths, contact modes, and joint-limit solutions. The spline coefficients still encode most of the difficult decision.
2. **RGB test-time perception is the bottleneck.** Accurate functional-surface correspondence, normal, curvature, and tangent recovery from RGB under occlusion is materially harder than using simulator mesh teachers. Oracle geometry performance would not establish deployment feasibility.
3. **Frame selection and action generation are conflated.** A failure may come from surface-pair selection, frame construction, or coefficient prediction. The current claim does not isolate which component causes geometry generalization.
4. **No tactile/force input limits contact claims.** The representation may improve geometric approach and placement, but it cannot by itself establish force regulation, friction-aware stability, or dynamic contact feasibility.

The singularity problem is not merely an implementation detail: it attacks the validity of the proposed central representation.

## 6. Claim ceiling

If implemented successfully, the strongest currently reviewer-defensible claim is:

> For visually observable manipulation tasks whose object-side and environment-side functional surfaces admit stable local directions, predicting a full trajectory in an ordered two-surface relational frame can improve cross-geometry trajectory transfer over world/end-effector frames, single-surface frames, and terminal relational-pose baselines.

The current evidence does **not** support claiming:

- the first relational or object-pair manipulation frame;
- the first surface-aware trajectory transfer method;
- the first geometry-aware VLA action representation;
- the first equivariant trajectory policy;
- a general action representation for arbitrary functional geometry;
- robust contact dynamics, force control, or physical feasibility;
- that RGB deployment preserves benefits observed with mesh/PointMap oracle surfaces.

## 7. What would be required to clear the novelty gate

Merely adding a VLA backbone, more tasks, or a learned surface detector would not be enough. A credible re-review would require a nontrivial mechanism that resolves the gauge ambiguity and yields a property absent from the closest work, for example:

- a distribution or equivariant frame field over the unresolved surface gauge rather than a deterministic principal-tangent frame;
- a proof or exact architectural guarantee that predicted action trajectories are invariant/covariant to surface parameterization, sign, and symmetry choices;
- explicit multi-contact relation-event transitions whose composition cannot be represented by terminal R-NDF alignment or a single-surface task frame;
- evidence that the two-surface relational structure, not merely better 3D perception, is the source of transfer.

That would be a materially different candidate and should receive a new novelty review.

## 8. Feasibility and E0 decision

### Decision

**Do not start the oracle non-GPU E0 for the present candidate.** The strict novelty gate fails, and the independent conceptual concern is already a NO-GO. Running an oracle trajectory experiment now risks validating a brittle task-frame implementation without resolving the contribution boundary.

### Diagnostic only, if a redesigned candidate is later approved

A future pre-GPU compiler diagnostic should first test whether the gauge is mathematically usable across a mesh suite containing planes, cylinders, spheres, symmetric openings, curved patches, partial crops, and realistic PointMap noise. It should be killed before policy training if any of the following holds:

1. frame direction has frequent sign/permutation flips under physically negligible perturbations;
2. a meaningful fraction of task surfaces has no stable principal direction;
3. identical physical trajectories produce discontinuous or high-variance coefficients;
4. a learned/smooth single-surface frame or R-NDF-style paired local-frame baseline is equally stable and expressive;
5. removing the second surface does not materially change the encoded trajectory or recoverability of the action.

These checks would diagnose representation validity; they would not by themselves establish publishable novelty.

## 9. Final verdict

**Novelty: 6.55/10 — FAIL.**

The ordered interacting-surface pair and full relation-event coefficient trajectory form a coherent residual idea, but the central scientific insight is largely covered by paired relational frames, local surface frame trajectory transfer, task-parameterized movement primitives, and geometry-aware/equivariant policies. The remaining mechanism is currently a plausible component recombination with a serious gauge singularity problem, not a reviewer-defensible greater-than-7 novelty contribution.

**Action:** archive as a potentially useful representation module, but do not authorize experiments or treat it as the next paper candidate without a symmetry-safe reformulation and a new strict novelty check.
