# Embodied WAM Review Rubric

## Contents

1. Required reviewer posture
2. Scientific checks
3. WAM-specific failure modes
4. Verdict format

## Required reviewer posture

Read the route card, implementation, configurations, raw logs, raw metrics,
analysis code, failed runs, and claimed results directly. Executor summaries are
navigation aids, not evidence. Look for the strongest falsification of the
mechanism before suggesting improvements.

## Scientific checks

### Problem and novelty

- Is the problem a real embodied bottleneck rather than a renamed architecture
  change?
- Is novelty separated into prediction representation and control usage?
- Does the nearest work already contain the claimed combination, objective, or
  evaluation?
- Is the contribution still meaningful if visual quality does not improve?

### Confounds and baselines

- Match data, parameters, pretraining, optimizer steps, GPU-hours, environment
  interactions, action horizon, observation history, and evaluation protocol.
- Include the strongest reproducible model-free VLA baseline, an appropriate
  world-model baseline, and an oracle/simulator upper bound when available.
- Test whether extra data, longer context, a larger decoder, or additional
  policy updates explain the gain.

### Model-level evidence

- Action controllability and counterfactual sensitivity.
- Calibration or uncertainty, including out-of-distribution behavior.
- Multi-step drift over the horizon actually used by the policy or planner.
- Prediction on the policy-induced distribution, not only held-out behavior
  data.
- Appropriate state, latent, contact, geometry, or task-relevant metrics. FVD,
  PSNR, SSIM, LPIPS, and latent loss are insufficient by themselves.

### Policy-level evidence

- Environment success/return with uncertainty over seeds and initial states.
- Robustness, sample efficiency, latency, memory, and wall-clock cost.
- Paired evaluation where tasks and starts can be shared.
- Whether the policy exploits model blind spots or imagined rewards.
- Whether gains persist when the world model is frozen and whether any claimed
  co-evolution is actually evaluated.

### Environment-level evidence

- Benchmark split hygiene and absence of train/evaluation leakage.
- Generalization across tasks, layouts, objects, language, or embodiments as
  required by the claim.
- Simulator agreement for any imagined success signal.
- Real-world claims require real evidence; simulation alone may support only a
  simulation-scoped claim.

### Statistics and integrity

- Sufficient seeds, confidence intervals, paired tests, and effect sizes.
- All reported values resolve to raw files and the named analysis code.
- Checkpoint, seed, task, video, and run selection are not cherry-picked.
- Failed runs and excluded samples are accounted for.
- Ground truth is independent of model output; metrics are not self-normalized.

## WAM-specific failure modes

Explicitly test for:

1. visually plausible but action-insensitive predictions;
2. short-horizon accuracy hiding compounding long-horizon drift;
3. high-quality generation with no downstream control benefit;
4. latent collapse or task-irrelevant predictive features;
5. planning or RL exploiting model error;
6. evaluating the model off the optimized policy distribution;
7. world-model pretraining data leaking benchmark evaluation trajectories;
8. gains caused by additional policy updates or environment interactions;
9. imagined success reported as environment success;
10. an oracle model or simple dynamics baseline matching the proposed method;
11. inference latency making the method unusable for the target control rate;
12. claims of policy/world-model co-evolution when one component is effectively
    frozen or updated on stale data.

## Verdict format

Return and persist:

```text
Score: <1-10>                 # routing heuristic, not acceptance
Verdict: ready | almost | not ready
Assurance: provisional | independent
Integrity: pass | warn | fail | blocked
Claim: yes | partial | no | unadjudicated

Critical weaknesses:
1. <weakness> 鈥?evidence path 鈥?minimum discriminating fix

Unsupported or overbroad claims:
- <claim> 鈥?why unsupported 鈥?defensible narrower wording

Required next evidence:
- <experiment/analysis> 鈥?expected decision change 鈥?estimated cost

WAM failure-mode audit:
- <each applicable failure mode and finding>
```

A positive score cannot override an integrity failure, missing raw evidence, or
an unadjudicated claim.

