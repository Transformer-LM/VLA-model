# Geometry-latent verifier / candidate-reranking scoop check

Date: 2026-08-29

## 1. Verdict

**REVISE — do not start a full build under the broad claim.**

The broad proposal — freeze a VLA, sample multiple action chunks, predict RGB/depth or point-map futures, and use geometry to rerank or selectively invoke more inference — is **Level 2: high overlap, bordering on Level 1 for some formulations**.

The central reason is that recent work already covers almost every component:

- frozen-policy candidate sampling and 3D-aware reranking: VeriSpace;
- WAM best-of-N selection by depth reprojection plus a selective gate: Gated GeoBoN;
- action-conditioned 3D point-flow rollout and MPC: PointWorld;
- action-conditioned latent rollout for frozen-VLA candidate ranking: DreamSteer;
- latent forward/inverse rollout, filtering, and execution reflection: PhysReflect-VLA;
- candidate safety confidence, rejection, and resampling: Pre-VLA;
- action-conditioned world-model verification plus formal conformal intervention calibration: CheckVLA;
- direct measurement of whether latent predictions preserve candidate-action ranking: Decision-Metric Alignment.

Therefore, these are **not sufficient novelty**:

1. replacing depth with point maps;
2. compressing depth into a latent;
3. adding a geometry auxiliary loss;
4. sampling several π0.5 action chunks and selecting one;
5. using a threshold to reject uncertain geometry predictions;
6. reporting pairwise ranking accuracy or showing that depth RMSE correlates with success.

The remaining potentially defensible delta is narrower:

> For a finite candidate set proposed by a frozen VLA, learn an action-conditioned task-geometry distribution and statistically calibrate the **decision regret of the selected action**, rather than calibrating depth error, generic safety confidence, or post-execution intervention frequency.

This version remains medium-risk: a reviewer may still call it a calibration wrapper unless the guarantee changes closed-loop decisions and survives matched direct-scorer baselines.

## 2. Delta

Provisional name: **Decision-Calibrated Geometric Action Regret (DC-GAR)**.

For candidate set \(\mathcal C_t=\{a^1,\ldots,a^K\}\), predict a task-centric geometry outcome distribution for each candidate:

\[
p_\theta(g_{t+1:t+H}\mid o_{\le t},a^k),
\]

where \(g\) is not dense RGB-D by default, but object-relative pose, clearance, end-effector/object point flow, and relevant relation/contact proxies.

Separate two quantities:

- predicted task cost \(\hat J_k\): which candidate appears best;
- model-trust/selection-risk \(U_k\): whether the geometry model can support that decision.

Calibrate a bound on selected-action regret,

\[
R_t=J_{\mathrm{env}}(a_{\mathrm{selected}})-\min_{a\in\mathcal C_t}J_{\mathrm{env}}(a),
\]

or on the event that the selected candidate is worse than another candidate by more than a tolerance \(\epsilon\). Execute the geometry-selected action only when the calibrated bound and top-two margin satisfy the acceptance rule; otherwise fall back to π0.5 top-1, resample, or actively re-observe.

The novelty is not “geometry helps,” but **decision-level risk control over geometry-based candidate selection**.

## 3. Decomposed claim

- Representation: task-centric metric geometry latent / point-flow distribution, not necessarily dense depth video.
- Observation: RGB or RGB-D, language, proprioception, optional multi-view history.
- Prediction target: candidate-action-conditioned relative pose, clearance, point motion, relation/contact proxy, and uncertainty.
- Control use: U3 candidate-action evaluation and selective execution.
- Policy: frozen π0.5 proposal model in the pilot.
- World model: frozen during selection; trained offline before evaluation.
- Primary claim: calibrated geometry-based selection lowers selected-action regret at a fixed coverage and latency budget compared with both RGB latent rollout and a direct action scorer.
- Non-claim: geometry alone solves long-horizon memory or provides universal physical safety.

## 4. Closest prior work

| Work | Date | What it already covers | Missing relative to DC-GAR | Overlap (0–4) |
|---|---:|---|---|---:|
| Gated GeoBoN, *Test-Time Scaling for WAMs via Zero-Shot Geometric Verification* | 2026-07 | WAM best-of-N; frozen geometry model; cross-view depth-reprojection ranking; action–future gate; selective extra sampling | No learned action-conditioned metric-geometry latent; no formal per-decision regret/coverage guarantee | 4 |
| VeriSpace | 2026-06 | Frozen VLA; K candidates; RGB-D/3D tokens; pairwise preference verifier; action reranking | Direct discriminative scorer rather than explicit future geometry distribution; no formal selection-risk calibration | 4 |
| PhysReflect-VLA | 2026-06 | Candidate chunks; geometric/relational abstract state; forward/inverse rollout; ranking/filtering; post-execution reflection | No explicit metric point-map rollout and no statistical selection-regret guarantee | 4 |
| PointWorld | 2026-01 | Action-conditioned full-scene 3D point-flow rollouts; multi-candidate MPPI/MPC; aleatoric variance | Uncertainty is not calibrated/used to control candidate-selection regret; task cost is hand-designed | 4 |
| DreamSteer | 2026-07 | Frozen VLA proposals; action-conditioned latent world model; language-value ranking | DINO/video latent rather than metric geometry; explicitly requires only relative ranking, not calibrated decision risk | 3 |
| τ0-WM | 2026-06/08 | Multiple candidates; cheap confidence filter; action-conditioned simulator; progress scores; selection and rectification | Large unified video system; no metric-geometry decision-risk calibration | 3 |
| Pre-VLA | 2026-05 | Pre-execution candidate safety/advantage verification, thresholding, rejection/resampling | Direct safety/advantage head; does not test trust in counterfactual geometry or selected-action regret | 3 |
| CheckVLA | 2026-07 | Independent action-conditioned latent WM; predicted-vs-observed verification; split functional conformal calibration; repair trigger | Post-execution committed-action verification; guarantee concerns unnecessary first intervention, not pre-execution candidate regret | 3 |
| Decision-Metric Alignment in Latent World Models | 2026-08 | Shows latent decodability does not imply correct action ranking; Plan–Real and CEM-stage rank metrics; action-conditioned auxiliary objectives | No VLA, no geometry verifier, and no selective calibrated decision rule | 3 |
| When to Trust Imagination | 2026-05 | Predicted-vs-observed discrepancy; adaptive chunk length and replanning | Post-execution adaptation, no candidate geometry ranking | 2 |
| WAM4D / WSA1 / PointAction | 2026-06/07 | Future depth/3D latent supervision or joint RGB–XYZ action generation | Geometry is used to shape/generate policy actions, not an independent decision-calibrated verifier | 2–3 |

## 5. Comparison result

Overall classification: **Level 2 — high overlap**.

- Compared with Gated GeoBoN: the broad “geometry chooses WAM rollouts and a gate saves compute” claim is already occupied.
- Compared with VeriSpace: the broad “3D-aware verifier reranks frozen-VLA candidates” claim is already occupied.
- Compared with PointWorld: “action-conditioned point-map/point-flow rollouts for candidate control” is already occupied.
- Compared with DreamSteer and τ0-WM: “sample, imagine, score, select/repair” is already occupied.
- Compared with CheckVLA: even conformal calibration around WAM-triggered intervention exists, although for a different decision event.
- Compared with Decision-Metric Alignment: “prediction quality must be judged by action ranking rather than reconstruction” is now an evaluation principle, not a new claim.

No located paper combines all four of the following in one method:

1. frozen VLA candidate set;
2. independently learned action-conditioned task geometry distribution;
3. calibration targeted at selected-action regret/top-candidate misselection;
4. a selective closed-loop execution rule evaluated under matched coverage and latency.

That conjunction is the only provisional gap found. It is an inference from the searched papers, not proof that no unpublished or unindexed work exists.

## 6. Minimal falsification experiment

### Gate A — candidate oracle headroom

In a branchable simulator, sample K π0.5 candidates from the exact same state and execute every candidate from cloned state. Compute:

- true best-of-K success minus π0.5 top-1 success;
- oracle top-k regret;
- candidate diversity in end-effector and object-effect space.

**Kill:** if oracle best-of-K improves success by less than 5 percentage points or candidates are nearly identical. No verifier can recover headroom that the proposal set does not contain.

### Gate B — geometry's incremental value

Use the same candidate dump, data, parameter budget, and latency budget for:

1. π0.5 top-1;
2. RGB/action direct discriminative scorer (VeriSpace/Pre-VLA-style);
3. RGB latent world-model scorer;
4. action-conditioned geometry/point-flow scorer;
5. decision-calibrated geometry regret selector;
6. privileged ground-truth geometry oracle.

**Kill:** if geometry fails to improve pairwise outcome ranking by roughly 5 points and top-k regret by roughly 10% over the matched direct scorer, or if oracle geometry itself cannot choose better actions.

### Gate C — calibration and selective utility

Measure:

- risk–coverage and regret–coverage curves;
- empirical coverage of the claimed regret bound;
- accepted-action misselection rate;
- closed-loop success, collision, false rejection/stagnation, and recovery rate;
- latency and extra-sampling frequency;
- calibration under locked in-distribution data, plus separate camera/object/material shift stress tests without claiming the ID guarantee transfers.

**Kill:** if uncertainty improves calibration metrics but does not improve selected actions, or if gains disappear after matching wall-clock budget.

## 7. Recommended execution order

1. Do only Gate A first; it needs no WAM training.
2. If headroom exists, train the simplest direct scorer and a small task-centric geometry predictor, not a full RGB-D diffusion model.
3. Compare them offline on identical candidate dumps.
4. Add decision-regret calibration only after geometry wins the matched comparison.
5. Run closed loop in two geometry-sensitive task families and one semantic negative control.
6. Use real-robot experiments only after the simulation causal result passes.

## 8. Search integrity note

The search covered 2024–2026 combinations of VLA/WAM, geometry/depth/point maps, candidate reranking, verification, uncertainty, calibration, conformal prediction, and action regret. The bundled paper-search pipeline returned transient source failures: arXiv API SSL EOF errors, Semantic Scholar HTTP 429, and DBLP/OpenAlex 5xx errors. Exact close papers were therefore checked through official arXiv abstract and full-HTML pages. Fifty-six keyword-collision results were excluded after abstract-level triage; the table above contains the semantically relevant closest set.

## 9. Bottom line

The experiment is worth doing **only as a cheap falsification study**, because it tests an important empirical question: does metric geometry actually change which VLA action should be executed?

It is **not worth building as “RGB WAM + depth/point-map latent reranking.”** That formulation is too close to Gated GeoBoN, VeriSpace, PointWorld, DreamSteer, and τ0-WM. Continue only if the paper is centered on calibrated selected-action regret and if the first two gates show genuine headroom over a matched direct scorer.
