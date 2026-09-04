# WitnessWAM v1 — Protocol-Relative Passive Witness Opportunities

**Revision target:** unify the data producer, estimand, hazard target, deployment horizon, and progress consumer.  
**Date:** 2026-08-31

## 1. Narrow claim

WitnessWAM predicts one quantity only:

> For a preregistered sensor protocol and the five low-level actions that the deployed VLA is about to execute, what is the distribution of the first window in which a pending physical relation becomes sensor-verifiable?

This is a policy-, action-prefix-, camera-, sensor-, predicate-family-, and label-protocol-relative opportunity time. It is not a universal earliest witness and not the truth of the predicate itself.

At the predicted opportunity, a separate frozen evidence likelihood updates the predicate belief. Before the opportunity the external task controller keeps the relation `PENDING`. There is no competing-risk head, no candidate action ranking, no active probe, no learned recovery policy, and no change to the VLA action head.

## 2. Common-parent compiled aliases

The unit is a common-parent lineage, not a frame or nuisance replica. From one fully serialized stable simulator parent, create a successful and a failed physical branch using family-specific interventions before the evaluation checkpoint. Return the robot to the same checkpoint pose and settle both branches. Accept the pair only if all locked non-descendant state agrees within registered tolerances and the allowed sensor protocol cannot distinguish the branches at time zero.

The branches are called **compiled sensor aliases**, not perfect causal twins. The state difference is allowed to include the minimal physical variables that constitute or directly support the relation; no simulator-only truth bit, weld, equality constraint, or artificial black occluder may be introduced.

Initial families and permitted branch differences:

1. `grasp-coupled(object, gripper)`: successful finger closure/contact/co-motion versus a naturally missed grasp. Permitted differences are object pose within the gripper-contact tolerance, finger-object contacts, and the resulting object velocity after the test prefix. Weld/constraint toggles are forbidden.
2. `inside(object, container)`: a successful release within the container interior versus a rim/outside miss produced by a small pre-checkpoint release offset. Permitted differences are object pose/contact relative to the container. The container rim or robot hand must provide native occlusion.
3. `supported-by(object, support)`: a stable placement/stack versus an unstable or off-support placement produced by a small pre-checkpoint offset. Permitted differences are object-support pose/contact and their physical descendants. Native hand/object occlusion only.

For every accepted pair, store the XML, flattened simulator state, mocap targets, actuator/controller state, task state, RNG states, camera parameters, action history, qpos/qvel, object pose/velocity, contacts, constraints, and a hash of the serialized clone. A duplicate replay test must produce matching future observations and states under the same action sequence before the lineage is eligible.

The acceptance ledger reports, per family: attempted, physically valid, stable, replay-deterministic, visually matched, time-zero ambiguous, five-step safe, later-opportunity, and every rejection reason.

## 3. Exact deployment intervention

At an accepted checkpoint, query one frozen VLA checkpoint once using the registered observation transform and random seed. Normalize and clip the output exactly as in its deployment client, then take the actual `h_exec=5` low-level actions. Restore both aliases and execute those identical five actions under common randomness.

The first study makes no claim beyond this five-step intervention. It does not use an expert suffix, a support-density estimate, an entire unexecuted action horizon, or a separately replanned continuation. If no witness opportunity appears in five steps, the lineage is right-censored at the deployment boundary.

## 4. Frozen opportunity-label protocol

The protocol is registered before neural model training and is independent of the WitnessWAM parameters.

For each predicate family, the protocol defines:

- the target and reference bodies;
- a privileged geometric truth predicate;
- camera projection and minimum visible-area rules for the relevant object regions;
- a relation-specific projected separation margin above the registered pixel/depth/proprio noise floor;
- a two-consecutive-window persistence rule;
- tie handling and interval censoring at the camera sampling resolution.

The earliest window satisfying visibility, projected-separation, and persistence is `tau_protocol`. No scan over learned encoders or classifier classes is allowed. A frozen, capacity-limited sensor evidence model is trained only on disjoint parent lineages to verify that protocol-positive windows are deployably distinguishable; it cannot change `tau_protocol`. If this translation-to-sensor check fails, the family is killed.

The estimand is therefore a single pair-level event time. The learning target is one discrete-time opportunity hazard with explicit right/interval censoring. At the opportunity, two frozen hypothesis likelihoods over the relation evidence perform the posterior update; those likelihoods are not event causes and are not called competing risks.

## 5. WitnessWAM model

Inputs:

- current RGB and proprioceptive history available to the deployed policy;
- predicate-family and target/reference object queries;
- the exact normalized five-step action prefix about to be executed.

Outputs:

- discrete opportunity hazard over the five executed steps;
- survival mass through step five;
- the predicted target/reference evidence region.

Training uses the censored hazard likelihood and region supervision. An optional privileged PointMap branch is an upper bound/teacher only. The deployable primary model is RGB+proprio; the previous 38-D PointMap E0 remains merely representation headroom and its integrity warnings travel unchanged. RGB-to-depth, instance segmentation, and PointMap projection are not silently assumed at deployment.

Mechanism necessity is preregistered: a capacity-matched visibility-only gate and a suffix-free hazard receive the same observation/history/object queries but not the action prefix. A prefix shuffle must damage opportunity ordering. If action conditioning gives no gain at matched risk/coverage/delay, the WAM claim is removed and the project stops rather than being relabeled.

## 6. Fixed external progress consumer

All closed-loop comparisons use the same non-learned finite-state task controller and the same low-level VLA executor. Each benchmark task is decomposed into a fixed subtask prompt sequence and registered relation postconditions.

- after an event-producing subtask, its postcondition becomes `PENDING`;
- while pending and before the predicted opportunity, the controller does not advance to the next subtask and continues the current subtask through ordinary five-step VLA calls;
- at an opportunity, the frozen evidence likelihood commits or retracts the postcondition;
- commit advances to the next registered subtask prompt;
- retract reissues the same subtask prompt once; no learned recovery is added;
- censoring for `B` consecutive five-step boundaries invokes the same preregistered conservative fallback for every method.

The task controller—not standard π0.5 itself—consumes `PENDING/commit/retract`. π0.5 or StarVLA is used only as the unchanged action executor. Therefore the paper must claim improvement to a VLA-based long-horizon system, not that standard π0.5 has acquired an internal memory API.

## 7. Preregistered compiler and oracle gates

Before any neural WAM training:

1. at least 100 independent common-parent lineages are attempted per family in the pilot, with splits by parent/object/seed;
2. duplicate replay divergence must stay below registered state and image tolerances for at least 99% of eligible parents;
3. the upper confidence bound of time-zero sensor separability must remain below AUROC 0.60 in each retained family;
4. at least two families must yield at least 25% accepted aliases that are time-zero ambiguous but gain a protocol-positive passive opportunity within five steps;
5. the independent frozen sensor evidence model must reach opportunity-window AUROC at least 0.85 in every retained family;
6. an oracle opportunity gate must reduce pre-opportunity false commit/retract by at least 30% relative to the strongest fixed-time/visibility-only rule at matched coverage and mean/P95 delay;
7. unresolved/censored predicates may not increase task timeout by more than 10 absolute points under the common fallback;
8. at least two normal five-step prefixes from the same observation stratum must change `tau_protocol` ordering; the action-prefix permutation test must reject invariance at preregistered alpha.

Failure of gates 1–5 stops before GPU training. Failure of gates 6–8 removes the mechanism-necessity or closed-loop claim.

## 8. Neural and closed-loop evaluation contract

Baselines share input capacity, task controller, evidence model, tuning budget, and fallback:

- framewise binary verifier;
- fixed delay selected on validation data;
- visibility-only three-state gate;
- suffix-free opportunity hazard;
- ordinary action-conditioned WAM discrepancy;
- oracle opportunity schedule upper bound.

Primary metrics are pre-opportunity wrong-decision risk, selective risk versus coverage, mean/P95 evidence delay, censoring/timeout rate, opportunity-time calibration, family-clustered confidence intervals, and closed-loop task success. A neural pass requires at least 30% relative reduction in pre-opportunity wrong decisions versus the strongest deployable baseline, no more than 10 points extra censoring/timeout, significant degradation under action-prefix shuffle, and a closed-loop gain under the shared finite-state controller.

## 9. Remaining implementation decisions

The experiment plan must freeze exact numeric tolerances, the five-step control rate, the three task instantiations, the action-prefix permutation test, the maximum `B`, posterior thresholds, model parameter budget, and all family aggregation rules. No easy family may compensate for failure of the second retained family.
