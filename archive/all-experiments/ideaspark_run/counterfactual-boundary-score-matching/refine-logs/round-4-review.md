# Round 4 Senior Method Re-evaluation

**CALIBRATION: none**

No curated good/bad proposal anchors were provided. The scores use the required weighted rubric without external taste anchors.

## Anchor Check

**Problem Anchor: PRESERVED.** The proposal still addresses geometry-induced local action invalidity while explicitly protecting unedited behavior and compiler-observed feasible alternatives. Its claim remains limited to compiler-generable, RGB-observable functional-geometry flips and does not drift into general safety, complete feasible-mode preservation, WAM reasoning, or deployment-time planning.

Fixing the learned support to the five actions actually executed before re-observation is faithful to the anchor: it defines the local response at the policy/controller interface rather than using a negative trajectory's later collision index as a surrogate phase label.

## Implementation and Leakage Audit

The proposal now matches the supplied local OpenPI Pi0/Pi0.5 implementation exactly:

- `t = Beta(1.5,1) * 0.999 + 0.001`;
- `x_t = t * noise + (1-t) * actions`;
- `u_t = noise - actions`;
- squared flow residual is averaged across action dimensions and, for CEFP, across the five executed action times.

The coupling is also correct. Within each `(BranchRecord, padding replicate)` comparison, positive, negative, and frozen-reference evaluations share the same scalar `t`, the same full `H x A` noise tensor, and the same suffix action padding. Consequently the interpolated suffix, suffix velocity target, and suffix noise are elementwise identical. Bidirectional action-token attention can use the common suffix as context, but it cannot read positive/negative identity from candidate-specific suffix tokens because those tokens no longer exist. Direct candidate-suffix leakage is therefore fixed.

`R=2` does not introduce contribution sprawl: it is a two-sample Monte Carlo estimate of the same padding-marginalized preference, with no new model or auxiliary loss. However, the proposed unseen-seed control mixes two different notions. Recomputing margins under three unseen padding seeds is a meaningful offline test of padding invariance. “Closed-loop effect by evaluation padding seed” is not defined, because padding is absent at inference; a closed-loop policy effect can depend on the training padding distribution only if separate models are retrained. That retraining is neither specified nor necessary for the core claim.

## Scores

| Dimension | Weight | Score | Assessment |
|---|---:|---:|---|
| 1. Problem Fidelity | 15% | 9.2 | The immutable problem, claim ceiling, deployment inputs, and support-preservation objective are all retained. The executed-prefix definition makes locality operational without changing the task. |
| 2. Method Specificity | 25% | 8.7 | The BranchRecord schema, native flow path, common random numbers, padding expectation, K-mode aggregation, training losses, deployment cadence, and falsifiers are concrete enough to implement. The remaining ambiguity is confined to the logically undefined “closed-loop effect across evaluation padding seeds” and whether padding chunks are precomputed/stored or sampled online. |
| 3. Contribution Quality | 25% | 8.5 | CEFP is now one focused mechanism: common-state, prefix-identifiable reference-adjusted flow preference. R=2 is estimator variance control, not a parallel contribution. Novelty remains incremental relative to the closest geometry-feasibility work, consistent with the strict jury's 7.15 novelty ceiling; the paper must not elevate the compiler, padding, or preservation regularizer into separate contributions. |
| 4. Frontier Leverage | 15% | 9.2 | The method now uses the actual Pi0/Pi0.5 flow parameterization and time distribution, reuses the frozen foundation policy as reference/padding prior, and avoids forced WAM, critic, or online search. This is natural foundation-model-era leverage. |
| 5. Feasibility | 10% | 6.5 | The model-side plan is feasible, but the data-side gate was silently weakened from the strict jury's overall/per-family yield floors of 15%/8% to 5%/3%. With only 100–200 attempted episodes, 5% yields roughly 5–10 records total before train/validation/test separation and before requiring two roster modes. That is not a credible substrate for five systems, held-out lambda selection, three seeds, 2–3 constraint families, coverage, worst-mode success, and held-out padding checks. The stated 20–40 A100-hour estimate also omits the multiplicative frozen-reference and R=2 candidate evaluations unless batching/caching is specified. |
| 6. Validation Focus | 5% | 7.5 | The validation remains compact and core-claim driven. Pair/prefix permutations, `L_geo`, whole-chunk preference, no-preservation, validity correlation, and unseen-padding margins are sufficient. The padding test must drop or define the closed-loop-by-evaluation-seed clause; no additional benchmark family is needed. |
| 7. Venue Readiness | 5% | 7.8 | The method is sharp and implementation-grounded, but the closest-work overlap remains substantial and the reliability-versus-roster-support hook is still an empirical hypothesis. A sparse compiler-selected dataset or post-hoc relaxed gate would make the venue story look constructed around rare favorable cases. |

## OVERALL SCORE

**8.48 / 10**

Weighted calculation: `0.15(9.2) + 0.25(8.7) + 0.25(8.5) + 0.15(9.2) + 0.10(6.5) + 0.05(7.5) + 0.05(7.8) = 8.475`.

## GAP

With no curated anchors, the relevant gap is to the explicit READY bar. The central method is now coherent: the OpenPI loss is exact, common state fixes the original phase confound, common suffix plus shared time/noise removes direct suffix-label leakage, and the two-padding average is a small expectation rather than module sprawl. The remaining gap is evidence feasibility and control logic. Lowering eligible-yield gates to 5% overall and 3% per family permits E0 to proceed with only a handful of highly selected records, too few to support held-out tuning, multi-mode coverage, worst-mode success, and three-seed conclusions. This also weakens the strict novelty jury's most important pre-training falsifier without a methodological reason. Separately, three unseen padding seeds can establish that offline margin sign/ranking is not tied to the two training paddings, but cannot index closed-loop performance of one padding-free deployed model. Restore a defensible data floor and state the padding control at the level it actually identifies; otherwise READY would reward a precise objective attached to an underpowered, selection-prone dataset.

## Required Fix for Dimension Below 7

### Feasibility — 6.5

- **Specific weakness:** The revised `>=5%` overall and `>=3%` per-family branchable-yield gates are materially below the pre-registered strict-jury kill thresholds and can pass with only 5–10 records. The proposed E0 analyses require distinct training, held-out selection, evaluation, constraint-family, and multi-mode strata.
- **Concrete fix:** Restore at least the strict-jury floors of **15% overall and 8% per retained constraint family**, keep the `>=25%` two-mode requirement, and add a pre-registered absolute-count floor sufficient to populate train/validation/test and each retained family before GPU launch. Report the complete attempted-pair ledger; do not merge near-duplicate checkpoints or planner seeds to meet the count.
- **Specific weakness:** The 20–40 A100-hour estimate does not account explicitly for `R=2`, K positives, the negative, and frozen-reference forward passes.
- **Concrete fix:** Provide a one-batch measured or implementation-derived forward-count budget. Precompute/store the two frozen-reference padding chunks per BranchRecord. If simultaneous R=2 is too costly, sample one of the two pre-registered paddings per optimizer step; this is an unbiased stochastic estimator of the same finite expectation and introduces no new method.
- **Priority:** **CRITICAL**

## Simplification Opportunities

1. Define the padding invariance test only on unseen-padding margin sign/ranking and simulator-validity correlation. Remove “closed-loop effect by evaluation seed” unless separate retraining is explicitly intended.
2. Precompute the two reference padding chunks. Optionally sample one replicate per optimizer step instead of evaluating both on every update; keep both for validation.
3. Keep preservation as one standard replay/reference term. If the no-`L_pres` result is null, delete it rather than creating a secondary preservation claim.

## Modernization Opportunities

**NONE.** The flow backbone and frozen reference are already used naturally. More components would reduce rather than improve the contribution.

## Remaining Actions

1. **CRITICAL:** Restore defensible relative and absolute BranchRecord data gates before authorizing E0.
2. **IMPORTANT:** Correct the unseen-padding falsifier so it tests offline margin invariance; do not attribute padding-seed-specific closed-loop effects to a model that uses no padding at inference.
3. **IMPORTANT:** State padding precomputation and the actual K/R/reference-forward compute multiplier; use stochastic replicate sampling if needed.

## Drift Warning

**NONE.** The anchor is intact and the method is simpler and more precise than in prior rounds. Restoring the data gate and correcting the padding control do not alter the research problem.

## Verdict

**REVISE**

The mechanism-level blockers are resolved, but the proposal does not reach READY because the relaxed compiler-yield gate can authorize an underpowered, heavily selected E0, and the current closed-loop padding-seed clause is not logically defined.
