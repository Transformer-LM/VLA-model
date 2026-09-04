# WAM Route Card — Object-addressed action-updated belief

Date: 2026-08-29

## Route card

```yaml
representation: R3/R4 hybrid — object-addressed task latent plus explicit pose/relation/belief variables
control_use: unresolved among U1/U6 training-time representation and U3 inference-time verification; evidence must select one primary route
observations:
  - RGB or RGB-D observation history
  - language instruction
  - proprioception
  - executed action-chunk history
prediction_targets:
  - persistent object identity/address
  - action-conditioned object content/pose change
  - object relations and task-progress events
  - belief support, contradiction, invalidation, or uncertainty
action_interface: explicit conditioning on executed or candidate action chunks
rollout_horizon: unknown; start with one chunk and test multi-chunk propagation
policy: frozen pi0.5/OpenPI preferred if personal assets and action interface pass preflight
world_model_update: offline training; frozen during initial policy evaluation
data_regime: existing personal offline data plus branchable simulation interventions
primary_claim: an address-conditioned, action-updated and correctable object belief improves long-horizon decision correctness beyond matched global history memory and either component alone
main_failure_mode: upstream object association errors become persistent false beliefs; additional capacity/history rather than the proposed mechanism explains gains
```

## Component separation

- **Object address:** answers which entity a language phrase and later observations refer to.
- **Dynamic content/pose:** answers the current visible and geometric state of that entity.
- **Action update:** predicts how an executed chunk should alter the object state even when the result becomes partly hidden.
- **Observation correction:** reconciles the predicted belief with later evidence and can invalidate a prior update.
- **Control use:** must change continuation, re-observation, recovery, or action selection. Better slot loss alone is insufficient.

## Falsifiable hypothesis shape

> On long-horizon manipulation tasks containing object ambiguity, occlusion, action-induced scene changes, or failed substeps, conditioning belief updates on stable object addresses and executed actions improves object-specific progress-state accuracy and closed-loop success relative to a parameter/context-matched global-memory baseline, while preserving the same policy and interaction budget.

Primary endpoint candidate: intervention-conditioned closed-loop recovery/success rate on paired initial states.

Mechanism diagnostic: correct object identity and correct object-specific relation/progress state after occlusion or an injected action failure.

Minimum pilot signal: the combined method must outperform both address-only and action-update-only variants and a matched global-memory transformer; otherwise the conjunction mechanism is refuted.

## Open choices reserved for evidence

- Whether the publishable route is training-time representation, inference-time verifier, or belief-conditioned recovery.
- Whether explicit 3D pose is necessary or object slot/content is sufficient.
- Whether counterfactual candidate rollout is needed; it is not assumed.
- Exact benchmark, policy checkpoint, object extractor, tracker, and action horizon.
- Whether upstream segmentation/address labels can be produced without new licensed data or unavailable internet access.

## Non-claims

- Concatenating OA-WAM slots with EvoScene memory is not itself a contribution.
- A persistent hidden state is not automatically a calibrated belief.
- Correct object binding does not establish execution correction.
- Lower next-slot prediction loss does not establish improved robot control.
- No real-robot claim is authorized in this run.
