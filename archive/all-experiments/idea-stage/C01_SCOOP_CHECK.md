# C01 Scoop Check

**Verdict:** `Level 2 — High Overlap / PARTIAL`  
**Reviewer route:** fresh `gpt-5.6-sol`, same-family provisional  
**Raw trace:** `.aris/traces/idea-discovery/2026-08-07_run01/002-c01-scoop-check.response.md`

## Defensible delta

No checked work contains the full budget-matched `future/equidistant-past × intact/distribution-preserving shuffled action` training matrix with a factorial interaction measured on both representation diagnostics and paired VLA closed-loop control.

The closest work is [CheckVLA](https://arxiv.org/abs/2607.26789), which compares aligned and action-shuffled execution verifiers but does not shape a VLA representation, include a past outcome, or estimate the full interaction. VLAFlow supplies a controlled-objective and marginal-preserving shuffle precedent; SelfWAM, AquaJEPA, dWorldEval, CoCo, and Hallucination in World Models occupy most action-sensitivity/counterfactual components.

Therefore C01 can claim only a **diagnostic negative-control protocol**. It cannot claim a new predictive objective, action conditioning, JEPA/WAM, or causal mediation.

## Required terminology repair

- Rename the statistic `2×2 factorial interaction contrast`, not classical DiD.
- Rename the action factor `intact vs shuffled`, not `correct vs shuffled`, because no action can cause a past outcome.
- Treat the past cell as a negative-control outcome under an explicit assumption, not a valid reverse world model.

## Main threats

1. Past and future targets have unequal conditional entropy/Bayes risk even when distance, variance, tokens, and FLOPs match.
2. Action shuffling may create conditional-support violations and contradictory supervision, so a positive interaction may be driven by uniquely harming the shuffled cell.
3. Past observations may leak through the policy history; any such leakage kills the design.
4. A factorial interaction does not prove the learned representation mediates control; C03-like intervention would be accessory evidence only.
5. One training seed per cell is a pilot, not an inferential result.

## Minimum controls now required

- Add action-only, dummy/noise-target, and no-action predictor controls.
- Use derangement within task × instruction × phase × proprioception × speed/action-norm × chunk-mask support; report support distance.
- Freeze one target encoder; audit target variance, current-target similarity, initial/final auxiliary loss, gradient norm/variance, and action-agnostic Bayes proxy.
- Require the future-intact predictor to beat persistence, observation-only, and action-agnostic models on strict holdout and show action-shuffle sensitivity.
- Use common initial states/random numbers for closed-loop evaluation; training seed, not rollout, is the replication unit.
- Use at least 3–5 independent training seeds for any substantive interaction claim.

## Decision

`REVISE / NO-RUN` remains in force. C01 survives deep novelty only as a narrow diagnostic, and its enlarged control/seed package must be shown feasible under 8 GPUh before implementation.

