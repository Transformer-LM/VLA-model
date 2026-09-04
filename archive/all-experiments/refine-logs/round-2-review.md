# Round-2 Method Review

<details open>
<summary>Full raw reviewer response</summary>

# Round-2 Senior Method Re-evaluation

**CALIBRATION: none.** Same-family provisional.

## Status

- Problem Anchor: PRESERVED.
- Dominant contribution: SHARPER.
- Simplicity: substantially improved; remaining controls are load-bearing.
- Drift Warning: NONE.
- Verdict: REVISE.

## Scores

| Dimension | Score | Weight | Weighted |
|---|---:|---:|---:|
| Problem Fidelity | 9.8 | 15% | 1.470 |
| Method Specificity | 8.2 | 25% | 2.050 |
| Contribution Quality | 7.5 | 25% | 1.875 |
| Frontier Leverage | 8.5 | 15% | 1.275 |
| Feasibility | 6.5 | 10% | 0.650 |
| Validation Focus | 8.8 | 5% | 0.440 |
| Venue Readiness | 6.2 | 5% | 0.310 |

**Weighted composite: 8.1/10**

Round 1 closed most issues: current-frame leakage, gradient-treatment execution, optimizer ambiguity, checkpoint/seed rules, Stage-2 empirical geometry, and claim ceiling. Remaining blockers are operational.

## GAP

The Stage-2 intervention must be computable during rollout without demonstrated actions or an unbudgeted online DINO teacher, and its token-shared whitening map must be dimensionally explicit. P/Q selection needs a genuinely untouched final fold. The GPU ledger must use a conservative horizon-aware rollout bound and include exact Stage-2 wrapper and per-seed builder costs. Inherent PFD overlap and two-task/single-host scope remain honest venue limitations, not reasons to add architecture or benchmarks.

## Remaining Blocking Issues

### 1. Stage-2 deployment definition

The builder residualizes mean delta using current DINO, demonstrated action, task and progress, but rollout lacks demonstrated action and might require unbudgeted online DINO. Mean delta is 2560-D while the Kronecker operator was described as 20,480-D.

Use the smaller route: learn T_feature from nuisance-residualized offline deltas, project its basis away from the nuisance-predictable delta subspace, then apply it at rollout to centered raw mean delta:

\[
v_{pred}=W^{-1}_{scale}T_{feat}W(\bar\delta-\mu_\delta),
\qquad
\Delta m^k_{pred}=v_{pred}\ \forall k.
\]

Define Q identically. This needs no online nuisance, DINO or demonstrated action. Inverse whitening applies only the linear scale, never the mean.

### 2. D_post fold reuse

Use folds 0–1 for mechanism fit/cross-fitting, fold 2 for ridge/rank validation, fold 3 for Q calibration/matching, and fold 4 as a locked final offline gate. Build and hash A/B/C, P, Q, hyperparameters and thresholds before opening fold 4. Open it once for post-training predictive change and final P-versus-Q checks.

### 3. GPU projection

Mean screen time times 1.25 is not a worst-case bound. Define the rollout upper value as the maximum of measured full-horizon time, observed failed-rollout upper time, and instrumented Stage-2-wrapper time, then add fixed reserve. Expand P/Q as measured per-seed builder cost times selected seed count. Include all loads/retries.

## Simplification Opportunities

1. Use a nuisance-orthogonal basis learned offline and apply it to centered raw A−B deltas; remove online nuisance subtraction.
2. Delete B's discarded shadow VJP; a frozen deterministic decoder has no training effect there.
3. Replace Kronecker notation with an explicit shared per-token removal vector.

## Modernization Opportunities

NONE.

## Remaining Fatal Gates

1. No Stage 2 if rollout-time inputs are unavailable.
2. No Stage 2 if projector/removal dimensions or inverse scaling are wrong.
3. No mechanism claim if Q is selected and certified on the same fold.
4. No Stage 1 if locked final offline gate opens before all A/B/C/P/Q choices freeze.
5. No run if horizon-aware complete projection including wrapper and per-seed builders exceeds 7.2 GPUh.
6. All prior predictive, C, checkpoint, seed, task, support, positive-control, Stage-1/2, and actual 8 GPUh gates remain binding.

**Final verdict: REVISE — 8.1/10.**

</details>

