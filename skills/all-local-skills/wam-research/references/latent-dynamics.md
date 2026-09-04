# Latent-dynamics world-model route

## Use this route

Use when the predictive state is a task-centric latent, recurrent state-space state, learned feature, discrete token, or explicit compact state rather than a decoded video target.

## Design choices to record

- encoder and whether it is frozen, pretrained, or jointly optimized;
- deterministic and stochastic latent components;
- action, reward, value, continuation, and termination heads;
- one-step versus multi-step training loss;
- latent overshooting, consistency, contrastive, reconstruction, or value-aware objectives;
- imagination horizon and start-state distribution;
- actor/value gradients through the model;
- uncertainty representation and out-of-distribution detection.

## Minimum baselines

- model-free policy with the same encoder and data;
- reconstruction-oriented versus task/value-oriented latent;
- one-step dynamics versus multi-step objective;
- ground-truth state or privileged-state upper bound where permitted;
- no-imagination or reduced-horizon variant;
- matched-capacity recurrent/transformer dynamics baseline.

## Required diagnostics

- latent collapse and effective dimensionality;
- reward, value, termination, and contact prediction by horizon;
- open-loop error and closed-loop replanning performance;
- downstream success with encoder/dynamics cross-swaps;
- policy performance versus imagination horizon;
- sensitivity to start-state distribution and policy shift;
- sample efficiency measured with identical environment interactions;
- representational probes that correspond to the claimed mechanism.

## Common invalid conclusions

- Lower latent loss means better control without showing task relevance.
- A learned latent is better because it is smaller.
- Sample efficiency improved when offline pretraining data or simulator calls were not counted.
- Planning gains belong to the representation when the planner also changed.

## Disentangling representation and planner

When feasible, evaluate a small cross-product:

| | Planner A | Planner B |
|---|---:|---:|
| Latent model A | run | run |
| Latent model B | run | run |

Use this to distinguish a better dynamics representation from a better optimizer or actor update.
