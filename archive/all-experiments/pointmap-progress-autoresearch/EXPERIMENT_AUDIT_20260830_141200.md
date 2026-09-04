# Experiment Audit Report

**Date**: 2026-08-30  
**Auditor**: GPT-5.6-Sol ultra (fresh same-family agent, read-only, provisional)  
**Project**: pointmap-progress-autoresearch

## Overall Verdict: WARN

## Integrity Status: warn

The stored E0 results are real and internally consistent, but the preregistered scientific gate failed. There is no evidence of fake ground truth, score self-normalization, phantom outputs, invalid-v1 contamination, or scope inflation. The remaining integrity warnings are incomplete raw simulator replay provenance and the absence of saved validation predictions/threshold candidate tables.

## Checks

### A. Ground Truth Provenance: WARN

Labels come from controlled LIBERO simulator interventions and the simulator task predicate, with contradictory physics outcomes rejected. Independent inspection verified all 360 samples, event/label/decision mappings, mask-to-depth correspondence, and PointMap geometry residuals. The exact BDDL contents, complete instance mapping, replayable simulator states, and distractor realized pose are not archived, so full raw-GT replay is unavailable.

Evaluation type: simulation_only; the occlusion subtest is synthetic_proxy sensor masking. No executed VLA action or real-robot ground truth is present.

### B. Score Normalization: WARN

All metrics are conventional and were recomputed exactly from 4,320 stored test predictions. No prediction-derived denominator or score rescaling was found. The warning is that validation predictions and the threshold candidate table were not saved, so the validation-fitted FRR operating point cannot be reconstructed without rerunning. “IMR@FRR5” must be read as test IMR under a threshold fitted for validation FRR <=5%; achieved test FRR differs across modalities.

### C. Result File Existence: PASS

The exact grid is 4 modalities x 5 held-family folds x 3 seeds = 60 completed runs. Dataset, manifest, code, config and result hashes match. Fold aggregation, confidence intervals, tensor sizes and all five G0 booleans were independently reproduced. Invalid v1 files are excluded by both names/hashes and aggregation checks.

### D. Dead Code Detection: PASS

All claim-bearing metric, threshold, aggregation and gate functions are called, and their outputs appear in stored result files. No phantom metric or dead gate was found.

### E. Scope Assessment: PASS

The evidence is correctly limited to five LIBERO task definitions treated as five semantic families, 12 resets per task, six controlled event types, five held-family folds and three model seeds. The artifacts do not claim closed-loop, VLA-distribution, WAM-causality or real-robot evidence.

### F. Evaluation Type: simulation_only

This is a controlled representation-headroom diagnostic with a synthetic sensor-mask subtest.

## Oracle Failure Diagnosis

The Oracle failure is genuine, but the simulator evidence is sufficient. A task-invariant rule using relative-pose change and target visibility reaches 359/360 decisions and macro-F1 0.99655. The learned Oracle instead includes raw absolute positions, quaternions and raw visibility counts, normalized on only three training families. Held-family inputs reach max absolute z-scores of 124.7, 43.1 and 55,698.8; the MLP frequently collapses to the majority continue class.

Therefore the dominant failure is non-invariant Oracle feature design plus severe held-family feature shift. Class imbalance and early stopping are plausible contributors but are not individually isolated.

## Action Items

- Replace the learned Oracle input with task-invariant relative geometry and binary/fractional visibility.
- Add a deterministic invariant Oracle held-family sanity probe.
- Freeze a decision rule for zero-visibility camera-shift samples.
- Save validation predictions, per-epoch metrics and threshold candidate tables.
- Archive exact BDDL files, simulator/library commits, instance mappings, distractor poses, camera transforms and replay state.
- Freeze an audit-input manifest before the next audit.
- Rerun all affected configurations under one new code/config hash before any E1/B2 work.

## Claim Impact

- E0 representation-headroom claim: unsupported.
- PointMap-as-Depth-substitute claim: unsupported.
- PointMap input-efficiency observation: supported only as a tensor-size fact (448 bytes versus 442,368 bytes for the registered Depth head input), with sensing/projection cost excluded.
- Action-conditioned WAM/VLA, progress verification, recovery and closed-loop claims: untested.
- Advance to E1/B2: not allowed under the preregistered gate.

Allowed statement:

> On five controlled LIBERO task definitions with 12 resets each, the preregistered E0/G0 diagnostic completed and failed its Oracle sanity and PointMap-vs-Depth gates; therefore no representation-headroom conclusion is supported.

Full reviewer trace: [.aris/traces/experiment-audit/2026-08-30_run01/001-integrity-audit.response.md](.aris/traces/experiment-audit/2026-08-30_run01/001-integrity-audit.response.md)
