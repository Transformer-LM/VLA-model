# Phase 3 terminal failure — anchor-separated-coadaptation

## Terminal status

All three audited candidates are `abandon` outcomes and are terminal under the current anchor-separated-coadaptation framing. None is eligible for `advance` or an in-place Phase 3.3 revision: each has at least one hard-floor finding that requires mechanism redesign, and the third candidate also has an exact-mechanism collision.

## Root audit: `phase3_critique/phase3_critique_output.json`

**Verdict:** `abandon` (`hard_floor`)

**Verdict rationale (verbatim):**

> blocking_findings_disposition[0] is upheld: the candidate can assign zero priority to the very policy-censored, unrepaired physical failure it claims to retain, and the blocking-obstacle rule requires abandon because correcting that product requires mechanism redesign rather than a field-level patch. recipe_application_check.entries[0].verdict is applied and falsification_structure_check.verdict is sound, while paper_pointed_threat.subsumption_argument finds no exact VLAW overlap, but those checks cannot override the executed load-bearing failure; gap_closure_reject_check.entries[0].reject_lessons_evaluated[1].lesson_quoted remains only borderline.

**Triggering check:**

- `blocking_findings_disposition[0].status = upheld`: the explicit product `r_{k,i}=c_{k,i}h_{k,i}` gives `h_{k,i}=0` and hence `r_{k,i}=0` whenever `ell_{k,i}=0<ell_{b_i,i}`. The executed case therefore gives no priority to an already-well-modeled but unrepaired, policy-censored failure; fixing it requires an `h`-independent retention channel or a different priority composition.

## Attempt 1: `attempt_1/phase3_critique/phase3_critique_output.json`

**Verdict:** `abandon` (`hard_floor`)

**Verdict rationale (verbatim):**

> The upheld blocking finding shows that Step 7's load-bearing sensitivity row has no executable producer, so the projected joint update cannot be formed without adding a new estimator and changing the mechanism. Independently, anti_pattern_check.mitigation_substantively_delivered is false because the matched heterogeneous_decomposition + structural_prior_encoding composition lacks the required isolated-leg ablations; C04's recipe is applied and its reject check is only borderline, but neither offsets the executed infeasibility.

**Triggering checks:**

- `blocking_findings_disposition[0].status = upheld`: Step 6 computes `g_j` from current-parameter SVD modes, a discrete sign partition, and black-box simulator responses without any proposed-update input. Literal differentiation with respect to the tentative update gives `c_j=0`, making every `g_j>0` constraint infeasible; supplying a finite-difference estimator or differentiable surrogate would redesign the mechanism.
- `anti_pattern_check.matched_pattern_id = audit_decomp_prior` with `mitigation_substantively_delivered = false`: the `heterogeneous_decomposition + structural_prior_encoding` composition lacks separate decomposition-only and prior-only arms. The required mitigation was an isolated-leg ablation showing a clear differential effect and a theoretically distinct property for the prior.

## Attempt 2: `attempt_2/phase3_critique/phase3_critique_output.json`

**Verdict:** `abandon` (`hard_floor`)

**Verdict rationale (verbatim):**

> gap_closure_reject_check.entries[0].reject_lessons_evaluated[4].lesson_quoted is triggered because WitnessCS is a generic randomized paired A/B, importance-weighted, anytime safe-policy-improvement gate wrapped around VLA-WAM rather than a distinct scientific mechanism. paper_pointed_threat.subsumption_argument identifies PACE as exact central-mechanism overlap, and blocking_findings_disposition[0] upholds that the stated certificate cannot accept even a perfect candidate within B_k=128. A power-restoring bound would replace the load-bearing test and is therefore a redesign, so advance and Phase 3.3 revision are both invalid.

**Triggering checks:**

- `gap_closure_reject_check.verdict = triggered`: “Pairing a single-task or small-sample instrument with broad capability claims triggers a scope-mismatch rejection, and assembling retrieval or engineering blocks without an isolating scientific insight reads as application rather than research.” The audit found WitnessCS to be an assembly of standard randomized paired evaluation, propensity weighting, a confidence-sequence acceptor, and rollback rather than a distinct learning or statistical mechanism.
- `paper_pointed_threat.addressable_via = unaddressable`: `semanticscholar:8289d4818261220bbf0df1665c99324a52684189` (PACE) already uses paired candidate/incumbent instances, anytime-valid sequential evidence, and evidence-gated commit for self-evolving agents. Importance correction and atomic VLA/WAM checkpoint commit are wrappers around that same central acceptor rather than a new mechanism.
- `blocking_findings_disposition[0].status = upheld`: for the admissible one-task `q=p=1` case at `k=1`, `t=128`, `alpha=0.05`, and `epsilon=0.2`, the stated radius is about `2.2879`, so even mean `X=1` gives `L≈-1.2879`; at `epsilon=0.4` the radius is still about `1.144`. Restoring positive-decision power requires replacing the load-bearing bound or materially changing the witness budget.

## User-side options

1. **Drop direction.** Stop work on anchor-separated co-adaptation and retain this record as the terminal evidence trail.
2. **Change framing.** Recast the contribution away from a novel co-adaptation mechanism—for example as a scoped diagnostic or application-grade evaluation study—and restart the bottleneck and claim analysis under that narrower framing.
3. **Re-run with a different direction.** Start a fresh IdeaSpark run with a different anchor problem and mechanism family; do not reuse any of these three terminal mechanisms as the candidate core.

The current framing is exhausted: ExitReplay, the projected residual-alignment update, and WitnessCS all remain terminal.
