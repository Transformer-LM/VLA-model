# Step 7 — Verdict, delta, and cheapest experiment

Timestamp: 2026-08-31 Asia/Shanghai

## Verdict

Level 1 — Full Overlap for the original claim. Feedback World Model already maintains an online latent feedback state from prediction–observation error, corrects future predictions without base-model updates, and uses the result to guide a robot policy.

## Defensible pivot delta

Unlike Feedback World Model, which adds the same observed latent feedback term to every candidate action at a decision step, a candidate-specific residual-field WAM would infer a calibrated distribution `delta(z,a)` over prediction errors and allow correction to decay or abstain as candidate actions move away from previously executed action support, targeting better counterfactual action ranking rather than only lower average latent MSE.

This delta is not yet a >7 novelty claim: ReDRAW already supplies an action-conditioned residual model offline, while adaptive control, Bayesian filtering, and GP residual dynamics are strong classical ancestors.

## Cheapest discriminating experiment

- Freeze one VLA and one WAM.
- At identical simulator states, generate a fixed candidate-action roster.
- Execute one candidate to reveal a residual, but evaluate correction on the unexecuted candidates using rollback ground truth.
- Compare base WAM, current-observation re-anchor, Feedback WM shared residual, offline ReDRAW-style `delta(z,a)`, and support-aware candidate-specific residual transport.
- Primary endpoint: pairwise candidate-ranking accuracy and top-k simulator regret; secondary: object pose/contact prediction, calibration, closed-loop success, latency.
- Kill if an oracle candidate-specific residual improves ranking by <5 percentage points or regret by <20%; also kill if ordinary re-anchoring, a direct action scorer, or FWM matches it at equal compute.

Decision: reject the generic idea; revise to candidate-specific, support-calibrated residual transport only as an exploratory premise test.
