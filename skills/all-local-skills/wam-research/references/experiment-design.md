# Falsifiable experiment design

## Contents

1. Hypothesis ledger
2. Experiment matrix
3. Stage gates
4. Ablation rules
5. Stop conditions

## Hypothesis ledger

```markdown
### H1 — short name
- Population/tasks:
- Intervention:
- Baseline:
- Proposed mechanism:
- Primary endpoint:
- Mechanism diagnostic:
- Downstream endpoint:
- Minimum meaningful effect:
- Refutation condition:
- Confounders:
- Required budget:
```

## Experiment matrix

For every run family record:

| Field | Required value |
|---|---|
| Purpose | sanity, baseline, mechanism, ablation, stress, final |
| Changed factor | exactly what differs |
| Fixed factors | data, model scale, optimizer, steps, horizon |
| Seeds | training and evaluation seeds |
| Budget | GPU-hours, environment steps, real trials |
| Primary metric | one preregistered endpoint |
| Secondary metrics | mechanism and safety diagnostics |
| Pass gate | numeric or categorical decision rule |
| Artifacts | config, commit, logs, checkpoint, videos |

## Stage gates

### Gate 0 — interface

Verify tensor shapes, action normalization, temporal alignment, camera ordering, reset semantics, reward/termination labels, and checkpoint loading.

### Gate 1 — capacity

Overfit a tiny dataset or single task. Failure here blocks scaling.

### Gate 2 — causality

Run shuffled/zero/counterfactual action controls. An action-conditioned model must react correctly to action changes.

### Gate 3 — pilot

Compare with the strongest reproducible baseline under a small matched budget. Continue only with a credible primary or mechanism signal.

### Gate 4 — mechanism

Test the causal component and a negative control. Do not proceed based only on aggregate benchmark gain.

### Gate 5 — robustness

Test horizon, policy shift, object/camera/task shift, uncertainty, and exploitation.

### Gate 6 — final

Run frozen configs over multiple seeds and the full evaluation protocol. Do not tune on final test results.

## Ablation rules

- Change one conceptual factor per core ablation.
- Include a parameter/compute-matched control for added modules.
- Separate more data from better objectives.
- Cross world models and planners/policies when attribution would otherwise be ambiguous.
- Include rollout horizon and update schedule for model-based RL.
- Preserve failed ablations and explain what they falsify.

## Stop conditions

Stop or revise when:

- the interface or overfit sanity test fails;
- the model ignores or incorrectly responds to actions;
- the pilot misses the declared minimum effect;
- gains disappear under matched data/compute;
- imagined improvement has no environment correlation;
- the policy exploits model errors faster than reliability controls correct them;
- resource cost makes the intended final evaluation infeasible.
