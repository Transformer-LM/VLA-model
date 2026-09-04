# Cycle-3 statistical and GPU-hour audit

## Hard verdict

The five-seed design is conditionally runnable as a controlled diagnostic, but it cannot support a confirmatory H1 mediation claim. The GPU budget is only conditionally feasible: before launch, the projected complete worst-case path must be at most 7.2 GPUh, preserving 0.8 GPUh safety margin.

## Experimental unit and estimand

The training seed is the experimental unit, not the rollout. For each seed, aggregate equally over the two fixed tasks and the ten common initial states per task:

`d_AB(seed) = mean(Y_A - Y_B)` and `d_AC(seed) = mean(Y_A - Y_C)`.

Tasks and initial states are repeated measurements within seed. The estimand applies only to the fixed early checkpoint, the equal-weight average of the two preregistered tasks, the defined seed distribution, and this preregistered C placebo. It does not generalize to all LIBERO, all world objectives, or natural mediation.

## Five-seed main test

Use preregistered one-sided exact sign tests. A must simultaneously beat B and C, so this is an intersection-union test and both components must pass at alpha .05 without Bonferroni.

- A>B: all five seed differences must be strictly positive.
- A>C: all five seed differences must be strictly positive.
- With five nonzero pairs, the minimum one-sided p-value is 1/32 = .03125.
- Any tie reduces effective n to four and makes the minimum p .0625, hence a failure.
- A two-sided n=5 test cannot pass .05.
- A paired t-test may be only a sensitivity analysis; rollout-level GLMM/bootstrap cannot create training replicates.

Require both pooled gains to be at least +10 success-rate points and prohibit a clear negative transfer on either task. This is a practical threshold, not proof that the true effect is at least 10 points.

## Power

The design has low power. Ignoring seed heterogeneity gives an optimistic 80% MDE around 11–18 points; moderate 5–10 point between-seed variation raises it to roughly 15–25 points. Requiring five positive signs often requires a true effect around 19–32 points for 80% gate-pass probability. Failure means only that no very large, cross-seed-consistent effect was observed; it does not exclude a useful 5–10 point effect.

## Stage 2

Only after both Stage-1 gates pass, define the primary mechanism contrast as:

`d_specific(seed) = SR(A_orth-removal) - SR(A_predictive-removal)`.

Require all five seed values strictly positive, mean difference at least +10 points, intact A to degrade under predictive removal, and orthogonal removal to show only a small descriptive degradation. Fit and freeze the predictive subspace, rank, layer, normalization, and placebo on independent offline data before any environment result. This supports only controlled necessity-like evidence relative to one predefined placebo.

## C placebo audit

Pre-register an episode-disjoint derangement seed, task/phase/speed bin errors, per-step adapter gradient norm, parameter-update norm, clipping, A/C gradient cosine and variance, and Adam moments. Do not resample C after outcomes. If gradient/update norm or clipping systematically differs by more than about 10%, or any episode/future-window identity leaks, C is invalid.

## GPU-hour audit

Budget all timing/debug pilots, cache, head training, adapter training, model loads, and rollout evaluation. GPU 2/3 parallelism reduces wall time but not GPUh.

Given 500 rollouts at roughly 3–6 GPUh, the non-rollout budget is only 1.2–4.2 GPUh. Twenty-five 4B model loads could alone cost 0.4–1.2 GPUh; keep one evaluator resident and hot-swap small adapters/interventions.

Hard rules:

- First measure one complete load, shared feature cache, head pretraining, one 500-step adapter run, and a performance-blind 20-rollout timing calibration.
- Count the pilot in the 8 GPUh cap.
- Before Stage 1, the worst-case complete 500-rollout path must project to at most 7.2 GPUh.
- Recompute before Stage 2 from actual consumption and stop if the projection exceeds 7.2 GPUh.
- Never treat multi-GPU wall-clock acceleration as GPUh savings.

## Fatal gates

- projected complete protocol above 7.2 GPUh;
- baseline outside roughly 20–80% success on the preregistered tasks;
- strict future predictor fails zero/task-mean/current-only/action-agnostic gates;
- fewer than five complete paired seeds or outcome-driven seed replacement;
- A>B or A>C is not 5/5 strictly positive, pooled gain below 10 points, or clear task negative transfer;
- C matching, leakage, or optimization audit fails;
- Stage-2 predictive removal is not more damaging than the matched orthogonal removal;
- full A-to-B activation patch does not reproduce B action output;
- action-output diversity/collapse explains the result without predictive-subspace specificity;
- any outcome-driven change to rollout count, task, rank, checkpoint, or placebo.

## Preferred same-rollout alternative

If cached-feature training and hot adapter switching remain within 7.2 GPUh, reallocate the same rollout count to **ten paired training seeds with five common initial states per task**. Stage 1 remains 300 and Stage 2 remains 200, while the number of adapter branches doubles. With ten seeds, 9/10 positive gives a one-sided exact p=.0107; 8/10 gives p=.0547. This improves training-seed coverage, subject to calibration proving the extra tiny adapter runs are affordable.

Overall: the five-seed version is a high-threshold diagnostic. For a more credible result, prefer ten training seeds if—and only if—the measured full projection remains at most 7.2 GPUh.
