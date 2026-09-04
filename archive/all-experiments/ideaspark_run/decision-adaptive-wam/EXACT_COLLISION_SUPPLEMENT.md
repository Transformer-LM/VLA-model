# Exact collision supplement (web-verified, 2026-08-30)

The structured Phase-0 connectors were degraded: arXiv returned SSL EOF, Semantic Scholar recent search returned 429, and host-reference resolution admitted 0/8 even though direct arXiv pages verified the records below. The full-text fetch also succeeded for 0/11 selected records. Therefore the absence of these works from `lit_results.json` is not evidence of novelty.

## RISE: Adaptive Imagination for World Action Models

- Primary record: https://arxiv.org/abs/2608.20430
- Submitted: 2026-08-20.
- Exact mechanism: a sequential `Roll/Stop` controller for WAM imagination. At each rollout prefix, a Latent Evaluator estimates currently revealed risk and expected future planning gain; a Rollout Gate weighs expected benefit against computation cost to choose a scene-dependent horizon.
- Collision: directly occupies adaptive WAM rollout horizon/value-of-computation. Restricting the application from driving to manipulation is domain transfer, not a new mechanism.

## VLA-ATTC: Adaptive Test-Time Compute for VLA Models with Relative Action Critic Model

- Primary record: https://arxiv.org/abs/2605.01194
- Submitted: 2026-05-02; revised 2026-05-28.
- Exact mechanism: an uncertainty-based cognitive clutch switches a VLA from reflexive execution to additional test-time candidate generation; a Relative Action Critic chooses among candidates using pairwise comparisons. Evaluated with π0.5 on LIBERO-LONG.
- Collision: occupies adaptive VLA compute/candidate selection and relative action-ranking decisions.

## When and How Much to Imagine

- Primary record: https://arxiv.org/abs/2602.08236
- Submitted: 2026-02-09; revised 2026-05-31.
- Exact mechanism: AVIC decides whether current visual evidence is sufficient and when/how much to invoke a world model; AVIC-R learns the policy with correctness reward minus imagination cost.
- Collision: occupies selective world-model invocation and scaling, including embodied navigation.

## When to Trust Imagination

- Primary record: https://arxiv.org/abs/2605.06222
- Submitted: 2026-05-07.
- Exact mechanism: future–reality consistency controls how many WAM-predicted actions are executed before replanning. This is adaptive execution rather than adaptive WAM-generation compute, so it is a boundary paper, not complete subsumption.

## Decision implication

The original direction—dynamically allocate rollout horizon, representation fidelity, candidate count, or tokens only when additional imagination is expected to change the executed action decision—has no defensible novelty above 7 as stated. RISE covers expected planning gain versus cost; VLA-ATTC covers adaptive candidate compute and pairwise action critics; AVIC covers invocation amount. A candidate must introduce a distinct load-bearing variable and mechanism, not combine these three.
