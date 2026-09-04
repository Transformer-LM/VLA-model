# Step 1 — Decompose the novelty

Timestamp: 2026-08-30 (Asia/Shanghai)

- **Research problem:** A fixed high-level manipulation relation or skill must generalize to unseen target-object/reference-object functional-geometry pairings where geometry changes the required grasp, pre-alignment, approach path, placement process, phase membership/order, or feasibility.
- **Problem framing:** Hold the relation/skill and semantic object roles fixed; train on individual geometry factors and seen pairings, then test held-out ordered pairings under terminal-pose-matched controls.
- **Core mechanism claimed:** Encode the target/reference pair with object-resolved PointMaps and use the pair geometry to adapt the internal HOW of a frozen or lightly adapted VLA, rather than merely predict a terminal 6D pose.
- **Key insight:** Pairwise functional geometry can change an entire executable skill even when category, instruction, and terminal target are unchanged; instance generalization and coordinate transfer do not test this compositional property.
- **Application domain:** Rigid-object manipulation relations such as inside, insert, hang, stack/on, and constrained placement, in simulation and on a real robot.

The strongest defensible first contribution is diagnostic: establish an oracle gap between terminal-pose conditioning and a complete executable HOW scaffold before training a new selector or adapter.
