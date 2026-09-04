# WitnessWAM v0 — Earliest Passive Witnesses for Progress Verification

**Status:** refinement input; not an experiment authorization  
**Date:** 2026-08-31  
**Strict pre-refinement novelty interval:** 7.2–7.7/10

## Problem

Long-horizon VLA execution often requires deciding whether a physical predicate such as `grasped(o)`, `inside(o,c)`, or `supported_by(o,s)` was established. Immediately after the relevant action, the result may be hidden by the gripper, object, container rim, or camera geometry. A framewise progress head or WAM discrepancy threshold is forced to classify before the sensor can contain decisive evidence, causing false completion, false rollback, repeated actions, and corrupted progress memory.

The method should answer a different question:

> Under the actions the deployed VLA will normally execute next, when and where can the current sensor stream first distinguish the predicate-true and predicate-false hypotheses?

## Claim boundary

WitnessWAM does not infer a hidden predicate from an information-theoretically ambiguous current frame, does not introduce an active probe, and does not guarantee general observability. It learns a policy-, suffix-, camera-, and sensor-conditional distribution over the first passive evidence opportunity. Before that opportunity, the progress state remains `PENDING`; only evidence observed inside or after a predicted opportunity may commit or retract it.

The maximum intended claim is:

> Training on matched hidden-state twins and interval-censored first-witness labels enables a WAM-based verifier to reduce progress decisions made before evidence is observable, and improves long-horizon execution at a matched pending/verification budget.

## Method

### M1. Matched hidden-state twin compiler

For predicate family `p`, construct simulator snapshot pairs `(s+, s-)` such that:

- `p(s+)=true` and `p(s-)=false` by privileged simulator state;
- task instruction, robot state, camera parameters, and visible distractors match;
- current RGB/proprioception are equal within a preregistered perceptual and geometric tolerance because the predicate-relevant difference is occluded or otherwise not sensor-identifiable;
- the pair is safe and admits the same short suffix.

The compiler must report matching residuals and reject pairs separable at time zero by a held-out sensor-only classifier.

### M2. Same policy-supported suffix intervention

Sample an ordinary suffix `a[t:t+H]` from a frozen VLA or an expert trajectory close to its action support. Restore both twins and execute the identical open-loop suffix with common simulator randomness. No diagnostic-only action, candidate search, or reranking is permitted.

Generate multiple nuisance replicas per twin pair by varying allowed camera noise, lighting, and noncausal distractors while holding the hidden predicate and suffix fixed.

### M3. First-witness and censoring labels

For each future window, determine whether deployable RGB/proprio evidence distinguishes the two hypothesis-conditional outcome distributions. A witness label requires both:

1. a privileged opportunity condition for the predicate-relevant object/relationship (visibility, nondegenerate geometry, and relation-specific margin); and
2. held-out cross-fitted separability of the allowed sensor features across nuisance replicas.

The earliest window satisfying both conditions is `tau*`. If no such window occurs before `H`, the sample is right-censored. Labels are interval-censored when frame rate or visibility ambiguity only locates the event to `[tau_l,tau_r]`.

This makes `tau*` a property of `(predicate family, twin pair, suffix, camera, sensor protocol)`, not an intrinsic property of the predicate.

### M4. Hypothesis-conditional witness hazard model

Given current observation/history, the uncertain predicate identity, and the known executable suffix, train a compact action-conditioned latent WAM to output:

- `lambda+(tau)`: hazard that a predicate-true-supporting witness first becomes observable;
- `lambda-(tau)`: hazard that a predicate-false-supporting witness first becomes observable;
- survival/censoring mass through the horizon;
- the object/relationship region and sensor channel expected to carry the evidence;
- hypothesis-conditional witness feature distributions used for the later likelihood update.

Use an interval-censored competing-risk likelihood plus region supervision and a twin contrastive term. The model is allowed to predict `non-verifiable within horizon`.

The initial implementation should predict PointMap/object-relative latent features rather than decode complete RGB-D video. The prior controlled E0 result supports only PointMap representation headroom, not this dynamics claim.

### M5. Evidence-pending runtime update

After an uncertain event, maintain `b_t = P(p=true | history)` and set the symbolic state to `PENDING`. As the unchanged VLA continues its ordinary suffix:

1. propagate the two hypothesis-conditional witness schedules;
2. do not commit or retract before the cumulative opportunity mass crosses a calibrated threshold;
3. when an opportunity arrives, update `b_t` from the observed witness likelihood ratio;
4. commit, retract, or remain pending using preregistered posterior thresholds;
5. if the horizon is censored, defer to a conservative fallback rather than treating absence as failure.

The WAM schedules evidence evaluation; it does not score or select candidate actions.

## Required falsifiers before model training

Run a simulator-oracle compiler E0 on at least three predicate families, targeting at least 300 accepted twins per family.

Kill the method if any occurs:

- fewer than two predicate families have at least 25% `initially ambiguous -> later passively distinguishable` samples;
- a time-zero sensor-only classifier exceeds the registered ambiguity ceiling;
- a fixed-time verifier achieves the same pre-evidence error at matched final discrimination and pending budget;
- oracle witness gating fails to reduce pre-evidence false commit/retract by at least 30% relative;
- more than 40% of episodes time out because of persistent `PENDING`;
- useful witnesses require diagnostic-only suffixes rather than ordinary policy support;
- the `tau*` ordering cannot be recovered after conditioning on suffix/camera, or its held-out rank correlation remains below 0.5.

## Neural E0 and closed-loop progression

Only after the compiler gate passes:

1. train the compact PointMap/object-latent hazard model on three GPUs and reserve one GPU for asynchronous validation;
2. compare against framewise progress classification, fixed-delay verification, a three-state visibility gate, ordinary WAM discrepancy, and a capacity-matched hazard model without action suffix;
3. require calibrated time-dependent risk, at least 30% relative reduction in pre-evidence wrong decisions, no more than 10% absolute increase in unresolved predicates, and a significant closed-loop success gain before scaling;
4. test suffix, camera, object-instance, and task-family shifts separately.

## Closest-work boundary

- *How Visible Are Silent Manipulation Failures?* studies episode-level modality separability, not matched predicate twins, first passive witnesses, or online pending semantics.
- IntentVLA/AliasBench studies history-dependent action ambiguity, not future observability of a progress predicate.
- CheckVLA, When to Trust Imagination, Foresight, and embedding-temporal-logic monitors verify predicted execution traces but do not model when evidence first becomes observable or censor decisions before that opportunity.
- Predictive-state representations and POMDP distinguishability are the strongest classical ancestors. The defensible residual is the exact policy-supported twin compiler, first passive witness/censoring target, and its use as a progress-memory commit rule. The method must not claim the invention of observability, survival analysis, or three-valued monitoring.

## Open decisions for refinement

1. Define the minimal simulator-supported predicate families that yield valid hidden-state twins without adding artificial black screens.
2. Specify the exact observation-matching test and time-zero ambiguity ceiling.
3. Define the witness opportunity producer without using the same learned feature head for labeling and evaluation.
4. Decide whether the hazard model needs full history or only an explicit prior over the pending predicate.
5. Define how the frozen π0.5/StarVLA suffix is generated and normalized across the two twins.
6. Specify the conservative fallback for right-censored predicates.
7. Bound runtime latency and identify which existing PointMap components can be reused honestly.
