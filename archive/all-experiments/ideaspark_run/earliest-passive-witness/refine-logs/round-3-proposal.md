# WitnessWAM v2 — Predicate-Preserving Passive Witness Scheduling

**Revision target:** remove retry/truth-change confounding and make oracle utility/action necessity numerical.  
**Date:** 2026-08-31

## Core estimand

From a common-parent compiled sensor-alias pair and one normal five-step post-event continuation, estimate the protocol-relative first opportunity to verify a relation whose truth remains unchanged throughout that continuation.

The model predicts a single censored opportunity hazard. A frozen evidence likelihood decides the relation only at/after an opportunity. The external controller uses `PENDING`, but it never repeats the event-producing prompt while waiting.

## Predicate-preserving continuation contract

Each benchmark skill has two preregistered phases shared by every method:

1. an event-producing phase (grasp, release into container, or place on target support);
2. one ordinary post-event continuation already present in successful demonstrations, such as gripper/hand withdrawal or transport away from the occluding configuration.

The continuation is generated once by the registered frozen VLA at the alias checkpoint and is limited to the five low-level actions actually executed before replanning. It is not selected for information gain and is executed once regardless of which verifier is evaluated.

For every decode seed, query both alias observations. The prefix is eligible only if the two normalized five-step outputs agree within the preregistered action tolerance; the canonical source branch is randomized and blinded, and source-balanced cross replay is reported. There is no claim of a policy-density score.

Privileged predicate truth is recorded after every low-level action. Eligibility requires `p+(0:5)=true` and `p-(0:5)=false`; the first truth change is a competing physical transition and rejects that prefix for witness-time supervision. Thus later visual difference is evidence about the checkpoint relation rather than a newly repaired or destroyed relation.

At runtime, while `PENDING`, the FSM consumes only this already-issued post-event continuation. It may transition early if a verifier decides, but it never calls the event-producing prompt again. At the five-step boundary, unresolved cases enter one common fallback. A separate recovery study is outside the claim.

## Producer families

1. `grasp-coupled(object, gripper)`: stable grasp versus natural miss; weld/equality toggles forbidden.
2. `inside(object, container)`: settled inside versus settled rim/outside miss under native hand/rim occlusion.
3. `on-target-support(object, target)`: two settled states, one on the named target support and one on an adjacent ordinary support/table. “Unstable hovering” and solver transients are removed.

All three use common-parent physical branches, full clone hashes, duplicate replay, native occlusion, parent-lineage splits, and the existing state-residual/acceptance ledger. The future-blind eligible denominator is frozen after physical validity, replay determinism, time-zero ambiguity, prefix action agreement, five-step safety, and predicate preservation—before looking for a future opportunity.

## Opportunity label and model

The independent deterministic protocol from v1 remains unchanged: family-specific privileged geometry, visibility, projected separation above the registered noise floor, and two-window persistence define one interval/right-censored `tau_protocol`. A disjoint-lineage frozen RGB/proprio evidence likelihood validates sensor translation but cannot alter labels.

WitnessWAM receives current RGB/proprio, object/relation queries, and the exact five-step prefix. It predicts one discrete opportunity hazard, survival mass, and evidence region. PointMap remains an optional privileged teacher/upper bound only.

## Fixed FSM utility evaluation

All thresholds and operating points are selected on validation lineages and frozen before test. Test comparison uses either the full preregistered risk–coverage–delay curve or one fixed operating point:

- decision coverage at least 90%;
- maximum wait five steps;
- mean delay no more than 0.5 step above the best deployable baseline at that coverage;
- identical timeout fallback and post-event continuation.

The primary utility endpoint is the total number of wrong FSM transitions plus wrong relation beliefs at the five-step boundary plus timeout penalties, with each component reported separately. It is not “pre-opportunity error,” which would favor the oracle by definition.

Before neural training, the oracle schedule must reduce this total endpoint at least 20% relative to the best fixed-delay, privileged-visibility-only, and deployable RGB-visibility rules at the frozen operating point; the lineage-bootstrap 95% interval must exclude zero in each of at least two families. It must also be non-dominated over the registered risk–coverage–delay range. Otherwise there is no scheduling headroom.

## Numerical action-conditioning necessity

Producer-level gate:

- generate `K=4` normal five-step prefixes per eligible lineage using four registered π0.5 flow decode seeds;
- require prefix action agreement across aliases for each seed and predicate preservation for both branches;
- in at least 30% of future-blind eligible lineages per retained family, changing only the normal prefix must shift `tau_protocol` by at least one control step or change opportunity-versus-censor status;
- report the within-lineage distribution, not only a permutation p-value.

Model-level gate:

- on held-out parents, objects, and prefixes, the suffix-aware hazard must improve integrated time-dependent Brier score by at least 10% relative or C-index by at least 0.05 over the capacity-matched suffix-free hazard;
- the family-clustered 95% interval must exclude zero for every retained family;
- prefix shuffling must erase at least 80% of that improvement and return performance to the suffix-free interval.

Failure of either gate kills the action-conditioned WAM claim instead of adding another module.

## Frozen pilot gates

1. At least 99% duplicate-replay determinism among eligible parents.
2. Per-family time-zero sensor AUROC upper confidence bound at most 0.60.
3. Per-family opportunity yield at least 25%, computed from the future-blind denominator.
4. Independent opportunity-window evidence AUROC at least 0.85.
5. Oracle total-FSM endpoint improvement at least 20% under the frozen operating rule, without timeout inflation above 10 points.
6. Producer- and model-level action-conditioning gates above.
7. At least two physically distinct relation families must pass every gate; no averaging rescue is permitted.

## Explicit nonclaims

- No active sensing, diagnostic action, candidate reranking, recovery learning, or internal π0.5 memory is introduced.
- The post-event continuation is ordinary and fixed across methods; the method schedules a decision about it, not the action itself.
- The paper does not claim perfect causal twins, universal observability, physical truth certification, or that PointMap deployment is solved.
- If the five-step opportunity yield is inadequate, the method is killed; the horizon is not lengthened after observing the result.
