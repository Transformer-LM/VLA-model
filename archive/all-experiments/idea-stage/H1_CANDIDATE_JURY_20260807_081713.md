# H1 Candidate Jury

**Verdict:** `REVISE / NO-RUN`  
**Reviewer:** fresh `gpt-5.6-sol`, xhigh, same-family provisional  
**Raw trace:** `.aris/traces/idea-discovery/2026-08-07_run01/001-candidate-jury.response.md`

## Ranking

| Rank | Candidate | Score | Classification | Decision |
|---:|---|---:|---|---|
| 1 | C01 time-arrow × action-identity 2×2 | 82 | DIAGNOSTIC/FINDING | conditionally retain; only primary-direction candidate |
| 2 | C02 controllability-matched target ladder | 75 | DIAGNOSTIC/FINDING | deep novelty check; no training |
| 3 | C03 predictive-subspace intervention | 71 | DIAGNOSTIC/FINDING | accessory to C01 only |
| 4 | C09 Strict Validity–Transfer Gate | 63 | DIAGNOSTIC/FINDING | deep novelty check; design incomplete |
| 5 | C07 action-contrastive JEPA | 59 | REJECT | directly crowded by AquaJEPA/SelfWAM |
| 6 | C05 horizon/chunk alignment | 57 | ORDINARY ABLATION | secondary only |
| 7 | C04 layer routing | 52 | REJECT | FLARE/GAM collision |
| 8 | C08 frozen-prior residual | 49 | REJECT | missing validated asset; outside budget |
| 9 | C06 compatible gradient | 43 | REJECT | generic PCGrad/CAGrad route |
| 10 | C10 heldout transfer gate | 41 | REJECT | generic ForkMerge/validation gating |

No candidate qualifies as `NEW METHOD`.

## Conditional primary: C01

**Allowed positioning:** a matched factorial diagnostic/finding, not a new future head, JEPA objective, WAM architecture, or state-of-the-art VLA.

**Provisional claim:** under fixed StarVLA initialization and LIBERO data, with parameters, target tokens, and training FLOPs matched within ±5%, only `future_correct` should create incremental closed-loop success, yielding positive `(future_correct - future_shuffle) - (past_correct - past_shuffle)`.

**Nearest-work boundary:** SelfWAM occupies action perturbation; VLA-JEPA, Fast-WAM, LiLa-WAM and VLAFlow occupy future-latent/removable-head and controlled objective comparisons. C01 survives only as a complete time-arrow × action-identity closed-loop identification matrix.

## Required preregistration before any run

- Lock one LIBERO-Object and one LIBERO-Spatial task using action-only success only, each within 30%–80%; no treatment-aware task selection.
- Lock the four cells, common checkpoint, data order, LoRA modules, head, target dimension, steps, tokens, optimizer, and ±5% compute tolerance.
- Shuffle within task × phase × speed bins and audit distribution preservation.
- Use at least 50 paired rollouts per cell/task with identical initial/evaluation seeds.
- Require `future_correct` to beat persistence and action-agnostic baselines on strict temporal/episode holdout and show shuffle sensitivity.
- Primary pilot threshold: policy DiD ≥ +10 percentage points; each task-wise DiD non-negative; one-sided paired-bootstrap 90% lower bound > 0; world-diagnostic interaction same sign with standardized effect ≥ 0.20.
- Kill on leakage, unmatched compute, failed strict `future_correct`, incomparable shuffle, sub-threshold/discordant DiD, or world-loss-only signal.
- Never train with the strict-failed CF-DynAlign predictor and never set its `lambda_cf` nonzero.

## Unresolved protocol conflict

The strict gate should prevent invalid world predictors from shaping a policy, but the factorial placebo cells intentionally use noncausal action/target relations and must still apply nonzero, matched auxiliary updates. Before implementation the protocol must distinguish:

- **treatment admissibility:** `future_correct` must pass the world-validity gate;
- **placebo validity:** placebo heads need only pass interface, optimization, target-variance, and finite-learning checks, and are never described as valid world models.

This exception must be preregistered and independently reviewed. If it cannot be justified, C01 is not executable.

## Deep novelty list

1. C01 full factorial identification.
2. C02 controllability as a prospective target-selection predictor.
3. C09 strict world validity as a predictor of policy transfer; attempt to falsify against generic auxiliary-task/model-selection work.

C03 may be run only after C01 checkpoints exist, using no new policy training. Its intervention evidence can establish at most necessity-like evidence, not complete causal mediation.

