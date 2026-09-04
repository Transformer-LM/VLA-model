# Strict Novelty Gap Audit — Active Causal Discrepancy Diagnosis (ACDD)

**Audit date:** 2026-08-31  
**Literature cutoff:** 2026-08-31  
**Verdict:** **FAIL / NO-GO under the strict novelty gate**  
**Novelty:** **6.90 / 10**  
**Required gate:** strictly greater than 7.0; 7.0 itself fails.  
**Naturalness:** **7.55 / 10**  
**Feasibility:** **6.25 / 10**  
**Scoop-check verdict:** **Level 2 — High Overlap**  
**Non-GPU dataset/oracle E0:** **Not authorized for the present candidate.**

## 1. Exact proposal audited

After a π0.5/VLA action prefix is executed, an action-conditioned WAM prediction disagrees with the observation. ACDD rejects the assumption that one scalar discrepancy identifies execution failure. It maintains three causal hypotheses:

- **E — execution failure:** actuation, interaction, or physical execution did not produce the intended effect;
- **M — model failure:** the WAM is misspecified, out of distribution, or locally wrong;
- **P — perception ambiguity:** the observation is insufficient or corrupted by occlusion/viewpoint ambiguity.

Each hypothesis defines a distribution over observable outcomes. On a discrepancy event, the robot chooses one bounded diagnostic action from a small safe set—viewpoint shift/reobserve, no-op or calibration pulse, guarded retreat—to maximize expected information gain over E/M/P minus task risk. It then updates the hypothesis posterior and routes downstream state updates:

- E retracts affected progress predicates and invokes recovery;
- M preserves task memory while locally discounting/adapting the WAM;
- P updates the visual belief without declaring execution failure.

The intended empirical signature is improved causal attribution and fewer false progress-memory corruptions **at matched initial residual**, rather than merely better binary failure detection.

## 2. Four-axis decomposition

### Problem framing

Runtime root-cause isolation after a VLA/WAM future–reality mismatch, where a similar residual may be caused by the robot, the learned world model, or ambiguous visual evidence. The system is evaluated not only on diagnosis but on whether wrong diagnosis corrupts long-horizon task memory.

### Core mechanism

Hypothesis-conditioned counterfactual observation models; a safe diagnostic intervention chosen by expected information gain minus task cost; Bayesian posterior update after the intervention; hypothesis-specific recovery and memory-update routing.

### Key insight

Passive residual magnitude is not causally identifying. A deliberately chosen physical probe can make competing explanations observationally distinguishable, and diagnosis must affect which long-horizon beliefs are retracted.

### Application domain

Vision-based VLA/WAM robotic manipulation, including chunked policy execution, runtime verification, recovery, and persistent task-progress memory. No tactile sensing is assumed.

## 3. Search scope and evidence rule

The audit searched the following mechanism signatures and then verified high-threat candidates on primary paper pages/full text:

1. `VLA WAM execution verification recovery discrepancy memory`;
2. `robot active fault diagnosis information gain probing action model uncertainty`;
3. `counterfactual fault hypotheses active control Bayesian update robot perception`;
4. `world model discrepancy execution failure model error perceptual ambiguity`;
5. the exact named systems Guardian, GTP-FA, CheckVLA, and When to Trust Imagination.

The unified paper-search arXiv connector encountered an SSL failure, while Semantic Scholar was partially rate-limited. This was not treated as negative evidence. High-risk candidates were instead verified on official arXiv HTML/abstract pages and, for s-FEAST, the primary Science Robotics article. This report therefore does **not** claim exhaustive proof that no exact paper exists.

## 4. Most important primary-source evidence

| Work | Exact mechanism verified | Relationship to ACDD | Threat |
|---|---|---|---:|
| [A Counterfactual Reasoning Framework for Fault Diagnosis in Robot Perception Systems](https://arxiv.org/abs/2509.18460), [full HTML](https://arxiv.org/html/2509.18460) | Maintains counterfactual fault hypotheses with hypothesis-specific reliability-test distributions; selects control inputs maximizing weighted Effective Information minus mission-deviation penalty; observes the result and updates hypothesis weights with Bayes' rule. It evaluates sensor damage, dynamic scenes, and visually deprived conditions. | This is almost the complete ACDD diagnosis algorithm with different hypothesis names and a navigation/perception application. It does not use a VLA/WAM residual and does not study task-memory corruption. | **Fatal mechanism-level neighbor.** |
| [Online tree-based planning for active spacecraft fault estimation and collision avoidance](https://doi.org/10.1126/scirobotics.adn4722) | s-FEAST maintains beliefs over physical and fault states and selects actions that resolve fault ambiguity while satisfying probabilistic safety constraints. It handles ambiguous actuator and sensor faults with online belief-space tree search. | Covers safe active fault diagnosis, posterior inference, and risk-aware diagnostic action selection. It does not address WAM misspecification or VLA progress memory. | **Fatal cross-domain active-diagnosis neighbor.** |
| [CheckVLA](https://arxiv.org/abs/2607.26789) | Uses a frozen action-conditioned world model for execution-time future–reality verification, conformally calibrated intervention risk, action-suffix rewriting, and an event-driven keyframe bank that preserves prior progress evidence across repairs. | Occupies WAM-based discrepancy monitoring, intervention, repair, and memory preservation, but treats excess risk as a trigger rather than diagnosing whether the cause is execution, WAM, or perception. | Strong VLA/WAM neighbor. |
| [When to Trust Imagination](https://arxiv.org/abs/2605.06222) | FFDC jointly reasons over predicted actions, predicted visual dynamics, actual observations, and language to determine whether the remaining WAM rollout is trustworthy, enabling adaptive action-chunk length and earlier replanning. | Passive trust estimation rather than active root-cause isolation. | Strong binary/trust baseline. |
| [Guardian](https://arxiv.org/abs/2512.01946) | Synthesizes diverse planning and execution failures and trains a multi-view reasoning VLM for fine-grained failure categories and step-by-step failure reasoning; improves downstream recovery. | Establishes fine-grained planning/execution failure attribution and failure-data synthesis, but performs passive visual diagnosis and does not separate WAM error from physical execution failure. | Strong attribution/data baseline. |
| [GTP-FA](https://arxiv.org/abs/2606.03385) | Learns a distribution over failure modes for failed manipulation trajectories and routes diagnosis to grasp-side or planning-side optimization. | Establishes diagnosis-specific downstream routing, but only between grasping and planning, without active probes or WAM/perception hypotheses. | Strong routing baseline. |
| [Model-Based Runtime Monitoring with Interactive Imitation Learning](https://arxiv.org/abs/2310.17552) | Uses latent action-conditioned dynamics, OOD detection, and a failure classifier to anticipate failures and solicit human intervention while models continue to improve from deployment data. | Covers model-based runtime monitoring and distinction between OOD and predicted failure, but not active causal diagnosis or autonomous memory routing. | Moderate-high monitoring neighbor. |
| [Failure Detection for Surgical Robot Imitation Policies via Flow-Matching World Modeling](https://arxiv.org/abs/2607.27511) | Detects action–observation inconsistencies through inverse-transport nonconformity under a flow-matching world model and conformally calibrates alarms without failure data. | A strong scalar/nonconformity baseline that ACDD explicitly aims to surpass; no causal attribution. | Moderate monitoring neighbor. |
| [EvoScene-VLA](https://arxiv.org/abs/2605.21862) | Maintains a persistent action-updated scene prior across action chunks and corrects it against fresh visual evidence. | Occupies action-updated scene belief and correction, but not cause attribution or diagnostic actions. | Strong memory neighbor. |
| [Goal2Skill](https://arxiv.org/abs/2604.13942) | A VLM manager maintains structured task memory, verifies outcomes, and performs error-driven correction around a VLA executor. | Occupies structured memory, verification, and recovery; diagnosis is not a causal WAM intervention problem. | Moderate-high memory/recovery neighbor. |
| [Do Robotic World Models Really Follow Actions?](https://arxiv.org/abs/2608.24885) | WorldEcho diagnoses failures of WAM action following beyond expert trajectories; WorldSync improves distributional coverage, action grounding, and intervention-effect alignment. | Directly establishes WAM misspecification/action-following failure as a real alternative to robot execution failure, but addresses it offline rather than attributing runtime discrepancy. | Important support and WAM-model baseline. |
| [Robot Action Diagnosis and Experience Correction by Falsifying Parameterised Execution Models](https://arxiv.org/abs/2105.09599) | Diagnoses execution failures by falsifying learned precondition models and uses diagnosis to correct/generate experience for policy improvement. | Establishes the diagnosis-to-targeted-adaptation pattern; no active information-gathering probe or WAM. | Moderate historical neighbor. |

## 5. The exact fatal overlap

The strongest reviewer objection can be stated precisely:

> ACDD instantiates Han et al. (arXiv:2509.18460) by setting the fault hypotheses to δ = {execution failure, WAM failure, perceptual ambiguity}, the reliability tests to WAM prediction–observation features, the admissible controls to a small safe probe set, and the mission-deviation penalty to manipulation risk; the post-probe Bayes update is the same, followed by an application-specific switch over memory and recovery actions.

This is not a vague thematic resemblance. Han et al. already use:

\[
u^*=\arg\max_{u\in\mathcal U}\left(\sum_i w_i\,\mathrm{EI}(u\mid\delta_i)-\lambda P(u)\right),
\]

followed by

\[
w_i'\propto w_i\,p(r'\mid \mathrm{do}(u),\mathrm{do}(\delta_i)).
\]

Those are the central two algorithmic moves in ACDD: choose an intervention for diagnosis under task cost, then update the causal-hypothesis posterior from its outcome. s-FEAST independently establishes safe active fault estimation over actuator and sensor fault beliefs.

Therefore the claim **“active causal discrepancy diagnosis by information-gathering robot actions” is already occupied**. Moving it into VLA×WAM is scientifically relevant, but under a strict novelty review it is an application transfer unless the VLA/WAM setting exposes and solves a genuinely new identifiability problem.

## 6. What remains coherent and different

ACDD still has a real, coherent residual delta:

1. **The hypotheses cross the policy–world-model–perception boundary.** Existing active FDI usually isolates components inside a known sensing/control system; ACDD asks whether disagreement indicts the physical execution, the learned predictive model, or the observation.
2. **Matched-residual interventions are a strong evaluation design.** Cases with similar initial residual but different causal source prevent a threshold or classifier from exploiting severity.
3. **The downstream cost is false task-memory corruption.** ACDD evaluates whether a wrong alarm retracts a genuinely completed predicate or triggers unnecessary recovery, not merely fault-classification accuracy.
4. **The probe vocabulary is deliberately bounded and manipulation-native.** The method does not launch generic exploration or an unconstrained recovery planner.

One-sentence defensible delta:

> Unlike Han et al., which actively isolates faults within a robot perception pipeline and stops at fault identification, ACDD applies diagnostic interventions to distinguish physical execution, learned-WAM, and visual-evidence causes of the same VLA/WAM residual, then measures whether cause-specific routing prevents false corruption of persistent manipulation progress memory.

This is crisp, but its novelty is largely in **problem definition, controlled evaluation, and downstream consequence**, not in the active-diagnosis algorithm.

## 7. Component overlap versus joint contribution

| ACDD component | Already occupied by | Residual contribution |
|---|---|---|
| Hypothesis-specific observable predictions | Counterfactual FDI | E/M/P are specific to the VLA–WAM–perception stack. |
| Information-gain diagnostic intervention | Counterfactual FDI, s-FEAST, dual control | Small manipulation-native probe vocabulary. |
| Task-risk penalty on probes | Counterfactual FDI and safe active fault estimation | Concrete manipulation risk definition. |
| Bayesian update after probe | Counterfactual FDI, belief-space active diagnosis | No meaningful generic algorithmic delta. |
| Fine-grained failure attribution | Guardian, GTP-FA, classical FDI | Includes WAM misspecification as a first-class cause. |
| WAM discrepancy trigger | CheckVLA, When to Trust Imagination, FoMo-FD | Attribution rather than binary intervention/trust. |
| Persistent scene/task memory | CheckVLA, EvoScene-VLA, Goal2Skill | Memory-integrity objective conditioned on diagnosis. |
| Cause-specific response | GTP-FA and standard fault isolation/recovery | Explicit preservation versus retraction of progress predicates. |
| Matched-residual evaluation | No exact match verified in the audited set | Strongest potentially publishable dataset/evaluation delta. |

The union is natural, but most interactions are direct: diagnose using an established active-FDI formulation and then select an established recovery/update branch. The memory-integrity metric raises the scientific value, but it does not by itself create a new diagnosis algorithm.

## 8. Naturalness audit

### Why the problem is natural

- CheckVLA, When to Trust Imagination, and FoMo-FD make decisions from future–reality mismatch; their false interventions are a real deployment risk.
- WorldEcho/WorldSync supplies direct evidence that action-conditioned WAMs themselves can ignore or misrender valid off-expert actions. A WAM residual therefore cannot safely be interpreted as robot failure.
- Long-horizon VLA systems increasingly maintain persistent progress/scene state. Incorrectly retracting or overwriting that state can cause repeated subtasks, unsafe recovery, or compounding plan errors.
- Active interventions are causally appropriate when passive observations are observationally equivalent.

### Why the proposed three-way routing is not yet fully natural

1. **E, M, and P are not mutually exclusive.** A slip can occur under occlusion while the WAM is also out of distribution. A single categorical posterior may force a false explanation.
2. **Cause does not determine task state.** `M` means the WAM is unreliable; it does not imply that the commanded physical effect succeeded. Unconditionally preserving progress memory under M is therefore not causally valid. `P` likewise means the observation is ambiguous, not that the progress predicate is true.
3. **The WAM is used to diagnose its own misspecification.** If the probe outcome model relies on the same WAM under hypothesis M, expected information gain can be circular and confidently wrong. The hypothesis likelihoods require independent or deliberately diversified evidence models.
4. **Diagnostic actions can alter the proposition being diagnosed.** Guarded retreat or a calibration pulse during contact may undo progress or create a new discrepancy. “Bounded” is not equivalent to “state preserving.”
5. **Some hypotheses are not identifiable without additional sensing assumptions.** A visually hidden object that failed to move and a WAM that predicted the wrong hidden motion may induce the same RGB/proprio trace even after a weak probe.

The more principled state is a joint belief

\[
p(c, z_{\text{progress}}\mid h),\qquad c\in\{E,M,P\},
\]

not a cause posterior followed by a deterministic memory switch. This is a material conceptual repair, not a cosmetic implementation detail.

## 9. Feasibility audit

### Feasible parts

- Simulator interventions can create actuator/control failures, contact failures, WAM corruptions/domain shifts, and camera occlusions with exact causal labels.
- A frozen π0.5 can supply action chunks while the diagnosis layer is developed independently.
- A small probe set keeps planning and safety validation manageable.
- The main metrics—post-probe attribution, information gain, false memory retraction, unnecessary recovery, task success, probe risk, and added latency—are measurable.

### Hard parts

- **Matched residual is not enough.** Matching only a scalar magnitude still allows shortcuts through task phase, camera view, object motion, duration, or failure severity. Cases must be matched across the full diagnostic context.
- **Real-world M labels are hard.** The same unexpected physical effect can be described as an execution failure, an unmodeled physical property, or WAM misspecification depending on the task specification.
- **Probe likelihood calibration is central.** A learned classifier over post-probe images is not automatically a causal hypothesis model.
- **Progress predicates need ground truth.** Otherwise “false memory corruption” may be scored by the same imperfect perception system being audited.
- **No tactile sensing reduces identifiability** for hidden contact, slip, and grasp retention. Proprioception and additional views can help but do not fully replace force/contact evidence.

Feasibility is therefore moderate in simulation and substantially harder on a real robot. The claim should start with visually testable execution effects rather than contact states that are unobservable from RGB/proprio.

## 10. Claim ceiling

The strongest current reviewer-defensible claim is:

> A controlled VLA×WAM benchmark and runtime system show that, at matched initial future–reality residual, actively probing the robot can better distinguish execution, model, and perception causes than passive discrepancy/uncertainty baselines, and cause-aware belief handling can reduce false progress-memory retraction.

The candidate should **not** claim:

- the first active causal fault diagnosis method;
- the first information-gain diagnostic controller;
- the first safe active fault estimator;
- the first fine-grained robot failure attribution system;
- the first WAM execution verifier or recovery mechanism;
- that E/M/P are generally identifiable from RGB/proprio;
- that M or P logically implies preserving the current progress predicate;
- that an E/M/P classifier alone is a causal diagnosis method.

If positioned honestly, the contribution is a **VLA×WAM-specific diagnosis problem, matched-residual benchmark, and memory-integrity finding**, with the active-FDI machinery credited as prior methodology.

## 11. Strongest reviewer rejection

> “The paper maps an existing active counterfactual FDI algorithm almost one-to-one onto a learned WAM residual. Hypothesis distributions, information-maximizing interventions, mission-risk penalty, and Bayesian posterior updates are already in Han et al.; safe active diagnosis of actuator/sensor faults is already in s-FEAST. The only new elements are the labels E/M/P and a downstream memory-routing heuristic, whose `M → preserve` and `P → do not retract` logic is not causally justified. The matched-residual benchmark may be useful, but it does not establish a novel method.”

This objection is strong enough to keep the score below the strict gate.

## 12. E0 authorization and kill criteria

### Decision

**Do not start a non-GPU dataset/oracle E0 for this exact candidate.** The novelty gate fails before experimentation. A positive oracle result would demonstrate that active diagnosis helps in the constructed simulator, but it would not answer the mechanism-overlap objection.

### If the candidate is materially reframed and re-reviewed

A future non-GPU compiler/oracle test could be justified only after replacing categorical cause-to-memory routing with joint cause/task-state inference or another nontrivial delta. It should be killed before GPU work if any of the following occurs:

1. the oracle-safe probe does not improve E/M/P macro-F1 or posterior log loss over reobservation/passive-history baselines at matched residual;
2. E/M/P labels cannot be made mutually auditable, or multi-cause cases dominate the dataset;
3. an oracle cause label does not materially reduce false progress-memory retraction relative to a conservative “defer update and reobserve” baseline;
4. probe actions change the task predicate often enough that post-probe diagnosis no longer refers to the original discrepancy;
5. residual matching leaves detectable shortcuts in task phase, camera pose, motion magnitude, or injected-failure type;
6. an independent verifier or a simple proprioception rule separates E/M/P just as well without a WAM;
7. WAM-based probe likelihoods become least reliable precisely in the M condition.

These are diagnostic criteria, not authorization to run the current method.

## 13. Final verdict

**Novelty: 6.90/10 — FAIL.**

ACDD targets a real and important failure mode, and its matched-residual plus memory-integrity framing is stronger than another scalar WAM verifier. Nevertheless, the proposed active causal diagnosis loop is almost exactly instantiated by existing counterfactual FDI and safe active fault-estimation work. The remaining VLA×WAM-specific delta is coherent but currently reads as an application and evaluation contribution followed by a questionable deterministic memory router.

**Recommendation:** archive the problem definition and matched-residual protocol; do not authorize experiments as the next >7 novelty candidate. A new review would be warranted only after a mechanism-level reformulation—most plausibly joint inference of root cause and task-progress truth with independently grounded, state-preserving diagnostic interventions.
