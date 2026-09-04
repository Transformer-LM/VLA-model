# AutoResearch Status

**Run:** `20260806-061818-vla-wam-world-action-model-latent-dynamics-model`  
**Overall status:** active  
**Next phase:** contract  
**Exploration level:** broad-field discovery  
**Selected macro direction:** none; human checkpoint required  
**Scope:** research through validated experiments; paper writing disabled

## Current objective

First map the broad intersection of embodied VLA and learned world models / WAM,
then compare five to eight macro research directions. Long-horizon manipulation,
video-generative WAM, latent dynamics, model-based RL, a robot embodiment, and a
benchmark are not preselected outcomes.

## First stopping point

The system will produce:

- `research-stage/FIELD_DISCOVERY_CONTRACT.md`
- `research-stage/LITERATURE_MAP.md`
- `research-stage/DIRECTION_LANDSCAPE.md`

It will then block `idea-discovery` and wait for the user's macro-direction
selection. It may rank and recommend directions, but cannot select one on the
user's behalf.

## Readiness

- Field mapping, literature discovery, and direction comparison: **ready**.
- All eight research phases are still pending; no research artifact or
  experiment has been produced yet.
- Local experiment execution: **blocked at preflight** because no NVIDIA GPU is
  detected and `compute.backend` is `unconfigured`.
- Paid compute and real-robot execution: disabled.
- Recorded usage: 0 GPU-hours, 0 paid cost, 0 robot trials.

## Active files

- Scientific brief: `RESEARCH_BRIEF.md`
- Automation and safety config: `AUTORESEARCH_CONFIG.json`
- Machine state: `.aris/autoresearch/active_run.json`
- Workflow skill: `.agents/skills/embodied-autoresearch/SKILL.md`

This dashboard is informational. The JSON run state and raw research artifacts
are authoritative.
