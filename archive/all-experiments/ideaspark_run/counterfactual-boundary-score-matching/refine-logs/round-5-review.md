# Round 5 Final Senior Method Re-evaluation

**CALIBRATION: none**

No curated good/bad proposal anchors were provided. The scores use the required weighted rubric without external taste anchors.

## Anchor Check

**Problem Anchor: PRESERVED semantically; no drift.** CEFP still solves the original bottom-line problem: when functional geometry invalidates a local portion of a continuous-action VLA response, update the actually executed local response while retaining unedited behavior and other verified feasible continuations. The proposal remains a train-time post-training method with RGB/proprioception/language-only deployment. It does not drift into WAM reasoning, online planning, a safety guarantee, or preservation of unenumerated modes.

The displayed Round 4 anchor is a condensed restatement rather than a verbatim copy of Round 0. This is archival hygiene, not methodological drift: the final report should restore the original wording verbatim and mark the old raw-index flaw as resolved, without changing the current method or claim.

## Round 4 Resolution Audit

### Data feasibility

The feasibility blocker is resolved. The proposal restores the strict-jury relative gates (`>=15%` overall, `>=8%` per retained family), preserves the full attempted-pair ledger, and adds a hard floor of 120 independent BranchRecords before GPU launch. Lineage-level deduplication and 72/24/24 splitting prevent adjacent checkpoints, repeated planner seeds, and trajectory perturbations from leaking across train, validation, and test. Requiring at least 30 records per family and at least 10 test records per family makes the two-family E0 interpretable. Failure to reach any gate stops training rather than relaxing the protocol.

One wording redundancy should be cleaned up: the BranchRecord schema and E0 objective already require `K=2` distinct roster modes for every accepted record, so “at least 30 records contain two modes” cannot be read as allowing the other 90 to have one. Under the stated schema, all 120 accepted BranchRecords must satisfy K=2; the 30-record clause is therefore redundant, not a methodological escape hatch.

### Padding expectation and leakage

The suffix-leakage repair remains sound. For a given record and padding replicate, all candidates share the complete suffix action tensor, full suffix noise, flow time, interpolated suffix input, and velocity target. Bidirectional action-token attention therefore receives no candidate-specific suffix identity.

The R=2 construction is coherent and small. Two reference padding chunks are generated and hashed before training; sampling one uniformly per optimizer step gives an unbiased stochastic gradient of the explicitly defined two-padding finite expectation, while validation averages both. This adds no model, head, or parallel paper contribution. The three unseen padding seeds are now used only for offline margin sign/rank and validity-correlation stability, which is the logically correct scope. They test whether the surrogate depends on the two chosen paddings without pretending padding exists at deployment.

### Native implementation and compute

The proposal exactly matches the supplied OpenPI Pi0/Pi0.5 path: clipped `Beta(1.5,1)` time, `x_t=t*noise+(1-t)*actions`, `u_t=noise-actions`, and mean squared flow residual on the five executed action times. The eight-example-forward bound is explicit and honest: six candidate evaluations for K=2 across trainable/reference paths plus trainable/reference replay evaluations. Batch concatenation, padding precomputation, a measured throughput gate, and an 80 A100-hour ceiling make E0 operationally bounded.

The “disable adapter to obtain the reference” compute shortcut assumes LoRA/adapters. If an in-place action-head update is selected instead, a frozen shadow of the updated head is required. E0 should simply pre-register LoRA/adapter tuning or account for that small frozen head copy; this is an implementation choice, not a blocker.

## Scores

| Dimension | Weight | Score | Assessment |
|---|---:|---:|---|
| 1. Problem Fidelity | 15% | 9.3 | The original problem, constraints, claim ceiling, and deployment interface are preserved. Executed-prefix support and lineage-controlled geometry flips directly operationalize the anchor. The non-verbatim anchor restatement is a final-document cleanup, not semantic drift. |
| 2. Method Specificity | 25% | 9.2 | The data schema, native OpenPI equations, shared randomness, finite-padding estimator, K aggregation, preservation path, inference cadence, gates, split, compute multiplier, and kill rules are implementation-ready. Only minor cleanup remains around the redundant multi-mode floor and adapter/reference implementation choice. |
| 3. Contribution Quality | 25% | 8.8 | There is one focused mechanism-level contribution with no bloat: common-state, prefix-identifiable, reference-adjusted native-flow preference. The method responsibly treats compiler, padding, mode roster, and preservation as protocol or standard machinery. The score remains below 9 because the strict novelty jury found substantial overlap with counterfactual obstacle construction and active-violation shaping; CEFP's novelty depends on the paired distributional/support result. |
| 4. Frontier Leverage | 15% | 9.3 | Pi0/Pi0.5 flow matching and the frozen foundation policy are used in their natural roles as action-distribution model and reference prior. No trendy but unnecessary WAM, critic, phase estimator, or deployment-time search is attached. |
| 5. Feasibility | 10% | 8.8 | Relative and absolute data gates, independent lineage splits, precomputed padding, stochastic replicate sampling, explicit forward count, measured throughput, and a hard compute ceiling make the small E0 credible. Whether the compiler actually yields 120 valid records is an intended pre-GPU falsifier, not an unresolved design flaw. |
| 6. Validation Focus | 5% | 9.2 | The five matched systems and correspondence, padding, support, preservation, and validity kills are minimal but sufficient for the core claim. No paper-scale benchmark expansion is required before E0. |
| 7. Venue Readiness | 5% | 8.6 | If E0 supports the registered reliability-versus-roster-support delta, the method has a sharp, timely paper shape. The closest-work overlap and compiler-defined scope remain honest limitations; failure of the `L_geo` comparison correctly kills the method claim rather than being papered over. |

## OVERALL SCORE

**9.06 / 10**

Weighted calculation: `0.15(9.3) + 0.25(9.2) + 0.25(8.8) + 0.15(9.3) + 0.10(8.8) + 0.05(9.2) + 0.05(8.6) = 9.060`.

## GAP

With no curated anchors, the relevant gap is to the READY bar and then to a completed paper. The proposal now clears the method-ready bar: the anchor is preserved, the central estimand is identifiable at the executed-prefix interface, the OpenPI implementation is exact, data selection is independently gated and auditable, compute is bounded, and the validation set is lean but decisive. The remaining gap is empirical, not a missing mechanism. The strict jury already showed that geometry flips and time-local feasibility shaping are close prior art; CEFP earns its contribution only if E0 demonstrates, at matched invalid-execution reduction, a support/coverage advantage over the direct `L_geo` reproduction and whole-chunk preference. Hybrid reference padding may also fail to transfer to coherent closed-loop chunks despite offline seed invariance. Both risks are exactly what the registered E0 and kill criteria are designed to falsify. Requiring a broader task suite, real-robot study, or full paper-scale benchmark before this E0 would add cost without resolving a current proposal blocker.

## Required Fixes for Dimensions Below 7

**NONE.** No dimension scores below 7, and no unresolved method-level blocker remains.

## Simplification Opportunities

1. Delete the redundant “at least 30 records contain two modes” clause or state explicitly that all 120 BranchRecords satisfy K=2; retain 30 only if it denotes a separate stratified analysis.
2. Pre-register LoRA/adapter tuning for E0 so the frozen-reference path is exactly “adapter disabled.” If action-head tuning is retained as an option, budget a frozen head copy explicitly.
3. Restore the Round 0 Problem Anchor verbatim in the final clean proposal and document later fixes under the method, not by rewriting the anchor.

## Modernization Opportunities

**NONE.** The proposal already uses the frontier primitive naturally. Additional modules would create contribution sprawl.

## Remaining Actions

These are execution steps and bounded E0 risks, not proposal blockers:

1. Run the 200-attempt yield pilot and stop if the 15%/8% gates fail; otherwise collect the 120 lineage-independent records under the unchanged compiler.
2. Unit-test common suffix/time/noise equality and the native OpenPI residual against the local implementation before training.
3. Measure the eight-example-forward update cost, enforce the 80 A100-hour ceiling, and run the registered single-seed mechanism E0 before any multi-seed expansion.
4. Let the direct `L_geo`, padding-invariance, correspondence, and support kill criteria terminate the idea if their thresholds fail; do not soften them post hoc.

## Drift Warning

**NONE.** The semantic Problem Anchor is preserved, the contribution remains singular, and all recommended execution checks stay within the authorized small E0.

## Verdict

**READY**

CEFP is ready to proceed to the pre-GPU compiler gate and, only if that gate passes, the bounded E0. READY here means the method proposal is sufficiently focused, concrete, modern, feasible, and falsifiable to test; it does not assert that the novelty or empirical claim has already been validated.
