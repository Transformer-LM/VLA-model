# Step 5 — Full-paper mechanism verification

Timestamp: 2026-08-31 Asia/Shanghai

## Feedback World Model (arXiv:2605.15705)

- Verified mechanism: latent prediction velocity receives an additive online correction `L e_t`, where `e_t` is observed latent minus the propagated feedback state; the same residual is used for every candidate action at the current decision.
- Consumer: the corrected latent defines an action-aware energy whose gradient guides diffusion-policy denoising.
- Scope: LIBERO-Plus, Robomimic, two real tasks; robot-initial-state OOD; base WM frozen and no parameter update.
- Important assumption: bounded latent residual; the additive feedback is candidate-action independent at a decision step.
- Evidence: arXiv HTML Sec. 4.2, Eqs. 8–13; Sec. 4.3, Eqs. 14–16.

## ReDRAW (arXiv:2504.02252)

- Verified mechanism: freeze a source latent WM and train an MLP residual `delta(z,a)` that corrects forward-dynamics logits on a small offline target-environment dataset.
- Consumer: actor–critic is optimized in corrected imagined dynamics.
- Scope: vision DMC and Duckiebot lane following; sim-to-real rather than general manipulation WAM.
- Limitation: paper states low-data residuals may only model conceptually simple dynamics changes and leaves foundation WMs open.

## Say, Dream, and Act (arXiv:2602.10717)

- Verified mechanism: adapt/distill a video generator; an action model consumes imagined frames plus real historical observations and treats imagination as an in-context example.
- Consumer: real observations ground action generation and compensate spatial inaccuracies in generated video.
- Scope: instruction-driven manipulation and long-horizon keyframe imagination.
- Boundary: it corrects actions despite WM errors, not the WM transition itself.

## When to Trust Imagination (arXiv:2605.06222)

- Verified mechanism: FFDC compares aligned future images/actions with real observations and language, outputs whether the remaining chunk is executable.
- Consumer: continue a long chunk or stop/replan early.
- Boundary: binary trust/replanning; the predicted future itself is not corrected.

## CheckVLA (arXiv:2607.26789)

- Verified mechanism: rolling action-conditioned prediction, standardized discrepancy, conformal trigger, suffix rewrite, and re-anchor at current observation.
- Consumer: runtime intervention and policy repair, with event memory.
- Scope: RoboCasa365 simulation; matched invocation budget.
- Boundary: re-anchors a frozen WM but does not learn an action-dependent correction to its future distribution.

## DreamX-Phi 1.0 (arXiv:2608.13489)

- Verified mechanism: per-arm SE(3) conditioning, optional latent depth auxiliary branch, SAM3 object masks, frozen V-JEPA relational regularization.
- Consumer: more action-faithful/object-consistent generated video.
- Scope: training-time model design; no online residual feedback.

## tau0-WM (arXiv:2606.01027)

- Verified mechanism: joint VAM plus action-conditioned video simulator; re-denoising selection and low-quality action rectification through a future-conditioned second policy query.
- Consumer: pre-execution action selection/refinement.
- Boundary: it rectifies actions based on model imagination; it does not correct the WM from realized prediction error.
