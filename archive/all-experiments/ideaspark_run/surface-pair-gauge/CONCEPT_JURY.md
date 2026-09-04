# Surface-Pair Gauge Action Representation: Skeptical Concept Jury

**Date:** 2026-08-31  
**Review route:** local Codex concept review; no delegated reviewer  
**review_independence:** same-family  
**acceptance_status:** provisional  
**Experiments run:** none  
**Evidence scope:** Candidate 3 in `pivot_candidates_after_giss.md`, the exact proposal supplied by the user, stated compute/sensing constraints, and known direct mechanism families; no broad literature search

## Executive Verdict

**Recommendation: NO-GO for end-to-end VLA/GPU implementation in the current form. CONDITIONAL GO only for the privileged, non-GPU gauge-transport falsifier below.**

The underlying problem is natural: insertion, hanging, sliding, and constrained placement are relations between interacting geometry, and base-frame actions often generalize poorly across size/layout changes. The proposed mechanism is not yet clearly a new learning principle. It currently looks like a task-parameterized movement primitive or spline expressed in a hand-designed two-surface coordinate frame, with a learned pair selector attached.

The most serious technical issue is not perception accuracy but **gauge well-posedness**. Centroids, normals, and principal tangents do not define a stable unique frame on flat, symmetric, cylindrical, low-curvature, partially observed, or nearly isotropic patches. Tangent eigenvectors can swap, flip sign, or rotate arbitrarily under tiny geometry/PointMap perturbations. Those are precisely common cases for slots, planar contacts, rods, hooks, and round containers. Unless the representation handles the surface pair's symmetry/stabilizer group explicitly, geometrically similar inputs produce discontinuous spline labels and decoded motions. A learned VLA cannot reliably repair a representation whose target coordinate system jumps.

The proposal should therefore earn permission in two stages:

1. show with privileged meshes, oracle surface pairs, no learning, and no residual controller that the two-surface gauge stably transports trajectories better than EEF-, object-, and single-surface frames;
2. only then test whether an RGB-derived PointMap student recovers enough of that oracle advantage.

## Scores

| Axis | Score | Judgment |
|---|---:|---|
| Scientific naturalness | **6.4 / 10** | Relational surface-to-surface motion is natural; the exact centroid/normal/principal-tangent gauge and two-surface sufficiency assumption are hand-designed and often singular. |
| Problem importance | **7.6 / 10** | Functional-geometry generalization is important for manipulation, especially under unseen widths, curvature, and layouts. Importance is limited if robust local geometry features or replanning already solve the same failures without a new action representation. |
| Implementation feasibility | **6.1 / 10** | The privileged gauge and spline are easy; RGB surface-pair selection, stable normal/curvature estimation, and contact execution without tactile sensing are the real bottlenecks. Four A100s suffice for small frozen-backbone heads after the oracle gate passes. |
| Novelty defensibility, provisional | **5.6 / 10** | Task-parameterized trajectory models already transform motions through multiple task frames; GEAR-VLA covers geometry-aware/canonical action representations; RPDiff and related relational/equivariant methods cover geometry-conditioned relative solutions. The remaining two-surface trajectory-gauge delta is narrow. |

## Natural VLA Problem or Coordinate-Frame Trick?

### The problem is natural

A trajectory for inserting an object into a slot should transform with the slot/object relation, not with the robot base. Likewise, hanging depends on hook/object geometry, and sliding depends on the relation between object support and environmental surface. A representation that factors out irrelevant global pose and scale can reduce the burden on a VLA action head.

### The current solution is predominantly a coordinate construction

The method prescribes:

- which geometric entities matter: exactly two ordered surfaces;
- their sufficient statistics: centroids, normals, principal tangents, separation, and relative curvature;
- the action basis: twist splines plus gripper events;
- the reconstruction map from coefficients to Cartesian motion.

Learning enters mainly through surface-pair selection, coefficient regression, and an optional dynamics residual. That is legitimate engineering, but it is not automatically a new VLA learning mechanism. The paper must show that the relational gauge removes a measurable source of variation that strong existing task frames cannot remove. Otherwise the contribution is “a carefully chosen frame plus a spline decoder.”

The optional residual controller is especially dangerous narratively. If it is powerful enough to repair reachability/contact errors, gains cannot be attributed to the gauge. It should be absent from the oracle test and only added after the representation itself clears the kill gate.

## Strongest Prior-Art/Mechanism Objection

> **This is a task-parameterized movement primitive in a brittle, hand-engineered two-surface frame. Task-parameterized GMM/GMR/HSMM and movement-primitive work already encode demonstrations in object/task frames and instantiate trajectories under new frame configurations; GEAR-VLA and relational/equivariant pose methods add modern geometry conditioning. “Ordered surface pair + twist spline” is an incremental frame specialization unless it solves a rigorously demonstrated covariance failure that those frames cannot.**

The objection has two parts.

### 1. Prior-art compression

Known direct mechanism families already cover most ingredients:

- **Task-parameterized GMM/GMR/HSMM and task-frame movement primitives:** represent demonstrations in one or more task/object frames, learn frame relevance, and synthesize trajectories after frame changes.
- **DMP/spline trajectory transport:** encode a motion compactly and instantiate it under new goals/frames.
- **GEAR-VLA and other geometry-aware/canonical action methods:** use geometry priors and canonicalized action representations for VLA generalization.
- **RPDiff, TAX-Pose, Neural Descriptor Fields, and equivariant diffusion/field methods:** represent object relations or generate relative SE(3) solutions from local geometry.
- **Classical local surface frames/point-pair features:** centroids, normals, curvature directions, and relative surface geometry are established 3D descriptors.

The defensible delta cannot be “geometry-aware action coordinates.” It must be the narrower claim that an **ordered interacting surface pair defines a stable trajectory-level gauge whose transported motion generalizes beyond multi-frame, single-surface, and EEF-relative alternatives**.

### 2. Gauge singularity

Let `G(S_obj,S_env)` be the proposed SE(3) frame. At minimum it should satisfy global equivariance:

`G(T S_obj, T S_env) = T G(S_obj,S_env)` for any rigid transform `T`.

That condition is insufficient when the surface pair has a nontrivial stabilizer group `H`: planar patches admit arbitrary tangent rotation without an additional cue; principal directions are undefined at equal curvatures; eigenvectors have sign ambiguity; cylindrical surfaces have rotational/axial symmetries; partially visible centroids move with occlusion. Then `G` is defined only up to an orbit `G H`, not as one continuous frame.

If the implementation picks one principal tangent by numerical convention, a tiny perturbation can send `G` to `G R_pi`, swap axes, or rotate it substantially. Gauge-covariant spline coefficients then jump even though the physical task changes smoothly. The proposal needs one of:

- an explicit quotient/orbit loss over all equivalent gauges;
- a task-observable orientation cue that resolves the symmetry continuously;
- invariant coefficients under the stabilizer group;
- multiple equivalent gauge hypotheses, which reintroduces multi-hypothesis complexity.

Without one, “gauge covariance” is a name rather than a property.

## Exact Representation Contract Needed

Before learning, the proposal must specify the representation mathematically.

1. **Surface roles:** define why the pair is ordered (`object-side`, `environment/tool-side`) and how role labels are obtained without test-time simulator semantics.
2. **Gauge map:** specify the origin and orthonormal axes and what happens when normals are parallel, anti-parallel, or principal curvatures are near-equal.
3. **Symmetry handling:** identify the stabilizer group for planes, cylinders, circular rims, and symmetric hooks; define the coefficient loss modulo that group.
4. **Twist convention:** if world/body twist is `xi(t)`, state whether encoded motion is `Ad_{G^{-1}} xi(t)` and how the spline basis is normalized across spatial scale and event duration.
5. **Event boundaries:** define how approach/contact/slide/release events and gripper events are aligned. Otherwise coefficient variance can be caused by phase misalignment rather than geometry.
6. **Decoder contract:** state whether the spline is a reference trajectory, direct Cartesian command, or input to an operational-space controller. Contact stability cannot be inferred from geometric covariance alone.

Two-surface sufficiency is itself a hypothesis. Insertion can depend on two slot walls plus object footprint; hanging can involve hook, object aperture, and gravity; sliding depends on support plane, object geometry, and obstacles. The proposal should not force all tasks into a pair if the functional relation is inherently ternary.

## Minimum Non-GPU Oracle Kill Test

**Purpose:** test the representation itself before adding RGB perception, a VLA, or a learned residual controller.

Use privileged simulator meshes and ground-truth ordered surface pairs. Select three relation families where a pair is at least plausible:

1. slot/insertion under held-out gap width and object scale;
2. hook/hanging under held-out curvature and aperture geometry;
3. surface-following/sliding under held-out plane orientation and obstacle layout.

For each family, use approximately five source geometries with successful demonstrations and ten held-out target geometries. Encode the same source trajectories with equal-capacity spline bases in:

1. robot base/world frame;
2. EEF-relative or start-pose-relative frame;
3. object-centric frame;
4. environment single-surface frame;
5. proposed ordered two-surface gauge.

Choose the source medoid/template coefficients under each representation, instantiate them on held-out geometry, and execute through the same deterministic low-level controller. Do **not** use a learned residual, RGB PointMap, VLA, planner at test time, or representation-specific trajectory tuning.

Measure:

- held-out simulator success and registered contact/clearance events;
- transported end-effector/object path error relative to successful oracle trajectories;
- coefficient dispersion across matched source geometries;
- sensitivity of decoded motion to small mesh/point perturbations;
- gauge jump rate under tangent sign swaps, principal-curvature near-ties, and partial surface cropping.

Apply the following kill rules before any GPU work:

- two-surface oracle success is less than **5 percentage points** above the strongest non-pair frame;
- removing either member of the ordered pair costs less than **2 percentage points**;
- gauge transport reduces matched-trajectory coefficient dispersion by less than **20%** versus the best single-frame baseline;
- more than **10%** of accepted surface pairs exhibit a frame jump larger than **30 degrees** under a pre-registered small perturbation, unless the decoded trajectory is explicitly invariant to that jump;
- gains come only from one relation family or disappear when event timing is normalized identically across baselines.

This is the cheapest decisive test because it grants the proposal perfect perception and exact surface semantics. If it fails, PointMap training or a VLA cannot make the coordinate system scientifically necessary.

## Feasibility With RGB-Derived PointMap/Geometry Teacher

### Privileged teacher

Simulator meshes can provide ordered patch pairs, normals, curvatures, event labels, and oracle gauges. Generating those labels is feasible. The teacher should also label degenerate/symmetric patches and the valid gauge orbit, not force an arbitrary principal-tangent sign into the target.

### RGB-derived PointMap student

The deployment problem is materially harder:

- a single RGB-derived PointMap may have scale/depth bias and missing backside geometry;
- centroids depend on segmentation and visibility;
- normals are first-order estimates, while curvature/principal tangents are second-order and substantially noisier;
- ordered patch-pair selection is combinatorial and semantically ambiguous;
- occlusion can hide the environment-side surface precisely during insertion/contact.

A feasible implementation is a frozen PointMap/VLM backbone plus a small role-conditioned patch-pair selector and coefficient head. Candidate patches should be pruned geometrically before ordered pair scoring. Training can distill simulator teacher pairs into RGB-derived patch distributions. The first learned test must report pair recall and gauge error separately from trajectory success; otherwise perception and representation failures are confounded.

### Pi0.5 and four A100s

Four A100s are sufficient for a bounded E0 with frozen PointMap/VLM/Pi0.5 features and trainable pair-selector/coefficient heads. The 48–96 A100-hour range is plausible only after surface preprocessing is cached and the residual controller is excluded. Full end-to-end fine-tuning, dense all-pairs patch attention, or multi-hypothesis symmetry resolution could exceed the estimate.

The proposed component count is already near the clarity limit:

1. PointMap/geometry student;
2. ordered pair selector;
3. gauge construction;
4. spline coefficient head and decoder;
5. optional dynamics residual.

The residual should be deleted from the initial method. Otherwise the paper becomes a perception + representation + controller stack rather than one focused action representation.

### No tactile sensing

Vision/proprioception can support pre-contact routing and quasistatic geometric alignment. It cannot reliably observe contact force, incipient slip, jamming, or friction changes. Therefore no-tactile claims should be restricted to geometry-driven transfer and simulator-stable contact schedules. Robust contact maintenance or real-world insertion safety would require tactile/force evidence or a much narrower claim.

## Outcome-to-Claim Matrix

| Oracle gauge | RGB gauge | Interpretation | Allowed next step |
|---|---|---|---|
| Fails frame baselines | Not run | Two-surface gauge is unnecessary or unstable | Kill concept; no GPU |
| Passes, but unstable under perturbation | Not run | Privileged geometry overfits a discontinuous frame convention | Redesign symmetry handling; no VLA |
| Passes and stable | Fails to recover at least half the oracle gain | Representation may work with privileged meshes, not as RGB VLA | Do not make VLA claim |
| Passes and stable | Recovers at least half the oracle gain | Conditional evidence for RGB relational action representation | Focused prior-art audit, then small frozen-backbone E0 |
| Only residual controller produces gains | Any | Gauge contribution is not isolated | Reject method claim or make residual the new project |

## Claim Ceiling

If all staged gates later pass, the strongest defensible claim is:

> For visually identifiable, pairwise functional relations with a stable or symmetry-aware surface gauge, expressing relation-event motion as two-surface-covariant twist splines improves held-out geometry transport over EEF-, object-, and single-surface task frames using a frozen VLA backbone.

The current concept cannot claim:

- a generally new idea of task-frame or geometry-canonical action representation;
- a unique gauge on symmetric/flat surfaces without explicit symmetry treatment;
- applicability to relations requiring three or more surfaces/entities;
- robust contact control without tactile sensing;
- a VLA contribution if gains require privileged test-time meshes;
- gauge benefit if a learned residual controller accounts for the improvement.

## Final Recommendation

**NO-GO for GPU experiments and NO-GO as a full VLA method in its current form.**

**Conditional continuation:** authorize only the privileged non-GPU oracle transport test. The concept earns a small RGB/PointMap E0 only if the two-surface gauge beats the strongest frame by at least five points, both surfaces are necessary, coefficient dispersion falls, and gauge discontinuities are controlled. Before GPU work, conduct a focused prior-art audit centered on task-parameterized movement primitives/GMMs, multi-frame trajectory learning, surface-frame control, GEAR-VLA, and relational/equivariant pose generation.

If the oracle passes, the cleanest method is **surface-pair gauge + spline head**, with the backbone frozen and the residual controller removed. If it fails, archive the idea rather than adding perception or control modules to compensate.
