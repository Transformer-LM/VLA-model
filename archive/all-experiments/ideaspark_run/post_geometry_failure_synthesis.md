# Post-Geometry-Failure Synthesis

**Date:** 2026-08-31  
**Scope:** exactly three bounded method candidates; no experiment run  
**Problem anchor:** a deployed π0.5 policy can execute a plausible chunk yet leave the physical task in a state inconsistent with its progress memory. The method must make the next memory update and recovery decision reliable under that divergence, using RGB and proprioception only, within 4×A100, without inventing a new action head or coordinate representation.

## Decision summary

| Candidate | Naturalness | Feasibility | Estimated novelty | Decision |
|---|---:|---:|---:|---|
| 1. Active Causal Discrepancy Experiments | **8.8** | **7.4** | **7.1–7.7** | **Winner, conditionally** |
| 2. Witness-Carrying Progress Actions | 8.9 | 8.1 | 6.8–7.5 | Retain as fallback, not novelty-cleared |
| 3. Task-Equivalent Recovery | 8.5 | 7.7 | 6.9–7.6 | Retain as fallback, not novelty-cleared |

Candidate 1 is the only winner because its estimated novelty lower bound is above 7.0 and its naturalness is at least 8.0. This assessment is conditional on the diagnostic action being selected from explicit cause-conditioned intervention predictions. If it becomes a three-class residual classifier followed by hard-coded routing, its mechanism novelty falls to roughly 6/10 and there is **no winner**.

## 1. Active Causal Discrepancy Experiments (ACDE) — winner

### Irreducible mechanism

1. When the action-conditioned WAM prediction and realized RGB/proprioceptive evidence disagree, instantiate three causal hypotheses: **A** commanded robot effect did not occur, **B** the WAM is misspecified or off-support although the task effect occurred, and **C** the current observation is aliased or insufficient. These are trained from residual-matched simulator interventions, so scalar discrepancy magnitude cannot identify the cause.
2. From a small task-safe library of reversible visual-motor probes, select one action maximizing expected information gain among the three hypothesis-conditioned next-observation distributions, subject to preserving already supported task predicates. Examples are a viewpoint-changing motion, a small observable free-space motion, or a reversible contact witness; the selected probe depends on which hypotheses remain confusable.
3. Update the causal posterior from the probe outcome and apply the corresponding state transition: **A** retract only predicates downstream of the unrealized effect and launch recovery from the last supported predicate boundary; **B** preserve observation-supported memory, conservatively update a low-rank WAM residual with the diagnostic transition plus replay anchors, and retry prediction; **C** keep the predicate pending and acquire a resolving view rather than corrupting memory or launching physical recovery.
4. Feed the corrected/pending predicate memory back through the ordinary π0.5 conditioning path. The π0.5 flow action head stays unchanged.

The diagnostic intervention is load-bearing: passive uncertainty, an ensemble, or a cause classifier is not the method.

**WAM route card:** R3 action-effect latent plus R4 explicit predicate belief; simulator intervention supervision; U4 discrepancy verification, U3 information-gathering control, and narrowly scoped U5 online WAM residual adaptation. Evaluate source-model calibration separately from intervention regret and closed-loop task recovery.

**Strongest likely overlap/objection:** [CheckVLA](https://arxiv.org/abs/2607.26789) and *When to Trust Imagination* already turn future–reality mismatch into intervention, while classical Bayesian experiment design and active perception already choose information-gathering actions; [Model-Based Runtime Monitoring](https://arxiv.org/abs/2310.17552) separates failure and OOD signals, and WAV/GTP-FA provide model/module diagnosis ancestors. A reviewer can therefore argue that ACDE is merely active fault diagnosis attached to a VLA. The answer is narrow: the contribution is the residual-matched, **interventionally identifiable** three-source decision and the demonstrated advantage of source-specific memory/WAM/recovery updates under equal apparent mismatch. Cause-naming accuracy alone would not support it.

**Cheapest non-GPU falsifier:** in a CPU simulator with privileged state, construct matched A/B/C triplets from the same pre-state and command, enumerate the safe probe library, and compute exact one-step cause information gain plus oracle downstream decision regret. Kill ACDE if no probe reduces posterior entropy by at least 0.2 bit over passive re-observation on most matched triplets, if A/B/C remain non-identifiable with deployable RGB/proprioception, or if oracle source-specific remedies do not beat one conservative recovery rule. This test precedes all neural training.

**Feasibility boundary:** freeze π0.5; train only a compact cause-conditioned effect model and WAM residual adapter on simulator interventions. Four A100s are sufficient. The main risk is data semantics, not compute: B must mean the physical postcondition is actually correct while the WAM is wrong, and C must preserve hidden state while changing observability. Mixed causes are out of the first study.

## 2. Witness-Carrying Progress Actions (WCPA)

### Irreducible mechanism

1. At an unresolved task predicate, use simulator counterfactuals to score ordinary *next-task* actions by two inseparable properties: nonnegative goal progress and how differently their observable outcomes distribute when the pending predicate is true versus false.
2. Preference-tune the unchanged π0.5 flow policy toward actions on the Pareto frontier of progress and predicate-witness value; do not add a runtime verifier gate or a separate diagnostic-only action head.
3. Execute the action and use its predicted likelihood ratio as the commit certificate: commit, keep pending, or locally retract the predicate before the following chunk.

The mechanism is dual control for task progress: the robot chooses a useful next action whose physical consequence also exposes whether its memory is correct. A no-op view change or generic uncertainty penalty is not WCPA.

**WAM route card:** R3 action-effect prediction plus R4 pending-predicate state; offline counterfactual supervision; U3 progress-with-information action shaping and U4 evidence-based memory update. Model quality and policy success must be reported separately.

**Strongest likely overlap/objection:** this sits close to active perception/dual control, [ProgressVLA](https://arxiv.org/abs/2602.23980), CheckVLA, and FlowPRO-style preference tuning. A reviewer may reasonably call it a robotics instance of information-seeking control plus preference fine-tuning. Its only defensible delta is that the information target is a *pending physical task predicate* and the selected action must simultaneously advance the original task; that is not yet enough for a novelty lower bound above 7.

**Cheapest non-GPU falsifier:** use privileged simulator predicates and exhaustive short rollouts from ambiguous boundaries. Kill WCPA if fewer than 60% of boundaries contain an ordinary progress-positive action with materially higher true/false outcome separation than the nominal next action, or if the oracle witness action does not reduce false commits/commit delay without lowering success. If only diagnostic detours carry information, this idea collapses into Candidate 1.

**Feasibility boundary:** the existing π0.5 action representation and flow head remain intact; offline labels and LoRA/preference tuning fit 4×A100. The risk is coverage: contact-rich tasks may not offer an informative, progress-positive next move at the point when memory is ambiguous.

## 3. Task-Equivalent Recovery (TER)

### Irreducible mechanism

1. In simulation, define two states as task-equivalent when they agree on supported predicates and admit the same remaining successful continuations, even if their pixels, robot pose, or object pose differ. Learn a compact equivalence test from privileged predicate/continuation labels.
2. From injected divergence states, generate recovery demonstrations to the **nearest reachable equivalence class**, preserving already completed independent predicates, rather than rolling back to an exact checkpoint or restarting the task.
3. Fine-tune the ordinary π0.5 policy on those recovery chunks and commit memory only after an RGB/proprioceptive certificate shows re-entry into the target equivalence class; then resume the original instruction.

The contribution would be semantic recovery to any continuation-equivalent state, not generic recovery data augmentation.

**WAM route card:** R3 task-equivalence latent with an R4 predicate certificate; simulator-supervised equivalence and recovery data; U3 semantic recovery target selection and U4 memory recommit. Test equivalence false-merges before policy learning.

**Strongest likely overlap/objection:** HELM/ReViP-style rollback and replanning already recover long tasks, while [goal-conditioned bisimulation](https://arxiv.org/abs/2204.13060) formalizes functional state equivalence and recovery/goal-conditioned RL already targets sets rather than exact states. A reviewer can therefore characterize TER as bisimulation-labelled recovery distillation. The VLA-specific delta—protecting completed predicates and recommitting progress only on class re-entry—is useful but not clearly new enough by itself.

**Cheapest non-GPU falsifier:** on the simulator state graph, use oracle predicates and a classical short-horizon controller to compare nearest task-equivalent recovery against exact-checkpoint rollback. Kill TER if equivalence false-merges exceed 5%, if the equivalent target is not at least 20% shorter/reachable more often under representative perturbations, or if preserving completed predicates gives no success advantage. This establishes whether the semantic target has headroom before learning an embedding or fine-tuning π0.5.

**Feasibility boundary:** oracle label generation and LoRA fine-tuning are compatible with 4×A100 and require no tactile sensing. The hard part is learning continuation equivalence without smuggling in a full task planner; keep the initial scope to tasks with explicit simulator predicates and short recovery certificates.

## Final recommendation

Advance **ACDE alone** to its non-GPU identifiability test. Do not combine it with WCPA or TER. A small E0 is justified only if the oracle probe has measurable information gain and oracle source-specific decisions reduce intervention regret. Failure of either condition means the four NO-GO pivots have not yet yielded a defensible method, and the correct result is **no winner**, not a larger stack.
