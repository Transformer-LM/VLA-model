# Post-SCWC Candidate Naturalness Screen

**Date:** 2026-08-31  
**Scope:** exactly three mechanism-level survivors  
**Constraints:** frozen π0.5/VLA and frozen WAM are sufficient for E0; RGB + proprioception only; no tactile; no experiment launched  
**Admission rule:** estimated novelty lower bound must be strictly above 7.0

## Screening result

| Candidate | Naturalness | E0 feasibility | Provisional novelty | Admission |
|---|---:|---:|---:|---|
| 1. Controllability-Phase Progress Certificates | **8.8** | **8.2** | **7.2–8.0** | Admit |
| 2. Policy-Conditional Correction Slack | **8.6** | **8.0** | **7.2–7.9** | Admit |
| 3. Endogenous Suffix Witnesses | **8.7** | **7.8** | **7.1–7.7** | Admit, highest migration risk |

These are narrow, provisional intervals rather than novelty acquittals. The lower bounds apply only to the exact mechanisms below. A generic classifier, confidence gate, WAM reranker, memory module, or recovery wrapper does not inherit them.

Two tempting families were screened out before this list: reversible-cycle WAM consistency now has a direct 2026 collision in [WorldCycle](https://arxiv.org/abs/2608.04964), and direct-versus-composed dynamics already has an explicit [semigroup-consistency diagnostic](https://arxiv.org/abs/2605.26324). Neither is repackaged below.

## 1. Controllability-Phase Progress Certificates (CPPC)

### Exact mechanism

1. Around an executed π0.5 chunk, form a fixed, task-safe basis of small action perturbations. The perturbations are **imagined only**: a frozen action-conditioned WAM predicts the corresponding object/task-feature displacements, and their finite differences form a local action→effect matrix.
2. Extract the matrix rank, principal subspace, and nullspace. Commit a contact-mediated progress predicate only when the observed change matches its expected controllability phase change—for example, grasp acquisition makes object motion locally controllable by gripper motion, while insertion removes lateral object-motion modes.
3. If later execution contradicts the certificate, find the most recent predicate whose required action→effect subspace is absent, retract that predicate and its causal descendants, and return the corrected progress state to the unchanged π0.5 conditioning path.

The perturbations are not candidate actions and are never reranked or executed. The contribution is a physical certificate for progress, not a better planner.

### WAM route

R3/R4 action-effect dynamics used as a U3 diagnostic without action selection; frozen policy, frozen WAM, simulator-labelled E0. Model-level endpoint is WAM/oracle controllability-subspace agreement; policy-level endpoint is false progress-commit reduction.

### Strongest cross-domain nearest work

The closest mechanism families are nonlinear/local controllability analysis, empowerment, contact-mode estimation, and learned skill precondition/effect models. [Black-box reachability safety layers](https://arxiv.org/abs/2204.07417) also estimate action-conditioned reachable effects, but use them to block unsafe trajectories. Classical contact-state estimators infer task phase from force, trajectories, or state classifiers.

### Why this is not merely an application migration

CPPC does not import controllability as a generic exploration or safety score. It makes a narrower, falsifiable robotics statement: **a semantic contact-progress event should coincide with a specific phase transition in the local controlled object dynamics**, and that transition can serve as an RGB/proprioceptive progress certificate. The output is neither a reachable-set planner nor a scalar uncertainty measure; it is the predicate-specific rank/subspace change used for selective progress correction.

The strongest objection is scope: many semantic predicates do not change local controllability, and video/latent WAMs may be least accurate at the contacts where the certificate is supposed to help. The initial claim must therefore be limited to contact-mediated predicates such as grasp, release, insertion, attachment, and constrained placement.

### Fastest kill test

Take 50–100 simulator-certified matched pre/post/false-positive states for two contact events. Apply the same 6–12 small safe perturbations in the simulator and frozen WAM; compare action→object-effect subspaces by principal angle and rank.

Kill CPPC immediately if:

- the **oracle simulator** signatures do not separate true versus false event states at AUROC ≥0.85;
- frozen-WAM subspace agreement with the oracle is below 0.70 on both events;
- a current-frame RGB/proprio predicate classifier matches the certificate on held-out perturbations;
- the effect exists for only one hand-designed event.

This E0 needs only frozen forward passes and short simulator branches; 4×A100 is ample.

## 2. Policy-Conditional Correction Slack (PCCS)

### Exact mechanism

1. Clone a simulator state and flip exactly one progress predicate in the conditioning presented to a frozen π0.5, leaving the physical state unchanged. At candidate intervention times `τ`, replace the false predicate with the oracle value and continue the same frozen policy. Binary-search the last `τ` at which this **memory edit alone** still recovers the oracle-memory success outcome.
2. From frozen WAM future features, fit a small survival/readout model for the remaining correction slack of each predicate: how many executable chunks remain before that memory error becomes behaviorally irreversible under this policy.
3. During deployment, spend a predicate recheck before predicted slack falls to the execution horizon; if the evidence overturns the predicate, edit the progress state and continue π0.5. There is no learned recovery policy and no generic failure probability.

The label is a causal deadline for correcting a specific memory error, not “will the robot fail?”

### WAM route

R3/R4 future task-state features used for U4 execution scheduling; policy and WAM frozen. Model endpoint is slack calibration; policy endpoint is success at a fixed number of rechecks, compared with immediate and periodic verification.

### Strongest cross-domain nearest work

The closest ancestors are viability kernels, last-safe-intervention analysis, survival/hazard models, and prospective runtime monitoring. [Model-Based Runtime Monitoring](https://arxiv.org/abs/2310.17552) forecasts risky future states, while [B2FF](https://arxiv.org/abs/2606.09258) studies recoverable VLA deviations through pre-imagined milestones. Neither, from the checked formulations, labels the last effective time of a *counterfactual progress-memory edit* under a frozen VLA.

### Why this is not merely an application migration

PCCS changes the supervised object. Physical viability methods ask whether the current state remains safe/reachable; survival models ask when failure occurs. PCCS intervenes on an internal semantic predicate while holding the physical state fixed and defines the deadline by the resulting **policy-level causal effect**. Thus two identical scenes can have different slack solely because the policy has been told different progress. This policy-conditional memory intervention is the irreducible mechanism.

The strongest objection is that “last correctable time” may not exist as a stable scalar: stochastic policies can alternate between correctable and uncorrectable regions, and the deadline depends on the frozen policy, task horizon, action seed, and memory interface.

### Fastest kill test

Before training any readout, use 50 simulator snapshots with one oracle predicate flip. Evaluate 5–8 intervention times under common random numbers and three policy seeds.

Kill PCCS immediately if:

- correctability is non-monotone in intervention time for more than 20% of snapshots;
- the deadline ordering agrees across policy seeds on fewer than 70% of snapshots;
- an oracle slack scheduler fails to beat immediate verification and fixed-period verification by at least 5 success points at the same recheck budget;
- editing the memory token has little causal effect on π0.5 actions or final success.

This is a simulator-oracle E0; no model or policy training is required for the kill decision.

## 3. Endogenous Suffix Witnesses (ESW)

### Exact mechanism

1. Build simulator pairs with matched current RGB/proprioception and identical task instruction but opposite truth for one progress predicate. From that shared observation, sample ordinary short continuation suffixes from frozen π0.5; execute each same suffix in both hidden states under coupled randomness.
2. Find the earliest downstream observable event whose distribution separates the two predicate states across the **policy-supported suffix distribution**. Compile that event and its time window as a predicate-specific witness; discard witnesses that require an unsafe or diagnostic-only action.
3. At deployment, π0.5 continues normally. The predicate remains pending until the witness associated with the realized action prefix appears or is decisively absent, at which point the system commits or retracts it. No extra probe, candidate reranking, or generic discrepancy threshold is introduced.

The physical task's own continuation turns a currently hidden progress fact into observable evidence.

### WAM route

R3/R4 action-conditioned futures used as a U4 passive monitor; simulator validates witness labels, while VLA and WAM stay frozen. Model endpoint is witness likelihood/separation; policy endpoint is false commit and unnecessary interruption at fixed execution cost.

### Strongest cross-domain nearest work

The closest theory is predictive-state representation and automata conformance testing: histories are distinguished by their responses to future action-observation tests. [Closing the Learning–Planning Loop with Predictive State Representations](https://arxiv.org/abs/0912.2385) learns a full predictive state for planning. The Nerode/distinguishing-sequence viewpoint is therefore a serious mechanism-level ancestor; delayed postcondition monitors and EventVLA-like execution-state work are the robotics neighbors.

### Why this is not merely an application migration

ESW does not learn a general PSR, automaton, or new memory architecture. It compiles the **minimal passive, executable witness for one externally meaningful task predicate**, constrained to the continuation distribution of a fixed VLA and validated in the physical simulator. Its scientific question is whether ordinary task execution can provide free evidence for progress facts that are unobservable at the current frame. The method is invalid if it needs a special information-gathering action; that would collapse into excluded active diagnosis.

This remains the highest application-migration risk of the three. A reviewer can argue that it is a policy-restricted distinguishing sequence. The novelty lower bound stays above 7 only for the paired hidden-state construction, passive witness constraint, and demonstrated long-horizon memory correction together; “PSR for VLA” would score below the gate.

### Fastest kill test

Use 50–100 matched hidden-state pairs and 16 cached π0.5 suffixes per pair. With privileged simulator truth, search for an RGB/proprio event reaching AUROC ≥0.85 within two chunks and before either suffix becomes unsafe.

Kill ESW immediately if:

- fewer than 60% of matched pairs admit such a passive witness;
- the witness arrives only after the false predicate has already caused irreversible task loss;
- a history-only classifier without suffix conditioning matches witness accuracy;
- useful separation requires choosing a special diagnostic suffix rather than following ordinary π0.5 support.

The first test can cache frozen forward passes and short simulator rollouts; no finetuning is needed.

## Comparative recommendation

1. **CPPC first:** strongest physical mechanism and clearest separation from generic monitoring; E0 can fail cheaply at the oracle-signature level.
2. **PCCS second:** directly measures when a progress error matters, but only viable if correction-time monotonicity is empirically real.
3. **ESW third:** most natural for partial observability, but it must survive the strongest “predictive-state application” objection.

Do not combine them before their individual oracle tests pass. CPPC certifies *what physical event occurred*, PCCS measures *when a memory error must be corrected*, and ESW identifies *which ordinary future observation will reveal an uncertain event*. A combined stack would obscure which scientific claim is supported.

## Evidence boundary

The search was intentionally bounded to recent WAM/VLA work and the strongest cross-domain mechanism ancestors. The absence of a direct title match is not proof of novelty; all three require a dedicated full-paper scoop check before implementation. No experiment, model training, GPU job, or simulator rollout was started for this screen.
