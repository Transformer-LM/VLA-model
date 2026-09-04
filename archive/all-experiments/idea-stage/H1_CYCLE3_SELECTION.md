# H1 Cycle-3 Candidate Selection: PGR-Audit

**Recorded:** 2026-08-07 09:06 +08:00  
**Direction:** H1 — predictive world objective shaping VLA representations  
**Decision:** `CONDITIONAL-GO → METHOD-PLAN`  
**Assurance:** same-family provisional  
**GPU consumed:** 0.0 GPUh

## Selected research question

**PGR-Audit — Predictive-Gradient Routing at a VLA Action Interface**

For a frozen-backbone, deterministic StarVLA policy, does allowing a strictly validated action-conditioned future-latent objective to update a newly inserted shared action-interface representation improve closed-loop behavior specifically because the future correspondence is valid, rather than because any auxiliary gradient regularizes the interface? If an effect exists, does a treatment-induced future-predictive component carry necessity-like behavioral evidence under a controlled intervention?

This is a **mechanistic diagnostic**, not a new future objective, adapter, VLA, WAM, or SOTA method.

## Why this candidate survived three idea cycles

Earlier candidates failed at least one load-bearing gate:

- future/past factorial designs lacked a valid comparable negative-control outcome;
- flow/SNR routes did not fit the deterministic StarVLA host;
- control-affine/Jacobian routes were not identifiable from single-action offline demonstrations;
- generic future bottlenecks collided with VLA-JEPA, VLAFlow, ProgressVLA, PFD, and related work;
- probe-only variants did not satisfy H1 because they could not let a world objective shape a shared policy representation.

PGR-Audit retains a narrow uncovered intersection:

1. randomized routing of a valid future gradient into a shared action interface;
2. both stop-gradient and support/gradient-norm-matched deranged-future controls;
3. a cross-fitted, action-output-matched intervention on the treatment-induced predictive component.

The novelty check remains **PARTIAL / Level 2 high overlap**. The closest threat is PFD; the residual contribution is the stricter causal-diagnostic protocol, not the components.

## WAM route card

- **Prediction space:** fixed DINOv2 latent future-minus-current residual, projected/whitened.
- **World-model family:** task-centric latent dynamics; no pixel/video decoding.
- **Action conditioning:** demonstrated 8-step action chunk.
- **World-model role:** training-time representation objective and diagnostic.
- **Policy coupling:** a low-rank shared action-token adapter is used by the frozen deterministic action head and the frozen future head.
- **Control usage:** no planning, model-based RL, or inference-time imagination.
- **Data/evaluation:** offline LIBERO demonstrations plus paired closed-loop LIBERO rollouts.
- **Claim ladder ceiling:** local policy effect and controlled necessity-like evidence; no physical causality or cross-architecture generality.

## Frozen host and smallest intervention

- Clean StarVLA HEAD: `3422b9f2387b6f682cf02802904a77b23ab13afd`.
- Baseline: Qwen3-VL-4B, eight action tokens, deterministic MLPResNet/L1 7D action head.
- Qwen and the existing action head stay frozen.
- Add only a shape-preserving, identity-initialized low-rank adapter:

  `m(h) = h + U V LN(h)`, with `h ∈ R^[B,8,2560]`.

- Pretrain one future head, then freeze it and clone identical weights/projection/normalization to every arm.
- Train from a fresh immutable personal feature cache. Do not reuse CF-DynAlign code, predictor, cache, or failed validity claim.
- At inference, discard the future head; only the small adapter remains.

## Three-arm randomized treatment

All arms start from the same fixed early checkpoint, cached representations, minibatch order, action loss, optimizer state, adapter initialization, and future-head checkpoint.

- **A — valid future gradient:** valid `q(m,a)` future loss updates the adapter.
- **B — stop-gradient:** the same valid future task/head/compute trains on `sg(m)`; the adapter receives only action-loss gradient.
- **C — deranged placebo gradient:** a pre-fixed, episode-disjoint, non-overlapping, task×phase×speed-matched deranged target updates the adapter. Its auxiliary adapter-gradient norm must remain within 0.9–1.1 of A batchwise.

Train A/B/C lockstep inside one process per training seed so batches and C-to-A gradient matching are exact. Log auxiliary/action gradient cosine, unclipped/clipped norm, clip rate, Adam moments/update norm, and all instability.

## Strict model-level gate

Before any policy claim, full `q(m,a)` must pass an episode-disjoint, time-embargo holdout and beat:

- zero/persistence and task/phase mean;
- action-only `q(a)`;
- state-only `q(m)`;
- equal-capacity action-agnostic/current-only baselines.

Both action shuffle and representation shuffle must significantly degrade prediction. Invalid `t+8` samples and episode-boundary clip padding are forbidden. Failure is a hard stop.

## Staged policy and mechanism evidence

### Stage 1 — controlled total effect

Evaluate A/B/C on two fixed, treatment-blind-selected non-saturated LIBERO tasks with common initial states.

Preferred design, if non-performance timing calibration keeps the entire protocol at or below 7.2 GPUh:

- 10 paired training seeds;
- 5 common initial states per task/arm;
- `10 × 2 × 3 × 5 = 300` rollouts.

The fallback five-seed design is permitted only as an explicitly exploratory diagnostic:

- 5 paired seeds;
- 10 common initial states per task/arm;
- the same 300 rollouts.

The seed count is frozen from timing and storage measurements **before any A/B/C success outcome is observed**.

For the preferred ten-seed design, A>B and A>C are a one-sided intersection-union gate. Each contrast must have at least 9/10 positive non-tied seed-level differences, pooled gain at least 10 success-rate points, and no task-level negative mean. Exact sign `p=0.0107` for 9/10 positive. Stage 1 failure forbids Stage 2.

### Stage 2 — controlled necessity-like evidence

Only after Stage 1 passes, evaluate:

- A with its cross-fitted treatment-induced predictive component removed;
- A with a matched-rank, matched-energy, orthogonal component removed.

The placebo must also match initial frozen-action-head output perturbation on independent holdout data. No test trajectory may select rank, layer, direction, or strength. The full A-to-B representation replacement must numerically reproduce B actions as a positive control.

Preferred ten-seed design: `10 × 2 × 2 × 5 = 200` rollouts. Require the predefined orthogonal-minus-predictive success contrast to be positive for at least 9/10 seeds, average at least 10 points, and predictive removal to attenuate the A−B gap by at least 50%.

## Model–policy–environment evidence contract

- **Model:** strict held-out prediction, action/representation shuffle sensitivity, cache parity, no episode leakage.
- **Policy:** action L1, action-output effective rank/diversity/cosine, gradient/update diagnostics, exact patch controls.
- **Environment:** paired LIBERO success over fixed tasks, seeds, and initial states; per-task results retained.

No latent metric alone may imply policy improvement, and no imagined outcome counts as environment evidence.

## Compute and execution gate

Read-only feasibility estimates:

- 500 rollouts: about 5.06 GPUh on the two faster candidate tasks;
- fresh cache, head pretraining, and five lockstep 500-step triplet trainings: about 0.5–1.2 GPUh;
- personal incremental storage: roughly 1.3 GiB, with about 2.6 TiB available.

The preferred ten-seed design doubles only the small cached-feature triplet training, not rollout count. A measured cache, one full triplet training, hot-switch parity, and 20-rollout timing calibration must be charged to the 8 GPUh cap. If the complete worst-case projection exceeds **7.2 GPUh**, the run stops; controls, seeds, or placebos may not be deleted to force a fit.

## Remote safety contract

- Use only SSH user `liu_meng`.
- Read/write only `<PERSONAL_RESEARCH_ROOT>`.
- All code, caches, dependencies, temporary files, logs, checkpoints, metrics, W&B offline files, videos, and results remain personal.
- Never use team/shared directories.
- Never use root, sudo, su, `.bashrc`, global Conda, system CUDA changes, or shared environments.
- Never modify the dirty CF-DynAlign StarVLA tree.
- Create an isolated clean H1 worktree/extension only after the method plan passes.
- Recheck every physical GPU immediately before every launch. Use physical GPUs 2/3 by default. Use 0/1 only if all four GPUs are proven idle at that moment.
- Never terminate, overwrite, or attach to unrelated jobs.

## Exact claim ceiling

If every gate passes, the strongest allowed claim is:

> On one fixed early deterministic StarVLA checkpoint and two preregistered LIBERO tasks, a strictly validated action-conditioned future-latent gradient produces a training-seed-consistent closed-loop gain relative to stop-gradient and a support/gradient-norm-matched deranged-future placebo; under cross-fitted, action-output-matched intervention, the treatment-induced future-predictive interface component carries task-local necessity-like evidence.

Do not claim full causal mediation, Qwen/VLM reshaping, a new objective/adapter/WAM, exclusion of every generic regularization mechanism, LIBERO/VLA/real-robot generality, or SOTA.

## Idea-discovery gate result

Three independent final checks returned conditional GO:

- novelty/identifiability: high-overlap diagnostic with a narrow residual delta;
- statistics: runnable only under strict seed-level inference and large-effect gates;
- implementation/budget: exact host insertion is feasible, but cache/hot-switch/timing gates are mandatory.

Therefore idea discovery is complete and the run advances to **method-plan**. No remote file has been written and no GPU hour has been consumed.

