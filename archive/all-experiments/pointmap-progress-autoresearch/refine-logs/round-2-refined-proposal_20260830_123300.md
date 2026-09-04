# Round 2 Refined Proposal: Trace-Conditioned Historical Relation Filter

**Date:** 2026-08-30  
**Contribution type:** attributable transition-prior versus observation-evidence study, not a generally new WAM architecture

## Anchor and scope

The method revises a previously committed, now non-active `inside/on` relation after the robot executes a later action chunk. It asks whether realized robot kinematics provide conditional value when the post-action object-relative geometry is ambiguous. Fully hidden exogenous changes without any online evidence are unidentifiable and must produce abstention/re-observation.

E0 controlled relation perturbations are diagnostic only: they validate PointMap capture, relation labels, observability, and typed rollback headroom. They do not support the action or WAM claim.

## Belief filter

For relation \(r_{ij}\), maintain \(q_t=P(z_t^{ij}=valid\mid h_t)\). A transition head yields a prior

\[
q^-_{t+H}=T_\theta(q_t,\phi_t^{ij},\tau_{t:t+H},r_{ij}).
\]

The frozen observation model supplies a visibility-conditioned log-likelihood ratio

\[
\Lambda_r(o,v)=\log\frac{p(o\mid z=valid,v,r)}{p(o\mid z=invalid,v,r)},
\qquad
\operatorname{logit}q_{t+H}=\operatorname{logit}q^-_{t+H}+\Lambda_r(o_{t+H},v_{t+H}).
\]

No extra visibility multiplier is used. Low-visibility bins are required to have an LLR near zero. Posterior thresholds, fixed on validation data at a 5% false-retraction budget, map to typed retract / re-observe / continue.

## Strict information sets

All traces end at the final applied control of the action chunk and are available before the post-action PointMap update.

- \(\tau^{cmd}\): commanded 7D controls only.
- \(\tau^{kin}\): actually applied 7D controls plus robot-only end-effector position/orientation change, gripper position/velocity, and joint proprioception sampled during the chunk.
- \(\tau^{fb}\): \(\tau^{kin}\) plus contact/force/event feedback. This is reported only as execution-feedback-conditioned, not pure dynamics.

Forbidden inputs to every transition prior are post-action RGB/depth/PointMaps, simulator object pose, object velocity, relation predicate, success flag, instance identity derived from the future state, contact labels outside \(\tau^{fb}\), or any derived outcome/ground-truth variable. The primary claim uses \(\tau^{kin}\). A contact-only gain cannot support it.

## Exact geometry representation

\(\phi_t^{ij}\) uses only the pre-action, object-addressed PointMaps in the robot-base-aligned world frame. “Object-relative” means subtracting the target robust centroid while retaining the base-frame axes. For target and reference, deterministically sample up to 128 visible points and compute:

- visibility/count;
- robust centroid and target-to-reference displacement;
- 10/50/90% coordinate quantiles;
- covariance eigenvalues and axis-aligned robust extents;
- minimum cross-cloud distance and signed containment/support margins when defined.

This deterministic 54D summary is frozen; no PointNet is trained in the first study. Learned/deployed masks and depth teachers replace simulator masks only after the simulator-geometry gates pass.

## Observation likelihood

For each relation and visibility bin, the POT-style observation features are signed predicate margins:

- `inside`: target-point inclusion fraction and distance to the reference robust box boundary;
- `on`: horizontal overlap, vertical gap, and support stability window.

Class-conditional histograms with Laplace smoothing are fitted on training task families only and frozen. The visibility bin is chosen from target/reference point counts. The same table, data, and posterior thresholds are used for every transition variant. This is a calibrated observation table, not a second neural contribution.

## Transition architecture and optimization

Traces are uniformly resampled or padded to 16 steps with a validity mask. The transition head contains:

1. a two-layer temporal 1D convolution, 64 channels, kernel size 3, masked mean pooling;
2. concatenation with \(q_t\), the 54D geometry summary, and a fixed one-hot `inside/on` token;
3. a two-layer MLP (128 hidden units, GELU) to one validity logit.

The entire trainable mechanism is under 100k parameters. It is trained with class-balanced binary NLL. One scalar temperature is fitted on validation NLL and applied to all test predictions. If the shared `inside/on` head needs relation-specific modules, the pilot falls back to `inside` only rather than adding branches.

## Mandatory paired action-effect design

E1 restores identical pre-states and runs physics-mediated controls. Outcome overlap is mandatory:

- the command/action-parameter distributions for preserved and invalidated outcomes must overlap;
- at least one action family must produce both outcomes through interaction-state variation;
- sampling is balanced within action family, duration, pre-state geometry bin, and post-observation visibility bin;
- held-out action templates and held-out task families are never used for fitting;
- propensity weighting is used if residual action-parameter imbalance exceeds a preregistered standardized mean difference of 0.1.

Trace shuffling occurs only within task family, action family, duration bin, pre-state geometry bin, and visibility bin. A command-semantic shortcut classifier is reported; if command alone separates labels in a matched stratum above 60% balanced accuracy, that stratum is rejected or rematched.

E2 uses either newly collected on-policy StarVLA/π0.5 chunks or exact-state replay of a chunk with its original restored state. Replaying a chunk on a different restored state is prohibited for the claim-bearing dataset. Scripted E1 results remain simulator debugging evidence and are never promoted to a VLA-distribution claim.

## Comparisons

1. POT-style observation LLR with a persistence prior.
2. Learned no-trace PointMap transition prior.
3. Within-stratum shuffled \(\tau^{kin}\).
4. Command-only \(\tau^{cmd}\).
5. Primary realized-kinematic \(\tau^{kin}\).
6. Separately named feedback-inclusive \(\tau^{fb}\).
7. Matched-capacity RGB/visual-feature verifier.
8. Simulator-geometry oracle.

## Primary statistic and gates

The decisive statistic is **retraction decision error at a validation-calibrated 5% false-retraction budget**, with 95% confidence intervals from a task-family cluster bootstrap. Supporting metrics are invalidation recall, NLL/Brier/ECE, risk-coverage, typed-retraction precision, latency, and closed-loop recovery/final success.

The primary claim is allowed only if \(\tau^{kin}\):

- lowers retraction decision error by at least 10% relative and improves invalidation recall by at least 5 points over the strongest observation/no-trace baseline;
- beats \(\tau^{cmd}\) if “realized execution” is claimed;
- loses its incremental gain under within-stratum shuffling;
- transfers to held-out action templates and task families;
- adds little on fully visible relations and abstains on hidden exogenous disturbances;
- survives learned PointMaps and changes closed-loop typed rollback/final success after the oracle recovery gate passes.

Otherwise the conclusion is explicitly narrower: object-relative PointMap verification may be useful, but action-conditioned WAM dynamics were not shown necessary.

## Complexity boundary

Frozen VLA and geometry teachers; deterministic PointMap summary; one sub-100k transition head; one frozen empirical observation table; one validation temperature; no video/depth decoder, diffusion, LLM planner, learned recovery policy, or `grasp/open` claim.
