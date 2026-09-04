# Geometry-Conditioned Backward Viability Tubes: Skeptical Concept Jury

**Date:** 2026-08-31  
**Review route:** local Codex concept review; no delegated reviewer  
**review_independence:** same-family  
**acceptance_status:** provisional  
**Experiments run:** none  
**Evidence scope:** Candidate 4 in `pivot_candidates_after_giss.md`, the exact concept supplied by the user, stated sensing/compute constraints, and known direct mechanism families; no broad literature search

## Executive Verdict

**Recommendation: NO-GO for learned reverse-tube/VLA implementation in the current form. CONDITIONAL GO only for the oracle, non-GPU viability-value test below.**

The problem is important and the control object is natural: locally collision-free behavior can enter states from which the goal is no longer reachable, so the correct object is a goal-conditioned viable/backward-reachable set rather than a one-step safety cost. The proposed implementation conflates three different things:

1. backward reachable/viability sets;
2. a generative reverse transition model;
3. a visual action-support condition plus recovery controller.

That conflation creates a fatal conceptual fork. Literal reverse simulation of contact is generally not physical because unilateral contact, friction, restitution, deformation, controller hysteresis, and dissipation are not invertible. If “rollback” instead means restoring earlier snapshots from successful **forward** trajectories, the data are valid but the method is no longer reverse dynamics: it is backward relabeling/reverse curriculum over the support already visited by successful policies. It cannot establish a predecessor tube outside those trajectories. Sampling new predecessors from a learned reverse model requires forward-dynamics verification or planning, which reintroduces the mechanism the proposal is trying to distinguish itself from.

Before modeling any tube, the project must show that an oracle viability signal materially improves decisions over compute-matched forward MPPI/MPC on tasks with genuine dead ends and that the viability label is inferable from RGB/proprioception without tactile state. A learned reverse diffusion model is premature until those two facts hold.

## Scores

| Axis | Score | Judgment |
|---|---:|---|
| Scientific naturalness | **6.8 / 10** | Backward viability is the right mathematical object for avoiding dead ends; reverse contact diffusion, latent tube intersection, and nearest-tube recovery are not yet natural or well defined. |
| Problem importance | **8.2 / 10** | Avoiding irreversible locally safe branches is important for narrow passages, pregrasp selection, and contact-rich manipulation. It addresses a real failure of short-horizon imitation and collision costs. |
| Implementation feasibility | **4.8 / 10** | Four A100s can train a low-dimensional reverse model, but cannot solve observability, contact irreversibility, data coverage, conservative tube estimation, and recovery correctness. Simulator engineering and state representation dominate compute. |
| Novelty defensibility, provisional | **5.8 / 10** | Viability kernels/backward reachable tubes, reverse curricula, bidirectional planning, learned reachability, trajectory diffusion, and MPPI already cover most ingredients. The remaining delta is amortizing geometry-conditioned viability into a visual VLA support representation. |

## Naturalness Versus Existing Control Objects

### Viability is natural

For geometry `g`, dynamics `x_{t+1}=f_g(x_t,a_t)`, safe set `S_g`, and goal set `G_g`, the finite-horizon backward viable sets are

`B_0(g)=G_g`,

`B_h(g)={x in S_g : exists a such that f_g(x,a) in B_{h-1}(g)}`.

The corresponding viable state-action support is

`Q_h(g)={(x,a): x in S_g and f_g(x,a) in B_{h-1}(g)}`.

This cleanly expresses the motivating failure: two actions can both be collision-free now while only one enters `B_{h-1}`. Conditioning a policy on an approximation of `Q_h` is scientifically sensible.

### The proposed “tube” is underspecified

The concept alternates between a set of predecessor states, a state-action trajectory distribution, a latent visual condition, and a recovery target. These are not interchangeable:

- a reverse sample distribution reflects the behavior/data prior, not the entire viable set;
- a dense viability kernel needs conservative membership, not merely likely samples;
- “the tube segment intersecting the current state” requires a state metric, time-to-go index, uncertainty model, and membership threshold;
- a point outside the learned tube may be viable but uncovered, so recovery can be a false alarm;
- the nearest tube point in Euclidean or latent distance need not be forward reachable without collision.

The proposal should choose one primary object. The smallest adequate candidate is a learned **viability value/support predictor** distilled from forward-verified reachability labels. A reverse generative dynamics model plus tube encoder plus recovery generator is already a multi-component planning system.

## Strongest Reviewer Objection

> **The method is caught between invalid reverse physics and ordinary reverse curriculum. If it generates predecessors by running dissipative contact dynamics backward, its samples are not guaranteed forward-realizable. If it uses only saved predecessors from successful forward rollouts, it merely relabels a narrow success dataset and learns the occupancy of the behavior policy, not a viability tube. Any attempt to expand that occupancy needs forward verification/planning, at which point the contribution becomes amortized planning rather than reverse dynamics.**

This objection should be resolved in terminology and data construction:

- never call snapshot restoration “reverse contact dynamics”;
- train only on forward-valid transitions `(x_t,a_t,x_{t+1})`;
- treat `q_phi(x_t,a_t | x_{t+1},g)` as a **proposal distribution**, not a physical inverse;
- forward-verify every generated predecessor/action before assigning viable status;
- report coverage relative to an oracle reachable graph, not just sample likelihood.

If forward verification is too expensive, the proposal has no trustworthy supervision for generated tube mass.

## Prior-Art/Mechanism Pressure

Known direct families leave a narrow novelty window:

- **Viability theory and Hamilton–Jacobi backward reachability:** backward reachable sets/tubes and viability kernels are classical control objects, including time-indexed safety/goal sets.
- **BaRC, Backplay, and reverse curriculum generation:** propagate training starts backward from goals/successes; using stored successful predecessors for curriculum is not new.
- **Bidirectional RRT/RRT-Connect and backward search:** build trees from goal and start to discover predecessor connectivity.
- **MPPI/path-integral control, MPC, and trajectory optimization:** forward-sample action sequences and account for long-horizon geometry without learning a reverse model.
- **Goal-conditioned trajectory diffusion/Diffuser-like planning:** generate full goal-reaching trajectories or action sequences from a learned distribution.
- **Learned reachability/value/barrier methods:** approximate viable/reachable sets or goal-conditioned value functions with neural models.

The defensible delta cannot be “use backward reachability.” It must be:

> a geometry-conditioned, visually queryable approximation of viable **action support** that improves a frozen VLA's dead-end avoidance over compute-matched forward planners and ordinary goal-conditioned/value conditioning.

If the implementation only augments successful predecessor states and behavior-clones them, novelty drops to reverse curriculum. If it performs online search through the learned tube, it becomes a planner and should be compared as one.

## Reverse Contact Dynamics: Fatal or Bounded?

### Fatal if interpreted literally

Contact transitions are many-to-one and dissipative. Sliding with Coulomb friction, impacts, sticking, grasp closure, jamming, and controller integrator state generally do not have unique or physically meaningful inverses. Reversing simulator time or forces can produce predecessors that no forward policy can realize.

### Bounded if reformulated as conditional predecessor proposals

A multimodal `q_phi(x_t,a_t | x_{t+1},g)` can model multiple possible predecessors from a dataset of **forward-valid** transitions. It need not invert physics analytically. But then:

- its support is limited by the forward data generator;
- each novel sample must pass forward consistency `f_g(x_t,a_t) approximately x_{t+1}`;
- recursively sampled chains accumulate off-manifold error;
- high probability under `q_phi` does not imply goal reachability unless the rest of the chain is verified.

Thus reverse contact dynamics is not inherently fatal after reframing, but the resulting method is a proposal model inside a forward-verified reachability pipeline. That is more complex and less novel than the current description suggests.

## Observation and No-Tactile Mismatch

The viability set is defined over full Markov state. Deployment observes `o=(RGB,proprioception,language)`. Without tactile/force signals, two full states can have nearly identical observations but different contact mode, frictional preload, grasp stability, jamming status, or controller memory; one may be viable and the other not.

If `h(x_1) approximately h(x_2)` but `1[x_1 in B_h] != 1[x_2 in B_h]`, no deterministic visual tube condition can be correct for both. The project must quantify this aliasing. Options such as recurrent belief state, tactile sensing, or uncertainty-aware conservative viability would change the method. The current claim should therefore be limited to pre-contact or visually/proprioceptively identifiable dead ends until evidence says otherwise.

## Nearest-Tube Recovery Is Not Valid by Construction

The recovery clause contains a second major flaw. For `x` outside an estimated tube, choosing

`x_star = argmin_{z in B_hat} d(x,z)`

does not imply that `x_star` is reachable from `x`, that the path remains safe, or that moving toward it reduces time-to-go. The nearest point can lie across an obstacle, on another contact manifold, or behind an irreversible transition.

A valid recovery must itself solve a forward reachability problem to the tube or be supervised with verified recovery trajectories. Adding that mechanism creates a second contribution and overlaps recovery planning. The smallest initial E0 should **delete recovery** and test only whether viability-conditioned action support prevents dead-end entry from states already covered by the tube.

## Cheapest Oracle Non-GPU Kill Test

**Purpose:** determine whether viability information, before learning, changes decisions enough to justify the project and whether the label is observable without tactile sensing.

Use three small simulator families with deliberately constructed locally safe forks:

1. a narrow-passage/obstacle layout where the wrong side is collision-free initially but cannot reach the goal;
2. a pregrasp family where one approach side leads to an unreachable or colliding final grasp;
3. a quasistatic contact/jam family where one contact order enters an irreversible dead end.

For each family, build a finite graph or tree using **forward-valid simulator transitions only**. Mark goal nodes and run backward dynamic programming/graph search to obtain an oracle time-indexed viable set and viable state-action labels. No reverse model, VLA, or GPU is used.

Compare from matched pre-branch start states:

1. the existing forward policy or short-horizon collision MPC/MPPI;
2. a compute-matched longer-horizon MPPI/MPC baseline;
3. the same controller with an oracle viability mask that rejects actions leaving the backward-reachable set.

Measure dead-end entry, task success, false rejection of oracle-solvable states, and intervention rate. From the same graph, find observation-nearest state pairs in RGB/proprio feature space and measure how often their oracle viability labels disagree.

**Kill the learned-tube concept before GPU if any condition holds:**

- the oracle viability mask reduces dead-end entry by less than **15 percentage points** relative to the strongest compute-matched forward baseline;
- oracle viability improves task success by less than **5 percentage points**;
- it falsely rejects more than **10%** of states with a verified goal-reaching path;
- more than **10%** of observation-nearest state pairs disagree on viability label because of hidden contact state/no-tactile aliasing;
- a modest increase in MPPI/MPC horizon closes at least **80%** of the oracle gap, showing that the problem is mainly planning horizon rather than a new representation need.

This is the cheapest decisive test because it grants perfect viability and removes all learning errors. If the oracle signal has little advantage, a learned reverse tube cannot justify its complexity. If the label is not observable, four A100s cannot repair the missing sensor state.

## What Exact Supervision Would Be Needed Later

Only if the oracle test passes should the learned stage be specified. Each training unit should contain:

- geometry `g` and full simulator state `x_t`;
- visual observation `o_t` available to the VLA;
- action `a_t` and forward successor `x_{t+1}=f_g(x_t,a_t)`;
- time-to-go/horizon index `h`;
- oracle or high-confidence label `V_h(x_t,g)` and action label `Q_h(x_t,a_t,g)`;
- lineage identifying the forward rollout/planner that established reachability;
- uncertainty/coverage indicator for states not certified either viable or nonviable.

The learned model must distinguish **negative** states/actions from merely **uncovered** ones. Treating “not in sampled reverse tube” as nonviable creates false recovery and unsafe support pruning.

The core metric is not reverse sample likelihood. It is action-level viable-support precision/recall against held-out oracle graph labels, plus closed-loop dead-end entry at a fixed action-query budget.

## Feasibility on Four A100s

### What is feasible

- training a low-dimensional conditional diffusion or viability network on simulator states;
- freezing Pi0.5/VLM and adding a small viability/tube-conditioning adapter;
- an 80–128 A100-GPU-hour bounded run if verified state-transition data already exist;
- pre-contact geometry families with fully observed simulator state.

### What is not yet credibly scoped

- representing a multimodal tube over robot pose, object pose, velocities, contact mode, controller memory, geometry, and time-to-go;
- learning reliable recursive predecessor chains under contact;
- mapping RGB/proprio observations into exact tube intersections without tactile belief state;
- conservative membership calibration, so uncovered states are not called nonviable;
- generating safe recovery to a tube without a forward planner;
- supporting multiple geometry families with enough coverage to learn a viability kernel rather than successful-trajectory occupancy.

The current architecture contains at least three new mechanisms: reverse diffusion, tube compression/encoder, and recovery-conditioned VLA generation. This exceeds the smallest-adequate-mechanism bar. Four A100s address training throughput, not simulator coverage or epistemic correctness.

The cleanest feasible pivot after an oracle pass would be **geometry-conditioned viability/action-support distillation**: use forward-verified oracle labels to train one compact viability-conditioned action adapter, omit reverse generation and omit recovery. That would be less novel but scientifically cleaner.

## Outcome-to-Claim Matrix

| Oracle viability advantage | Observation aliasing | Interpretation | Allowed next step |
|---|---|---|---|
| Fails 15pp/5pp gates | Any | Dead-end problem is not large enough beyond stronger forward planning | Kill concept |
| Passes | >10% label disagreement | Viability matters but is not observable under no-tactile inputs | Restrict to pre-contact or change sensors; no contact-tube claim |
| Passes | <=10% disagreement | Visual viability conditioning may be useful | Build smallest viability-value/support adapter first |
| Only nearest-tube recovery adds benefit | Any | Recovery planner, not backward tube, is the mechanism | Reframe as recovery planning or reject original claim |
| Reverse model fits snapshots but fails forward verification | Any | Learns behavior occupancy, not physical predecessor support | Kill reverse-dynamics claim |

## Claim Ceiling

If the oracle and a later learned E0 both pass, the strongest defensible claim is:

> On visually identifiable geometry families with forward-verified dead-end structure, a learned geometry-conditioned approximation of viable action support reduces entry into goal-unreachable states compared with compute-matched short-horizon VLA/MPC baselines.

The current concept cannot claim:

- physical inversion of contact dynamics;
- recovery of the full viability kernel from successful rollback trajectories;
- that absence from a sampled tube implies nonviability;
- safe nearest-tube recovery without verified forward reachability;
- general contact viability from RGB/proprioception without tactile sensing;
- novelty of backward reachability, reverse curricula, or goal-conditioned trajectory generation.

## Final Recommendation

**NO-GO for GPU experiments and NO-GO for the full reverse-diffusion + tube-encoder + recovery system.**

**Conditional continuation:** authorize only the oracle non-GPU graph/reachability test. If oracle viability clears the registered dead-end and success gates and observation aliasing remains below threshold, proceed to a focused prior-art audit and the smallest learned **viability-support adapter**. Do not begin with recursive reverse contact diffusion or recovery.

If the oracle fails, archive the idea. If the oracle passes but the visual label is aliased, restrict the project to pre-contact tasks or reconsider the no-tactile constraint rather than hiding the observability failure inside a larger model.
