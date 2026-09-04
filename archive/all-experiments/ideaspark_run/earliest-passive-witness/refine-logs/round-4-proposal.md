# WitnessWAM v3 — Deployment-Valid Passive Witness Scheduling

**Revision target:** close the deployment-selection, visibility-baseline, action-lock, metric, and decode-key gaps from Round 3 without adding a second research problem.  
**Date:** 2026-08-31

## One-sentence method

Given the current RGB/proprioception, an object–relation query, and the exact five low-level actions already queued by a frozen VLA, WitnessWAM predicts the first *passive evidentiary opportunity* at which that relation can be distinguished from a physically matched alternative; until that opportunity, the external task-progress memory remains `PENDING`, while the action queue itself is never changed.

The claim is deliberately narrow: policy- and sensor-conditional witness scheduling should reduce false progress-memory commits/retractions compared with framewise verification, fixed delays, RGB visibility scheduling, and an equally action-conditioned visibility-hazard model. It does not claim active sensing, recovery, or an internal memory mechanism inside π0.5.

## 1. Structural continuation contract known before rollout

The experiment has an event-producing phase followed by one ordinary five-action continuation from the frozen π0.5 policy. A family is retained only if this continuation belongs to a preregistered, command-checkable structural envelope:

- `grasp-coupled(object, gripper)`: the gripper command does not reopen or reclose; the end effector withdraws or transports monotonically away from the initial grasp region; no target re-approach occurs; translational and rotational velocities remain under registered safety bounds.
- `inside(object, container)`: the gripper remains open; end-effector distance from the object–container interaction region is nondecreasing; no commanded re-approach, new grasp, or deliberate object/container contact occurs; velocities remain bounded.
- `on-target-support(object, target)`: the gripper remains open; end-effector distance from both object and named support is nondecreasing; no commanded re-approach or new contact occurs; velocities remain bounded.

These tests use only the queued denormalized physical commands, robot kinematics, named bodies, and the current checkpoint. They are evaluated before the five-action rollout and require no future predicate truth or learned eligibility model.

The **pre-prefix denominator** contains every common-parent lineage that is physically valid, replay deterministic, time-zero sensor-ambiguous, action-agreeing, safe, and inside this structural envelope. Privileged predicate truth is then audited after every executed action for every member of that denominator. A retained family must preserve the original truth on at least 95% of this entire denominator. Every truth transition remains in the denominator and is counted as a contract violation and closed-loop failure; it is never silently deleted or relabeled as a witness. Only the truth-preserving members can supply `tau_protocol` supervision, because a changed fact cannot identify evidence about the original fact. If fewer than two physical relation families pass 95%, the method is killed rather than adding an eligibility classifier.

Thus the learned method is deployed under a family-level continuation contract whose empirical precision is explicitly measured, not on a future-filtered easy subset.

## 2. Common-parent producers and frozen opportunity labels

Each accepted parent simulator state is cloned into a physically natural sensor-alias pair:

1. stable grasp versus natural miss;
2. settled inside versus settled rim/outside miss;
3. settled on the named support versus settled on an adjacent ordinary support.

Weld/equality toggles, hovering objects, solver transients, camera-only changes, and retries are forbidden. Clone hashes, duplicate replay, source-balanced cross replay, the full state residual, and every rejection reason are written to an append-only ledger. Parent lineages, not frames or prefixes, define train/validation/test splits.

A frozen, deterministic privileged protocol labels the earliest interval `tau_protocol ∈ {1,…,5,censored}` at which the pair's relation truth is sensor-distinguishable. It combines family-specific geometry, visibility of the queried regions, pairwise projected separation above a registered sensor-noise floor, and two-frame persistence. The protocol is fixed before neural training. A disjoint-lineage RGB/proprio evidence likelihood translates an opportunity into positive/negative relation evidence but cannot alter the opportunity labels.

## 3. Exact VLA prefix and action-lock semantics

Four server-side paired π0.5 flow-decode PRNG keys are fixed in the experiment registry before any rollout and used without replacement. Each key queries both aliases with the same decode noise. Raw normalized outputs and denormalized, clipped physical commands are cached.

Action agreement is computed in deployment command space, not normalized token space: per-step translation, rotation, gripper command, and any environment-specific actuator dimensions must all satisfy preregistered tolerances. A lineage enters the K-prefix action-necessity analysis only when at least three of the four fixed keys pass paired agreement, safety, and the structural envelope; missing keys are recorded and are never replaced. All four attempts remain in the yield denominator.

For every evaluated verifier, actions 1–5, their timing, the current prompt, and the next-subtask prompt are immutable once the chunk begins. An early verifier decision can only write a **staged, timestamped belief**. It cannot cancel an action, emit a new action, repeat the event prompt, or change the prompt. The first accepted staged decision is frozen for that chunk. At the five-action boundary, that staged belief is atomically committed to—or withheld from—the external progress memory; only then may the FSM advance, retract, or invoke the common fallback.

This creates identical physical trajectories for all verifiers. A transient witness can still matter because it may appear before the boundary and later become occluded; the scheduler may cache it without changing control. If simply observing the final frame is sufficient, the fixed-boundary baseline will win and the proposed mechanism is killed.

## 4. WitnessWAM and the decisive smaller baseline

WitnessWAM receives:

- current RGB and proprioception;
- named object/reference queries and the predicate type;
- the exact five-step denormalized action prefix.

It predicts one discrete interval-censored opportunity hazard, survival/censoring mass, and a queried evidence region. It is trained only on frozen protocol labels from truth-preserving audit members. PointMap may be used only as a privileged teacher or oracle upper bound; the deployable primary model is RGB+proprioception.

The decisive alternative is a **capacity-matched action-conditioned visibility hazard**. It receives exactly the same RGB, proprioception, queries, predicate type, and five-step prefix, has the same encoder capacity and hazard head, and is trained only to predict when the target/reference regions cross the registered visibility threshold. It never receives pairwise projected separation, relation-opportunity labels, or privileged predicate truth.

WitnessWAM keeps its mechanism claim only if, on held-out parent lineages, it improves both:

1. integrated time-dependent Brier score for `tau_protocol` by at least 10% relative to this visibility-hazard baseline; and
2. the fixed-FSM total error by at least 10% relative to the same baseline,

with the common-parent lineage-bootstrap 95% confidence interval excluding zero separately for every retained family. Otherwise the honest conclusion is that action-conditioned visibility scheduling is sufficient.

## 5. Baselines and fixed FSM endpoint

All methods receive the same immutable physical chunk and use the same first-accepted staged-decision rule:

- immediate/framewise RGB relation verifier;
- fixed decision times at steps 1–5, selected on validation only;
- final-boundary-only verifier;
- privileged visibility-only rule;
- deployable RGB visibility scheduler;
- capacity-matched action-conditioned visibility hazard;
- suffix-free relation-opportunity hazard;
- WitnessWAM;
- privileged `tau_protocol` oracle upper bound.

The primary operating point is selected on validation and frozen: at least 90% decision coverage, maximum wait five actions, and mean decision time no more than 0.5 action later than the best deployable baseline at the same coverage. The full risk–coverage–delay curve is secondary and cannot replace the primary result post hoc.

The primary system endpoint is a preregistered unit-cost total per lineage: one error if the staged boundary commit has the wrong relation value, one error if an incorrect advance/retract transition is atomically applied, and one error for unresolved timeout. Components are also reported separately; no oracle timing appears in the error definition. A single wrong commit may incur both a wrong-belief and wrong-transition error because these are distinct downstream states, and this weighting is frozen before test.

Before any neural experiment, the privileged oracle schedule must improve this endpoint by at least 20% over the best fixed-time, boundary-only, privileged-visibility, and deployable RGB-visibility baselines at the registered operating point, without increasing timeout by more than ten percentage points; the per-family lineage-bootstrap 95% interval must exclude zero in at least two families. Otherwise there is no scheduling headroom.

## 6. Action-conditioning necessity

The sole primary predictive metric is **integrated time-dependent Brier score**; C-index is diagnostic only.

Producer gate:

- exactly the four registered paired decode keys are attempted without replacement;
- among lineages with at least three valid prefixes, changing only the normal π0.5 prefix must shift `tau_protocol` by at least one action or change opportunity/censor status in at least 30% of lineages per retained family;
- preservation failures and missing prefixes remain in the attempt ledger and yield denominator.

Model gate:

- suffix-aware WitnessWAM must improve integrated Brier score by at least 10% relative to the capacity-matched suffix-free hazard on held-out parents, objects, and prefixes;
- prefix shuffling must erase at least 80% of this gain and return performance to the suffix-free confidence interval;
- uncertainty is estimated separately within each family by resampling common-parent lineages, never by treating the two or three families as statistical clusters.

Failure of either gate kills the action-conditioned WAM claim.

## 7. Frozen E0 gates

1. Duplicate replay determinism ≥99% among physically eligible parents.
2. Time-zero sensor AUROC upper 95% bound ≤0.60 per family.
3. Structural-envelope truth preservation ≥95% over the complete pre-prefix denominator per retained family.
4. Opportunity yield ≥25% over that same denominator; violations stay in the denominator.
5. Independent opportunity-window evidence AUROC ≥0.85.
6. Oracle total-FSM endpoint improvement ≥20% under the frozen operating rule, with timeout inflation ≤10 percentage points.
7. Producer-level and model-level action-conditioning gates above.
8. WitnessWAM's two numerical gains over the action-conditioned visibility hazard above.
9. At least two physically distinct relation families pass every applicable gate; no averaging rescue and no post hoc horizon extension.

## 8. Claim boundary and stop conditions

The paper may claim only that, under a preregistered five-action structural continuation contract, a relation-aware action-conditioned WAM can predict the earliest passive evidentiary opportunity and reduce false external progress-memory updates relative to visibility scheduling and fixed verification rules.

It does not claim active sensing, action reranking, failure recovery, physical truth certification, universal observability, internal π0.5 memory, or a deployable PointMap pipeline. If the continuation contract, oracle headroom, action necessity, or visibility-baseline comparison fails, the study stops or contracts to the corresponding diagnostic result; no extra module is added to rescue it.
