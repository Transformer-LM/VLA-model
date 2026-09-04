# Cycle-3 final jury

## Final verdict: CONDITIONAL-GO

The candidate may enter method refinement, isolated implementation, and a timing pilot. It is not yet a publishable new method and must not skip the preregistered gates to launch the complete 500-rollout experiment.

**Overall score: 5.9/10**

| Dimension | Score | Judgment |
|---|---:|---|
| Novelty | 4.5/10 | PFD already covers future correction, pure-finetune and shuffled-future controls; the remainder is strict gradient routing, matched placebo, and intervention |
| Identifiability | 6/10 | A/B/C identifies a local total effect relative to stop-grad and one specified placebo, not full mediation |
| Host fit | 8/10 | Identity low-rank adapter fits frozen Qwen and the deterministic frozen head |
| Statistics | 5/10 | Five paired seeds can reject only a large and uniformly signed effect |
| Budget | 6.5/10 | Potentially below 8 GPUh, but 500 rollouts dominate and timing must be measured |
| Reviewer value | 5.5/10 | Valuable as a strict mechanism diagnostic if all gates pass, insufficient as a new WAM/VLA method |

## Required method-plan corrections

1. Pretrain and then freeze the future head before three-arm training. Clone identical head weights, projection, and normalization state into A/B/C so target-specific head adaptation is not another treatment.
2. On episode-disjoint, time-embargo holdout, full `q(m,a)` must beat action-only `q(a)`, state-only `q(m)`, task/phase mean, zero/persistence, and equal-capacity baselines. Action and representation shuffles must both degrade prediction.
3. C must be a fixed, episode-disjoint, non-overlapping future-window derangement within task×phase×speed bins. Keep its adapter auxiliary-gradient norm within 0.9–1.1 of A batchwise and log gradient cosine, unclipped/clipped norm, clipping rate, Adam update norm, loss, and stability.
4. The Stage-2 orthogonal placebo must match rank, energy, and frozen-action-head sensitivity, calibrated on independent holdout by matching initial action-output perturbation norm.
5. Fit the predictive subspace per seed on episode-disjoint data using cross-fitting; never use test rollouts to choose rank, direction, or intervention strength. A full `m_A→m_B` patch must reproduce B action exactly and pass interpolation/support checks.

## Preregistered statistical gates

For Stage 1, aggregate both tasks inside each training seed. Use one-sided exact sign tests for A−B and A−C as an intersection-union gate. All five nonzero seed differences must be positive (`p=1/32=.03125` for each); ties fail. Both average gains should be at least ten percentage points, and neither task may have a negative mean difference.

For Stage 2, use the single primary contrast `SR(A_orth)-SR(A_pred-remove)`. Require all five seeds positive, mean at least ten points, and predictive removal to attenuate the A−B gap by at least 50%. Stage 1 failure forbids Stage 2.

Negative results cannot establish that future objectives are generally ineffective.

## Budget gate

Measure the complete cache, head pretraining, one 500-step adapter run, and a 20-rollout calibration, counting all of it against the cap. If:

`T_cache + T_head + 15*T_adapter + 25*T_20rollout + overhead`

projects above 7.2 GPUh, record NO-RUN. Do not remove controls, seeds, or placebos to force it under budget.

## Exact claim ceiling

If every gate passes, the strongest allowed claim is:

> For one fixed early StarVLA checkpoint, two preregistered LIBERO tasks, and a specified low-rank action-interface adapter, valid action-conditioned future-latent gradients produce a five-seed-consistent closed-loop gain relative to stop-gradient and a support/gradient-norm-matched deranged placebo; under cross-fitted, action-output-matched interventions, removing the treatment-induced future-predictive component harms that gain more than removing an orthogonal component, providing task-local necessity-like evidence.

Do not claim causal mediation, reshaping the frozen Qwen/VLM backbone, a new objective/adapter/WAM, exclusion of all generic regularization, LIBERO/VLA/real-robot generality, SOTA, or physical causal world modeling.

If Stage 1 passes but Stage 2 fails, only the controlled total effect of future-gradient routing may be reported; no representation-mechanism claim is supported.

Any world-gate failure, C instability, seed-direction failure, task inconsistency, action-output-placebo failure, patch-control failure, or budget projection above 7.2 GPUh converts the candidate to NO-GO.
