# Round 1 Refined Proposal: Trace-Conditioned Historical Relation Filter

**Date:** 2026-08-30  
**Scope:** containment/support relations only; falsification-first

## Problem anchor

A VLA has completed and committed an `inside` or `on` relation, moved to a later subtask, and then executes another action chunk. The old relation may remain valid or be invalidated. When the post-action view is ambiguous, a current geometric predicate alone may be insufficient and a memory-only system may preserve stale progress. The target is exact revision of that historical, non-active relation—not active-subtask checking, generic failure detection, or a new recovery policy.

No method can infer a fully hidden exogenous disturbance that leaves no observation, proprioceptive, contact, or event evidence. Such cases must yield uncertainty/re-observation.

## State decomposition

For each committed relation \(r_{ij}\), maintain an ontic validity belief and a separate epistemic reliability:

\[
q_t^{ij}=P(z_t^{ij}=\mathrm{valid}\mid h_t),\qquad v_t^{ij}\in[0,1].
\]

Object addresses, relation type, and commit time are fixed ledger metadata. Address mistakes are evaluated as a diagnostic, not a relation-state class.

## Transition prior

The frozen PointMap encoder produces object-relative, world-frame geometry \(\phi(P_t^i,P_t^j)\). A single small head predicts

\[
q^-_{t+H}=T_\theta(q_t,\phi(P_t^i,P_t^j),\tau^{exec}_{t:t+H},r_{ij}),
\]

where \(\tau^{exec}\) is the realized execution trace: applied controls plus proprioceptive/end-effector/gripper trace, and contact proxy when available. A command-only variant uses \(\tau^{cmd}\) and is named command-conditioned. The method does not jointly decode RGB-D video or predict \(\Delta g\).

## Shared observation likelihood

All geometry variants use the same frozen POT-style typed predicate and visibility model on the post-action PointMaps:

\[
\operatorname{logit}q_{t+H}=\operatorname{logit}q^-_{t+H}+w(v_{t+H})\Lambda_r(P_{t+H}^i,P_{t+H}^j).
\]

When visibility is high, current geometry dominates. When it is low, the transition prior may provide conditional value. If posterior evidence remains insufficient, the filter abstains and requests re-observation.

## Ledger decision

Thresholds are calibrated on validation data at a fixed false-retraction budget:

- low posterior: retract only relation \(r_{ij}\);
- middle posterior/reliability: re-observe;
- high posterior: preserve and continue.

Verifier correctness is reported separately from the frozen policy's ability to recover after a correct retraction.

## Evidence ladder

### E0: controlled representation and rollback headroom

Controlled simulator relation events validate RGB/depth/PointMap capture, typed labels, observability, current-predicate behavior, and oracle typed-rollback utility. They may show that object-relative PointMaps are a useful compact alternative to full depth frames. They cannot support any action-conditioned WAM claim.

### E1: paired physics-mediated action effects

Restore identical pre-states and execute paired scripted control chunks through simulator physics:

- relation-preserving versus relation-invalidating robot interactions;
- matched camera motion, co-motion, and visibility;
- same/similar commands with different realized outcomes where possible;
- task-family- and action-template-disjoint evaluation.

Log command, actually applied controls, end-effector/proprio/gripper trajectory, contact proxy, before/after RGB-D, object PointMaps, and ground-truth relation.

### E2: replayed or newly collected VLA chunks

Run or replay StarVLA/π0.5 action chunks from restored states, retaining realized traces and outcomes. Compare observation-only, no-action learned prior, action-shuffled, command-conditioned, realized-trace-conditioned, and matched RGB filters.

### E3: closed-loop typed rollback

Only after oracle recovery and E1/E2 gates pass, attach the filter to a frozen VLA and compare typed retraction with global rollback/re-observation. Do not train a recovery policy.

## Decisive comparisons

1. POT-style observation-only belief filter.
2. Learned no-action PointMap prior.
3. Action-shuffled trace prior.
4. Command-conditioned PointMap prior.
5. Realized-trace-conditioned PointMap prior.
6. Matched RGB action/trace-conditioned verifier.
7. Simulator-geometry oracle.

## Claims and gates

The only possible WAM claim is conditional:

> On a preregistered post-action observation-aliasing distribution for historical containment/support relations, realized execution traces add significant conditional value to an otherwise identical PointMap belief filter.

Required gates:

1. E0 PointMap projection/delta and relation labels pass deterministic sanity checks.
2. Oracle typed rollback improves final success by at least 5 points and recovery success is at least 20%.
3. On paired E1/E2 strata, realized-trace conditioning improves invalidation recall by at least 5 points and decision error by at least 10% over the strongest observation/no-action baseline at the same false-retraction budget.
4. Action/trace shuffling collapses the incremental gain.
5. Realized trace beats command-only if the paper uses the word executed.
6. Fully visible relations show little artificial action benefit; hidden exogenous disturbances cause abstention rather than confident hallucination.
7. Learned PointMaps retain the result; oracle-only gains are reported only as diagnostics.
8. Closed-loop recovery and final success improve before any control claim is made.

If any central gate fails, report the narrower result: object-relative PointMap verification may be useful, but WAM dynamics are not shown necessary.

## Complexity boundary

Frozen VLA, frozen PointMap/depth/segmentation encoders, one transition-prior head, one fixed/calibrated fusion rule, no RGB-D video generation, no diffusion, no LLM planner, no learned recovery policy, and no `grasp/open` claims in the first study.
