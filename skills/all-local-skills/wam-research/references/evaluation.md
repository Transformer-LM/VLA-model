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

## Claim ladder

Use the strongest claim supported by all lower levels:

1. improves predictive metric;
2. improves action-conditioned or task-state prediction;
3. improves candidate ranking or planning in model;
4. improves policy in held-out simulator tasks;
5. improves robustness under distribution shift;
6. improves real-robot performance.

Do not jump levels. State the missing evidence needed for the next level.
