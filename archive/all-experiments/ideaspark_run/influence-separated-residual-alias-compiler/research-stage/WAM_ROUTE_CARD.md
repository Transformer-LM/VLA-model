# ISRAC WAM Route Card

## Route card

```yaml
representation:
  compiler: simulator-native explicit physical state and contact graph
  evaluated_WAMs: [R4 explicit state dynamics, R3 task latent, later R1/R2 video]
control_use: U3 candidate-action evaluation and runtime correction
observations: [main RGB, wrist RGB, proprioception, language, executed-action history]
prediction_targets: [future task effect, progress/success/risk score, optional future video or latent]
action_interface: action-conditioned candidate chunks
rollout_horizon: short chunk and four-chunk suffix in E0; longer horizon only after calibration gate
policy: frozen strong StarVLA for candidate support
world_model_update: frozen during alias evaluation
data_regime: simulator for compiler and ground truth; offline trajectories for WAM fitting
primary_claim: influence-separated compilation yields certified feedback aliases more efficiently than matched-budget perturbation baselines and exposes held-out feedback-WAM false transport
main_failure_mode: target-WAM leakage, task-specific rules, controller-state mismatch, low-support actions, or ordinary OOD rather than feedback non-identifiability
```

ISRAC itself is not a new world-model representation. It is a WAM-blind,
simulator-grounded diagnostic compiler for the U3 feedback/correction use case.
The first target should be an action-conditioned state or task-latent dynamics
model because it is cheap enough for matched baselines. Video-generative WAMs
are a held-out transfer test, not required to establish the compiler mechanism.

## Evidence contract

- **Embodiment:** LIBERO Franka first; RoboTwin only after a clean environment
  and action-interface audit.
- **Task family:** multi-task language-conditioned manipulation, including
  articulated fixtures and object placement.
- **Policy interface:** frozen StarVLA, 8x7 action chunks; candidates must come
  from the policy support rather than scripted actions.
- **Compiler observables:** full simulator state, contact graph, RGB, depth and
  proprioception are permitted for certification, not for deployed policy input.
- **WAM role:** after an executed factual action, predict/evaluate an unexecuted
  candidate and optionally update the candidate score from the factual residual.
- **Authority:** simulation/offline only; no paid compute, external upload,
  shared storage, or autonomous real-robot motion.

## Falsifiable hypothesis

On successful frozen-StarVLA manipulation trajectories, restricting physical
search to parameter blocks that have zero measured influence on the complete
factual transcript but are activated by a subsequent policy candidate will
produce at least twice the certified-pair yield of the best matched simulator-
call random/grid baseline, while preserving factual RGB/depth/proprio/state
within deterministic repeat noise.

If that compiler gate passes, feedback methods that transport a factual WAM
residual to a different candidate action will show higher paired ranking regret
or correction harm on the alias set than on severity-matched ordinary physical
perturbations. A target model score is forbidden from compiler search.

## Primary endpoints

- **Compiler endpoint:** certified pairs per simulator call and per automatically
  screened boundary.
- **Mechanism diagnostic:** factual transcript max difference, candidate first
  divergence versus parameter first activation, and candidate physical-effect
  separation.
- **Model endpoint:** counterfactual pairwise ranking accuracy, calibration,
  false-transport rate and top-k regret.
- **Policy endpoint:** chosen-action environment regret and closed-loop success;
  imagined success alone is insufficient.
- **Environment endpoint:** deterministic simulator replay and cross-task/
  cross-platform certificate transfer.

## Refutation and decision rules

1. If matched random/grid/CMA-ES yields as many certified pairs per simulator
   call, the influence-separated compiler claim fails.
2. If certification requires task-specific exceptions, action-indexed switches,
   scripted failures or target-WAM scores, ISRAC fails.
3. If aliases do not increase false transport relative to severity-matched
   ordinary perturbations, the WAM correction-harm claim fails even if the
   compiler is a useful simulator-testing tool.
4. If the feedback-free WAM is harmed equally, the effect is ordinary OOD and
   not residual transport.
5. If a strong frozen VLA compensates and both worlds succeed, report behavior
   divergence only; do not promote it to task harm.

## Current evidence boundary

The current LIBERO pilot has four successful frozen-policy trajectories. On the
three newest tasks, six of eight automatically screened boundaries produced 24
certified compliance pairs. The original closed-loop pair succeeded in both
worlds (84 versus 85 steps), and the friction family was weak. These are partial
compiler results only; matched baselines, a second mechanism/platform, multiple
seeds and any WAM correction-harm claim remain open.

## Decision

**RUN the matched-budget compiler falsifier.** Do not train a new 5B WAM until
the compiler beats its baselines. If the gate passes, fit or reuse the smallest
faithful action-conditioned feedback model first, then test a held-out stronger
WAM.
