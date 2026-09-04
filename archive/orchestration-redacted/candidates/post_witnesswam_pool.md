# Post-WitnessWAM problem-first candidate pool

**Purpose:** unranked, mechanically deduplicated input to a fresh strict jury.  
**Scope:** no tactile; simulator-falsifiable; no experiments started.  
**Hard exclusions:** auxiliary-label-only work, generic memory, confidence/visibility gates, ordinary WAM reranking/MPC, WAM-generated data, simple 3D input, generic DPO/flow preference, set diffusion, surface frames, functional-geometry transfer, active FDI, generic conformal calibration, backward-reachability tubes.

## C1 — Observation-Contingent Branching Action Chunks

**Problem.** Open-loop VLA chunks cannot condition their remaining actions on whether an uncertain contact/placement event actually succeeded, while re-querying a 3B policy at every step is slow.

**Mechanism.**

1. A native VLA head jointly emits a shared short prefix, a small typed branch condition over the future observation, and two or three conditional suffixes.
2. Simulator rollback constructs paired outcomes after the same prefix: success, recoverable miss, and optionally ambiguous outcome; suffixes are trained jointly so that each solves its own branch while sharing the prefix.
3. Deployment executes the prefix, evaluates the branch condition from the newly arrived RGB/proprio observation, and executes the already-produced suffix without another large-model call or WAM reranking.

**Changed interface:** the VLA output becomes a depth-1 closed-loop policy tree rather than one open-loop chunk.

## C2 — Low-Rank Within-Chunk Feedback Fields

**Problem.** Fixed VLA chunks cannot react to continuous deviations that do not justify a full replan.

**Mechanism.**

1. The VLA outputs a nominal action chunk plus a low-rank set of feedback gains for each step.
2. A small frozen visual/proprio encoder measures the residual between current features and the nominal feature trajectory.
3. The gains map residuals into bounded per-step action corrections inside the chunk.

**Changed interface:** the action head emits a local feedback controller, not only an open-loop sequence.

## C3 — Minimal Physical Task-Repair VLA

**Problem.** Existing rejection systems mainly detect absent objects or false linguistic premises; they do not handle tasks that are semantically valid but physically infeasible under the current geometry or kinematics.

**Mechanism.**

1. Compile the instruction into a small set of task constraints and query a simulator/TAMP oracle for feasibility.
2. If infeasible, compute the minimum allowed physical edit that restores a solution: an enabling manipulation such as moving an obstruction, opening a receptacle, changing object orientation, or selecting an explicitly permitted alternative referent.
3. Train a VLA to output either the original action chunk or a `repair-subgoal -> original-goal` action sequence; evaluate minimality and actual post-repair task success.

**Changed decision set:** the policy may transform the environment to make the original goal feasible, rather than act, refuse, or hallucinate.

## C4 — Counterfactual Infeasibility Certificates

**Problem.** A scalar refusal does not reveal whether the VLA understands why a manipulation is physically impossible.

**Mechanism.**

1. The VLA outputs either a physical action or a minimal unsatisfied constraint set over reachability, collision, containment, ordering, and robot limits.
2. Each predicted core is tested with simulator counterfactuals: relaxing every member separately must change the feasibility result in the claimed way, while irrelevant edits must not.
3. A certificate routes the system to a bounded counterproposal or human request, never to ordinary low-confidence abstention.

**Changed causal interface:** negative capability is a falsifiable intervention certificate that controls the next system action.

## C5 — Causal Identity from Action-Effect Histories

**Problem.** Appearance-based object addresses fail after occlusion, identical-object swaps, or appearance changes; a persistent ID should depend on how the same physical entity responds to interventions.

**Mechanism.**

1. Maintain for each object slot a compact response signature mapping recent robot action directions/contact modes to observed object motion and relation changes.
2. Bind post-occlusion detections to historical roles by likelihood under these action-effect signatures, not only appearance or position.
3. When multiple bindings remain possible, choose an ordinary policy-supported task action that both advances the task and maximally separates the predicted object responses; update binding from the outcome.

**Changed causal interface:** object identity is intervention-indexed and can alter which entity the VLA acts on.

## C6 — Intervention-Commuting Object Addresses

**Problem.** Object-slot models can pass appearance tracking metrics while still binding an action to the wrong object.

**Mechanism.**

1. Construct paired scenes that permute two object roles and correspondingly retarget the same object-level intervention.
2. Train a joint object-addressable WAM/VLA so that action and future-object predictions commute with this permutation, while non-target slots preserve their trajectories.
3. At deployment, the address used by the VLA action head is the same address whose intervention effect is checked by the world head.

**Changed optimization object:** correctness is a commutative interventional diagram, not static slot similarity or ordinary next-frame loss.

## C7 — Interventional Effect-Quotient Action Interface

**Problem.** Joint-space action labels fragment physically equivalent behaviors across geometry and embodiments, whereas generic latent actions often encode appearance or motion style rather than task effects.

**Mechanism.**

1. In simulator interventions, declare two temporally extended chunks equivalent only when they induce the same distribution over task-object relation changes while preserving the same protected relations across nuisance variations.
2. Learn a quotient encoder whose code identifies this effect-equivalence class and a geometry/embodiment-conditioned decoder that realizes one valid member.
3. The VLA predicts an effect-class code; the decoder outputs the concrete chunk. No WAM search or test-time candidate ranking is used.

**Changed causal interface:** VLA and low-level control communicate through interventional effect classes rather than joints, poses, video motion, or unconstrained latent actions.

## C8 — Predicate-Preservation Action Policies

**Problem.** Long tasks are non-monotonic: an action can advance the current subgoal while silently invalidating a previously established relation.

**Mechanism.**

1. Build matched simulator states with the same visible next subtask but different already-established predicates that must remain true.
2. Train the VLA under a constrained objective: complete the next subtask while minimizing actual deletion of protected predicates under execution, including delayed clobbering.
3. At test time, the protected set changes the chosen physical path or manipulation order; success requires both new progress and preservation.

**Changed optimization object:** maximize progress subject to causal non-interference with prior achievements, rather than predict a progress token or store more history.

## C9 — Compensable Action Chunks

**Problem.** Recovery is usually designed only after failure, but some nominal actions destroy all cheap recovery options.

**Mechanism.**

1. A VLA jointly emits a nominal chunk and one bounded compensation chunk for each preregistered recoverable failure branch.
2. Simulator rollback verifies before execution that each compensation restores a task-equivalent continuation state after its corresponding failure, without undoing protected predicates.
3. Runtime branch evidence selects either the nominal continuation or the precommitted compensation; actions without a valid compensation are disallowed when an equally successful compensable action exists.

**Changed decision set:** nominal actions are selected partly by whether they carry an executable contingency, not only by predicted success.

## C10 — Task-Equivalent Recovery Targets

**Problem.** Returning to an exact checkpoint can be unnecessary or impossible; recovery only needs a state that preserves the same remaining task possibilities.

**Mechanism.**

1. Define two states as task-equivalent when they satisfy the same protected predicates and admit the same policy-supported continuation language to the goal.
2. A learned recovery policy targets the nearest reachable member of that equivalence class, rather than the historical pose or image.
3. Resume the frozen nominal VLA and test whether success and protected predicates match exact rollback with lower recovery cost.

**Changed recovery interface:** recovery targets a continuation-equivalence set instead of a single state.

## C11 — Actual-Cause VLA Post-Training

**Problem.** Terminal failure labels assign blame to an entire long trajectory, although only one earlier action chunk may have caused the failure.

**Mechanism.**

1. For failed simulator episodes, use rollback to replace subsets of earlier chunks with matched successful alternatives while holding the remaining trajectory policy fixed where possible.
2. Compute a minimal actual-cause set: chunks whose replacement changes the terminal outcome and for which strict subsets do not.
3. Fine-tune only causally responsible policy decisions while constraining unrelated successful chunks to preserve their original action distribution.

**Changed optimization object:** post-training minimizes error on minimal causal decisions rather than all frames, final reward, or generic hard negatives.

## C12 — Predicate-Lifecycle Credit Assignment

**Problem.** Progress rewards treat relation creation as permanent, even when later actions invalidate it.

**Mechanism.**

1. Represent each task predicate by physical add/delete events and a persistence interval, not a monotone progress scalar.
2. Attribute positive credit only to additions that survive their required interval; assign deletion cost to the later action that breaks the relation.
3. Optimize the VLA in simulator for task completion plus preservation of independent predicate lifecycles.

**Changed optimization object:** reward is based on complete predicate lifecycles and explicit deletion credit, not instantaneous or monotone progress.

## C13 — Search-Adversarial WAM Training

**Problem.** A WAM trained for average prediction error can be systematically exploited by the planner's argmax, even if its ordinary rollouts look accurate.

**Mechanism.**

1. Run the exact frozen best-of-N/MPC search at multiple budgets and replay selected candidates in the simulator.
2. Update the WAM against the worst selected-action real regret over budgets, with a replay constraint that preserves ordinary-distribution fidelity.
3. Deployment uses the unchanged planner and WAM; the claim is that adversarially trained dynamics resist search-amplified optimism as N grows.

**Changed optimization object:** minimize worst post-selection physical regret, not average prediction loss or generic uncertainty.

## C14 — Planner-Invariant Action Dominance

**Problem.** Scalar WAM scores make action choice sensitive to search budget and score exploitation.

**Mechanism.**

1. Learn a partial-order world interface that declares action A to dominate B only when A's task effects are no worse and protected-relation violations no greater across registered nuisance interventions.
2. Train the order directly from paired simulator transitions, preserving `incomparable` outcomes rather than forcing a scalar ranking.
3. The planner may only prune dominated actions and must retain incomparable modes; evaluate whether selected real performance is invariant to search-budget increases.

**Changed decision interface:** WAM exposes a robust partial order instead of reward/value/confidence scores.

## C15 — Reversibility-Semantic World Action Model

**Problem.** Pixel prediction does not tell the controller whether an action's physical effects can be undone after a mistake.

**Mechanism.**

1. Execute action/inverse-action cycles in simulator and label which object-relation changes return, which remain hysteretic, and which cause irreversible loss.
2. Train an action-conditioned WAM to predict a structured reversibility class and a valid inverse-action equivalence class jointly with future state.
3. A VLA action head is optimized to prefer reversible progress early in uncertain phases and reserve irreversible actions for states satisfying explicit preconditions.

**Changed prediction and optimization:** the WAM models reversibility semantics and the VLA changes when irreversible actions enter its feasible set.
