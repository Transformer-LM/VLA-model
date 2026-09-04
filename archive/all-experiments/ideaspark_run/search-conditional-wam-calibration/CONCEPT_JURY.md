# CONCEPT JURY — Search-Conditional WAM Calibration (SCWC)

**Date:** 2026-08-31  
**Review stance:** independent, skeptical, mechanism-first  
**Experiments run:** none  
**Decision:** **NO-GO as a new-method paper**

## Bottom line

SCWC targets a real and scientifically natural failure: best-of-`N` or MPC search changes the action distribution from “ordinary WAM queries” to “actions selected partly because their WAM errors are favorable.” Calibration must therefore be evaluated on the output distribution of the complete search procedure, not on marginal candidates.

The proposed correction is nevertheless not novel enough for the stated gate. [Confidence on the Focal / JOMI](https://arxiv.org/abs/2403.03868) already develops finite-sample conformal coverage conditional on a data-dependent selection event, explicitly including top-`K` and optimization-based selection. Applying that principle to WAM-selected action chunks, with search budget and support as contexts, is a compelling robotics audit and perhaps a useful systems wrapper; it is not presently an irreducible statistical mechanism. Combined with [DreamSteer](https://arxiv.org/abs/2607.02865), which supplies the exact frozen-VLA → WAM-rollout → value-argmax interface, and [Imperfect World Models are Exploitable](https://arxiv.org/abs/2605.15960), which supplies the exploitation phenomenon, the remaining contribution is primarily application and evaluation.

## Scores

| Dimension | Score / interval | Assessment |
|---|---:|---|
| Scientific naturalness | **8.7/10** | Correctly evaluates the WAM on the distribution induced by its actual decision use. |
| Problem importance | **8.1/10** | More test-time compute becoming less reliable is consequential for WAM-guided VLA deployment. |
| Feasibility | **8.2/10** | Frozen π0.5/WAM and cached candidate rollouts fit comfortably within 4×A100; simulator-label volume, not GPU capacity, is the limiting resource. |
| Novelty | **5.8–6.8/10** | Strong domain-specific delta, but selection-conditional conformal inference already covers the load-bearing statistical move. |

The novelty lower bound is not above 7.0, so the requested GO condition is not met.

## WAM route card

```yaml
representation: R3 task-progress latent or R4 explicit progress/failure prediction
control_use: U3 candidate-action evaluation; optionally U4 MPC
observations: [RGB, proprioception, language, action history]
prediction_targets: [future task progress, failure risk]
action_interface: conditioned
rollout_horizon: planner-specific and fixed within each calibration regime
policy: frozen pi0.5
world_model_update: frozen
data_regime: held-out simulator calibration plus deployment inference
primary_claim: selection-adjusted bounds control risk of the search-selected action across budgets
main_failure_mode: post-selection undercoverage and distribution shift of high-scoring winners
```

This is a natural U3/U4 reliability layer, not a new WAM representation.

## Decomposed novelty claim

- **Problem framing:** WAM calibration after a frozen VLA/planner selects the apparent best action from `N` candidates or an MPC search.
- **Core mechanism:** replay the complete selector on held-out states, then fit cross-fitted one-sided conformal bounds conditional on search budget and action support; use the bound to accept, rerank, shrink search, or fall back.
- **Key insight:** marginal candidate calibration is not preserved after optimizer selection; larger search exposes more positive WAM errors.
- **Application domain:** RGB/proprioceptive VLA manipulation with a frozen WAM, no tactile sensing.

## Strongest fatal overlap

**JOMI is the fatal mechanism-level overlap.** It begins from the same statistical observation—marginal conformal validity can fail for units chosen by a data-dependent process—and constructs prediction sets with coverage conditional on selection. Its framework permits arbitrary calibration-permutation-invariant selection rules and works out top-`K`, constrained, and optimization-based cases. It also notes that selecting only the largest predicted value turns inference into a tail problem with few effective calibration samples.

SCWC's budget/support bins do not escape this prior art:

1. If each calibration row is the winner produced by a fixed planner at budget `N`, ordinary split/Mondrian conformal on those winner rows already calibrates the *selected-output distribution* at that `N`.
2. If the claim is conditional on a candidate winning relative to the other candidates in the same set, JOMI's selection-reference construction is the more principled existing mechanism.
3. Cross-fitting protects against training/calibration reuse; it does not itself solve selection-conditional exchangeability, continuous support conditioning, simulator-to-real shift, or adaptive changes to the final selector.

Accordingly, “conditioning explicitly on the selection event” cannot be advertised as SCWC's new statistical idea.

## Exact differences from named neighborhoods

| Prior neighborhood | What it already owns | What SCWC adds | Jury assessment |
|---|---|---|---|
| Conservative model-based optimization / pessimistic offline MBRL | Penalize unsupported actions or optimize a lower-confidence/worst-case value before selection. | Empirically calibrate error *after the complete search operator* and expose risk as a function of `N`. | Useful evaluation delta, but not a fundamentally new form of conservatism. |
| Selection-conditional conformal inference / JOMI | Exact post-selection coverage for top-`K` and optimization-driven focal units. | WAM regret/failure as the outcome, VLA action support as a covariate, and budget adaptation as the controller response. | Application transfer; strongest novelty blocker. |
| Conformal planning / risk control | Wrap learned predictions or trajectories in calibrated sets and enforce risk/constraint thresholds. | Calibrate the action selected by a specified search procedure rather than every trajectory marginally. | Narrow, defensible distinction, but JOMI already supplies its statistical principle. |
| [When to Trust Imagination](https://arxiv.org/abs/2605.06222) | Future–reality consistency changes execution chunk length and replanning after physical observations arrive. | Pre-execution risk correction for optimizer-selected candidates and explicit search-budget pressure. | Clear difference; not a fatal overlap. |
| [Imperfect World Models are Exploitable](https://arxiv.org/abs/2605.15960) | Formal preference reversal, inevitability on large policy sets, and a safe planning horizon. | An empirical VLA best-of-`N` curve plus a frozen-model mitigation. | It blocks any general “search exploits imperfect WMs” novelty claim. |
| [DreamSteer](https://arxiv.org/abs/2607.02865) | Frozen VLA samples action chunks, frozen latent WAM imagines them, value model ranks them, and argmax is executed. | Audits and corrects winner reliability across candidate counts. | Exact application interface; SCWC is a reliability wrapper around it. |
| Uncertainty-aware / robust MPC | Propagate epistemic/aleatoric uncertainty, tighten constraints, shorten horizon, or optimize robust objectives. | Treat search budget itself as selection pressure and validate conditional coverage of the selected action. | Distinct diagnostic, but the deployment response—pessimize, shrink horizon, fallback—is standard. |

## Additional logical blockers

### 1. The target quantity is underspecified

“Real regret” and “failure risk” are not interchangeable nonconformity scores. If the bound is on optimism

`e = predicted_gain − realized_gain`,

then accepting only when `predicted_gain − qα > baseline_gain` can support a lower-bound decision. If the score is regret relative to the oracle best real candidate, comparing predicted gain with that bound does not yield the stated safety decision. SCWC must choose one target and derive the accept rule from it.

### 2. Calibration must include the final composite selector

The proposal first calibrates the winner of a search, then uses the bound to accept/**rerank**, shrink `N`, or fall back. Those responses define a new adaptive selection rule. A guarantee calibrated only on the original argmax does not automatically survive the second selection. The held-out replay must execute the entire final pipeline, including tie-breaking, fallback, and adaptive budget choice. Once done, the method is even more directly an application of post-selection conformal inference.

### 3. Coverage does not imply monotonic task performance

A one-sided coverage statement can control the frequency with which realized gain falls below a bound. It does not by itself prove that task success cannot decrease as `N` grows. A no-degradation claim additionally needs either a valid lower bound on improvement relative to the exact fallback action and a composite decision guarantee, or must remain an empirical claim. False acceptance, conservative rejection, and multi-step state-distribution shift can all break monotonic performance while nominal one-step coverage holds.

### 4. Simulator calibration has no automatic deployment guarantee

Exchangeability is required. Held-out simulator states do not make real deployment winners exchangeable when contacts, camera observations, object physics, or the VLA proposal distribution shift. “Global conformal” and “selection-adjusted conformal” are both invalid under an unhandled sim-to-real shift. The first defensible claim is therefore simulator-conditional, not general robot risk control.

### 5. Large budgets create a tail-sample problem

At large `N`, the winner lies deeper in the optimistic tail and support strata become sparse. Fine `N × support × task/horizon` conditioning can yield unstable or vacuous bounds. Pooling across regimes recovers sample size by imposing a model, but weakens distribution-free conditional validity. Four A100s do not solve this label-efficiency problem.

## Cheapest non-GPU falsifier

Use a **cached candidate table**, not new VLA or WAM inference. Each simulator snapshot needs at least 16–32 previously generated candidates with: WAM predicted gain, action-support score, and realized short-horizon progress/failure. On CPU:

1. Form nested best-of-`N` selections for `N ∈ {1,2,4,8,16}` by subsampling the cached rows; bootstrap by independent snapshot, never by correlated candidate.
2. Measure selected optimism, true improvement over the first/base VLA action, and miscoverage of a global conformal bound.
3. Compare predeclared `N/support` Mondrian SCWC against (a) ordinary ensemble/support LCB and (b) a JOMI/top-`K` selection-conditional implementation using the same labels.
4. Recalibrate and evaluate the **complete** accept/rerank/fallback rule, not the pre-filter argmax.

Kill SCWC as a method if any one holds:

- selected optimism or failure does not worsen materially with increasing `N` on independent snapshots;
- marginal/Mondrian calibration is already within 3 percentage points of nominal selected-action coverage at every `N`;
- JOMI or a support-aware LCB matches SCWC within 2 points of coverage and selected real gain at the same fallback rate;
- nominal coverage fails by more than 3 points after the final accept/rerank/fallback rule is applied;
- the bound becomes vacuous for the budgets where exploitation is largest.

This is an oracle/statistical kill test and needs no GPU training. It tests both whether the motivating phenomenon exists and whether SCWC contributes beyond the strongest prior mechanism.

## Feasibility audit

- **Compute:** favorable. Frozen π0.5 and WAM scoring/caching are feasible on 4×A100; conformal fitting is CPU-scale.
- **Implementation:** moderate. The planner must be deterministic or log all random seeds, candidate identities, scores, horizons, support features, and final selection events. Cross-fitting must be split by simulator state/task lineage, not candidate row.
- **Data:** the real bottleneck. Ground-truth regret requires executing every cached candidate or otherwise obtaining oracle progress, and large-`N` tail conditioning needs many independent states.
- **Modalities:** RGB and proprioception suffice; tactile absence is not a conceptual blocker because the target is selector calibration, though hidden contact failures limit label fidelity.
- **Claim ceiling:** simulator best-of-`N` risk control for a fixed VLA/WAM/planner pair. Cross-task, cross-planner, MPC, or real-robot guarantees require fresh exchangeability evidence.

## Scoop comparison verdict

**Level 2 — High Overlap.** Against JOMI, SCWC matches the problem insight, the core post-selection conformal mechanism, and the key exchangeability argument; the main differing axis is the robotic WAM application. DreamSteer matches the VLA/WAM search interface but lacks calibration. Imperfect World Models are Exploitable matches the problem phenomenon and model-based planning domain but uses a different formal mechanism. No single robotics paper reviewed here implements the exact wrapper, but the conjunction leaves less than a >7 novelty lower bound.

**Delta, stated at its defensible ceiling:** Unlike JOMI, which gives general selection-conditional prediction sets for top-`K` and optimization-selected tabular units, SCWC applies post-selection calibration to the regret of WAM-ranked VLA action chunks and exposes how reliability changes with search budget, enabling a calibrated fallback to the base VLA.

That is a useful application delta, not yet a new-method delta.

## Evidence map

- **Confidence on the Focal: Conformal Prediction with Selection-Conditional Coverage** (Jin & Ren, JRSS-B 2025 / arXiv:2403.03868): direct mechanism collision; full HTML method and appendices checked. It explicitly covers top-`K`, optimization-based selection, sample splitting, and the small-reference-set problem in the selected tail.
- **DreamSteer** (arXiv:2607.02865): exact VLA/WAM best-of-`N` interface; full HTML method, experiments, and limitations checked. It uses fixed deployment models and reports ranking failures, but not selection-adjusted calibration.
- **Imperfect World Models are Exploitable** (arXiv:2605.15960): local full-text extraction checked. It formalizes model-induced preference reversal and large-policy-set exploitability.
- **When to Trust Imagination** (arXiv:2605.06222): future–reality verification and adaptive execution; different timing and control variable.
- **Conformal Autoregressive Generation: Beam Search with Coverage Guarantees** (AAAI 2024 / arXiv:2309.03797): conformal calibration can be coupled to a search width; different output and guarantee, but further reduces the novelty of treating search budget as a conformal control variable.

The automated multi-source search returned 61 deduplicated records but was noisy; arXiv failed with SSL EOF for all three queries, OpenAlex had HTTP 504 retries, and Semantic Scholar had HTTP 429 retries. The decisive papers above were verified through primary arXiv/AAAI/JRSS-B pages and existing local full-text extracts. This is a strong provisional overlap assessment, not proof that no 2026 paper is missing.

## Final recommendation

**NO-GO.** Do not invest in SCWC as the next core-method candidate under a novelty-lower-bound-above-7 rule. If retained at all, frame it as a compact empirical/audit study of the WAM search scaling curve, implement JOMI or an equally strong selection-conditional baseline rather than renaming conditional quantiles, and limit the contribution claim to the VLA/WAM interface. The non-GPU cached-table falsifier should decide whether even that study has headroom.
