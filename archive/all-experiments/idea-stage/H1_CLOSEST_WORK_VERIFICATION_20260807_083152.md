# H1 Closest-Work Primary-Source Verification

## Outcome

Five new load-bearing neighbors were checked against primary arXiv full text by a fresh same-family reviewer and independently re-opened by the local executor. None is a complete precedent for a world objective that directly shapes shared VLA parameters, but each occupies a key component.

| Work | Verified intervention | Where applied | Downstream use | Safe H1 boundary |
|---|---|---|---|---|
| CheckVLA | retrained action-shuffled world model preserving action-token marginals; retrained observation-only control | separate frozen verifier | execution-time detection and suffix repair | no predictive gradient enters the VLA |
| dWorldEval | test-batch derangement with `pi(i) != i`; probabilistic action swapping | inference-time world-model input | imagined policy evaluation/ranking | no retraining or policy shaping |
| Hallucination in World Models | one-step teacher-forced action-shuffle ratio; repeated-last-frame rollout baseline | world-model evaluation | CEM MPC | no shared VLA or policy auxiliary |
| CoCo | reference/inverse/zero/mirror structured counterfactual losses | standalone world-model training | CEM planning and MBPO | no shuffle and no VLA representation update |
| VLAFlow | batch-shuffled language targets; future-latent branch cannot read noisy actions | shared VLA pretraining/fine-tuning | closed-loop transfer | occupies generic future-latent shaping, but not action-conditioned future prediction |

## Corrections frozen for later use

- dWorldEval has the strictest verified action derangement, but it is purely test-time and not phase/state support matched.
- Hallucination uses a persistence baseline and action shuffle, but the former is a static rollout comparator and the latter is a one-step diagnostic; neither is a capacity-matched learned action-agnostic model.
- CoCo uses structured counterfactual interventions, not shuffled actions; inverse and zero-action assumptions do not automatically hold for irreversible contact dynamics.
- VLAFlow’s shuffle ablation concerns action-derived language targets, not future actions. Its future-latent predictor is structurally observation/language conditioned because latent queries cannot attend noisy action tokens.
- CheckVLA is the strongest training-time shuffled-action neighbor, but its world model is an independent execution verifier. It cannot support a claim about predictive objectives shaping policy representation.

## Consequence for cycle 2

The generic H1 statement “future latent prediction improves VLA representation” is occupied by VLAFlow and multiple WAM/VLA works. A revised method must change the causal path by which action information enters the predictive objective, or produce a genuinely new matched identification result. It cannot rely on the mere presence of a future head, action shuffle, or action conditioning.

Full reviewer evidence with sections, tables, and overclaim boundaries: `.aris/traces/idea-discovery/2026-08-07_run01/005-closest-work-fact-check.response.md`.
