# Round 3 Senior Method Re-evaluation

**CALIBRATION: none**

No curated good/bad proposal anchors were provided. The scores use the required weighted rubric without external taste anchors.

## Anchor Check

**Problem Anchor: PRESERVED.** CEFP still addresses the immutable problem: correct the locally invalid physical response induced by functional geometry while retaining unaffected behavior and other feasible continuations. Fixing the optimized support to the five actions actually executed before re-observation makes “local” operational at deployment rather than changing the problem. The proposal remains train-time VLA post-training, not a planner, WAM, online shield, or safety guarantee.

The Round 2 suffix-leakage blocker is resolved at the data-tensor level. Within a BranchRecord, positive and negative examples now differ only on `E={0,...,h_exec-1}`; padding actions, interpolated suffix inputs, and base-noise suffix are identical. A bidirectional action expert therefore cannot recover candidate identity from candidate-specific suffix tokens because none are present.

## Scores

| Dimension | Weight | Score | Assessment |
|---|---:|---:|---|
| 1. Problem Fidelity | 15% | 9.2 | The fixed executed-prefix support, common branch state, preservation constraints, and receding-horizon contract closely match the anchor. The claim is appropriately conditional on compiler-defined branchable records and does not overreach to all feasible modes or general robot safety. |
| 2. Method Specificity | 25% | 7.8 | The interfaces, BranchRecord acceptance rules, padding construction, loss aggregation, deployment cadence, and kill gates are now highly concrete. One implementation-critical equation remains wrong for the selected backbone: local OpenPI Pi0/Pi0.5 uses `x_t=t*noise+(1-t)*actions`, target `u_t=noise-actions`, and `t~Beta(1.5,1)*0.999+0.001`, not the proposal's reversed interpolation/velocity with uniform time. The two conventions can be reparameterized abstractly, but they are not interchangeable when calling the pretrained model with its native time convention and asymmetric training-time distribution. |
| 3. Contribution Quality | 25% | 8.5 | The method has one dominant contribution and no contribution sprawl: prefix-identifiable, common-state, reference-adjusted flow-residual preference. Common padding is an elegant minimal repair rather than a new module. The novelty remains intentionally narrow, consistent with the strict jury's claim ceiling, but the mechanism is now substantially more reviewer-defensible. |
| 4. Frontier Leverage | 15% | 8.2 | Flow matching is the natural interface and no unnecessary WAM, critic, phase network, or deployment-time search has been added. The score is held below the top tier only because the proposal currently labels a non-native interpolation and time schedule as the native π0.5 objective. |
| 5. Feasibility | 10% | 8.0 | `h_exec=5`, common padding, fixed execution cadence, backward branch search, checkpoint reproducibility, and the pre-GPU yield gates make implementation realistic within the stated compute. Data sparsity remains an explicitly gated empirical risk rather than an unacknowledged assumption. |
| 6. Validation Focus | 5% | 8.5 | The five systems and existing permutation/deletion tests directly target the core claim. The experiment set remains compact. The common-padding locality check needs a corrected decision rule, but it can replace the current suffix-probe wording rather than expand the experiment menu. |
| 7. Venue Readiness | 5% | 7.8 | If the native objective is corrected and the padding control is made logically decisive, the proposal has a sharp method-paper shape. Venue readiness is still bounded by the strict jury's marginal novelty result and by the need for E0 to show that active-violation `L_geo` truly loses support at matched reliability. |

## OVERALL SCORE

**8.30 / 10**

Weighted calculation: `0.15(9.2) + 0.25(7.8) + 0.25(8.5) + 0.15(8.2) + 0.10(8.0) + 0.05(8.5) + 0.05(7.8) = 8.300`.

## GAP

With no curated anchors, the relevant gap is to the explicit READY bar. CEFP has closed the conceptual gaps from Rounds 1 and 2: it compares decisions from one physical state, uses the exact deployment execution window, removes candidate-specific suffix information, and reduces the method to one preference objective plus standard preservation. The principal remaining gap is now implementation fidelity rather than architecture. The written path, velocity target, and uniform time sampling do not match the local OpenPI Pi0/Pi0.5 loss; implementing the proposal verbatim would fine-tune the pretrained velocity field under a reversed time coordinate, sign-flipped target, and different time weighting. A secondary gap is that one frozen-reference padding sample creates hybrid prefix/suffix chunks whose seam may favor compatibility with that arbitrary padding rather than physical validity. Identical padding removes direct label leakage, but it does not by itself establish padding invariance. These are bounded corrections, yet READY requires them to be specified before E0 rather than repaired implicitly in code.

## Required Fixes for Dimensions Below 7

**NONE.** All dimensions score at least 7. The remaining actions below are nevertheless required because READY permits no unresolved blocker.

## Simplification Opportunities

1. Replace the current flow equations verbatim with the three-line OpenPI-native convention; do not present an alternative time parameterization or maintain two notations.
2. Remove the current candidate-suffix/suffix-only-probe acceptance sentence. It does not establish CEFP locality: showing that a contaminated candidate-suffix variant is probe-predictive says nothing about whether CEFP depends on its arbitrary common padding.
3. Keep the fixed `h_exec=5` support. Do not reintroduce variable masks, event alignment, or a learned phase component.

## Modernization Opportunities

**NONE.** The selected primitive is already current and appropriately minimal. The needed change is exact conformance to the existing π0.5 training API, not another model component.

## Remaining Actions

1. **CRITICAL:** Use the exact OpenPI-native loss convention throughout: `t~Beta(1.5,1)*0.999+0.001`, `x_t=t*xi+(1-t)*a_tilde`, and `u_t=xi-a_tilde`. Positive, negative, and reference evaluations must share the same sampled `t` and `xi`; common suffix construction remains unchanged.
2. **IMPORTANT:** Make common padding a defined expectation or a robustness-controlled Monte Carlo estimate rather than an arbitrary single-seed condition. The smallest fix is to sample a small fixed number of reference paddings per BranchRecord and average the per-padding margins, or to pre-register a padding-seed swap that must preserve margin ranking and effect direction. This is a control for the core estimand, not a new experiment block.
3. **IMPORTANT:** Correct the locality kill rule: CEFP should fail if prefix-identity permutation retains the gain or if changing only the common padding seed changes the margin/effect direction materially. A suffix-only probe on the deliberately contaminated candidate-suffix variant is diagnostic but cannot validate CEFP by itself.

## Drift Warning

**NONE.** The original anchor is intact, the dominant contribution is sharper, the method is simpler, and diffusion/flow machinery is used naturally. Correcting the native convention and padding control does not change the research question.

## Verdict

**REVISE**

The major alignment and suffix-leakage defects are fixed. The proposal is not READY because its supposedly native π0.5 objective still disagrees with the actual OpenPI loss convention, and its common-padding control must rule out dependence on an arbitrary hybrid suffix.
