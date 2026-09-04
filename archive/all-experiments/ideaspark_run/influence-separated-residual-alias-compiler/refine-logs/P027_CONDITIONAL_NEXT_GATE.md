# P027 Conditional Next Gate

**Written while P026 was still running.** This document is prospective and does
not declare P026 successful. P027 is authorized only if the exact locked P026
analyzer reports both pre-registered gates as passed:

1. ISRAC point yield is at least 2x the strongest simple matched-step baseline;
2. both hierarchical paired-bootstrap 95% lower bounds are greater than 1.

If either gate fails, do not launch P027. Write a kill/pivot report instead.

## P027-A: strong black-box optimizer falsifier

- Search space: the same legal contact blocks and physical parameter domain used
  by ISRAC. No target-WAM score, ranking, feature, or gradient may be read.
- Baselines: candidate-contact CMA/CEM-style mixed search and an unconstrained
  scene-block CMA/CEM-style mixed search. Block identity is categorical and the
  physical value is continuous in log space.
- Feasibility: the complete factual transcript must remain inside the locked
  repeat envelope. Infeasible evaluations still consume their full measured
  simulator-step cost.
- Search signal: among feasible evaluations, maximize candidate-state
  divergence with deterministic lexicographic tie breaking. This is a strong
  physics-oracle optimizer, not a random selector.
- Budget: exact simulator steps, including nominal runs, failed trials,
  repeats, and final certification, are matched per source/candidate cell.
- Seeds and stopping rules are frozen before the first optimizer outcome is
  read. The comparison unit remains a held-out policy-supported boundary.
- Gate: ISRAC must retain a material yield advantage with a paired 95% interval
  above 1 against the strongest optimizer. Otherwise the efficiency claim is
  weakened or killed.

## P027-B: second physical mechanism

- Mechanism family: friction, using the already declared legal endpoints
  0.05, 0.30, and 1.50.
- Use the same admitted sources, frozen candidates, selectors, seeds, evidence
  schema, verifier, step accounting, and analysis hierarchy as P026 unless a
  new versioned amendment is frozen before any friction outcome is read.
- Report friction separately from compliance; do not pool them to rescue a
  failed family.
- Gate: nonzero cross-task certified yield plus a consistent advantage over the
  strongest matched baseline. A compliance-only effect does not support a
  mechanism-general compiler claim.

## P027-C: downstream feedback-WAM harm pilot

- Freeze and hash certified twins before loading any evaluated WAM.
- Evaluate at least two held-out feedback interfaces plus a feedback-free
  control on identical candidate bundles.
- Primary endpoints: false residual transport, pairwise ranking inversion,
  correction-harm rate, and corrected-vs-uncorrected rollback regret.
- Negative control: severity-matched ordinary physical perturbations.
- Required interpretation: higher harm on aliases for at least two feedback
  methods, without an equal degradation in the feedback-free control. If this
  fails, ISRAC remains a simulator compiler result and is not promoted to a
  WAM correction claim.

### Server-side feasibility inventory (recorded before P026 completion)

- Personal assets already present under `<PERSONAL_RESEARCH_ROOT>` include the
  FastWAM source tree, a prefix-scoped FastWAM environment, Wan base-model
  assets, all four LIBERO LeRobot datasets, and prior FastWAM checkpoints.
- The FastWAM implementation exposes an action-conditioned video path, so a
  candidate-action feedback interface can be built without downloading new
  source code or base weights.
- Existing 4500-step FastWAM weights were trained on the user's box dataset
  with `action_conditioned: false`. They are engineering assets only and must
  not be reported as a LIBERO action-conditioned WAM result.
- If P026 passes, first run a smallest action-conditioned FastWAM load/forward
  sanity after an immediate GPU-idle check. Only then train a LIBERO pilot.
- A lightweight learned latent-dynamics WAM and the FastWAM video/latent path
  should be treated as distinct held-out interfaces. Pixel and latent scores
  from one checkpoint alone do not count as two independent models.
- All new checkpoints, caches, logs, and outputs remain under
  `<PERSONAL_RESEARCH_ROOT>`; no server-side internet installation is allowed.

## P027-D: influence-separated residual router pilot

This is the corrective method, not another alias detector. It is launched only
after P027-C demonstrates measurable feedback-WAM harm.

- Infer a factorized influence distribution for the executed action and each
  future candidate over physical interfaces (for example object--support,
  gripper--object, object--container, and robot--obstacle).
- Attribute the observed WAM residual to those factors instead of attaching one
  global residual to the whole scene.
- Transport a residual component to a candidate only when the candidate's
  influence posterior overlaps the attributed factor with calibrated support.
- If support is absent or ambiguous, preserve the uncorrected VLA ranking and
  abstain/reobserve; abstention is charged and reported, not counted as success.
- Compare: no feedback, global residual transport, global uncertainty gating,
  influence-overlap routing, and an oracle influence mask upper bound.
- Primary endpoints: correction-harm reduction and rollback regret. Secondary
  endpoints: useful-correction retention, abstention rate, calibration, closed-
  loop task success, and latency.
- Kill condition: if a plain uncertainty gate or direct action scorer matches
  the router under equal data/parameters/compute, do not claim a new correction
  mechanism.

## Claim discipline

P026 can establish only a compiler-yield result against simple baselines. A
novelty score above 7/10 remains conditional on P027-A, P027-B, and P027-C (or
equally strong independently reviewed evidence). No real-robot safety claim is
authorized by these simulation experiments.
