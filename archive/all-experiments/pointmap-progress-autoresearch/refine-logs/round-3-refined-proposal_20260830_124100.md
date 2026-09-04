# Round 3 Refined Proposal: Trace-Conditioned Historical Relation Filter

**Date:** 2026-08-30  
**Claim type:** conditional value of a transition prior on a frozen observation-aliasing population

## Problem and evidence boundary

The method revises a historical, non-active `inside/on` relation after a later robot action chunk. It tests whether a realized robot-kinematic trace improves a PointMap belief filter when the post-action geometry is ambiguous. Fully hidden exogenous changes with no online evidence are unidentifiable and require re-observation.

Controlled simulator teleports and sensor masks are E0 diagnostics only. They validate RGB/depth/PointMap capture, typed relation labels, missingness, current-predicate behavior, and rollback headroom; they cannot support an action-conditioned claim.

## Belief update and information sets

For relation \(r_{ij}\), maintain \(q_t=P(z_t^{ij}=valid\mid h_t)\). The transition prior is

\[
q^-_{t+H}=T_\theta(q_t,\phi_t^{ij},\tau_{t:t+H},r_{ij}).
\]

Traces end at the last applied control before the post-action PointMap:

- \(\tau^{cmd}\): commanded 7D controls;
- \(\tau^{kin}\), the claim-bearing trace: applied controls plus robot-only end-effector, gripper, and joint proprioceptive sequence;
- \(\tau^{fb}\), appendix ablation: \(\tau^{kin}\) plus contact/force/event feedback, named execution-feedback-conditioned.

Post-action images/PointMaps, simulator object states, object velocities, relation/success labels, future-derived identities, and feedback outside \(\tau^{fb}\) are forbidden transition inputs.

The observation update is

\[
\operatorname{logit}q_{t+H}=\operatorname{logit}q^-_{t+H}+\Lambda_r(o_{t+H},v_{t+H}),
\]

with one frozen observation table shared by all transition variants.

## Exact 54D pre-action geometry schema

PointMaps are in robot-base-aligned world axes and translated by the target robust centroid. Each visible cloud is reduced by deterministic voxel selection: quantize at 5 mm, sort voxel keys lexicographically, retain the point nearest each voxel center, then use fixed evenly spaced indices if more than 128 points remain.

Each object contributes 20 values, in this exact order:

1. present mask (1);
2. clipped visible-count fraction (1);
3. robust centroid in the target-centered base frame (3);
4. coordinate quantiles q10/q50/q90 (9);
5. covariance eigenvalues in descending order (3);
6. q90-q10 robust extents (3).

Target and reference blocks therefore contribute 40 values. The pair block contributes 14:

1. reference-minus-target centroid displacement (3);
2. absolute displacement (3);
3. minimum cross-cloud distance (1);
4. axis-wise robust-box overlap ratios (3);
5. inside signed margin and validity mask (2);
6. support signed margin and validity mask (2).

Total: 40+14=54. If an object cloud is empty, its present/count values and remaining block are zero. If either cloud is empty, pair measurements are zero and both margin-validity masks are zero. A single-point cloud has zero covariance and extents. A relation-inapplicable margin is zero with mask zero. No NaN or variable-length value reaches the model.

## Frozen observation likelihood

For each relation type, reduce visible post-action geometry to one deterministic scalar signed predicate score:

- `inside`: minimum of centered inclusion-fraction margin and normalized robust-box boundary margin;
- `on`: minimum of horizontal-overlap margin, normalized vertical-gap margin, and temporal support-stability margin.

Visibility uses four fixed point-count bins: missing (either cloud under 16 points), 16–31, 32–63, and at least 64. For each non-missing bin and relation, fit a univariate 32-bin class-conditional histogram on training task families; bin edges are equal-frequency edges of the pooled training scores and duplicate edges are merged. Counts use Laplace smoothing \(\alpha=1\). The LLR is the log ratio of smoothed valid versus invalid bin probabilities. The missing bin has LLR exactly zero, without fitting. Tables are frozen before validation and shared across variants.

## Frozen aliasing population

Using only the observation table and validation split, calibrate an observation-only filter with a persistence prior. Let \(\theta^-_r\) be its relation-specific retract threshold at false-retraction rate at most 5%, and \(\theta^+_r\) its continue threshold at false-continue rate at most 5%. Freeze both. The preregistered aliasing set is

\[
\mathcal A_r=\{o:\theta^-_r<q^{obs}(o)<\theta^+_r\}.
\]

Membership uses no test label and is fixed before transition-model evaluation. The primary result is on \(\mathcal A_r\); the full test distribution is supporting evidence. The study reports the size, class prevalence, task coverage, and visibility composition of \(\mathcal A_r\) so that an empty or degenerate slice cannot be hidden.

## Transition head and probability calibration

Trace inputs are resampled/padded to 16 time steps with a mask. A two-layer temporal 1D convolution (64 channels, kernel 3) plus masked mean pooling is concatenated with \(q_t\), the 54D geometry vector, and a fixed `inside/on` token; a two-layer 128-unit GELU MLP emits one logit. Total trainable parameters must remain below 100k.

Training uses prevalence-preserving shuffled batches and ordinary binary NLL—no class weighting or balanced sampling. Deployment/training prevalence is reported. A two-parameter affine calibration \(a\ell+b\) is fitted once on validation NLL and frozen for test. If relation-specific branches are needed, the first study falls back to `inside` only.

## Mandatory causal data construction

E1 restores identical pre-states and executes physics-mediated actions. Preserved and invalidated outcomes must overlap in command/action parameters; at least one action family must yield both outcomes through interaction-state variation. Sampling is matched by action family, duration, pre-state geometry, and post-observation visibility. Residual standardized mean difference above 0.1 triggers rematching or propensity weighting. A command-only shortcut classifier above 60% balanced accuracy rejects the stratum.

Trace shuffling is only within task, action family, duration, pre-state geometry, and visibility strata. Held-out action templates and task families remain untouched.

E2 uses newly collected on-policy VLA chunks or exact original-state replay. Different-state replay is prohibited. Scripted E1 evidence is never promoted to a VLA-distribution claim.

## Per-variant operating points and primary statistic

Every transition variant shares the observation table and validation split, but receives its own validation-only retraction threshold. For invalidity score \(s=1-q\), select the threshold with the greatest validation TPR among empirical candidates satisfying FPR \(\le0.05\); the always-negative threshold is available, so the constraint is always attainable. Freeze the threshold before testing.

The primary statistic is

\[
\mathrm{IMR@FRR5}=1-\frac{\#\{invalid\ events\ retracted\}}{\#\{invalid\ events\}},
\quad
\mathrm{FRR}=\frac{\#\{valid\ events\ retracted\}}{\#\{valid\ events\}}\le0.05.
\]

`Re-observe` counts as an invalidation miss in this binary primary statistic. Three-way retract/re-observe/continue cost is supporting evidence with preregistered unit cost for any wrong terminal decision and zero cost for a correct terminal decision; risk-coverage separately reports abstention rather than hiding it. The unit is one historical ledger-update event. Report 95% task-family cluster-bootstrap confidence intervals. If the empirical validation threshold yields FPR below rather than exactly 5%, report the achieved FPR without interpolation.

## Claim gates

On \(\mathcal A_r\), \(\tau^{kin}\) must reduce decision error at least 10% relative and improve invalidation recall at least 5 points over the strongest observation/no-trace baseline, while respecting FRR≤5%; beat command-only for a realized-execution claim; lose incremental gain under within-stratum shuffling; transfer to held-out actions/tasks; survive learned PointMaps; and improve closed-loop typed rollback/final success after the oracle recovery gate.

The failure statement is fixed as:

> Execution-trace conditional value was not established on the preregistered aliasing population.

It must not be rewritten as a universal necessity claim.

## Complexity boundary

Frozen VLA and geometry teachers; deterministic PointMap summary; one sub-100k transition head; one frozen univariate observation table; validation-only affine calibration and per-variant threshold; no RGB-D video decoder, diffusion, LLM planner, learned recovery policy, or `grasp/open` claim.
