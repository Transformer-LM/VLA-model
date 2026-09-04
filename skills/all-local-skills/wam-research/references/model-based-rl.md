# Model-based RL with embodied world models

## Use this route

Use when learned dynamics generate transitions for planning, value estimation, candidate ranking, synthetic replay, or policy optimization.

## Regimes

### Offline imagination

Train the world model on a fixed dataset and optimize a policy without new environment data. Primary risks are coverage, extrapolation, and policy exploitation.

### Online model-based learning

Alternate real/simulated data collection, world-model updates, and policy updates. Account separately for environment interactions, model updates, and policy compute.

### Frozen world-model RL

Optimize a policy against a fixed model. Evaluate the final policy on both the model's training distribution and the shifted policy distribution.

### Co-evolution

Update policy and world model over time. Specify the update schedule, replay mixture, lag, target distributions, and stability controls.

## Model-error controls

- uncertainty ensemble or calibrated predictive distribution;
- rollout-horizon truncation;
- uncertainty or disagreement penalty;
- conservative reward/value estimates;
- real-state or keyframe reinitialization;
- masked or filtered policy updates on unreliable transitions;
- periodic environment validation and policy-distribution refresh;
- holdout trajectories from policies not used to fit the model.

## Minimum comparisons

- supervised/imitation policy before RL;
- model-free RL with matched real/simulator interactions;
- world-model RL without the proposed reliability mechanism;
- oracle simulator RL when available;
- frozen versus updated world model when co-evolution is claimed;
- several imagination horizons.

## Exploitation audit

1. Find trajectories with high imagined return and low environment return.
2. Cluster discrepancies by contact, occlusion, object state, gripper state, and horizon.
3. Test whether uncertainty identifies the failures.
4. Re-evaluate after each major policy update.
5. Report maximum and tail exploitation, not only the mean correlation.

## Accounting

Report real transitions, simulator transitions, imagined transitions, world-model training FLOPs/time, policy training FLOPs/time, and total wall-clock. Do not call a method more sample-efficient when it only shifts uncounted cost to offline data or simulator generation.
