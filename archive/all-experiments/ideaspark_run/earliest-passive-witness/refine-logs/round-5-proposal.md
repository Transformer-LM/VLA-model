# WitnessWAM v4 — Earliest Passive Witnesses for Safe Progress-Memory Updates

**Revision target:** make the continuation contract fully deployable and test whether explicit witness-time modeling is irreducible to buffered temporal verification.  
**Date:** 2026-08-31

## Problem and claim

A frozen VLA can execute a plausible action chunk while its external long-horizon progress memory is still unable to tell whether a relation such as `grasped`, `inside`, or `on-target-support` is true. Writing progress immediately can corrupt later planning; treating every temporary mismatch as failure can also retract correct progress. The missing variable is not simply confidence or visibility, but the first policy- and sensor-conditional opportunity at which the relevant physical alternatives become distinguishable.

WitnessWAM receives current RGB/proprioception, an object–relation query, and the exact five low-level actions already queued by π0.5. It predicts a discrete, interval-censored hazard over the earliest passive evidentiary opportunity. Before that opportunity the external task relation remains `PENDING`; when an opportunity occurs, a separately frozen evidence likelihood may stage a positive or negative belief. The physical chunk never changes, and the staged belief is applied atomically only at the chunk boundary.

The allowed claim is narrow: under a preregistered five-action continuation contract, explicit relation-opportunity supervision reduces false progress-memory updates beyond fixed timing, action-conditioned visibility prediction, and capacity-matched full-history boundary verification. Failure against either smaller mechanism kills the WitnessWAM claim.

## 1. Deployable continuation envelope

No body pose, segmentation, depth, PointMap, simulator geometry, future truth, or learned eligibility model is used to decide whether a queued chunk belongs to the continuation contract.

At the end of the event-producing phase the controller records:

- the robot end-effector pose from proprioception;
- the gripper mode;
- one preregistered **skill retreat axis** in the robot base frame.

The retreat axis is a fixed skill/controller parameter registered before data collection—for example the demonstrated post-release withdrawal direction or post-grasp transport direction—not a vector reconstructed from a target object's privileged pose. The exact denormalized, clipped commands queued for steps 1–5 are integrated from that checkpoint into desired EEF increments. A prefix belongs to the envelope iff:

1. its cumulative translation projected on the retreat axis is monotonically nonnegative;
2. no step reverses that projection beyond a preregistered physical tolerance;
3. orthogonal translation, rotation, command velocity, and acceleration stay within fixed bounds;
4. `grasp-coupled` keeps the gripper mode closed without reopening/reclosing, while `inside` and `on-target-support` keep it open without reclosing;
5. no environment-specific actuator command changes outside the registered skill interface.

This checkpoint-EEF-relative rule is checkable using only inputs available to the deployed controller before rollout. Its physical adequacy is not assumed: privileged per-step relation truth audits its precision over all attempts, and a family is killed if preservation is below 95%.

Two populations are frozen and used consistently:

- `D_attempt`: all four fixed-key attempts for every physically valid, exactly replayable, time-zero-ambiguous common parent. Every attempt stays in the ledger without replacement. Paired disagreement, unsafe commands, and envelope rejection are contract-coverage failures, not relation-outcome examples.
- `D_contract`: the subset of `D_attempt` that passes paired action agreement, five-step safety, and the command-only envelope. This is the denominator for truth preservation and delayed-opportunity yield.

Contract coverage `|D_contract| / |D_attempt|` must be at least 60% separately in every retained family and all rejection reasons are reported. This prevents a very narrow envelope from manufacturing high preservation. Within `D_contract`, a subsequent truth transition counts as a preservation violation, contributes zero to delayed-opportunity yield, and counts as a fixed-FSM system failure; it is never silently removed. Delayed-opportunity yield is `truth-preserving contract attempts with tau_protocol in steps 2–5 / |D_contract|`, so transition and censored attempts remain in its denominator. Only truth-preserving `D_contract` attempts may supervise `tau_protocol`, because a changed relation is not evidence about the original relation. Confidence intervals resample parent lineages so four keys from one parent are never treated as independent.

## 2. Physical producers and opportunity protocol

Common-parent simulator checkpoints are branched into natural alternatives:

- stable grasp versus natural miss, with no weld/equality edit;
- settled inside versus settled rim/outside miss;
- settled on the named support versus settled on an adjacent ordinary support.

Hovering objects, solver transients, camera-only edits, retries, and post-checkpoint direct object mutation are forbidden. Clone hashes, duplicate replay, state residuals, source-balanced paired execution, visibility, predicate truth, and every rejection reason are stored in an append-only audit ledger. Parent lineages define all train/validation/test splits.

A deterministic privileged protocol frozen before training labels `tau_protocol ∈ {1,…,5,censored}` using family-specific relation geometry, queried-region visibility, pairwise projected separation above a registered sensor-noise floor, and two-frame persistence. It labels the first sensor opportunity, not the physical relation itself. A disjoint-lineage frozen RGB/proprio evidence likelihood maps evidence at an accepted opportunity to positive or negative relation belief and cannot alter timing labels.

The primary deployed WitnessWAM uses RGB+proprioception. PointMap/depth may appear only as a teacher or oracle upper bound and cannot be required by the main result.

## 3. Frozen π0.5 prefixes and action lock

Exactly four server-side paired π0.5 flow-decode PRNG keys are preregistered before rollout and used without replacement. The same key queries both aliases. Raw normalized outputs and denormalized clipped physical commands are cached. Agreement is evaluated per step in deployment command space using separately frozen translation, rotation, gripper, and task-specific actuator tolerances.

All four attempts remain in `D_attempt` and in the contract-coverage report. Preservation and delayed-opportunity denominators use `D_contract` only, with truth transitions retained as failures as defined above. A lineage enters the within-lineage K-prefix action-necessity test only if at least three of four keys belong to `D_contract`; missing/invalid keys are recorded and never replaced.

For all verifiers, actions 1–5, timing, current prompt, and next-subtask prompt are immutable after the chunk starts. A decision before step 5 creates one timestamped staged belief; the first accepted staged decision is frozen for the chunk. It cannot cancel/replace actions, repeat the event prompt, or advance the next task. At step 5 the staged belief is atomically committed or withheld, and only then may the common external FSM advance, retract, or invoke the identical fallback.

This keeps physical trajectories identical. A transient witness can matter only if its evidence is usefully cached for the boundary. Therefore a full-history boundary verifier is mandatory, not optional.

## 4. Model and two decisive smaller mechanisms

WitnessWAM and all learned baselines receive the same initial RGB/proprioception, object/reference query, predicate type, exact five-action prefix, and encoder budget. WitnessWAM predicts the opportunity hazard, survival/censoring mass, and queried evidence region.

### A. Action-conditioned visibility hazard

This capacity-matched model receives the same inputs and action prefix but is supervised only on when the target/reference regions cross the registered visibility threshold. It never receives pairwise separation, relation-opportunity labels, or predicate truth.

WitnessWAM must improve, separately in every retained family:

- integrated time-dependent Brier score for `tau_protocol` by at least 10% relative; and
- fixed-FSM total error by at least 10% relative,

with paired parent-lineage bootstrap 95% intervals excluding zero. Otherwise the result contracts to action-conditioned visibility scheduling.

### B. Capacity-matched full-history boundary verifier

This model receives the same query and, at step 5, the complete actual five-step RGB/proprio/action trace. It uses the same visual encoder capacity, temporal-token budget, evidence likelihood capacity, augmentation, validation tuning budget, and training lineages as WitnessWAM. It receives no `tau_protocol`, opportunity labels, or privileged geometry and emits one relation belief only at the boundary. Temporal attention/pooling is unrestricted within the matched budget, so it can exploit a witness that appeared transiently at any earlier step.

WitnessWAM must reduce the same fixed-FSM total error by at least 10% relative to this history verifier in every retained family, with paired parent-lineage bootstrap 95% intervals excluding zero, at matched decision coverage. If it does not, the honest conclusion is that buffered temporal verification is sufficient; explicit earliest-witness timing is rejected even if its timing metric is accurate.

The boundary verifier is evaluated under its natural single boundary decision, while streaming schedulers use the first-accepted staged-decision rule. Both ultimately affect the FSM only at the same boundary. There is no artificial latency advantage for WitnessWAM.

## 5. Remaining baselines and endpoint

The registered comparison set is:

- immediate/framewise RGB relation verification;
- fixed decision steps 1–5 chosen on validation only;
- final-frame-only verification;
- the full-history boundary verifier above;
- privileged visibility-only and deployable RGB-visibility rules;
- the action-conditioned visibility hazard above;
- capacity-matched suffix-free opportunity hazard;
- WitnessWAM;
- privileged `tau_protocol` oracle upper bound.

The primary operating point is frozen on validation: decision coverage ≥90%, maximum wait five actions, and identical fallback. Full risk–coverage–delay curves are diagnostic only. Because the history verifier naturally decides at the boundary, the primary comparison to it is matched coverage and FSM error, not an imposed mean-delay penalty.

The unit-cost system endpoint per attempt is frozen before test: one error for wrong staged/boundary relation belief, one for an incorrect atomic advance/retract transition, and one for unresolved timeout. Components are also reported. An error can affect both belief and transition because these are different downstream states. Neither error definition uses `tau_protocol`.

Before neural training, the oracle schedule must improve this endpoint by at least 20% over the best non-neural/fixed-time and visibility baselines without raising timeout more than ten percentage points, with per-family parent-lineage-bootstrap confidence. The oracle need not beat a learned full-history verifier before that verifier is trained, but the final method must.

## 6. Action-conditioning and statistical gates

Integrated time-dependent Brier score is the sole primary timing metric; C-index is diagnostic.

Producer necessity requires that, among parents with at least three valid fixed-key prefixes, changing only the ordinary π0.5 prefix shifts `tau_protocol` by at least one step or changes opportunity/censor status in at least 30% of parents per retained family.

Model necessity requires suffix-aware WitnessWAM to improve integrated Brier score by at least 10% over the suffix-free hazard; shuffling prefixes must erase at least 80% of the gain and return performance to the suffix-free confidence interval. Comparisons and uncertainty are paired within common-parent lineages and reported separately for each relation family.

## 7. Frozen stop gates

1. Duplicate replay determinism ≥99%.
2. Time-zero sensor AUROC upper 95% bound ≤0.60 per family.
3. Contract coverage `|D_contract| / |D_attempt|` ≥60% per retained family, with all four fixed keys in `D_attempt` and no replacement.
4. Command-only envelope truth preservation ≥95% over `D_contract` per retained family.
5. Delayed opportunity yield ≥25% over `D_contract`, defined as truth-preserving attempts with `tau_protocol` at steps 2–5; transitions and censoring remain denominator failures.
6. Independent opportunity-window evidence AUROC ≥0.85.
7. Oracle fixed-FSM improvement ≥20%, timeout inflation ≤10 percentage points.
8. Producer and model action-conditioning gates above.
9. Both ≥10% WitnessWAM gains over action-conditioned visibility hazard.
10. ≥10% fixed-FSM gain over the capacity-matched full-history boundary verifier.
11. At least two physically distinct relation families pass every applicable gate; no averaging rescue, replacement keys, learned eligibility model, or post-hoc horizon extension.

## 8. Nonclaims

There is no active sensing, candidate reranking, recovery learning, internal π0.5 memory, universal observability, or physical truth certification. The method schedules evidence for an external relation memory while executing an already-issued normal chunk. A PointMap/depth deployment stack is not claimed. If visibility prediction or buffered history matches the method, WitnessWAM is rejected rather than expanded with another module.
