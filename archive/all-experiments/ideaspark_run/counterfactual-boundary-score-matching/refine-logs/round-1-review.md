# Round 1 Senior Method Review

**CALIBRATION: none**

No curated good/bad proposal anchors were provided. Scores therefore use the required weighted rubric without external taste anchors.

## Scores

| Dimension | Weight | Score | Assessment |
|---|---:|---:|---|
| 1. Problem Fidelity | 15% | 8.0 | The proposal directly targets local correction under functional-geometry invalidation while measuring preservation of unaffected behavior and alternative feasible continuations. It respects the claim ceiling and does not drift into WAM reranking, general planning, or safety guarantees. The remaining concern is methodological rather than a change of problem: the proposed branch construction does not yet identify the local response that should receive credit. |
| 2. Method Specificity | 25% | 5.5 | The data record and high-level pipeline are implementable, but the central estimator is not. `L_boundary`, `L_comp`, and `L_mode` have no equations; the proposal does not state whether the same diffusion/flow noise and time are coupled across candidates, how masks are normalized, how K positives are aggregated, what margin is optimized, or how a π0.5 flow target replaces the stated denoising-error surrogate. Most importantly, it still applies a window derived from the invalid continuation without defining the positive-side support on which the comparison has the same meaning. |
| 3. Contribution Quality | 25% | 6.5 | There is a plausible dominant contribution—reference-adjusted preference between invalid and feasible alternatives from a common physical state—but it is obscured by three nominal losses and a supporting “mode retention” contribution built from familiar anchoring and group-balancing tools. The strict jury already establishes that geometry flips, active-violation localization, and generic mode preservation are not independently novel. The paper is focused only if common-state masked preference is the sole mechanism-level claim and preservation terms are clearly regularization/evaluation machinery. |
| 4. Frontier Leverage | 15% | 7.5 | Diffusion/flow action modeling is used naturally as the train-time distributional interface, and excluding a learned WAM, critic, and deployment-time planner is the right restraint. However, the proposal must formulate the objective in the native parameterization of the chosen backbone: π0.5 is flow-matching, so a generic “denoising error” description is not yet technically faithful. |
| 5. Feasibility | 10% | 6.0 | The non-GPU gate, frozen backbone, and parameter-efficient E0 are sensible. The blocking feasibility tension is that a checkpoint “immediately before” the first violation may be too late for any dynamically feasible alternative, whereas moving it earlier restores branchability but permits positive and negative trajectories to enter different phases before the current mask. K planner successes within a fixed H and equal terminal semantics are not yet guaranteed. |
| 6. Validation Focus | 5% | 8.0 | The two validation blocks are compact and claim-driven. Direct comparison to the closest `L_geo`, whole-chunk preference, mask/pair permutations, and deletion of preservation terms is sufficient for the core thesis. No broader benchmark menu is needed at this stage. |
| 7. Venue Readiness | 5% | 6.0 | The novelty is timely but narrow and the strongest-neighbor delta is responsibly stated. A top-venue paper is not yet supportable because the core preference estimand and its alignment semantics remain ambiguous; without resolving them, a positive result could be attributed to generic planner imitation or regularized fine-tuning rather than boundary-local counterfactual learning. |

## OVERALL SCORE

**6.63 / 10**

Weighted calculation: `0.15(8.0) + 0.25(5.5) + 0.25(6.5) + 0.15(7.5) + 0.10(6.0) + 0.05(8.0) + 0.05(6.0) = 6.625`.

## GAP

With no curated anchors, the relevant gap is to the explicit READY bar. The proposal is much closer to a defensible method paper than a vague module sketch on problem fidelity, restraint, and validation focus, but it remains well below READY on the central mechanism. Sharing `z_b` fixes the precondition confound only at `t=0`; it does **not** make the invalid trajectory’s later violation indices phase-aligned with a positive branch after the branches have diverged. Thus the current construction relocates the original positive/negative alignment flaw rather than eliminating it. In addition, the absence of a native flow-preference equation makes it impossible to tell whether the claimed locality is an actual training property or only a data annotation. The proposal reaches the next tier only when the compared action support is defined from the common decision boundary, the objective is written exactly, and the familiar preservation machinery is subordinated to that one contribution.

## Required Fixes for Dimensions Below 7

### Method Specificity — 5.5

- **Specific weakness:** A common initial checkpoint does not justify reusing the negative collision window on a positive branch. The branches can differ in path homotopy, contact order, and event timing immediately after `z_b`. `L_boundary` is also underspecified for both diffusion and flow heads.
- **Concrete fix:** Replace the negative-derived collision mask with a **common-state decision-prefix estimand**. Search backward for the latest checkpoint `z_b` from which the invalid suffix and at least K feasible continuations exist. Let `D=[0,d)` be a short action prefix beginning at that exact shared state; compare alternative prefixes as competing continuations from the same condition, and make no claim that later per-index states are equal. Do not apply `M^-` to positive raw indices. If retaining the first-violation window is essential, instead define a candidate-specific event map `D_k=phi_k(M^-)` and reject pairs lacking that mapping.
- **Concrete fix:** Write the native objective. For a flow head, define masked flow residual `e_theta(a,c,D)` with a sampled flow time and base noise; use the **same sampled time/noise as common random numbers** for positive and negative candidates; set `g_theta=-e_theta+e_ref`; optimize `softplus[-beta((g_theta(a_k^+)-g_theta(a^-))-delta)]`. State mask normalization, K-positive aggregation, margin, and gradient stops. Use the analogous noise-prediction residual only for a diffusion head.
- **Priority:** **CRITICAL**

### Contribution Quality — 6.5

- **Specific weakness:** Three losses make the method look like a bundle, while `L_comp` and generic per-mode retention are established tools. The current supporting contribution risks claiming novelty for the evaluation lens and regularization rather than the paired preference mechanism.
- **Concrete fix:** Make common-state reference-adjusted flow preference the only method contribution. Fold K positive modes into the core loss through an explicit mean or smooth worst-mode aggregation of per-mode margins, eliminating a separately branded `L_mode`. Rename `L_comp` as a standard reference/replay preservation regularizer and state that it is not novel. Treat roster coverage and complement drift as measurements of the core claim, not a second method contribution.
- **Priority:** **IMPORTANT**

### Feasibility — 6.0

- **Specific weakness:** “Immediately before tau” can be past the last controllable avoidance point. A fixed H can also exclude slower feasible homotopies or give candidates different terminal meaning.
- **Concrete fix:** In the CPU compiler, perform a backward checkpoint search and select the **latest branchable state**, not a fixed lead-in. Accept a record only if controller cache/RNG hashes match, the negative and K positives start from that state, and all candidates satisfy the same pre-registered horizon/terminal-event contract. Report branchable-record yield in the existing attempted-pair ledger; if the yield or mode multiplicity misses the jury’s kill criteria, stop before E0.
- **Priority:** **CRITICAL**

### Venue Readiness — 6.0

- **Specific weakness:** The present claim cannot distinguish boundary-aware preference from ordinary preference learning on planner demonstrations, and “first violation” remains a weak novelty hook already partly covered by active-violation shaping.
- **Concrete fix:** Rewrite the paper claim as one falsifiable sentence: *given alternatives from the same branchable physical state, reference-adjusted preference over the branch decision prefix suppresses the invalid continuation with less policy/support drift than active-violation geometry shaping or whole-chunk preference.* Keep first-violation detection as a data-construction tool, not a novelty claim. The existing `L_geo`, whole-chunk, mask/pair permutation, and preservation deletion comparisons are enough to test this sentence; do not add more experiment families before it survives E0.
- **Priority:** **IMPORTANT**

## Simplification Opportunities

1. Replace `L_boundary + L_mode` with one K-positive, mode-balanced preference objective; retain per-mode metrics for auditing.
2. Demote the first contiguous violation run from a claimed mechanism to a tool for locating a backward-search region. Train on the aligned decision prefix that begins at the shared state.
3. Present complement anchoring as one standard reference/replay regularizer, not as an independent contribution.

## Modernization Opportunities

1. Instantiate the objective directly as reference-adjusted **masked flow-matching residual preference** for π0.5, with coupled flow time/noise across each pair. This is a cleaner use of the backbone than a generic denoising-error label.
2. Use a smooth worst-mode aggregation over the K per-mode preference margins instead of adding a new mode head, critic, or factorized policy.

## Drift Warning

**NONE.** The proposal still solves the immutable Problem Anchor. The recommended change moves credit to the true common-state branch decision and therefore strengthens, rather than changes, the original local-correction problem.

## Verdict

**REVISE**

The direction is promising and appropriately restrained, but shared pre-violation branching alone does not solve phase alignment. The next proposal must define the preference on a truly common decision support (or provide candidate-specific event alignment) and give the exact flow/diffusion objective before any GPU experiment is justified.
