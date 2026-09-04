# Refinement Report

## Start

The initial BLSM proposal tried to apply the negative trajectory's first-violation interval to positive trajectories. This was not causally interpretable because the positives could be in different skill phases at the same raw time index.

## Final Mechanism

The refined method, **Common-State Executed-Prefix Flow Preference (CEFP)**, makes four decisive changes:

1. Positive and negative continuations start from the same complete simulator/controller/RNG checkpoint.
2. Only the five actions actually executed before re-observation retain candidate identity; all unexecuted suffix tokens use an identical frozen-reference padding.
3. Preference uses the exact OpenPI π0/π0.5 native flow path and shared `t` and noise, with frozen-reference residual adjustment.
4. K=2 verified feasible alternatives are optimized jointly, while replay/reference regularization and lineage-held-out evaluation test whether reliability gains destroy action support.

## Why This Is Not a Depth or WAM Add-On

Depth, PointMap and WAM rollout were deliberately removed from the final mechanism. The target failure is not missing geometry representation alone; it is distributional collapse when geometry supervision rejects one invalid action. Simulator geometry is used only to compile honest counterfactual records and labels. Deployment remains RGB + proprioception + language π0.5.

## Closest-Work Boundary

arXiv:2604.17896 already covers counterfactual obstacle placement, same-start/same-goal replanning, and active-violation geometry loss. CEFP's narrower claimed delta is executed-prefix, reference-adjusted flow preference over multiple verified feasible alternatives, with explicit support-preservation evaluation. The claim is killed if direct `L_geo` matches CEFP on edited success, mode coverage and worst-mode success.

## Remaining Risks

- The compiler may not yield enough independent, two-mode BranchRecords.
- Common reference padding may still influence margins despite identical suffixes.
- A direct geometry loss may be sufficient, eliminating the need for CEFP.
- The frozen-reference flow margin may correlate weakly with simulator validity.

These are empirical E0 questions, not hidden assumptions. The protocol stops before GPU or terminates the claim when the registered gates fail.
