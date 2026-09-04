# Research Wiki Query Pack

_Auto-generated. Do not edit._

## Project Direction
# Research Brief — Object-addressed action-updated belief for VLA

**Status:** authorized for autonomous idea discovery, method planning, implementation, and offline/simulation experiments  
**Paper writing:** disabled

## Starting observation

OA-WAM separates persistent object address from dynamic content and pose, improving language-to-object binding. EvoScene-VLA maintains an action-updated scene belief across action chunks so that state changes need not be reconstructed only from the latest image.

Neither component alone establishes reliable long-horizon execution. The research question 
## Open Gaps
# Gap map

Pending evidence-map synthesis.
# Gap Map (2026-08-29)

- G1: learned per-object-address action-effect innovation is missing between OA-WAM-style binding and EvoScene-style global correction.
- G2: selective object/relation belief correction under occlusion, ID swaps, and execution failures is not isolated by current VLA/WAM memory systems.
- G3: equal-magnitude discrepancy attribution among execution failure, association failure, and unobservability is under-evaluated.
- G4: object-level belief must demonstrate downstream decision value beyond better prediction metrics.

The broad combination "object memory + WAM + verifier/recovery" is not a gap; POT-VLA, HarnessWAM, CheckVLA, RB-VLA, and Reflective VLA already cover major parts.

## Failed Ideas (avoid repeating)
- **Interaction-Fingerprint Belief for Object Identity**: 
## Recent Relationships (2 total)
  exp:ifb-v5-m1a-headroom --invalidates--> claim:privileged-mass-friction-headroom
  idea:interaction-fingerprint-belief --tested_by--> exp:ifb-v5-m1a-headroom
