# Action-Fiber Set Diffusion: Skeptical Concept Jury

**Date:** 2026-08-31  
**Review route:** local Codex concept review; no delegated reviewer  
**review_independence:** same-family  
**acceptance_status:** provisional  
**Experiments run:** none  
**Evidence scope:** Candidate 1 in `pivot_candidates_after_giss.md`, the stated compute/deployment constraints, and known direct prior-art families; no broad literature search

## Executive Verdict

**Recommendation: NO-GO for GPU implementation in the current “joint K-set diffusion” form. CONDITIONAL GO only for the non-GPU action-fiber audit below.**

The underlying problem is real: one visible state and functional geometry can admit multiple physically distinct approach, routing, and contact modes, while single-demonstration behavior cloning underrepresents that support. The proposed *learning object*, however, is not yet scientifically irreducible. Deployment consumes one action chunk and the proposal neither ranks nor otherwise uses relationships among the K outputs. If one slot is selected without a set-level decision rule, an exchangeable K-set predictor is observationally reducible to the marginal distribution of a randomly selected slot. In that case, unbalanced OT is a mode-balancing or multiple-hypothesis training regularizer—not evidence that robot control requires a jointly generated set.

The proposal becomes defensible only if it shows both:

1. the rollback-verified “fiber” is a stable, reproducible set-valued target rather than a planner-seed roster; and
2. joint set coupling beats a standard conditional diffusion trained on the identical, mode-balanced verified data and evaluated with the identical K-sample budget.

Until both conditions hold, the expected novelty is closer to multi-sample diffusion plus curated data augmentation than to a new action-generation mechanism.

## Scores

| Axis | Score | Judgment |
|---|---:|---|
| Scientific naturalness | **6.2 / 10** | The feasible-action fiber is natural; a fixed unordered K-set with UOT is not yet the natural control interface because only one member is consumed and no set-level decision is made. |
| Problem importance | **7.3 / 10** | Multimodal feasible support matters for geometry OOD, contact alternatives, and recovery from local mode collapse. Its importance is lower than claimed if any one reliable mode suffices and alternatives are never used downstream. |
| Implementation feasibility | **5.8 / 10** | A small K joint adapter is possible on four A100s, but a genuine set decoder requires cross-slot coupling and Pi0.5 action-token changes; batching K independent samples is easy but collapses the contribution. Verified set construction is likely the larger cost. |
| Novelty defensibility, provisional | **5.5 / 10** | Diffusion Policy already models multimodal action distributions; RPDiff covers geometry-conditioned multimodal solutions; set/Hungarian/OT prediction and multi-hypothesis trajectory losses are established. The remaining delta is narrow and must be empirically irreducible to mode-balanced single-policy learning. |

## What Is Scientifically Natural—and What Is Not

### Natural core

For a condition `c=(RGB, proprioception, instruction, geometry)`, define the viable action support

`F(c) = {a_{0:H-1} : rollback(c,a) satisfies the registered safety and terminal predicates}`.

This is a legitimate set-valued object. It captures routing homotopies, approach sides, grasp/contact schedules, and other alternatives that a single demonstration does not identify. Using simulator rollback to certify membership is also natural for an offline, simulation-first method.

### Unnatural leap

The true control object is still a conditional distribution or policy over `F(c)`. A fixed K-point output is only a finite quantization of that distribution. It becomes scientifically meaningful as a *joint set* only if correlations among the K elements have a downstream role—for example, contingency coverage, allocation across known modes, or a set consumer. Candidate 1 explicitly removes feasibility scoring/reranking and executes only one mode. Therefore:

- if K chunks are independent Pi0.5 samples, there is no joint-set mechanism;
- if they are coupled but one is chosen uniformly, only the one-slot marginal affects control;
- if UOT forces slots toward different target clusters, the method is a learned diverse codebook/multiple-hypothesis predictor unless jointness beats marginal mode balancing;
- if a selector is later added, the paper changes into candidate generation plus selection and collides with the reranking family the pivot intended to avoid.

This is not merely a presentation issue. It determines whether the central object is a policy distribution, a K-point quantizer, or a set-valued controller.

## Strongest Reviewer Objection

> **The environment observes one executed chunk, so the joint law over the unexecuted K−1 chunks is causally irrelevant. Any exchangeable K-set generator followed by random/symmetric slot selection induces a single-action marginal policy. Unless the method beats an identical-data, mode-balanced standard diffusion under the same K-sample budget—and beats simple diverse subset selection—the UOT set loss is only multi-hypothesis regularization/data reweighting.**

This objection is stronger than “the planner set is incomplete.” Even with perfect feasible-set labels, a jointly predicted set is unnecessary if its joint structure is never consumed. A top-venue reviewer will ask for an irreducibility result, not just improved coverage over single-demonstration BC.

The decisive comparison is not positive-only BC. It is:

1. standard conditional Pi0.5/action diffusion trained on every rollback-verified chunk with **mode-uniform sampling weights**;
2. K i.i.d. samples from that model at evaluation;
3. N i.i.d. samples followed by action-space farthest-point/K-medoids selection down to K, with the same total sampling/compute budget;
4. a conventional K-head multiple-choice/winner-take-all predictor;
5. the proposed genuinely cross-slot-coupled set decoder.

If (5) does not beat (1)–(4) on rollback precision and mode recall at fixed K, the “set diffusion” claim should be dropped even if all methods improve over demonstration-only BC.

## Direct Prior-Art Pressure

No novelty acquittal is possible without a focused search, but known mechanisms already occupy most ingredients:

- **Diffusion Policy / flow-based action heads:** conditional multimodal action distributions and K-sample generation are native behavior, not new set learning.
- **RPDiff:** local-geometry-conditioned multimodal relational pose generation already establishes that geometry can condition multiple robot solutions; temporal chunks and rollback certification are the remaining task-specific differences.
- **Multiple Choice Learning and multi-hypothesis trajectory prediction:** fixed K outputs, winner-take-all assignment, diversity, and mode coverage are established prediction mechanisms.
- **DETR/Hungarian set prediction, Deep Sets, Set Transformer, and set/point-cloud diffusion:** permutation-invariant matching and exchangeable set generation are generic prior machinery.
- **Best-of-N and diverse decoding:** improvements from presenting K alternatives do not by themselves imply a new conditional-support objective.

Unbalanced OT is an implementation choice, not automatic novelty. In fact, relaxed marginals can work against the stated goal: if target-mass deletion is cheap, rare feasible modes are precisely what UOT will discard. The target-side deletion penalty must be high and asymmetric enough that missed modes remain expensive.

## Exact Set-Valued Supervision Required

The target cannot be “K planner samples.” It must be an auditable empirical measure over reproducible rollback-verified modes.

### 1. Build a mode-balanced target measure

For each checkpoint `c`, collect all attempted planner/controller chunks and retain only chunks that reproduce under checkpoint rollback and satisfy the same registered terminal/violation predicates. Cluster successful chunks using a pre-registered functional distance, not raw action L2 alone:

`d_func(a,b) = alpha*d_EE_path(a,b) + beta*d_object_path(a,b) + gamma*d_event(a,b)`.

`d_event` must encode ordered contact/gripper events; path terms must be normalized by workspace/task scale. Let `m(j)` be the resulting mode of verified chunk `a_j`, with `M_c` reproducible modes and `n_m` chunks in each mode.

The target empirical measure should be

`mu_c = sum_m (1/M_c) * sum_{j:m(j)=m} (1/n_m) delta_{a_j}`.

This gives each discovered mode equal mass rather than allowing planner frequency to define “ground-truth” importance. It must be called a **compiler/planner roster measure**, not the complete feasible action set.

### 2. Define a genuinely joint predicted measure

The model outputs

`nu_theta(c,z) = sum_{k=1..K} q_k delta_{a_hat_k}`,

with fixed `q_k=1/K` or explicitly predicted normalized masses. To justify “joint,” the K outputs need permutation-equivariant cross-slot coupling or shared set-level latent interaction. K independent noise samples batched through an unchanged action head do not satisfy this requirement.

### 3. State the asymmetric UOT objective

A minimally complete objective is

`min_{T>=0} <T,C> + eps*H(T) + tau_pred*KL(T1 || q) + tau_tgt*KL(T^T1 || w)`,

where `w_j=1/(M_c*n_{m(j)})`, `C_kj=d_func(a_hat_k,a_j)`, and `tau_tgt` is large enough that deleting a rare target mode is expensive. Duplicate predictions must either compete for the same target mass or pay prediction-mass deletion cost.

The current phrase “penalize probability mass in infeasible regions” is not implemented by UOT alone. Exact simulator rollback is non-differentiable, and an invalid chunk can be close in action distance to a feasible chunk. The paper may honestly claim that UOT pulls predictions toward the verified roster. It may claim a direct invalid-mass penalty only if it adds a differentiable signed-distance/contact cost, policy-gradient estimator, or learned feasibility critic. Each option changes complexity and prior-art exposure; none should be smuggled into the current claim.

## Exact Set Metric Required

Evaluation must use simulator rollback from the **same checkpoint** for every predicted member and must separate precision from coverage.

For a predicted K-set:

- **Rollback precision:** `P_valid = (# predicted chunks satisfying the registered predicates)/K`.
- **Roster-mode recall:** `R_mode = (1/M_c) sum_m 1[there exists a rollback-valid prediction assigned to mode m]`.
- **Set F1:** harmonic mean of `P_valid` and `R_mode`; report both components, never F1 alone.
- **Worst-mode hit rate:** minimum across target modes of the probability that at least one of K predictions hits that mode.
- **Rollback UOT distance:** evaluation-only UOT between the mode-uniform target measure and predicted measure, with an explicit cemetery cost for invalid predictions and an explicit missed-mode cost. This prevents invalid or unmatched mass from disappearing silently.
- **Coverage curve:** `R_mode(K)` and `P_valid(K)` for fixed `K in {1,2,4,8}`, with equal total action-model forward/sample budgets across methods.

Closed-loop success is necessary but not a set metric. If one slot is selected uniformly, expected immediate viability is governed by `P_valid`, not by joint set coverage. Any claimed control benefit from `R_mode` must state how alternative coverage affects replanning or future geometry without adding a hidden selector.

## Cheapest Non-GPU Kill Test

**Goal:** determine whether a stable multi-mode fiber exists and whether joint allocation has headroom over independent samples. Run no model training.

Use approximately **45 simulator checkpoints**: 15 each from aperture, shelf/obstacle-routing, and hook/contact-schedule families. At each checkpoint:

1. launch 32 planner/controller seeds under one fixed protocol;
2. rollback-verify every candidate and retain the full attempted ledger;
3. split seeds into two disjoint halves of 16;
4. independently cluster verified chunks in each half with the pre-registered `d_func`;
5. match clusters across halves and compute bidirectional mode recall;
6. compare empirical K-i.i.d. roster sampling with the oracle K-medoids/farthest-point subset for `K<=8`.

**Kill the current joint-set concept before GPU if any condition holds:**

- fewer than **30%** of checkpoints contain at least two modes reproduced in both seed halves;
- median bidirectional cross-half mode recall is below **0.70**;
- doubling from 16 to 32 seeds changes discovered mode count by more than **25%** on the median checkpoint, showing an unsaturated planner roster;
- at fixed K, oracle diverse subset selection improves mode recall by less than **5 percentage points** over K i.i.d. samples from the mode-balanced empirical roster, leaving negligible headroom for learned joint coupling.

This is the cheapest decisive test because it uses only the proposed data compiler and asks whether the set target and the need for correlated K outputs exist at all. A failure means no amount of GPU training can validate the paper's central object.

## Implementation Feasibility Under the Stated Constraints

### Pi0.5/action diffusion integration

A standard Pi0.5/action head produces one `H x A` chunk. There are two materially different implementations:

1. **Batch K independent noise samples.** This is easy, preserves the frozen backbone, and fits four A100s—but is ordinary multi-sample diffusion, not a joint set model.
2. **Create K coupled action slots.** This requires a trainable permutation-equivariant cross-slot adapter or a `K x H` action-token layout with controlled positional encoding and attention. Full attention can scale roughly with `(K*H)^2`; K=8 may be expensive even with a frozen VLM. A realistic E0 should begin with K=2 or 4, LoRA/action adapter tuning, mixed precision, and checkpointing.

Sinkhorn/UOT over K-by-J sets is computationally negligible. The difficult parts are stable target-set construction, cross-slot architecture, and differentiating any claimed invalid-mass term.

### Data and compute

The proposed 50,000–100,000 states with up to eight verified chunks implies 400,000–800,000 successful rollback executions plus failed planner attempts. One to two CPU days is plausible only with aggressive simulator parallelism and short horizons; it should not be assumed. The non-GPU audit must estimate eligible multimode yield and seconds per verified mode before committing.

Four A100s are sufficient for a bounded adapter E0 at K=2–4 if the VLM is frozen. They do not make a genuinely joint K=8 Pi0.5 action expert automatically cheap. The original 48–80 A100-hour estimate is provisional until a one-batch memory/throughput measurement exists.

### No tactile sensing

No tactile input is acceptable for visible clearance and pre-contact routing modes. Claims about distinct post-contact schedules must be limited to differences inferable from RGB/proprioception; otherwise the policy is asked to choose among modes whose relevant state is partially unobserved. Simulator rollback can label such modes but cannot make them identifiable at deployment.

## Claim Ceiling

Even if a later E0 succeeds, the strongest currently defensible claim is:

> On compiler-defined states with multiple reproducible, visually identifiable, rollback-verified action modes, a cross-slot-coupled K-hypothesis policy trained against a mode-balanced roster measure improves validity–coverage trade-offs over mode-balanced standard diffusion and K-i.i.d. sampling at the same data and sample budget.

The current concept cannot claim:

- recovery of the complete feasible action fiber;
- novelty of multimodal diffusion, K samples, permutation-invariant prediction, or OT matching;
- direct suppression of all infeasible mass without an implemented differentiable signal;
- real-robot contact-mode coverage without tactile sensing or real-world validation;
- value from joint set structure if only the selected-slot marginal changes.

## Final Recommendation

**NO-GO for GPU experiments and NO-GO as a paper mechanism in its current form.**

**Conditional continuation:** authorize only the 45-checkpoint CPU/planner audit. If the roster is reproducibly multimodal and oracle diverse K-selection has at least five points of recall headroom over K i.i.d. mode-balanced samples, reformulate the method around a precise roster measure and run a tiny architecture sanity check. The first GPU baseline must be mode-balanced standard diffusion with K i.i.d. samples—not demonstration-only BC.

If the audit passes but joint coupling cannot beat that baseline, retain the data result and abandon “set diffusion.” If it does beat it, then a focused novelty check against multi-hypothesis trajectory prediction, set diffusion, and robot action-set generation becomes mandatory before scaling.
