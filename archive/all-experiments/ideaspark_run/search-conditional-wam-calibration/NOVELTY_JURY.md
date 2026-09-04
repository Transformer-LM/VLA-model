# Strict Novelty Jury — Search-Conditional WAM Calibration (SCWC)

**Audit date:** 2026-08-31  
**Literature horizon:** through 2026-08  
**Gate:** novelty must be **strictly greater than 7.0**; 7.0 is a failure  
**Verdict:** **FAIL**  
**Novelty:** **6.9 / 10**  
**Naturalness:** **8.6 / 10**  
**Feasibility:** **7.8 / 10** for a fixed, registered simulator/search family; substantially lower for real-robot conditional guarantees  
**Scoop level:** **Level 2 — high component/mechanism overlap, no verified paper containing the whole WAM-specific package**

## Executive judgment

SCWC identifies a real and well-posed failure mode: maximizing an imperfect WAM score over more candidates can increase the winner's positive model error even when ordinary candidates appear calibrated. A WAM-search amplification curve would be useful evidence, especially for DreamSteer-style deployment steering.

The stated method, however, does not clear the strict novelty gate. Its three steps have a direct decomposition into known mechanisms:

1. **Search exploits model error:** the optimizer's curse and world-model exploitation.
2. **Calibrate the selected output of a procedure:** conformal risk control and post-selection conformal inference.
3. **Penalize uncertain gains or fall back:** pessimistic model-based optimization, selective prediction, and uncertainty-aware MPC.

Most importantly, if each calibration and test example runs the **same complete search procedure** and emits one selected action, then the searcher can be treated as part of the prediction algorithm. Split conformal/CRC applied to the final selected output already accounts for the search's internal selection under exchangeability. Conditioning by a registered budget and coarse support bin is then a standard grouped/Mondrian-style application unless SCWC contributes a genuinely new guarantee for adaptive changes of budget, depth, or support.

Thus the residual novelty is primarily a compelling **VLA×WAM empirical diagnosis and evaluation protocol**, not yet a >7.0 algorithmic contribution.

## Exact claim decomposition

| Proposed component | Closest established mechanism | Jury assessment |
|---|---|---|
| Replay identical VLA/WAM search at increasing budgets and measure the selected action's optimism, true regret, failure, support, and selection pressure | Optimizer's curse; world-model exploitation; search-over-model-error evaluations | Useful WAM-specific audit, but the causal/statistical mechanism is known |
| Cross-fitted risk bound conditional on budget/support/selection | Conformal Risk Control; selective/post-selection conformal prediction; group-conditional or weighted conformal calibration | Directly overlapping unless a new simultaneous/adaptive-search theorem is supplied |
| Risk-adjust selected gain, reduce budget, or fall back to base VLA | Pessimistic model-based optimization, lower-confidence-bound selection, selective prediction, uncertainty-aware MPC | Standard intervention once a risk bound exists |
| Require selected-action risk control and no degradation as search grows | Risk control is plausible at registered fixed budgets; monotonic task performance does not follow from marginal CRC | The latter is an empirical target, not an automatic guarantee |

## Strongest prior-art chain

There is no verified single paper with precisely the complete SCWC implementation. That absence is not sufficient for novelty because the proposed composition follows the natural solution path of the following exact neighbors.

### 1. Problem mechanism: model exploitation and optimizer's curse

- [Imperfect World Models are Exploitable](https://arxiv.org/abs/2605.15960) formalizes ranking reversal between a learned world model and the true environment over policies, and argues that exploitation becomes difficult to avoid as the policy set grows. This is the closest statement of SCWC's core failure mode.
- [Optimizer's Information Criterion](https://arxiv.org/abs/2306.10081) studies optimistic bias induced when an optimizer chooses a decision using an estimated objective. SCWC's selected WAM score minus true progress is a robotics instance of this optimizer's curse.
- Pessimistic model-based offline RL already responds to model exploitation with uncertainty penalties, support restrictions, or shortened imagined rollouts; representative mechanisms include [Pessimistic Model-based Offline RL under Partial Coverage](https://arxiv.org/abs/2107.06226) and [Uncertainty-driven Trajectory Truncation](https://arxiv.org/abs/2304.04660).

### 2. Domain/search carrier

- [DREAMSTEER](https://arxiv.org/abs/2607.02865) samples VLA action chunks or primitives, rolls them out in a latent world model, and ranks the imagined outcomes. It supplies almost exactly the search procedure that SCWC proposes to audit, although it does not provide SCWC's post-search calibration.
- [When to Trust Imagination](https://arxiv.org/abs/2605.06222) uses future–reality consistency to adapt execution/replanning. It is execution-time verification, not pre-execution post-selection calibration, so it is not an exact scoop.
- [Do Robotic World Models Really Follow Actions?](https://arxiv.org/abs/2608.24885) diagnoses action-following failures of robotic world models away from expert actions. This strengthens the premise that searched candidates can expose WAM error, but does not calibrate a selected candidate.

### 3. Risk and post-selection calibration

- [Conformal Risk Control](https://arxiv.org/abs/2208.02814) provides distribution-free control of expected monotone losses. At a fixed registered budget, applying CRC to the **complete searcher's selected output** is a mandatory baseline and may already solve the claimed calibration problem.
- [CAP: Online Selective Conformal Prediction with FCR Control](https://arxiv.org/abs/2403.07728) explicitly constructs calibration after adaptive selection and supplies selection-conditional guarantees in its setting. The selection unit differs from internal planner best-of-N, but the statistical idea substantially overlaps SCWC's wording.
- [Conformal prediction after efficiency-oriented model selection](https://arxiv.org/abs/2408.07066) addresses validity after data-dependent model selection.
- [Optimized Conformal Selection](https://arxiv.org/abs/2411.17983) and [Multivariate Conformal Selection](https://arxiv.org/abs/2505.00917) provide additional evidence that calibration and candidate selection are already a developed statistical interface.
- [Optimal Model Selection for Conformalized Robust Optimization](https://arxiv.org/abs/2507.04716) connects model selection, decision risk, and conformalized robust optimization, including individualized conditional decision-risk considerations.

### 4. Conformal planning and policy evaluation

- [Forking Uncertainties: Reliable Prediction and MPC with Sequence Models via Conformal Risk Control](https://arxiv.org/abs/2310.10299) calibrates trajectory predictions with CRC and uses them inside MPC.
- [Distribution-Free Risk-Aware Planning and Control Using Conformal Spectral Risk Control](https://arxiv.org/abs/2606.04185) integrates conformal spectral-risk control into risk-aware MPC.
- [Safety Beyond Training Data: OOD MPC via Conformalized SLS](https://arxiv.org/abs/2602.12047) uses state/control-dependent conformalized model-error bounds for robust MPC.
- [Conformal Off-Policy Evaluation in Markov Decision Processes](https://arxiv.org/abs/2304.02574) and [Confident Off-Policy Evaluation and Selection through Self-Normalized Importance Weighting](https://arxiv.org/abs/2006.10460) cover calibrated or confidence-bound-based evaluation/selection of policies from logged data.

These works do not individually contain the SCWC robotics experiment, but together leave a narrow residual method claim.

## Closest exact mechanism

The closest exact **algorithmic baseline** is:

> For each registered search budget, regard DreamSteer/MPC plus its WAM scorer and argmax as one fixed predictor; on held-out contexts, calibrate the selected output's regret or failure loss with ordinary split CRC; at deployment, accept it only when its risk-adjusted gain exceeds the base VLA.

This baseline already contains the internal selection event because calibration observes the final output of the same stochastic search procedure. SCWC must outperform it in validity, efficiency, or adaptability. Merely naming the method “search-conditional” or adding budget/support as covariates is insufficient.

## Fatal reviewer objection

> “This is the optimizer's curse/model exploitation measured in a DreamSteer-style action search, followed by generic conformal risk control on the complete planner's output and a standard pessimistic fallback. Where is the new statistical or learning mechanism?”

That objection is currently valid.

## Why the claimed conditional guarantee is delicate

1. **Fixed versus adaptive search.** Calibration at each fixed budget does not automatically cover a deployment rule that chooses or shrinks the budget using the same calibration data. Simultaneous calibration or an outer/nested calibration layer is required.
2. **Conditional coverage.** Exact distribution-free per-state coverage conditional on continuous support density or a detailed selection event is generally not supplied by ordinary conformal methods. Coarse registered groups can give groupwise guarantees, but sparse bins weaken both validity and usefulness.
3. **Changing candidate distribution.** VLA sampling temperature, prompt, candidate generator, WAM checkpoint, search depth, and planner heuristics are part of the calibrated algorithm. Altering any of them can invalidate the guarantee.
4. **Counterfactual regret labels.** True regret requires simulator outcomes for the selected candidate and credible alternatives, not only the selected trajectory's success. This is available in a rollback-capable simulator but not automatically on a real robot.
5. **Support density is not truth.** A learned support score can be used as a conditioning covariate, but its own error is not removed by conformalization unless it is included in the full calibration protocol.
6. **Risk control is not monotonic utility.** A bound on failure or regret does not prove that task success is non-decreasing with search budget. A fallback can keep risk flat while erasing all additional search benefit.

## Coherent residual contribution and claim ceiling

The strongest defensible paper-shaped residual is:

> **At registered VLA×WAM search procedures and budgets, best-of-N/deeper search amplifies selected-action WAM optimism and real regret; calibrating the complete search output with budget/support-aware held-out simulator rollouts enables a risk-controlled accept-or-fallback policy.**

Permissible claims:

- first systematic VLA×WAM measurement of search-amplified WAM optimism, if a renewed exact search verifies that priority;
- fixed-procedure, fixed-budget marginal or groupwise selected-action risk control under stated exchangeability assumptions;
- improved risk–coverage or success–fallback tradeoff versus candidate-wise uncertainty, global pooled calibration, and uncalibrated search;
- empirical robustness across registered VLA/WAM/search combinations.

Claims that are **not** currently defensible:

- a new general conformal or post-selection inference method;
- distribution-free per-instance conditional control for arbitrary support values;
- validity under arbitrary adaptive search-budget changes;
- guaranteed non-decreasing task performance with increasing search budget;
- general real-robot regret control without counterfactual outcome labels;
- immunity to WAM exploitation outside the calibrated candidate/search distribution.

## What would be needed to exceed 7.0

At least one non-trivial residual must be made precise and validated, for example:

1. a simultaneous finite-sample risk guarantee over **nested, adaptively selected search budgets**, including the budget-selection rule;
2. a valid correction for search-generated, dependent candidate sets whose selection pressure varies across depth, with a demonstrable efficiency gain over calibrating each complete searcher separately;
3. an anytime rule that safely expands or stops search while preserving a pre-registered risk guarantee;
4. a WAM-specific observable enabling materially tighter valid bounds than generic full-pipeline CRC, with an ablation showing the gain is not merely extra calibration data.

Without one of these, the work should be presented as a benchmark/diagnostic plus a strong baseline rather than as a fundamentally new calibration algorithm.

## Feasibility

The simulator version is technically feasible with frozen VLA and WAM if rollback can evaluate candidate chunks. The expensive part is not conformal fitting; it is obtaining true outcomes for many candidates at many states and reproducing the exact stochastic search procedure. Four A100s help generate WAM scores but do not remove simulator rollout cost or counterfactual-label requirements.

Real-robot validation is materially harder because exhaustive candidate regret is unavailable. A real system can test selected-action failure and fallback, but should not claim exact true-regret calibration unless the counterfactual ground truth is separately established.

## E0 decision

**AUTHORIZED: a non-GPU search-amplification premise audit only.**  
**NOT AUTHORIZED: full SCWC method training or a paper-level novelty claim.**

The audit is genuinely non-GPU only if held-out states already contain cached VLA candidate actions, WAM scores, and simulator truth/rollback outcomes. If WAM inference or missing simulator rollouts must be generated, it is no longer a non-GPU audit.

### Minimal E0

1. For each held-out state, build one maximum candidate pool and evaluate every candidate in the WAM and rollback simulator.
2. Use nested prefixes of that same pool for `N = 1, 2, 4, 8, 16, 32`; this prevents changing candidate sets from confounding the effect of budget.
3. At each `N`, reproduce the exact deployed argmax/search rule and record:
   - selected WAM optimism: predicted progress minus true progress;
   - selected true regret relative to the best truly feasible candidate in the pool;
   - failure rate;
   - base-VLA and random-selection outcomes;
   - support density and ensemble uncertainty, if available.
4. Use paired state-level bootstrap intervals and a preregistered trend test against `log N`.
5. Include two mandatory controls: oracle true-score search, which tests whether useful search headroom exists, and candidate-wise uncertainty penalization, which tests whether SCWC's premise survives a standard pessimistic baseline.

### E0 kill criteria

Stop SCWC if any of the following occurs:

1. selected optimism, true regret, and failure do not show a reproducible adverse trend with budget/depth;
2. the effect disappears when candidate pools are nested and the same states are paired across budgets;
3. candidate-wise ensemble/support pessimism already removes amplification without sacrificing the oracle search gain;
4. a simple per-budget CRC baseline on the complete searcher's output controls risk as well as the proposed conditional construction;
5. oracle true-score search does not materially outperform the base VLA, meaning there is no useful search gain to preserve;
6. simulator counterfactual labels are unstable or the deployed candidate/search distribution cannot be reproduced.

## Final decision

SCWC is a **high-naturalness, worthwhile diagnostic direction**, and the non-GPU premise audit is justified. The current method is nevertheless a coherent recombination of model-exploitation analysis, post-selection/conformal risk control, and pessimistic fallback. Its strict novelty score is **6.9/10**, so it **FAILS** the required `> 7.0` gate and should not yet advance to GPU experimentation as the selected final idea.

## Search-integrity note

The jury used primary official arXiv records/full texts where available and did not interpret a missing search hit as evidence of nonexistence. During broad discovery, some third-party connectors returned SSL or rate-limit failures; those failures were treated only as retrieval limitations, not as novelty evidence. The conclusion above rests on the primary sources listed in the report.
