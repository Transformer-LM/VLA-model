# Idea Candidate Pool — Pre-Jury

**Direction**: expanded non-tactile VLA / WAM / VLA×WAM search  
**Status**: mechanically deduplicated; not ranked; no candidate accepted  
**Rule**: every objectively feasible, non-duplicate candidate is passed to a fresh same-family provisional jury.

## C01 — Causal Residual Attribution and Decision

- **Method**: Generate same-prestate/same-command triplets for execution failure, WAM misspecification and observation ambiguity; match scalar WAM residual distributions; learn a factorized source posterior from forward residual, inverse action consistency, model support and observability; choose repair/reobserve/distrust by minimum expected intervention regret.
- **Hypothesis**: A source-aware decision reduces harmful interventions even when scalar mismatch cannot distinguish causes.
- **Minimum pilot**: frozen policy/WAM, controlled LIBERO or RoboCasa perturbations, 3 classes × held-family split; compare final decision regret and source macro-F1.
- **Nearest collision**: CheckVLA, When to Trust Imagination, WAV, SC3-Eval, Runtime Monitoring.
- **Fatal test**: failure+OOD concatenation or a direct PointMap checker matches source-aware routing.
- **dedup_key**: `residual-source-posterior-decision-regret`

## C02 — SourceBlind: Residual-Matched Verification Benchmark

- **Method**: Build a benchmark only: every base transition receives three counterfactual perturbations with matched mismatch magnitude but different correct interventions; audit CheckVLA-like, FFDC-like, uncertainty, OOD and observation-only verifiers.
- **Hypothesis**: Current scalar verifiers exhibit high intervention regret despite similar anomaly AUPRC because they conflate causes.
- **Minimum pilot**: 300–1,000 paired events across at least five held-out task families.
- **Nearest collision**: CheckVLA failure analysis, ARB4WM, VLA-Arena, ReViP false-completion benchmark.
- **Fatal test**: existing scalar verifier retains low regret after residual matching or source labels depend on privileged arbitrary taxonomy.
- **dedup_key**: `residual-matched-source-benchmark`

## C03 — Independent Consistency Triangle

- **Method**: Use three separately trained/evidence-isolated channels: forward action-effect prediction, inverse action reachability, and cross-view observability; diagnose the broken edge of the triangle and map it to a controller action.
- **Hypothesis**: Independent channels prevent shared WAM bias from disguising model errors as robot failures.
- **Minimum pilot**: matched small encoders on PointMap/proprio features with channel-shuffle and shared-backbone controls.
- **Nearest collision**: WAV forward–inverse asymmetry and SC3-Eval forward–inverse/cross-view consistency.
- **Fatal test**: independence adds no benefit over WAV-style cycle score or source accuracy does not change decisions.
- **dedup_key**: `independent-forward-inverse-observability-triangle`

## C04 — Active Disambiguation Before Repair

- **Method**: When execution and model-error posteriors overlap, select a short view-change/reobserve action that maximizes expected source information; repair only after the extra observation.
- **Hypothesis**: A cheap information action prevents unnecessary rollback in occluded/ambiguous states without causing stagnation.
- **Minimum pilot**: simulated camera/wrist-view choices with fixed reobserve cost, risk–coverage and task-time evaluation.
- **Nearest collision**: ActiveVLA, active perception/POMDP planning, CheckVLA.
- **Fatal test**: fixed second view or always-reobserve matches adaptive information gain.
- **dedup_key**: `active-source-disambiguation-before-repair`

## C05 — Source-Aware Progress-Memory Firewall

- **Method**: Place source attribution between a WAM verifier and long-horizon progress memory; execution failure may invalidate a relation, model error cannot rewrite memory, and ambiguity marks the relation unobserved until rechecked.
- **Hypothesis**: Most long-horizon harm from a fallible WAM comes from corrupting persistent task state rather than one bad action veto.
- **Minimum pilot**: freeze π0.5; inject relation failure, appearance/model shift and occlusion after a successful subgoal; measure memory corruption radius, false completion and recovery.
- **Nearest collision**: EvoScene-VLA, MemoryVLA++, CheckVLA event bank, EventVLA/ChainVLA, classic belief revision.
- **Fatal test**: stateless source-aware verification yields the same final success, or a direct current-state relation checker suffices.
- **dedup_key**: `source-aware-progress-memory-firewall`

## C06 — Episodic World-Model Fault Bank

- **Method**: Store only verified WAM errors indexed by action, object-relative geometry and nuisance context; retrieve them to calibrate future residuals without modifying the policy or global WAM parameters.
- **Hypothesis**: Local fault memory lowers repeated false interventions under recurring deployment shifts while avoiding catastrophic online adaptation.
- **Minimum pilot**: recurring camera/background/object shifts, compare no adaptation, parameter TTT and retrieval calibration.
- **Nearest collision**: WAM-TTT, Mem-World, adaptive memory, test-time calibration.
- **Fatal test**: ordinary kNN/OOD calibration matches or memory causes failures under nonrecurring shifts.
- **dedup_key**: `episodic-world-model-fault-memory`

## C07 — Functional-Geometry Strategy-Shift Benchmark and WAM

- **Method**: Hold language, semantic class and final relation/pose fixed while changing target–reference geometry so the successful grasp/alignment/approach strategy changes; evaluate π0.5, 3D VLA and WAM candidate selection.
- **Hypothesis**: Current geometric VLAs handle coordinate shift better than strategy-topology shift; an action-conditioned object-pair world model can recover part of the gap.
- **Minimum pilot**: parametric insertion/hanging/placement tasks with terminal-matched counterfactual pairs and oracle candidate headroom.
- **Nearest collision**: GEAR-VLA, Lift3D-VLA, DreamWAM, ForeTime-VLA; GIFT/RPDiff/FMB.
- **Fatal test**: target 6D pose or PointMap concatenation closes oracle gap; no genuine strategy switch exists.
- **dedup_key**: `functional-geometry-strategy-shift`

## C08 — Feasibility-Calibrated Negative Competence for VLA

- **Method**: Estimate calibrated feasible/marginal/infeasible probability for object–reference–robot geometry and select execute, alternate strategy or reject.
- **Hypothesis**: VLA confidence does not capture physical infeasibility, especially at clearance and reachability boundaries.
- **Minimum pilot**: continuous aperture/clearance/reachability sweeps with held-out shapes and robot poses.
- **Nearest collision**: OBEYED-VLA absent-target rejection, VLAConf, classical collision/reachability checking.
- **Fatal test**: deterministic geometry planner completely solves the setting or the VLA adds no semantic uncertainty.
- **dedup_key**: `feasibility-calibrated-negative-competence`

## C09 — Task-Effect Quotient Action Learning

- **Method**: Collapse trajectories into equivalence classes when they produce the same task relation, safety and geometric outcome; train the policy/verifier on the set rather than a single demonstration path.
- **Hypothesis**: effect-set supervision reduces demonstration-style bias and improves geometry-shift action diversity.
- **Minimum pilot**: multi-solution simulator trajectories, compare BC/flow/diffusion diversity plus binary success scorer.
- **Nearest collision**: ABot-M0 action manifold, ForeTime-VLA action-equivalence objective, outcome-conditioned RL/IL.
- **Fatal test**: ordinary multimodal action head plus success scorer matches the quotient objective.
- **dedup_key**: `task-effect-quotient-action-learning`

## C10 — Support-Constrained WAM Selection Under Planner Pressure

- **Method**: Adversarially increase candidate-search budget, estimate policy/action support and WAM uncertainty, then constrain selection by a calibrated support-risk envelope.
- **Hypothesis**: more test-time WAM search eventually reverses real action ranking; support constraints delay or prevent this reversal.
- **Minimum pilot**: search-budget curves with imagined-vs-ground-truth ranking and regret.
- **Nearest collision**: WAV, WoVR, PROWL, Imperfect World Models are Exploitable, conservative MBRL.
- **Fatal test**: ensemble uncertainty or KL-to-policy alone prevents exploitation under matched compute.
- **dedup_key**: `support-constrained-wam-planner-pressure`

## C11 — Residual-Onset Causal Graph

- **Method**: Align commanded-versus-realized motion, object PointMap motion, camera residual, ensemble disagreement and support score; infer the temporal order in which residual streams change; route the inferred source to repair/reobserve/distrust.
- **Hypothesis**: Final-frame residuals look similar, but their precursor order contains source information.
- **Minimum pilot**: 8–20 frame windows around paired events; compare endpoint MLP, unordered temporal encoder and onset graph.
- **Nearest collision**: temporal event-triggered VLA correctors and CheckVLA.
- **Fatal test**: sampling rate cannot stably resolve onset order, or endpoint features match wrong-intervention rate.
- **dedup_key**: `residual-onset-causal-graph`

## C12 — Minimal-Intervention Explanation Model

- **Method**: Fit three constrained explanations for one discrepancy: the smallest effective-action correction, WAM/dynamics correction, or observation-nuisance correction; compare calibrated explanatory costs and choose a source-specific intervention.
- **Hypothesis**: Competing constrained explanations are more identifiable and interpretable than a monolithic three-class encoder.
- **Minimum pilot**: frozen WAM on paired events; compare direct classifier versus three explanation modules on source calibration and decision regret.
- **Nearest collision**: system identification, robust observation models, WAV-style model validation.
- **Fatal test**: one flexible module explains all causes, costs cannot be cross-calibrated, or classification performs identically.
- **dedup_key**: `minimal-intervention-explanation-model`

## C13 — Cross-View Cross-Model Evidence Lattice

- **Method**: Cross observer invariance (views/PointMap), predictor invariance (independent WAM heads) and executor trace consistency; assign causal meaning to which axes disagree.
- **Hypothesis**: View-specific, model-specific and physical invariant disagreements separate the three sources better than one high-capacity verifier.
- **Minimum pilot**: two views or RGB-D+PointMap, 2–3 lightweight WAM heads, held-family paired triplets and risk–coverage curves.
- **Nearest collision**: SC3-Eval cross-view consistency, WAM ensembles, multi-view perception.
- **Fatal test**: error axes are too correlated, one stream matches the lattice, or latency is disproportionate.
- **dedup_key**: `cross-view-cross-model-evidence-lattice`

## Objective feasibility gate

All thirteen candidates have a simulator/offline pilot under one week on the available four A100 GPUs. None is mechanically eliminated at this stage. The generation shard's cause-triplet, active-probe and progress-memory variants were mechanically merged into C01/C02, C04 and C05; three structurally distinct outputs remain as C11–C13. Novelty, impact and scientific quality are reserved for the jury.
