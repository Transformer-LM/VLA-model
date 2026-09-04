# Functional-Geometry Composition for VLA — Scoop Check

Date: 2026-08-30

## Proposed claim

Keep the high-level instruction, semantic roles, and goal relation fixed, but hold out ordered target–reference geometry pairings. At test time, the new pairing must change the executable HOW: grasp region/orientation, pre-alignment, approach direction/path, placement depth, phase membership/order, or feasibility. Pair PointMaps condition a frozen or lightly adapted VLA to produce that geometry-specific execution.

## Claim decomposition

| Axis | Proposed value |
|---|---|
| Input | target PointMap, reference/receptacle PointMap, language relation, baseline VLA chunk |
| Output | variable-length executable keyposes/contact phases or corrected action chunk |
| Generalization | both factor values individually seen; their ordered pairing held out |
| Critical control | same instruction and matched terminal goal, but different geometry requires different internal path/phases |
| Intended claim | pairwise functional geometry, not object identity or terminal pose alone, determines the executable HOW |

## Search coverage

Queries covered functional geometry, unseen object–receptacle pairs, compositional manipulation, point-cloud skill transfer, object-centric trajectories, and geometry-aware VLAs/WAMs, with emphasis on 2023–2026. Connectors returned useful results from arXiv/OpenAlex/Crossref and web search; arXiv PDF download intermittently failed with SSL EOF and Semantic Scholar was rate-limited. The verdict is therefore a strong prior-art warning, not a proof of global non-existence.

## Nearest prior art

| Work | What it already covers | Remaining difference |
|---|---|---|
| Efficient Data Collection via Compositional Generalization (RSS 2024) | explicitly holds out factor combinations, including object type × container type, in a real put-inside task | does not isolate matched-terminal-goal cases where pair geometry forces a phase/path change |
| GIFT (2025/2026) | transfers grasp/contact functions, object–environment constraints, and geometry-consistent trajectories to substantially different shapes | one-shot correspondence transfer; not a VLA pair-composition split and mostly preserves demonstrated operation structure |
| FMB (IJRR 2024/2025) | functional grasp, reorientation, insertion, geometry variation, and composition/ordering of manipulation skills | benchmark is not centered on held-out ordered source–receptacle pairings with terminal-pose-matched diagnosis |
| RPDiff (2023) | paired object/scene point clouds, relational placement, novel geometries of both objects and scenes | predicts final relational pose; not an explicit diagnosis/adaptation of the full internal skill HOW |
| MATCH POLICY (2024) | paired point clouds and pick/preplace/place keyframes for insertion/hanging; unseen configurations | registers new observations to stored demonstrations; does not test systematic factor composition that changes phase membership/order |
| SPOT (2024) | target-relative object SE(3) trajectories encode intermediate constraints and drive closed-loop action plans | learns task trajectories rather than isolating pair-compositional functional geometry |
| CoA-VLA (2024) | object, grasp-part, placement-space, and movement-path affordance chain inside a VLA | unseen-pose/obstacle generalization, but not the proposed controlled held-out pair split |
| OA-WAM (2026) | persistent object addresses, content/pose slots, next-slot prediction, and action generation | object binding under shifts; no functional-pair HOW evaluation or counterfactual verification |
| Lift3D-VLA (2026) | explicit point-cloud reasoning, future geometry prediction, temporally structured action generation | broad 3D VLA improvement rather than isolated pair-compositional HOW |
| PointVLA (2025) | point clouds injected into a VLA and geometry-driven adaptation such as unseen table heights | broad geometry conditioning; not pairwise functional composition |

## Verdict

- Broad claim — “new geometry should make a VLA change its trajectory”: novelty level 2/5 (heavily overlapping), approximately 3.5–4.5/10.
- Narrow diagnostic claim — “under matched terminal goals, held-out ordered geometry pairs require changes in internal execution phases/path, and current VLAs fail specifically there”: novelty level 3/5, approximately 6–7/10, subject to a deeper benchmark audit.
- Proposed method — “PointMaps plus four fixed phase correction heads”: not presently defensible. It assumes the phase scaffold is already known and total, whereas geometry may add, remove, or reorder phases. Once phase scheduling is learned, it overlaps with existing affordance-chain, keyframe, and trajectory methods and needs a sharper mechanism.

## Necessity gate

Run an oracle ladder before training a full method:

1. frozen VLA;
2. VLA + target/reference PointMaps;
3. VLA + oracle terminal 6D pose;
4. VLA + oracle executable keypose/contact-phase sequence.

Proceed only if the oracle executable sequence substantially exceeds the oracle terminal pose on held-out pairings, while terminal targets and task semantics are matched. Otherwise the problem reduces to perception/pose estimation, motion planning, or low-level control rather than a new VLA research problem.

## Defensible one-sentence delta

Unlike prior work that transfers a demonstrated trajectory, predicts a relational goal pose, or evaluates generic factor composition, this work would isolate and learn held-out target–reference geometry composition that changes the executable internal structure of an otherwise fixed manipulation skill under matched semantic and terminal-goal conditions.
