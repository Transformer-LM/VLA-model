# Round 2 Senior Method Re-evaluation

**CALIBRATION: none**

No curated good/bad proposal anchors were provided. The scores below use the required weighted rubric without external taste anchors.

## Anchor Check

**Problem Anchor: PRESERVED.** The bottom-line target remains local correction of geometry-induced physical invalidity while retaining unaffected behavior and alternative feasible continuations. Moving the comparison to competing prefixes from the latest branchable common state strengthens that target. The proposal has not drifted into planner learning, online verification, WAM rollout, or a general safety guarantee.

The Round 1 phase-alignment objection is substantially resolved. The revised method no longer transfers a negative trajectory's raw violation indices onto positive trajectories and no longer claims that divergent rollouts remain state- or phase-aligned. It compares alternative action prefixes from one identical physical/controller/RNG state, which is a coherent preference data unit.

## Scores

| Dimension | Weight | Score | Assessment |
|---|---:|---:|---|
| 1. Problem Fidelity | 15% | 9.0 | The immutable anchor is explicit and faithfully carried through the data unit, objective, preservation term, deployment path, and metrics. The claim is now correctly limited to compiler-defined, common-state alternatives and support drift. |
| 2. Method Specificity | 25% | 6.5 | The revision supplies the missing BranchRecord contract and a nearly implementation-ready native flow objective. However, the stated masked residual is not yet prefix-isolated: `x_t(a)` contains the entire positive or negative H-step action, while only the output residual is masked to D. A bidirectional action expert can therefore use candidate-specific suffix tokens outside D to predict the prefix residual, defeating the claim that preference is learned from the short competing prefix. The proposed beta calibration is also undefined at initialization because `theta=theta_ref` makes every `g_theta(a)` and hence every reference-adjusted margin exactly zero. |
| 3. Contribution Quality | 25% | 8.0 | The contribution is now singular and well disciplined: common-state reference-adjusted flow-residual preference. First-violation localization is a compiler tool, K-mode handling is part of the same objective, and preservation is explicitly standard regularization. This is a cleaner and more defensible delta from active-violation geometry shaping, although its novelty remains deliberately narrow rather than paradigm-level. |
| 4. Frontier Leverage | 15% | 8.5 | π0.5-native flow matching is used as the natural distributional interface, with coupled time/noise and no forced WAM, critic, or inference-time planner. The modern primitive is doing real methodological work rather than decorating the proposal. |
| 5. Feasibility | 10% | 7.0 | Backward search for the latest branchable state, checkpoint hashing, fixed-H/terminal contracts, explicit exclusion accounting, and a CPU kill gate make the plan executable under the stated resources. Eligible-pair density and multi-mode yield remain empirical risks, but the proposal correctly treats them as pre-training falsifiers. |
| 6. Validation Focus | 5% | 8.5 | The five systems and existing kill tests are lean and sufficient for the central claim. Pair permutation, random-prefix replacement, direct `L_geo`, whole-chunk preference, and no-preservation comparisons are the right necessity tests. No additional benchmark block is required before E0. |
| 7. Venue Readiness | 5% | 7.0 | The paper shape is now focused and timely, with an honest nearest-neighbor delta and claim ceiling. It is not READY because the current masked objective can exploit suffix information and therefore does not yet operationalize its advertised locality; positive E0 results under that estimator would remain mechanistically ambiguous. |

## OVERALL SCORE

**7.73 / 10**

Weighted calculation: `0.15(9.0) + 0.25(6.5) + 0.25(8.0) + 0.15(8.5) + 0.10(7.0) + 0.05(8.5) + 0.05(7.0) = 7.725`.

## GAP

With no curated anchors, the relevant comparison is to the explicit READY bar. The revision closes the largest conceptual gap from Round 1: the estimand now begins at a genuinely common decision state, contribution sprawl is removed, and the flow objective is mostly concrete. The remaining gap is concentrated rather than architectural. Masking the loss does not mask the information available to a bidirectional flow model: because `x_t(a)` still includes the ground-truth candidate suffix, the network may distinguish feasible from invalid records using actions outside D and route that information into outputs inside D. This would make “outside-prefix preservation” and “prefix-local preference” properties of the loss indices, not of the learned estimator. In addition, beta cannot be normalized from the robust standard deviation of `m_k` at the frozen-reference initialization because that distribution is identically zero. Until the input support and scale calibration are corrected, the method remains a strong REVISE rather than READY.

## Required Fix for Dimension Below 7

### Method Specificity — 6.5

- **Specific weakness:** `e_theta(a,c_b,D)` masks residual positions but feeds the full candidate-dependent `x_t(a)` to `v_theta`. Unless the action expert is proven causal/future-blind with respect to action positions, outputs on D can attend to `a_notD`. The preference can therefore learn from suffix identity rather than the common-state decision prefix.
- **Concrete fix:** Make the estimator **prefix-identifiable**. For both members of a pair, ensure every action-model input outside D is identical and cannot reveal candidate identity. The cleanest compatible implementation is to truncate/pad to D and apply an attention/padding mask that prevents D outputs from attending to non-D action tokens; an alternative is a documented causal action attention pattern. If neither is supported by the backbone, abandon the locality claim and optimize the whole continuation. Merely masking the residual or adding `L_pres` is insufficient.
- **Specific weakness:** At `theta=theta_ref`, `g_theta(a)=e_ref(a)-e_theta(a)=0`, so all `m_k=0`; their robust standard deviation cannot calibrate beta.
- **Concrete fix:** After the existing mean normalization, pre-register a fixed beta, or derive beta from the nonzero scale of unadjusted frozen-reference residual contrasts rather than reference-adjusted margins. State the statistic and epsilon floor exactly; do not run a pilot optimization solely to tune beta.
- **Priority:** **CRITICAL**

## Simplification Opportunities

1. Delete the impossible “normalize reference-adjusted margin standard deviation at initialization” procedure and use a pre-registered beta after residual normalization.
2. Keep one standard preservation term on a clearly defined replay distribution. Avoid separate prose-level preservation rules for positive suffixes, negative suffixes, and ordinary replay if they reduce to the same frozen-reference output-matching operator.
3. Retain first violation only as the backward-search endpoint; do not reintroduce first-run ablations or a phase model.

## Modernization Opportunities

**NONE.** The proposal already uses the chosen flow backbone natively and appropriately. The remaining issue is estimator correctness, not a need for a newer module.

## Remaining Actions

1. **CRITICAL:** Prevent suffix-to-prefix information leakage in the flow residual estimator, or explicitly change the claim to whole-continuation preference.
2. **IMPORTANT:** Replace the zero-variance beta calibration with a mathematically defined fixed-scale rule.
3. **IMPORTANT:** State the receding-horizon execution contract—how many predicted actions are executed before replanning and how this relates to variable D—so that “local correction” has the same meaning in training and deployment. This is an interface clarification, not a request for another experiment.

## Drift Warning

**NONE.** The dominant contribution is sharper, the system is simpler, and the frontier leverage is appropriate. Correcting prefix identifiability preserves the Problem Anchor.

## Verdict

**REVISE**

The shared-state prefix construction fixes the original raw-index phase-alignment flaw. The remaining blocker is that the current flow estimator can still read candidate-specific suffix actions while being scored only on D, so it has not yet guaranteed that the learned preference is actually prefix-local.
