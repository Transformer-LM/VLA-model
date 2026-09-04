# ISRAC P025-v5 claim-driven experiment plan

## Core claim

A target-WAM-blind compiler can use realized contact-support subtraction to
construct physical twins whose complete factual transcript is identical but
whose policy-supported candidate future differs, at materially higher witness
yield per fixed simulator-step budget than simple search baselines.

The compiler primitive is:

`candidate realized geom support \ factual-prefix realized geom support`

Only simulator-native, action-independent parameter endpoints are changed.
The target feedback WAM is excluded from compilation and is introduced only in
a held-out post-hoc audit.

## Evidence gates

### G0 — Protocol integrity

- fresh seeded reset and benchmark initial state for every twin;
- replay warmup plus complete executed policy prefix;
- candidate actions continue without an intermediate restore;
- saved candidate boundary and repeated prefix endpoint both pass absolute and
  repeat-noise gates;
- every `env.step` is counted at runtime;
- raw RGB, depth, state, proprio, contact pairs, actions and static model arrays
  are immutable evidence;
- an independent verifier rebuilds all traces and certificates;
- adversarial tamper suite must reject every mutation.

Status: one-boundary sanity passed; 5/5 tamper attacks rejected.

### G1 — Eight-boundary mechanism coverage

Run the three-block ISRAC selector on the eight policy boundaries previously
screened from three LIBERO goal tasks.

Primary outputs:

- eligible-boundary count;
- unique witness count, deduplicated by trajectory, boundary, candidate action,
  geom address and parameter family;
- certified endpoint-pair count;
- failure-reason distribution;
- charged and measured simulator steps.

Stop if fewer than three boundaries are eligible or if no unique witness
survives formal verification.

### G2 — Fixed-budget simple baselines

For every eligible boundary, run seeds 0, 1 and 2 for:

- ISRAC contact-support subtraction;
- candidate-contact selection;
- random-scene geom selection.

All selectors use the same pool-independent `SHA256(seed | geom address)`
priority and the same three-block charged cap.  Invalid boundaries are excluded
for every selector, never counted as zeros.

Primary statistic: unique witnesses per one million charged simulator steps.

Pass condition:

- point ratio versus the strongest simple baseline at least 2.0;
- seed-cluster/boundary bootstrap 95% lower bound above 1.0.

### G3 — Strong search and mechanism transfer

If G2 passes:

- compare against a budget-matched Bayesian/CMA-style parameter/address search;
- repeat with the friction endpoint family;
- require the advantage not to be confined to one task or one geom.

Failure routes to compiler redesign or kill; it is not repaired by increasing
the budget only for ISRAC.

### G4 — Held-out WAM relevance

Freeze a feedback WAM or action-conditioned future scorer after the compiler
dataset is fixed.  Measure whether certified aliases cause:

- imagined ranking reversal;
- erroneous intervention/correction;
- task-progress misclassification;
- real-simulator regret or correction harm.

Required controls:

- ordinary random physics perturbations;
- non-certified candidate-contact perturbations;
- direct action scorer without a WAM;
- target WAM never used to choose compiler parameters.

The paper-level WAM claim is killed if certified aliases do not create more
held-out decision harm than these controls.

### G5 — External validity

Repeat the minimal compiler and WAM audit in a second simulator or benchmark.
Until this passes, claims remain LIBERO/MuJoCo-specific.

## Reporting rules

- P022/P024 are protocol-debug diagnostics and cannot support claims.
- P025-v2/v3/v4 are failed recovery branches and remain in the audit trail.
- P025-v5 is the first admissible protocol.
- A visual/video example is illustrative only; witness yield and decision harm
  are the primary outcomes.
- No novelty score above 7/10 is reported until at least G2 passes robustly;
  the existing fresh review rates the idea 7.4/10 only conditionally.
