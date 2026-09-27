---
name: wam-research
description: Design, classify, and validate embodied world-model and World Action Model research. Use for literature synthesis, idea generation, novelty analysis, method comparison, experiment planning, baseline and ablation selection, or result auditing involving action-conditioned video generation, video/pixel-latent WAMs, task-centric latent dynamics, learned robotic dynamics, imagination planning, model-based reinforcement learning, VLA post-training with world models, or policy-world-model co-evolution.
---

# WAM Research

Turn an embodied world-model direction into a correctly classified, falsifiable research program. Separate representation choices from control usage, then require evidence at the world-model, policy, and environment levels.

## Core distinction

Never treat these labels as mutually exclusive:

- **Video-generative WAM** describes what is predicted or decoded.
- **Latent dynamics world model** describes the predictive representation.
- **Model-based RL** describes how a policy uses learned dynamics.

A method may be video-generative and model-based RL, or latent-dynamics and model-based RL. Classify every method on both axes before comparing it with another method. Read [references/taxonomy.md](references/taxonomy.md) for the complete classification scheme.

## Workflow

### 1. Establish the research contract

Extract or ask for only the missing items that materially affect the study:

- embodiment, task family, observation modalities, and action representation;
- offline, simulation, online-real, or mixed data access;
- intended world-model role: representation, predictor, simulator, planner, critic, or policy component;
- target VLA/policy and benchmark;
- available GPUs, wall-clock budget, environment interactions, and real-robot trials;
- primary claim and acceptable failure criterion.

Do not select a framework before the hypothesis and evidence contract are explicit.

### 2. Build an evidence map

For each seed paper or repository, record:

1. observation and prediction spaces;
2. action conditioning and action horizon;
3. training objectives and data sources;
4. policy-world-model coupling;
5. planning or RL algorithm;
6. reported metrics, baselines, and evaluation environment;
7. limitations stated by the authors versus limitations inferred independently.

Trace load-bearing claims to primary papers, official repositories, or official documentation. Use `paper-search`, `research-lit`, and `scoop-check` for current literature and prior-art verification. Do not invent citations or rely on title/abstract alone when method details affect the conclusion.

### 3. Classify the proposed route

Produce a route card using the axes in [references/taxonomy.md](references/taxonomy.md). Select and read the applicable route references:

- decoded or pixel-latent video prediction: [references/video-generative-wam.md](references/video-generative-wam.md);
- task-centric latent/state dynamics: [references/latent-dynamics.md](references/latent-dynamics.md);
- planning or policy optimization through learned dynamics: [references/model-based-rl.md](references/model-based-rl.md).

Read multiple route references for hybrid methods.

### 4. State a falsifiable hypothesis

Write the hypothesis as:

> On **population/tasks**, intervention **X** changes **mechanism M**, producing measurable effect **Y** relative to **baseline B**, while preserving **constraint C**.

Add:

- one primary endpoint;
- one mechanism diagnostic;
- one downstream control endpoint;
- a minimum effect or decision threshold;
- at least one observation that would refute the mechanism;
- the expected compute and data cost.

Reject ideas whose novelty is only a component swap without a mechanism, or whose claimed benefit cannot be separated from additional data, parameters, compute, or environment interactions.

### 5. Design staged experiments

Follow [references/experiment-design.md](references/experiment-design.md). Use this order:

1. cheapest shape and interface checks;
2. one-task overfit or oracle sanity test;
3. matched-budget pilot against the strongest reproducible baseline;
4. mechanism and negative-control experiments;
5. component ablations;
6. long-horizon and distribution-shift stress tests;
7. multi-seed benchmark evaluation;
8. simulator-to-real or real-robot validation only after earlier gates pass.

Include a model-free policy baseline, an appropriate world-model baseline, and an oracle/simulator upper bound when available. Match data, parameter scale, optimizer budget, environment steps, action horizon, and evaluation protocol unless the difference itself is the tested intervention.

### 6. Validate at three levels

Read [references/evaluation.md](references/evaluation.md) and report evidence separately:

- **Model level:** predictive accuracy, controllability, uncertainty, calibration, and long-horizon drift.
- **Policy level:** return/success, robustness, sample efficiency, and exploitation of model errors.
- **Environment level:** simulator agreement, benchmark generalization, and real-world transfer where applicable.

Do not use FVD, PSNR, SSIM, LPIPS, or latent prediction loss alone as evidence of improved robot control. Do not use imagined success alone as evidence of real success.

### 7. Audit results before making claims

Use `experiment-audit` and `result-to-claim`. Check:

- multiple seeds and uncertainty intervals;
- paired evaluation when tasks and initial states can be shared;
- cherry-picked checkpoints, tasks, videos, or seeds;
- train/evaluation leakage and benchmark contamination;
- unequal data, compute, interaction, or parameter budgets;
- policy exploitation of world-model blind spots;
- world-model evaluation on the policy distribution actually used for optimization;
- frozen-model versus co-evolution claims;
- online versus offline interaction accounting;
- failed runs and excluded samples.

Downgrade the claim when any required evidence is missing. Preserve negative results and failure boundaries in `research-wiki`.

## Output contract

Unless the user requests files, return a concise research packet inline:

1. **Route card** — classification on both axes and why.
2. **Evidence map** — nearest work, differentiator, and unresolved collision risk.
3. **Hypothesis ledger** — claim, mechanism, prediction, and refutation condition.
4. **Experiment matrix** — baselines, ablations, controls, seeds, budgets, and gates.
5. **Validation plan** — model, policy, and environment metrics.
6. **Risk register** — hallucination, drift, exploitation, distribution shift, and resource risks.
7. **Decision** — run, revise, defer, or reject, with the cheapest next discriminating experiment.

When persistence is requested, use the same headings in project Markdown files and link each result to its configuration, checkpoint, logs, dataset version, and code commit.

## Integration with installed skills

- Use `idea-discovery-robot` for broad embodied ideation; use this skill to classify and constrain WAM ideas.
- Use `paper-search`, `research-lit`, `novelty-check`, and `scoop-check` for evidence and novelty.
- Use `experiment-plan` and `experiment-bridge` after the hypothesis passes review.
- Use `openpi`, `openvla-oft`, or `cosmos-policy` only when the selected method uses that stack.
- Use `weights-and-biases` for run lineage and matched comparisons.
- Use Isaac Lab skills only when Isaac Lab is part of the chosen experimental environment.

Do not launch two research orchestrators for the same stage. The active top-level workflow owns state and resources; this skill supplies WAM domain decisions without launching another orchestrator.

## Sources and framework routing

Read [references/sources.md](references/sources.md) before recommending a current implementation. Verify mutable capabilities against primary repositories or official documentation at task time.

## Failure diagnosis and experiment feedback

Read [references/failure-diagnosis.md](references/failure-diagnosis.md) when interpreting failed training or rollouts. Return expected outcome, observed evidence, ruled-out explanations, remaining uncertainty, and the next discriminating experiment. Preserve inconclusive outcomes. Select required evidence per claim using the evaluation reference; justify non-applicable endpoints.
