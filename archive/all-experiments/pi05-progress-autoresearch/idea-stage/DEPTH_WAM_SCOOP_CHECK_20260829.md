# Depth-augmented WAM scoop check

Date: 2026-08-29

## Verdict

- Literal claim — generate RGB futures, estimate a depth sequence, compress RGB+depth into latent, and use it to improve VLA/WAM: **Level 1 — Full Overlap**.
- Defensible reframe — retain an independently predicted, action-conditioned, calibrated geometry latent specifically for candidate-action verification/reranking, without dense RGB-D decoding: **provisional Level 2 — High Overlap**.

The literal claim is directly blocked by PAD-depth, FlowDreamer, TesserAct, X-WAM, PointAction, WAM4D, WSA1, and RynnWorld-4D. The reframe differs mainly in the control use: verification and calibrated refusal rather than joint action generation or inverse dynamics.

## Delta

Unlike WAM4D/WSA1, which use future geometry chiefly to shape or jointly generate policy actions, the proposed narrow version independently predicts a candidate-action-conditioned metric geometry latent and uses calibrated RGB–geometry disagreement to rerank, reject, or re-observe, measured by candidate ranking regret, unsafe-action false negatives, and closed-loop recovery—not merely depth error or policy success.

## Why naive post-hoc depth is weak

Running a monocular depth estimator on every generated RGB frame does not create independent physical evidence: the depth inherits the RGB hallucination, adds temporal flicker and scale drift, and compounds errors autoregressively. FlowDreamer already implements this family. PointAction reports a direct cascade ablation in which generated-RGB-plus-DA3 geometry underperforms joint RGB–XYZ prediction.

## Recommended representation/control card

- Representation: RGB video latent plus a separate metric-geometry latent; dense depth decode is optional and only used for audits.
- Inputs: observation history, language, proprioception, and an explicit candidate action chunk.
- Targets: future metric depth/point geometry, object-relative distance, clearance/contact events, and calibrated uncertainty.
- Control use: candidate reranking, execution verification, selective intervention, or active re-observation.
- Policy relation: freeze pi0.5 initially and use it only as a proposal model.
- Primary claim: at matched parameters and wall-clock budget, geometry latent improves action-effect ranking and safety under occlusion/viewpoint/metric shifts.
- Failure modes: pseudo-depth scale drift; reflective/transparent/thin objects; camera motion; latent compression erasing boundaries and contact gaps; cost growing with candidate count.

## Closest prior work

1. PAD-depth (arXiv:2411.18179): jointly denoises future RGB, depth, and actions; direct broad overlap.
2. FlowDreamer (arXiv:2505.10075): action-conditioned RGB-D transition; predicts RGB then applies a depth estimator; closest to the user's original pipeline.
3. TesserAct (arXiv:2504.20995): separately VAE-compresses and jointly generates future RGB, depth, and normals.
4. Geometry-aware 4D Video Generation (arXiv:2507.01099): joint RGB and pointmap latent generation with multi-view 3D consistency.
5. GWM (arXiv:2508.17600): action-conditioned 3D Gaussian latent dynamics.
6. PointWorld (arXiv:2601.03782): action-conditioned metric 3D point-flow future for MPC.
7. MVISTA-4D (arXiv:2602.09878): multi-view future RGB-D generation and test-time action inference.
8. X-WAM (arXiv:2604.26694): unified future multi-view RGB-D, state, and action prediction with a lightweight depth branch.
9. GEM-4D (arXiv:2605.22882): geometry-foundation-model distillation into a single RGB video stream with no extra inference cost.
10. PointAction (arXiv:2606.03943): joint RGB–XYZ latent future and point-to-action decoder; direct evidence against post-hoc depth cascades.
11. WAM4D (arXiv:2606.14048): training-time future-depth register readouts; geometry branch removed for policy inference.
12. LaWAM (arXiv:2606.15768): efficient policy-facing future latent without pixel decoding; establishes that latent compression alone is not novel.
13. WSA1 (arXiv:2607.03941): action-conditioned future 3D latent jointly coupled to action generation without dense geometry decoding.
14. RynnWorld-4D (arXiv:2607.06559): joint RGB/depth/flow latent modeling; policy consumes internal 4D features without full denoising.

## Minimal falsification experiment

Use the same trajectory data and matched compute for four variants: RGB-only latent; RGB plus training-only depth auxiliary loss; separate action-conditioned RGB/geometry latents; oracle sensor-depth upper bound. Freeze the proposal policy. Evaluate insertion, stacking, clutter/occlusion, and pushing/contact tasks plus a color/semantic negative-control task.

Measure metric and temporal depth consistency, object-relative pose and clearance/contact prediction, action-shuffle sensitivity, pairwise candidate-outcome ranking, top-k regret, closed-loop success/collision, false intervention, and latency. Kill the idea if gains vanish after matching compute/data, a direct discriminative scorer matches it, improvements remain confined to depth metrics, or pseudo-depth collapses under camera/material shifts.

## Bottom line

Depth is meaningful for geometric control failures, but it will not by itself fix long-horizon task memory. The broad RGB+depth WAM idea is scooped. The only promising continuation is to make geometry a low-cost, action-conditioned and calibrated decision variable for verification/reranking, and to prove that it changes the selected action rather than merely generating better-looking 4D videos.
