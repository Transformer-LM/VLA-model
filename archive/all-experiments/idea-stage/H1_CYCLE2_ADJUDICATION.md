+# H1 Cycle-2 Adjudication

**Recorded:** 2026-08-07 08:43 +08:00  
**Host:** deterministic StarVLA-OFT (Qwen3-VL-4B + 8 action tokens + MLPResNet/L1 7D action head)  
**Decision:** `REVISE / NO-RUN`

## Load-bearing host facts

- The reusable baseline is not a flow/diffusion policy. It has no denoising timestep, noisy-action trajectory, or native action SNR.
- Its persisted config freezes `qwen_vl_interface`; the 1k–30k checkpoints primarily train the deterministic action MLP. A claim about shaping shared VLM representations would require a new shared adapter/LoRA, while an unmodified run can at most shape action-head representations.
- The final checkpoint is saturated on LIBERO; any policy experiment must use a preregistered non-saturated checkpoint or a robustness endpoint.
- The existing CF-DynAlign implementation remains inadmissible: its strict held-out world-validity gate failed, so `lambda_cf` must stay zero.

## Candidate adjudication

| Candidate | Novelty | Host fit | Identifiability | 3-seed ≤8 GPUh | Decision |
|---|---|---|---|---|---|
| Policy-Trajectory Outcome Consistency | narrow/partial | fail: needs diffusion trajectory | conditional | conditional | reject for this host |
| ASAF action-SNR-aligned foresight | narrow/partial | fail: no action SNR/noise path | conditional | conditional | reject for this host |
| CATF control-affine tangent foresight | weak cross-point delta | pass | fail as a Jacobian claim on single-action offline demonstrations | conditional | reject |
| Action-readout predictive bottleneck | occupied/structural deadlock | pass | fail: 56D path collides with predicted-action world guidance; wider path leaves a control-nullspace shortcut | fail for full controls | reject |
| Future-defined state-alias separation | mining delta only | pass | conditional | fail for required controls | reject |
| Successor-geometry distillation | loss-swap delta only | pass | conditional | fail for required controls | reject |

## Why CATF is not promoted

The proposed `d_hat = B(h)u` head is not enough to identify a local visual control Jacobian from ordinary offline imitation trajectories: each state typically contains only one demonstrated action. A state-dependent `B(h)` can explain the observed displacement without learning counterfactual action effects. Same-task/phase action shuffling tests sensitivity but does not recover missing local interventions.

Its structural delta is also compressed by primary-source neighbors:

- [VERA](https://arxiv.org/html/2605.27817) already learns an image-conditioned forward Jacobian mapping robot commands to image-space motion.
- [Fast-LeWM](https://arxiv.org/html/2606.26217) already learns current-latent + action-prefix → multi-horizon future latents.
- SPARK and robot-state contrastive VLA regularization already occupy dynamics-aware/control-aware representation adaptation.
- Classical control-affine/Koopman latent dynamics precede the VLA intersection.

CATF could be described only as a low-rank action-conditioned endpoint predictor, which removes its claimed novelty.

## Cycle-2 conclusion

No new method candidate simultaneously passes:

1. current-literature novelty;
2. causal/diagnostic identifiability;
3. compatibility with the deterministic frozen-VLM host;
4. a matched, three-seed, model-policy-environment evidence package within 8 GPUh.

This is an evidence-gated `NO-RUN`, not an implementation failure. Zero GPU hours have been consumed.

## Cycle-3 route

The final allowed idea cycle will test one narrower route: whether a reviewer-defensible **mechanistic diagnostic/negative-result study**, rather than a new method, can be executed using a small shared adapter, early StarVLA checkpoints, strict future-validity gates, causal representation interventions, and paired LIBERO rollouts. It must still pass novelty, identifiability, and the 8 GPUh cap before any remote write or training.

