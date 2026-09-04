# E0/G0 v3 Experiment Integrity Audit

Timestamp: 2026-08-30 15:22 +08:00  
Reviewer: fresh same-family GPT-5.6-Sol cross-check (`/root/e0_v3_integrity_audit/fresh_integrity_reviewer`)  
Overall integrity: **WARN**  
Exact frozen G0 gate: **PASS (5/5)**  
Routing: **allow result-to-claim with warnings and strict claim ceiling**

## Exact independently recomputed gate

| Condition | Recomputed value | Verdict |
|---|---:|---|
| Oracle macro-F1 ≥ 0.75 | 0.9532298678442299 | PASS |
| Oracle achieved test FRR ≤ 0.05 | 0.03666666666666667 | PASS |
| PointMap IMR ≤ Depth IMR + 0.05 | 0.1222222222222222 ≤ 0.40555555555555556 | PASS |
| PointMap F1 ≥ Depth F1 − 0.03 | 0.9001641945503025 ≥ 0.6187439587301378 | PASS |
| PointMap input at least 10× smaller | 152 × 10 ≤ 442,368 bytes | PASS |

Task-family cluster bootstrap was independently recomputed after averaging three seeds per fold, using 10,000 resamples and seed 20260830:

- PointMap−Depth macro-F1: `+0.251420`, 95% CI `[+0.031512, +0.467698]`.
- PointMap−Depth IMR: `−0.233333`, 95% CI `[−0.583333, +0.116667]`.

The point-estimate gate passes. Because the paired IMR interval crosses zero, the evidence does not support a robust or statistically resolved IMR superiority claim.

## Evidence completeness

R020–R023 each contain 5 folds × seeds `{17,29,43}` = 15 unique runs, 1,080 test predictions, 1,080 validation predictions, complete epoch histories and full threshold candidate tables. Across four modalities this is 60 learned runs, 4,320 test records and 4,320 validation records. Sample coverage, task-family splits, labels, probabilities, selected thresholds, metrics and aggregate values were independently replayed.

Remote read-only verification confirmed:

- dataset SHA-256 `ea15283b03bec58092c08f98bc284c22c7a75f48ad572b71ee4eca716fad9655`;
- manifest SHA-256 `3fffc93c264e47122a8b5069e45efbaccf90d3e206940a90339295cb68657191`;
- 360 samples and class counts 240/60/60;
- all NPZ labels match manifest and R020–R025 traces;
- R025 Oracle and PointMap predictions exactly reproduce from the raw NPZ and current geometry code.

R025 deterministic Oracle independently reproduces accuracy `0.997222`, macro-F1 `0.996549`, confusion matrix `[[239,0,1],[0,60,0],[0,0,60]]`. Its only error is the pre-documented sample 170 camera-shift/zero-post-visibility edge.

## Integrity checks

- Fake ground truth: not found. Labels come from pre-defined simulator interventions and predicate checks, not model outputs.
- Leakage: not found. Entire task families define train/validation/test splits; no event IDs or labels enter features.
- Score-normalization fraud: not found. Geometry uses a fixed 0.30 m physical scale, not model- or family-fitted normalization.
- Seed selection: not found. All registered seeds are present.
- Phantom/failed runs: not found. The failed R025 launch and failed R024 dtype replay are explicitly separate logs and absent from aggregation; all accepted jobs exit 0.
- Post-hoc test thresholding: not found. Every selected threshold is fitted on validation probabilities and replayed on test.
- Scope inflation: not found in primary artifacts. Claim ceilings consistently say simulator-mask representation headroom only.

## Three required warnings

### 1. R011 geometry dependency is not fully bound

The current `audit_e0_dataset.py` still expects the old 112-D PointMap shape, whereas the repaired geometry emits 38-D features. R011 did not record its runtime geometry SHA, so its PointMap-projection subcheck is not exactly replayable with the current dependency combination. This does not flip G0 because the raw NPZ, labels, and all 360 current PointMap projections were independently rebuilt through R025 with current code hashes.

### 2. NumPy sentinel portability

The aggregator correctly restores the original torch float32 probabilities, and all 60 selected thresholds, test metrics and gates replay exactly. However, the intended `no_retract` first candidate is affected by NumPy scalar-promotion: in the remote environment it retracts the single maximum-score sample rather than strictly none. None of these 60 sentinel candidates was selected, so the accepted metrics and gate are unchanged. Future code must use an explicit dtype-stable sentinel and log the NumPy version.

### 3. Unregistered `min_epochs=20` protocol drift

The v3 trainer added a 20-epoch early-stopping floor globally, while the repair plan described RGB/Depth baselines as unchanged. This changes 2/15 RGB and 3/15 Depth best checkpoints relative to v2; PointMap and Oracle best checkpoints are unaffected. It is not gate-flipping: substituting the v2 Depth means still leaves both PointMap-vs-Depth G0 conditions passing, and the v3 Depth is stronger, making non-inferiority harder. The deviation must remain disclosed.

## Claim ceiling

Supported: on five controlled LIBERO task definitions and 360 simulator events using simulator instance masks and metric depth, the repaired object-relative PointMap representation passes the frozen point-estimate headroom gate; learned and deterministic Oracle sanity checks pass; the verifier tensor is much smaller than complete Depth.

Not supported: realized-action-trace value, action-conditioned WAM necessity or novelty, VLA improvement, recovery, closed-loop success, learned/deployed masks, broad LIBERO generalization, real-robot behavior, sim-to-real, or a general claim that PointMap replaces complete Depth.

This audit authorizes only the next `result-to-claim` decision. It does not itself authorize promoting E0 into a WAM/VLA contribution.
