# H1 WAM Route Cards

**Run:** `20260806-vla-wam-expanded-field-map`  
**Status:** route-family classification before concrete Idea selection  
**Scientific boundary:** the world objective may shape training representations; it does not plan, rerank actions, generate training trajectories, or remain required at deployment.

## Route family A — decoded or pixel-latent future co-training

```yaml
representation: [R1, R2]
control_use: [U1, U6]
observations: [third-person RGB, optional wrist RGB, proprioception, language]
prediction_targets: [future RGB, video latent, optical-flow or motion image]
action_interface: joint or conditioned
rollout_horizon: aligned to the action chunk; no recursive deployment rollout
policy: VLA with a continuous action/chunk head
world_model_update: joint during training; world output path removed at action-only inference
data_regime: fixed offline robot demonstrations
primary_claim: predictive visual co-training changes shared features and improves closed-loop action quality
main_failure_mode: pixel nuisance, extra-capacity/compute confounding, task-progress shortcut, negative transfer
```

**Occupied territory:** GR-1/2, UVA, WorldVLA, DUST, Fast-WAM, Motion Image Diffusion, SelfWAM, and DreamWAM already cover the basic construction. A new project cannot be justified by merely adding future RGB, motion, action conditioning, self-mask, geometry, or semantic prediction.

**Required controls:** action-only; same-shape dummy/static auxiliary; temporally wrong target; action-shuffled target where action enters; equal data, trainable parameters, target tokens, optimizer steps, and approximate FLOPs.

## Route family B — task-centric future-latent objective

```yaml
representation: R3
control_use: [U1, U6]
observations: [RGB, optional multi-view RGB, proprioception, language]
prediction_targets: [stop-gradient frozen-encoder future feature or feature residual]
action_interface: conditioned or joint
rollout_horizon: one chunk-aligned future target; no inference-time rollout
policy: VLA or language-conditioned visuomotor policy
world_model_update: frozen target encoder; lightweight predictor joint with selected policy modules
data_regime: fixed offline robot demonstrations
primary_claim: future-feature prediction shapes an action-useful shared latent without requiring pixel generation
main_failure_mode: latent leakage/collapse, temporal shortcut, predictor invalidity, auxiliary loss improving without policy transfer
```

**Occupied territory:** DynaMo, VPP, VLA-JEPA, JEPA-VLA, LiLa-WAM, and related latent WAMs cover the generic future-latent recipe. “Lightweight,” “frozen encoder,” “leakage-free,” or “head removed at inference” is not enough for novelty.

**Required controls:** current/static feature; past or time-reversed feature; target shuffle; equal-dimensional random projection; action-agnostic predictor; persistence and action-agnostic dynamics baselines; strict episode/temporal split.

## Route overlay C — matched causal identification

```yaml
representation: R1|R2|R3, fixed within an experiment
control_use: U1|U6
observations: identical across all cells
prediction_targets: [aligned future, matched noncausal/placebo targets]
action_interface: identical across all cells
rollout_horizon: fixed and chunk-aligned
policy: one fixed VLA checkpoint and PEFT interface
world_model_update: identical head and gradient route across cells
data_regime: one frozen offline split
primary_claim: only the action-causally aligned future treatment produces an incremental representation and policy effect
main_failure_mode: controls are detectably easier, compute is unmatched, or closed-loop effect is too small to distinguish
```

This is an experimental-identification overlay rather than a new representation family. Its contribution would have to be the causal evidence contract, not a new future head.

## Route overlay D — predictive-objective admissibility

```yaml
representation: R3
control_use: U1|U6
observations: [RGB, proprioception, language]
prediction_targets: [future latent or residual]
action_interface: conditioned
rollout_horizon: fixed short/chunk-aligned horizon
policy: fixed VLA with a small trainable action-side adapter
world_model_update: predictor validated separately; policy receives auxiliary gradients only under a predeclared gate
data_regime: fixed offline robot demonstrations with strict temporal holdout
primary_claim: world supervision should shape the policy only when it passes world-validity and action-transfer criteria
main_failure_mode: gate reduces to generic gradient surgery, overfits the validation stream, or never activates
```

This overlay is motivated by observed negative transfer. It remains only a candidate route: a novelty review must distinguish it from PCGrad/CAGrad, auxiliary-task weighting, and validation-based multi-task optimization.

## Cross-route evidence gates

1. **World/model gate:** the predictor must beat persistence and action-agnostic baselines on a strict temporal/episode holdout. Failing this gate prohibits nonzero policy auxiliary weight.
2. **Interface gate:** future observations and action chunks must be aligned by episode/step ID; no future information may enter the deployed policy input.
3. **Budget gate:** treatment and controls must match initialization, data, policy modules, auxiliary-head shape, steps, and approximate compute.
4. **Policy gate:** a world-loss reduction alone is insufficient; paired closed-loop success or a preregistered action endpoint must move in the predicted direction.
5. **Mechanism gate:** the selected diagnostic must distinguish causal dynamics information from task progress, static content, target complexity, and generic regularization.
6. **Deployment gate:** action-only inference must remain identical; otherwise the work exits H1 toward planning/joint inference.

## Current route decision

Do not commit to A, B, C, or D before candidate jury and novelty review. Route A and the plain form of B are crowded. Overlays C and D contain the clearest unresolved scientific questions, but D requires an especially strict prior-art and “generic optimizer” rejection check.

