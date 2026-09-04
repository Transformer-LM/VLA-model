# Literature Map — Long-Horizon VLA Progress, Verification, and Recovery

Search date: 2026-08-24 (Asia/Shanghai)

## Scope and queries

The map covers VLA memory, task-progress estimation, task-state belief, postcondition verification, failure detection/recovery, counterfactual evaluation, and optional WAM action-effect prediction. Main query families:

1. `vision language action long horizon task memory progress recovery`
2. `VLA history memory long horizon manipulation`
3. `world model episodic memory robot failure recovery action chunk`
4. `retractable task belief robot manipulation progress verification`
5. `calibrated subtask completion vision language action long horizon`
6. `observation aliasing history dependent VLA benchmark`
7. `world action model outcome verification failure recovery memory`
8. exact-title and citation-chain searches for π0.5, MemoryVLA, HAMLET, KEMO, Goal2Skill, LoHo-Manip, ProgressVLA, RB-VLA, μVLA, and task-progress probes.

Sources: arXiv, OpenAlex, Crossref, DBLP, OpenReview, Semantic Scholar, primary project/publisher pages, and locally extracted full papers. Semantic Scholar repeatedly returned HTTP 429; DBLP and some OpenAlex requests had transient 429/504/TLS errors. These failures are recorded as coverage limitations rather than treated as negative evidence.

## Evidence clusters

### C1. Reactive π0.5 and hierarchical semantic control

- **π0.5** (arXiv:2504.16054) predicts a semantic subtask and then a low-level action chunk, but its formal inputs center on current observation and instruction rather than a persistent verified task state. The public OpenPI release does not automatically reproduce every high-level inference component from the paper.
- Implication: the user's observed long-horizon failure may be a missing task-management interface rather than an action-head defect.

### C2. Generic history and memory

- **MemoryVLA** (arXiv:2508.19236, ICLR 2026) retrieves perceptual and cognitive memories.
- **HAMLET** (arXiv:2510.00695, ICLR 2026) isolates recurrent history tokens and shows that naive frame concatenation is weak.
- **KEMO** (arXiv:2606.23589) stores kinematically detected task-event keyframes and reports gains over a memory-free π0.5 baseline.
- **μVLA** (arXiv:2606.12497) isolates minimal recurrence. It improves in-distribution partial-observability tasks but transfers poorly to tasks with different memory semantics and is not intended for arbitrary horizons.
- Consensus: history matters. Contradiction/limit: retaining history does not ensure correct task-state semantics or transfer.

### C3. Semantic planning and explicit progress memory

- **Explicit Language Memory** (arXiv:2608.04765) recursively stores completed stages, current state, failure, and next intent. Its real-robot evidence is short, and the paper states that language memory cannot compensate for low-level control or missing recovery data.
- **LoHo-Manip** (arXiv:2604.21924) maintains completed/remaining plans and visual traces in receding horizon; limitations include reliance on task grounding and a 2D trace inadequate for precise/contact-rich interaction.
- **Goal2Skill** (arXiv:2604.13942) combines structured memory, outcome verification, an error register, reflection, and recovery. Its full-paper evaluation is limited to five RMBench tasks, with modest absolute recovery success in hard cases.
- Collision: generic `memory + verifier + replan/recovery` is already occupied.

### C4. Progress estimation and internal progress signals

- **TaKSIE** (arXiv:2410.11013; WACV 2025) uses recurrent visual progress representations for subgoal image generation.
- **ProgressVLA** (arXiv:2603.27670) regresses normalized scalar progress, predicts future latent states with an inverse-dynamics world model, and guides action diffusion toward larger predicted progress.
- **Decoding Task Progress from VLA Representations** (arXiv:2608.13474) linearly probes π0.5 progress and uses deviations as an OOD/stall detector. The paper explicitly notes that normalized time conflates elapsed time with semantic completion and that the signal is not meaningfully steerable.
- **ProgVLA** (arXiv:2605.28231) adds progress heads and progress-aware policy learning.
- Gap: scalar monotonic progress cannot represent branching prerequisites, reversible achievements, or uncertainty over which stage is active.

### C5. Learned belief and partial observability

- **RB-VLA** (arXiv:2602.20659) maintains a compact action-conditioned latent belief trained with RSSM-style world objectives and targets perceptual aliasing. It already blocks `add a recurrent latent belief` as a standalone novelty.
- **μVLA** and **MIKASA-Robo** demonstrate that memory semantics, not only memory capacity, determine generalization.
- Gap: current latent belief work does not expose evidence lineage, calibrated predicate-level uncertainty, dependency-aware retraction, or correctness of rollback after false completion.

### C6. Verification, monitoring, and recovery

- **RACER** (arXiv:2409.14674) adds perturbed failure/recovery demonstrations with rich language.
- **TCoT** (AAAI 2026, DOI:10.1609/aaai.v40i8.37577) combines global/local trajectories with failure detection and recovery.
- **World Action Verifier** (arXiv:2604.01985) verifies state plausibility and action reachability in underexplored world-model regions.
- **When to Trust Imagination** (arXiv:2605.06222) compares predicted and realized futures to adapt execution chunks and replan.
- Gap: detection, task-state correction, and recovery competence are usually trained/evaluated together, obscuring which mechanism causes the gain.

## Nearest-work collision matrix

| Candidate contribution shape | Closest work | Collision |
|---|---|---|
| Add visual/keyframe memory to π0.5 | KEMO, MemoryVLA, HAMLET | Direct; reject |
| Add recurrent latent belief | RB-VLA, μVLA | Direct; reject |
| Estimate scalar progress | ProgressVLA, ProgVLA, π0.5 progress probe | Direct; reject |
| Language summary of completed steps | Explicit Language Memory, LoHo-Manip | Direct; reject |
| Structured memory + verifier + recovery | Goal2Skill, TCoT | High; insufficient alone |
| WAM predicts future and reranks actions | ProgressVLA, WAV, When to Trust Imagination | High; must prove a different role |
| Evidence-linked, multi-hypothesis, retractable task state evaluated on history-counterfactual twins | No full match found | Open but vulnerable to RB-VLA, Goal2Skill, POMDP/belief-space planning |

## Decisive unresolved evidence

1. Oracle current-subtask and oracle completion labels must materially improve the reproduced VLA; otherwise progress memory is not the bottleneck.
2. Paired same-observation/different-history states must produce different correct next decisions; a current-frame policy should fail by construction.
3. A method must recover from a deliberately false completion write and retract dependent downstream state, not merely retain more history.
4. Structured task-state gains must survive matched parameter, data, inference-call, and recovery-demonstration budgets.
5. Any WAM variant must outperform a discriminative verifier and geometry/VLM baselines on calibration and downstream decision quality, not only prediction loss.

## Working gaps carried into ideation

- G1 oracle-progress headroom.
- G2 structured non-monotonic task state versus scalar progress.
- G3 evidence-grounded retraction of wrong memory.
- G4 counterfactual history-identifiability protocol.
- G5 necessity of WAM for outcome verification.
- G6 separation of detection/state correction from recovery-data coverage.
