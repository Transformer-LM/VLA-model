# WAM Route Card — Long-Horizon Progress, Verification, and Recovery

## Research contract

- Population: long-horizon, multi-stage robot manipulation episodes in which the same current observation may require different actions because completed stages or prior failures differ.
- Base executor: a reproducible action-chunk VLA, initially π0.5 because the user already has a working reproduction; a second VLA is permitted only to test backbone-independence.
- Observations: RGB, language, and proprioception; force/tactile are optional evidence channels rather than assumptions.
- Primary failure decomposition: history forgetting, progress misclassification, low-level motor failure, action-chunk monitoring failure, and recovery-policy failure.
- WAM role: optional action-effect predictor or verifier. A WAM will be rejected if a matched VLM, geometric postcondition model, or learned discriminative verifier provides the same benefit.
- Data regime: existing demonstrations and logged rollouts first; controlled simulation or real-robot perturbations may later provide failure/recovery evidence under a separate execution gate.

## Route classification

The direction permits three routes that must be compared rather than conflated:

1. No-WM baseline: frozen VLA plus explicit task-state tracker or memory.
2. R4 + U3: explicit task/postcondition state model used for candidate or outcome verification.
3. R2/R3 + U3/U4: pixel-latent or task-latent action-effect model used to compare imagined and realized outcomes, then update task belief or replan.

The selected Idea must state which route it uses. Video decoding alone is not a contribution, and model-based RL is out of scope unless the policy is actually optimized through learned dynamics.

## Falsifiable hypothesis shape

> On memory-dependent long-horizon manipulation tasks, replacing append-only history with an evidence-gated task state that can retain uncertainty and retract previously asserted completion will reduce false stage advancement and improve paired end-to-end success relative to matched memory and progress-planning baselines, without relying solely on extra data, parameters, or inference calls.

Primary endpoint: paired task success under controlled ambiguous-history and injected-failure conditions.

Mechanism diagnostic: false-progress rate, belief calibration, and successful rollback after contradictory evidence.

Downstream endpoint: recovery success and unnecessary-retry rate.

Refutation: an oracle progress label does not materially improve the base VLA; or a matched append-only memory/verifier attains the same false-progress and task-success results.

## Open choices for evidence map

- Whether task belief should be symbolic, language-valued, object-relational, or learned latent.
- Whether verification should use discriminative postconditions, geometry, VLM reasoning, or WAM action-effect prediction.
- Whether the strongest publishable contribution is a method, diagnostic benchmark, training objective, or calibrated selective-execution protocol.
- Which public task suite exposes genuine observation aliasing, reversible progress, and recoverable failures without confounding low-level competence.

## Hard exclusions

- Raw frame concatenation, ordinary RNN/Transformer memory, generic keyframe storage, or rolling text summaries as the sole novelty.
- Generic planner–executor decomposition or verifier–replan loops without a new measurable mechanism.
- Claims based only on memory reconstruction, future-video quality, or imagined success.
