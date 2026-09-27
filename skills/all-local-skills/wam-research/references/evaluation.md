# World-model evaluation and claim audit

## Contents

1. Evaluation layers
2. Metrics
3. Statistical protocol
4. Distribution-shift audit
5. Claim ladder

## Evaluation layers

Evaluate all applicable layers independently.

| Layer | Question | Evidence examples |
|---|---|---|
| Prediction | Does the model predict held-out futures? | horizon curves, state/contact/reward errors |
| Causality/control | Do action changes produce correct changes? | counterfactual tests, ranking accuracy |
| Calibration | Does confidence match correctness? | ECE/Brier/NLL, risk-coverage curves |
| Decision | Does using the model select better actions? | top-k regret, planning return |
| Policy | Does the learned policy improve? | success/return, robustness, sample efficiency |
| Transfer | Does it survive domain/embodiment shift? | held-out tasks, cameras, objects, real robot |

## Metrics

### Common

- success and return with confidence intervals;
- failure taxonomy and per-task results;
- inference latency, throughput, memory, and control frequency;
- data, environment-interaction, and compute budgets.

### Video-specific

- visual metrics such as FVD/LPIPS/PSNR/SSIM only as descriptive evidence;
- object pose, contact, gripper, geometry, and task-event accuracy;
- temporal consistency and horizon-conditioned degradation;
- action sensitivity and counterfactual correctness.

### Latent/state-specific

- multi-step state/latent, reward, value, continuation, and termination errors;
- task-relevant probe accuracy;
- uncertainty and out-of-distribution detection;
- planning consistency and downstream control.

### Model-based RL-specific

- imagined versus environment return gap;
- rank correlation and top-k regret;
- exploitation rate and tail failures;
- performance versus rollout horizon;
- environment interactions to threshold performance.

## Statistical protocol

- Predeclare the primary metric and aggregation unit.
- Use at least three independent training seeds for stochastic training when feasible; use more evaluation episodes than training seeds.
- Pair tasks, initial states, and random seeds across policies when the environment allows it.
- Report interval estimates and per-task distributions, not only a grand mean.
- Correct or label exploratory claims when many variants are searched.
- Keep checkpoint selection rules identical and fixed before final evaluation.
- Report all planned exclusions and failed runs.

## Distribution-shift audit

Evaluate the world model on:

1. behavior/data-collection policy trajectories;
2. initial policy trajectories;
3. intermediate policy trajectories;
4. final optimized policy trajectories;
5. deliberately perturbed or adversarial action sequences.

A model accurate only on the behavior-policy distribution is insufficient evidence for imagination-based policy optimization.

## Claim-specific evidence

Select required evidence for the actual claim; prediction, policy and transfer
are not a mandatory monotonic ladder. Better task control can coexist with worse
pixel reconstruction. Report that tradeoff explicitly.

| Claim | Required evidence |
|---|---|
| Better prediction | held-out target-specific, horizon-specific prediction evaluation |
| Better action conditioning | action interventions, independent targets and controls |
| Better closed-loop control | environment success/return, uncertainty, matched budgets |
| Gain caused by mechanism M | intervention/ablation of M and confound controls |
| Better robustness | declared shifts with held-out evaluation |
| Better real transfer | corresponding real-robot evidence and comparison |

Scope every claim to the tasks, embodiments and budgets actually tested.

## Statistical decision contract

Before a confirmatory run specify estimand, population, independent training unit,
evaluation unit, pairing keys, task weighting, minimum meaningful effect,
checkpoint selection, interval method and stopping rule. Episodes nested in one
trained policy are not independent training replicates. Use paired task/start
comparisons where possible and an analysis respecting run/task clustering.
The number of seeds is a resource/design choice, not proof of adequate power.

Distinguish supported, refuted (including ruled-out meaningful benefit), and
inconclusive. A wide interval is not proof of no effect. Label exploratory changes
and confirm them separately; do not tune on final held-out outcomes. Budget stops
may yield an honest incomplete/inconclusive dossier.
