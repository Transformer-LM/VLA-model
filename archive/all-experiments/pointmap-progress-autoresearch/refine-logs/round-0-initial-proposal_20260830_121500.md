# Round 0 Initial Proposal: Historical Relation Retraction Necessity Test

**Date:** 2026-08-30  
**Status:** falsification-first; not yet a paper claim

## Problem anchor

A long-horizon VLA can commit a relation such as `inside(cup, drawer)` and move to a later subtask. A later action, object motion, or external disturbance may invalidate that historical relation while the affected object is partly or fully unobservable. Current RGB progress memory can preserve a stale completion, while a current 3D predicate can only judge what is visible now. The research question is not whether PointMaps are useful in general, but whether an executed-action-conditioned metric transition is necessary to retract the correct historical relation without causing a global rollback.

## Dominant hypothesis

For a persistent ledger of typed object relations, an action-conditioned object-relative PointMap transition model will improve invalidation recall and reduce false retraction under partial observability relative to (i) a complete POT-style static 3D supervisor, (ii) a two-frame no-action geometry classifier, and (iii) a matched RGB action-conditioned verifier.

This is a necessity hypothesis. If the no-action geometry or POT-style baseline ties the model, the WAM-dynamics claim is rejected.

## Minimal method

Maintain a ledger entry

\[
b_t^{ij}=(q_i,q_j,r_{ij},c_{ij},v_i,v_j,t_{commit}),
\]

where object addresses \(q\) and the typed relation \(r\) are fixed by the task parser, \(c\) is confidence, and \(v\) is current visibility.

For each committed relation, construct two sparse world-frame PointMaps from RGB-D plus instance association and summarize them in the target-object frame. A compact transition head predicts

\[
p(\Delta g_{ij}, y_{ij}\mid P_t^i,P_t^j,a_{t:t+H},b_t^{ij}),
\]

where \(y\in\{preserved,invalidated,unobservable,wrong\text{-}relation\}\). A deterministic ledger policy maps only `invalidated` to typed retraction, `unobservable` to re-observe, and `preserved` to continue. It never performs global rollback.

Only the PointMap encoder and transition head are trainable. The VLA, RGB encoder, depth/segmentation teacher, and recovery policy remain frozen. No RGB-D video decoder is trained.

## Strong baselines

1. **POT-style supervisor:** persistent object records, current metric predicates, visibility/confidence, and a temporal stability window.
2. **Two-frame geometry delta:** identical PointMaps and ledger, but no executed action.
3. **Matched RGB verifier:** before/after RGB, identical action, ledger, capacity, data, and optimization.
4. **Global event verifier:** emits only failure/uncertainty and therefore forces global rollback or re-observation.
5. **Oracle geometry:** simulator object poses and predicates; establishes headroom and label correctness.

## Decisive data slice

Use LIBERO relation tasks, with task-family-disjoint validation, to build controlled post-completion events:

- preserved static;
- object and container co-motion;
- camera motion with relation preserved;
- relation invalidated by a later action/effect;
- relation preserved but object made unobservable;
- distractor/wrong object changes;
- geometry-negative semantic control.

The first pilot may use simulator PointMaps and controlled world interventions to establish representation headroom. It cannot support an executed-VLA-action or closed-loop claim until it is followed by replayed or newly collected VLA action chunks.

## Claims and anti-claims

**Possible primary claim:** action-conditioned metric transition is necessary for accurate historical relation retraction under observation aliasing.

**Anti-claims that must be ruled out:**

- improvement comes only from access to depth/segmentation;
- two-frame geometry, without action, is sufficient;
- a hand-written 3D predicate is sufficient;
- the model only detects generic visual change;
- gain exists only with simulator ground truth;
- classifier improvement does not change recovery or final task success.

## Preregistered gates

1. Simulator state restore error must be exactly zero, relation labels must agree with LIBERO predicates, and PointMap projection must reconstruct known body poses within 2 cm median error.
2. Oracle typed retraction must improve post-perturbation final success by at least 5 percentage points, with recovery success at least 20%; otherwise stop before learned models.
3. On an independent test split, the action-conditioned model must improve invalidation recall by at least 5 points and reduce decision error by at least 10% relative to the strongest matched baseline.
4. Action shuffle must remove a substantial fraction of the gain. If not, the action-conditioned/WAM claim fails.
5. If learned PointMaps lose the result relative to simulator geometry, the result is an oracle-only diagnostic.
6. Closed-loop evaluation is allowed only after gates 1–4 pass.

## Scope and resources

The initial controlled dataset and small verifier are CPU/GPU-light. Use only the user's personal server directories. Use GPUs 2/3 when individually idle; 0/1 only if independently verified idle. Pilot ceiling is 32 GPU-hours, no paid compute, and no real-robot trials in this run.

## Known novelty risk

POT-VLA already provides persistent role-indexed 3D records, visibility/confidence, typed predicate checks, re-observation, and recovery. EV-WM and CheckVLA already provide action-conditioned event/future verification. Therefore, the only potentially defensible delta is precise retraction of a previously completed, non-active relation, together with evidence that action-conditioned metric dynamics are necessary. The current broad novelty score is 4.0/10.
