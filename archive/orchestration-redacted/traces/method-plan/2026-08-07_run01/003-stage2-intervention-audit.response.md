# Stage-2 intervention audit

**Verdict: NO-GO as written; repairable before rollouts.**

Fatal flaws:

1. Residualizing only future y does not create a conditional predictive subspace. Cross-fit and residualize both delta and y against frozen current representation/DINO, action chunk, task and progress.
2. A free projector over flattened 8x2560 can mix token slots, while an ambient random orthogonal placebo is almost certainly outside the empirical adapter-delta manifold.
3. No held-out incremental-predictivity gate prevents a noise subspace from being called predictive.

Required redesign:

- Preassign episode-disjoint mechanism-fit, rank-validation and placebo-calibration splits.
- Fit PCA/whitening from residual delta without y, then ridge reduced-rank regression with nested episode CV. Require positive held-out incremental R2 against an episode-permutation null.
- Because the head mean-pools tokens, use a token-shared operator P=P_token kron T_feature with P_token=11^T/8 rather than a free 20480-D geometry.
- Generate Q inside the same whitened empirical delta span, covariance-orthogonal to P, with identical token structure. On independent calibration data, match latent energy and actual per-task/per-token action-output perturbation and require negligible future predictivity.
- Freeze all nuisance models, rank, P, Q and selection before any Stage-2 rollout.
- Require cached A-to-B action parity below 1e-6 plus a tiny deterministic rollout-trace parity smoke. This is an implementation control only.
- Count ties as failures. Require A_orth within 5pp of intact A, predictive removal to erase at least 50% of the A-B gap without grossly undershooting B, and no task reversal.

The ceiling is controlled, placebo-relative reliance on a preregistered linear treatment-associated predictive subspace, not mediation.

