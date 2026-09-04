# E1/B2 implementation freeze: physics-mediated realized-kinematic value

Frozen: 2026-08-30 15:35 +08:00  
Trigger: `CLAIMS_FROM_RESULTS_20260830_153000.md` authorizes E1/B2 conditionally  
Scientific claim under test: whether realized robot kinematics adds conditional value for revising a previously valid object relation under post-action observation aliasing.

## Claim boundary

E1 is the first claim-bearing experiment. E0's 38-D two-frame feature is not reused or renamed as the E1 transition state. E1 implements the proposal's deterministic **54-D pre-action PointMap summary** and a separate post-action observation likelihood. Simulator object state is permitted only for dataset labels, matching/audit and Oracle analysis; it is forbidden from learned transition inputs.

Primary transition inputs end at the final applied control before the post-action observation:

- `tau_cmd`: 7-D controls actually passed to `env.step`;
- `tau_kin`: `tau_cmd` plus robot-only end-effector, gripper and joint proprioception;
- contact/force/event signals, if logged, remain appendix-only `tau_fb` and cannot support the kinematic claim.

No direct target/reference pose mutation is allowed after the transition-start snapshot. Direct placement is allowed only to construct diverse valid pre-action states, followed by robot approach, settling, a relation-validity recheck and a fresh exact snapshot.

## Mandatory protocol repairs

1. E1 uses a dtype-stable true no-retract sentinel: the next representable float32 value above the maximum validation invalidity score, followed by an assertion that zero validation samples retract. NumPy version is recorded.
2. All learned variants use fixed final-state training: 80 epochs, identical batch construction, seeds `{17,29,43}`, no early stopping and no best-checkpoint selection. Validation is used only for affine calibration and operating thresholds.
3. All E0 integrity WARNs remain in provenance. R025 is cited for repaired 38-D E0 projection evidence; R011 is not cited as a current geometry replay.

## Physics-mediated rollout cell

For each task/reset, construct several relation-valid target placements spanning relation margin while keeping the reference and scene fixed. Move the robot to an object-relative pre-contact pose using closed-loop Cartesian commands. The approach is preconditioning, not part of the claim-bearing trace. After approach:

1. settle and verify the relation still holds;
2. save the exact simulator transition-start snapshot;
3. capture the pre-action RGB, metric depth, instance masks and PointMaps;
4. execute a fixed 16-step chunk: 8 push controls plus 8 zero/settling controls;
5. record every command and post-step robot-only kinematic observation;
6. capture the post-action observation only after the final recorded step;
7. label preserved/invalidated from the simulator predicate.

Push families are horizontal `±x` and `±y`, with command magnitude and duration shared across paired pre-state variations. At least one action family must yield both outcomes because of interaction/pre-state variation. Command parameters must overlap by construction; the same command template is reused across relation margins.

The primary trace is expressed as change from the first robot state, not absolute world pose, to reduce task-identity shortcuts. Pre-action object-relative geometry remains a separate input.

## Data split and matching

- Entire task families and action templates are held out for test.
- Training/validation/test never split sibling rollouts from the same transition-start state.
- Matching strata include task, action family, duration, pre-action relation-margin bin and post-observation visibility bin.
- Standardized mean difference above 0.1 requires rematching or propensity weighting.
- A command-only shortcut classifier above 60% balanced accuracy rejects the affected claim-bearing stratum.
- Trace shuffling is only within the same matching stratum.

## Stage P0: environment and trace preflight

One task, CPU/OSMesa only. Required:

- exact state restore and deterministic zero-action replay;
- observation keys for end-effector, gripper, joint state, two-view RGB/depth/instance masks;
- nonzero Cartesian commands move the end-effector;
- every trace field has a fixed finite shape;
- action trace is recorded before post observation;
- no system/shared write and no GPU requirement.

P0 is engineering evidence only.

## Stage P1: small paired physics rollout pilot

Start with two accessible tasks, one `inside` and one `on`, at least 8 valid pre-states per task and all four push families. P1 passes only if:

- at least 64 accepted physics-mediated rollouts;
- both preserved and invalidated outcomes are present;
- at least one action family contains at least 8 samples of each outcome;
- relation state changes only through `env.step` after the transition snapshot;
- command-only balanced accuracy is at most 0.60 under grouped cross-validation;
- all target labels and simulator-state fields are excluded from learned input arrays;
- exact replay, hash and schema audits pass.

If P1 lacks outcome overlap, change pre-state margin coverage or push geometry and rerun P1. Do not train the transition model on a command-leaking dataset.

## Stage P2: main E1 data and learned variants

Only after P1 passes. Required comparisons use the same data, splits and fixed training protocol:

1. observation likelihood plus persistence prior;
2. learned no-trace transition prior;
3. within-stratum shuffled `tau_kin`;
4. command-only `tau_cmd`;
5. primary realized-kinematic `tau_kin`;
6. matched RGB/visual verifier;
7. simulator-geometry Oracle;
8. optional feedback-inclusive `tau_fb`, clearly appendix-only.

On the validation-frozen aliasing population, `tau_kin` must reduce IMR@FRR5 by at least 10% relative and 5 percentage points absolute versus the strongest observation/no-trace baseline, keep achieved test FRR at most 5%, beat command-only, and lose its incremental advantage under within-stratum shuffling. Three task-family-aware seeds and task-family cluster bootstrap intervals are mandatory.

## Stop conditions

Stop before main training if physics rollouts do not create matched outcome overlap, command-only exceeds 60% balanced accuracy, the aliasing population is empty or task-concentrated, or robot-only kinematics is numerically identical to command-only after normalization. Stop the main claim if `tau_kin` fails the registered IMR/FRR gate; report that execution-trace conditional value was not established.

## Resource and server contract

All writes remain under `<PERSONAL_RESEARCH_ROOT_ALIAS>`; use only SSH user `liu_meng`, no root/sudo/su, no profile/system/shared changes and no downloads. P0/P1 collection is CPU OSMesa. GPU training uses physical 2/3 first; physical 0/1 are allowed only when individually idle immediately before launch. No real robot is used in this autonomous stage.
