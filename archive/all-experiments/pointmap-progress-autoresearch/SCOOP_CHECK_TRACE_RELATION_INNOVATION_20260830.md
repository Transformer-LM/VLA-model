# Scoop check: trace-conditioned historical relation revision

Date: 2026-08-30

## Verdict

**Level 2 — High Overlap.** The broad combination of persistent object/scene state, 3D grounding, action-conditioned verification, event memory, and recovery is substantially covered by POT-VLA, CheckVLA, EvoScene-VLA, ChainVLA, ReViP, EV-WM, EventVLA, and HELM. The remaining defensible delta is a narrow empirical/mechanism claim about whether the *realized* kinematic trace adds information beyond intended commands and post-action geometry for retracting one previously completed, now non-active relation.

## Delta

Unlike POT-VLA, which refreshes shared 3D object records and evaluates current geometric predicates, and CheckVLA, which verifies the currently committed action chunk against commanded-action-conditioned futures, the proposed work isolates whether the robot's realized execution trace adds information beyond both intended commands and post-action PointMap evidence for selectively retracting one previously completed, now non-active object relation under visual aliasing, while otherwise requesting re-observation.

## Decomposed claim

- Problem framing: decide whether a historical `inside/on` relation, previously marked complete, was invalidated by a later action when the post-action view is ambiguous.
- Core mechanism: fuse a pre-observation transition prior conditioned on realized kinematics with a frozen PointMap observation likelihood, then output `retract / re-observe / continue` for the exact relation.
- Key insight: commanded action and current geometry can be observationally aliased; the difference between commanded and realized motion may identify physics-mediated invalidation.
- Application domain: long-horizon VLA manipulation with action chunks, object-relation progress memory, occlusion, co-motion, slip, and later disturbance.

## Closest prior work

- POT-VLA (arXiv:2607.18016): persistent role-indexed RGB-D/3D object records shared by action generation and geometric predicate verification; supports `continue/retry/reobserve/reground/replan`. Overlap: 3/4 axes.
- CheckVLA (arXiv:2607.26789): frozen action-conditioned world model verifies committed chunks, conformally controls intervention, rewrites the suffix, and keeps event keyframes. Overlap: 3/4 axes.
- EvoScene-VLA (arXiv:2605.21862): recurrent action-updated, observation-corrected geometric scene prior across chunks. Overlap: 3/4 axes.
- ChainVLA (arXiv:2608.02326): joint revisable execution state with progress context, sparse event memory, and unexecuted motion tail. Overlap: 2/4 axes.
- ReViP (arXiv:2601.16667): false-completion benchmark and vision-proprioception rebalance for object drop, distractor swap, and relayout. Overlap: 2/4 axes.
- EV-WM (arXiv:2606.13053): action-conditioned latent rollout decoded into structured relation/event states for predicate-grounded planning and gating. Overlap: 2/4 axes.
- EventVLA (arXiv:2606.20092): sparse task-critical visual evidence memory for non-Markovian VLA tasks. Overlap: 2/4 axes.
- HELM (arXiv:2604.18791): episodic memory, learned state verifier, and rollback/replanning for long-horizon VLA recovery. Overlap: 2/4 axes.

## Innovation gate

The method is paper-worthy only if a held-out, matched experiment establishes all of the following:

1. Realized trace beats intended-command-only, post-PointMap-only, current 3D predicate, and generic RGB verifier baselines at a fixed low false-retraction rate.
2. Within-stratum trace shuffling removes the gain, ruling out action-family shortcuts.
3. The gain concentrates in visually aliased, physics-mediated invalidation cases rather than easy visible failures.
4. Typed local revision reduces both false completion and wrong/global rollback in closed-loop VLA execution.
5. The result holds with learned perception rather than simulator-state geometry at test time.

If items 1–3 fail, the specific novelty does not exist and full VLA/WAM training should stop. Existing E0 PointMap-vs-Depth results establish representation headroom only and do not establish this novelty.

## Search limitations

The unified keyword search produced mostly off-topic matches; arXiv API requests failed with an SSL EOF error and Semantic Scholar returned HTTP 429 on two queries. Exact-title verification and full-text checks were therefore completed on the official arXiv pages for the closest candidates.
