# Round-1 Method Review

<details open>
<summary>Full raw reviewer response</summary>

# Round-1 Senior Method Review

**CALIBRATION: none.** No human-curated known-good or known-bad proposal anchors were provided; none are inferred.

## Scores

| Dimension | Score | Weight | Weighted |
|---|---:|---:|---:|
| Problem Fidelity | 9.5 | 15% | 1.425 |
| Method Specificity | 6.5 | 25% | 1.625 |
| Contribution Quality | 6.5 | 25% | 1.625 |
| Frontier Leverage | 8.0 | 15% | 1.200 |
| Feasibility | 6.0 | 10% | 0.600 |
| Validation Focus | 7.5 | 5% | 0.375 |
| Venue Readiness | 5.5 | 5% | 0.275 |

**Weighted composite: 7.1/10**

**Verdict: REVISE**

The direction is faithful, unusually disciplined, and correctly framed as a narrow diagnostic rather than a new WAM architecture. It is not READY because several load-bearing quantities are not yet operationally defined, the raw DINO-difference target permits a current-frame shortcut, Stage-2 preregistration is incomplete, and the 7.2 GPUh decision rule is not auditable enough. The remaining high-overlap novelty with PFD is real and should be documented, not “fixed” by adding modules.

## GAP

The gap to READY is primarily identifiability and preregistration, not model capacity or benchmark breadth. The proposal needs one common nuisance-residualized future target, an executable batch-gradient normalization rule, a fully frozen and hashed Stage-2 construction before Stage-1 outcomes, and a deterministic GPU-hour ledger that includes all 530 possible rollouts and all pilots. These revisions would make the two local claims defensible. They would not remove the inherent venue risk from a two-task, single-host, high-overlap protocol contribution; that risk should remain explicit rather than motivating architecture, RL, planning, or benchmark sprawl.

## Core Method Assessment

### 1. Does head pretraining and freezing make A/B/C a valid treatment?

**Conditionally yes.** Pretraining one future head on the identity interface, freezing it, and cloning its exact weights, projection, whitening state, and normalization into A/B/C is the correct minimal choice. It prevents arm-specific decoder learning from becoming an additional treatment and makes A−B a clean comparison between permitting and blocking a specified frozen loss gradient.

The treatment is not fully specified until the proposal also freezes the head training seed, optimizer, schedule, stopping rule, checkpoint-selection rule, deterministic eval behavior, and hashes of the head, projection, whitening statistics, split manifest, and target generator before strict-test opening. The claim remains conditional on this one frozen decoder.

### 2. Batch gradient matching

Use detached FP32 norms over the adapter parameters:

\[
g^{act}_j=\nabla_{\phi_j}L_{action},\qquad
g^{fut}_j=\nabla_{\phi_j}L_{future},
\]

\[
\lambda_A=
\frac{\kappa\lVert g^{act}_A\rVert_2}
{\lVert g^{fut}_A\rVert_2+\epsilon},
\qquad
\lambda_C=
\frac{\lambda_A\lVert g^{fut}_A\rVert_2}
{\lVert g^{fut}_C\rVert_2+\epsilon}.
\]

Define accumulation precision, included parameters, epsilon, scale caps, zero-gradient handling and whether matching is measured before clipping. Scalar norm matching does not match direction, covariance, curvature, action-gradient cosine, Adam moments or effective updates. The allowed interpretation is only that A beats one fixed stratified, auxiliary-gradient-norm-matched deranged-target algorithm.

### 3. DINO residual leakage

The raw target \(E(o_{t+8})-E(o_t)\) can be dominated by reconstructing the negative current embedding. Use one common cross-fitted nuisance-residualized target for the frozen head and Stage 2:

\[
r_t=y_t-b(E(o_t^{main}),E(o_t^{wrist}),task,progress).
\]

Compare full q(m,a) with equal-capacity state-only, action-only, current-DINO-plus-action, nuisance, task/progress and zero baselines. Both action and representation derangements must degrade held-out prediction. This still does not establish physical dynamics.

### 4. Seed rule and budget

Choose ten seeds iff an automated timing-only full-path upper projection is at most 7.2 GPUh; otherwise five iff its upper projection is at most 7.2; otherwise stop. Count cache, head, 30 baseline-screen rollouts, possible 300 Stage-1 and 200 Stage-2 rollouts, triplet trainings, projector, loads, failures/retries, physical GPU count times wall time, and at least 10% reserve. Persist the choice before any treatment rollout. Ten-seed sign inference requires ten contrasts and at least nine positive; ties cannot be silently discarded.

### 5. Checkpoint screen

Freeze exact checkpoint paths/hashes, task IDs, screen states 0..4, rollout seeds/horizon/termination/missing-run policy, pooled formula/tie rule, and final states. Each task independently must lie in the admissible range; pooled success alone is insufficient. The claim must say treatment-blind-selected checkpoint from a preregistered set.

### 6. Stage-2 projector/placebo

Before any Stage-1 outcome, freeze and hash mechanism splits, centering/normalization, nuisance target, ridge/rank/tie/refit rules, projector metric, orthogonal candidates/score, support/interpolation thresholds, and failure behavior. Draw the placebo inside empirical treatment-delta support, orthogonal to the predictive projector. Match rank, removed energy, and frozen-head action perturbation within 10%; no qualifying candidate means no Stage 2. The predictive component needs held-out residual-target predictivity over the selected orthogonal component.

### 7. Claim language

Use “held-out future-latent predictive-validity gate,” “paired controlled algorithmic treatment,” “task/progress/action-norm-stratified and auxiliary-gradient-norm-matched,” and “treatment-blind-selected checkpoint from a preregistered set.” If Stage 2 fails, only the Stage-1 algorithmic contrast remains.

## Dimensions below seven

- **Method Specificity 6.5 — CRITICAL:** gradient controller, nuisance target, head artifact, projector/support rules and C thresholds are not executable. Add exact formulas/order and freeze/hash choices before outcomes.
- **Contribution Quality 6.5 — IMPORTANT:** keep only one contribution: a preregistered sequential identification contract. Treat cache, adapter, projector and sign test as machinery.
- **Feasibility 6.0 — CRITICAL:** measure a complete lockstep triplet and persist an immutable 10/5-seed GPU-hour ledger with reserve.
- **Venue Readiness 5.5 — IMPORTANT:** close current-frame leakage, harmful-placebo and post-outcome projector loopholes; do not add architecture or benchmark sprawl.

## Simplification Opportunities

1. Use one nuisance-residualized target for head, gate and Stage 2.
2. Delete the implementation “supporting contribution.”
3. Build and hash Stage-2 artifacts before opening Stage-1 outcomes.

## Modernization Opportunities

**NONE.**

## Drift Warning

**NONE.**

## Exact Fatal Gates

1. Head, split, nuisance target, projection, derangement, hyperparameters or selection rules are not frozen and hashed before strict-test opening.
2. Invalid/padded t+8, episode overlap, donor-window overlap, nondeterministic preprocessing or statistic leakage.
3. Full head fails the preregistered 5% held-out gates against the strongest equal-capacity baselines or either shuffle gate.
4. Cache/online parity, identity-adapter parity or hot-switch isolation fails.
5. Detached FP32 gradient control is not followed; nonfinite/undefined fallback exceeds 1%; fewer than 95% of batches satisfy the A/C norm ratio.
6. C leakage, fixed points, outcome-driven resampling, update mismatch, clipping mismatch, collapse or C more than 5pp below B.
7. No preregistered checkpoint has both task-level screen success rates in range.
8. Seed count uses treatment outcomes, seed set changes or full projection exceeds 7.2 GPUh.
9. Stage 1 misses seed signs, 10pp, task-direction or correspondence-specificity gates.
10. Stage 2 runs after Stage-1 failure.
11. Projector/placebo choices are outcome-adaptive.
12. Predictive projector lacks held-out predictivity, A-to-B patch parity fails, support fails or no matched placebo exists.
13. Stage 2 misses sign, 10pp or 50%-attenuation gates.
14. Projected use exceeds 7.2 GPUh or actual use exceeds 8 GPUh.
15. The claim exceeds the stage-specific ceiling.

**Final verdict: REVISE.**

</details>

