# Research Brief

**Status:** ready-for-discovery; expanded field map complete; delegated direction selected; authorized for autonomous candidate review and gated experiments  
**Scope:** research only; paper writing disabled

## Objective

Search across VLA-only, WAM-only, and VLA×WAM research—not only the previous
sixteen directions—and produce one naturally motivated, implementable idea that
receives a skeptical provisional novelty score greater than 7.0/10. A score may
not be inflated to pass the gate. If no candidate passes after structural
pivots, preserve the negative result instead of forcing an idea.

## Selected direction after expanded field discovery

The 37-direction non-tactile map selected **X8+X14: source-aware
VLA×WAM verification with counterfactual causal evaluation**. The target problem
is to distinguish three causes that can create similar future–reality residuals:

1. the commanded action genuinely failed in the environment;
2. the action succeeded but the WAM was misspecified or out of support;
3. the observation is too ambiguous to decide.

The causes must lead to different actions: repair/replan, reobserve, or distrust
and optionally update the WAM. Functional-geometry HOW generalization remains
the first structural fallback if exact novelty review scores this direction at
or below 7.0/10.

## Hard scientific constraints

- The contribution must be more than adding Depth, PointMap, memory, a verifier,
  or another familiar component.
- The problem must occur in real VLA control or learning, not only in a benchmark
  constructed to favor the method.
- Every candidate needs an exact nearest-work comparison, falsifiable mechanism,
  matched baseline, negative control, and inexpensive go/no-go pilot.
- No method may require tactile or force sensors. Allowed signals are RGB,
  RGB-D, inferred/observed PointMaps or 3D geometry, proprioception,
  end-effector/joint execution traces, actions, and language.
- A positive representation metric alone is insufficient; the final evidence
  must affect policy decisions or environment outcomes.

## Search coverage

Build an expanded landscape with up to eight macro groups and as many distinct
subdirections as the evidence supports. Explicitly include:

1. VLA objectives, architectures, memory, action representations, uncertainty,
   generalization, post-training, and deployment adaptation.
2. WAM representations, controllability, uncertainty, data, evaluation,
   system identification, and model exploitation.
3. VLA×WAM representation learning, planning, verification, recovery, policy
   improvement, synthetic experience, co-evolution, cross-embodiment transfer,
   and other evidence-supported couplings.
4. Directions missing from the previous sixteen-direction map.

The user delegated direction and idea selection to the workflow. Do not pause
for a ranking choice; record the selection rationale and continue only if the
novelty and feasibility gates pass.

## Compute and execution authority

- Remote host: `<REMOTE_USER>@<PRIVATE_SERVER>` via Windows OpenSSH and the user's
  existing Ed25519 key.
- Read/write only `<PERSONAL_RESEARCH_ROOT>`.
- Never use root, sudo, su, `.bashrc`, global Conda, system CUDA, or shared
  directories. The server lacks unrestricted external internet access.
- GPUs 0–3 are available candidates, but each GPU must be checked immediately
  before launch for both memory/process occupancy. Never preempt or share a GPU.
- Prefer GPU implementations for neural pilots. CPU is limited to orchestration,
  metadata checks, compilation, and analyses that do not benefit from CUDA.
- Paid compute and private-data upload are prohibited.
- Live real-robot motion remains disabled until an exact connection and safety
  protocol is separately available; offline robot data are allowed.

## Required progression

1. Expanded field/evidence map.
2. Candidate pool with explicit kills and pivots.
3. Exact-title and mechanism-level novelty audit.
4. Skeptical review with a strict `>7.0/10` idea gate.
5. Method and claim-driven experiment plan.
6. Hash-bound implementation review and GPU sanity pilot.
7. Matched experiments, integrity audit, and result-to-claim decision.

Do not begin full training merely because GPUs are idle. Once a candidate passes
the idea and preflight gates, proceed directly without waiting for another
confirmation.
