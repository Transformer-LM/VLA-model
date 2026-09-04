# WAM and world-model taxonomy

## Contents

1. Two-axis classification
2. Representation axis
3. Usage axis
4. Route card
5. Comparison rules

## Two-axis classification

Classify a method independently by representation and usage. Terms in the literature are inconsistent; prefer operational descriptions over names.

| Axis | Question | Typical values |
|---|---|---|
| Observation | What enters the model? | RGB, RGB-D, proprioception, language, history |
| Prediction | What is predicted? | decoded frames, video latents, task latents, states, rewards, termination |
| Action interface | How do actions enter or leave? | conditioned input, jointly denoised action, inverse dynamics, latent action |
| Dynamics | How is time modeled? | autoregressive, diffusion/flow, RSSM, transformer, ensemble |
| Control use | How does the policy consume predictions? | representation only, reranking, MPC, imagined RL, joint policy |
| Update regime | What changes during policy learning? | frozen WM, alternating updates, joint training, co-evolution |
| Data regime | Where do transitions come from? | fixed offline, simulator, online real, mixed |

## Representation axis

### R1. Decoded video/pixel prediction

Predict future observable frames. Strong interpretability; expensive rollouts and pixel-level nuisance variation.

### R2. Pixel-latent video prediction

Predict compressed visual tokens or VAE latents, often with diffusion or flow objectives. It is still video-generative when decoded video is the semantic prediction target.

### R3. Task-centric latent dynamics

Predict compact features optimized for reward, value, controllability, or reconstruction. Photorealistic decoding may be absent or auxiliary.

### R4. Explicit state/dynamics model

Predict robot/object state, reward, contact, or termination. Useful when state is observable or privileged during training.

## Usage axis

### U1. Representation pretraining

Use the world model to initialize features; no rollout-based control claim.

### U2. Goal or trajectory proposal

Generate future observations/keyframes, then recover actions with inverse dynamics or a goal-conditioned policy.

### U3. Candidate-action evaluation

Roll out candidate actions and rank them using reward, value, success, or constraint predictions.

### U4. MPC/planning

Optimize action sequences through repeated learned-model rollout and replan from new observations.

### U5. Imagination-based policy optimization

Treat learned dynamics as an environment for actor-critic, PPO/GRPO, or another policy update.

### U6. Joint world-action policy

Predict video/state and actions in one coupled model, or share representations and objectives between policy and dynamics.

## Route card

Fill every field; use `unknown` rather than guessing.

```yaml
representation: R1|R2|R3|R4
control_use: U1|U2|U3|U4|U5|U6
observations: []
prediction_targets: []
action_interface: conditioned|joint|inverse-dynamics|latent-action|other
rollout_horizon: null
policy: null
world_model_update: frozen|alternating|joint|coevolution
data_regime: offline|simulator|online-real|mixed
primary_claim: null
main_failure_mode: null
```

## Comparison rules

- Compare methods with the same task interface before attributing effects to architecture.
- Separate representation quality from the control algorithm using cross-combinations where feasible.
- Separate world-model improvement from extra data or interaction.
- Treat model-based RL as a usage pattern, not a representation family.
- Label privileged-state models explicitly; do not compare them directly with vision-only models without qualification.
- Report action horizon, observation history, replanning frequency, and execution chunking.
