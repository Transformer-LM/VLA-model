# Video-generative WAM route

## Use this route

Use when the model predicts decoded frames or video latents, jointly predicts video and actions, generates visual subgoals, or acts as an action-conditioned video simulator.

## Research roles

| Role | Interface | Critical evidence |
|---|---|---|
| Visual planner | language/current view to future frames | goal reachability and action recovery |
| Action-conditioned simulator | observation + candidate actions to future video | counterfactual action sensitivity and rollout calibration |
| Candidate ranker | several action rollouts to score | ranking accuracy and policy improvement |
| Joint WAM | coupled video/action generation | contribution of coupling versus shared scale/data |
| RL environment | policy actions to imagined transitions/rewards | exploitation resistance and real/sim agreement |

## Minimum baselines

- the same policy without the video world model;
- a frozen pretrained video model without the proposed adaptation;
- an action-agnostic video predictor where relevant;
- a shorter-horizon or one-step predictor;
- a physics simulator or real-environment oracle when available;
- a matched-capacity latent/state world model when the claim concerns visual generation.

## Required diagnostics

- shuffle, zero, and counterfactual action tests;
- multi-step drift by horizon, not only an aggregate score;
- task-state/contact/event accuracy in addition to visual quality;
- reward/success calibration on held-out policy distributions;
- correlation between imagined ranking and real/environment ranking;
- adversarial search for actions that look successful only in the model;
- evaluation under policy shift after RL updates;
- latency, memory, and generated frames per control decision.

## Common invalid conclusions

- Better FVD implies better manipulation.
- Visually plausible video is causally sensitive to action.
- Higher imagined success proves real success.
- A video model trained on policy rollouts generalizes to a newly optimized policy.
- Improvement from more video data proves the architectural contribution.

## Useful experiment

Use the same candidate action sets across world models. Measure pairwise ranking accuracy against simulator or real outcomes, calibration error, top-k regret, rollout latency, and downstream closed-loop success. This isolates decision usefulness from video aesthetics.
