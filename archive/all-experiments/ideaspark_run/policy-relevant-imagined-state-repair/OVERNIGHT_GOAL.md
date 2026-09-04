# Overnight execution goal

**Deadline:** 2026-09-03 12:00 Asia/Shanghai  
**Scope:** policy-relevant imagined-state repair for downstream VLA decisions
**Safety:** simulation/offline only; no real-robot motion; no external
network/install; all remote artifacts under `<PERSONAL_RESEARCH_ROOT>`.

## Decision objective

Determine whether an independent geometry witness can repair a WAM imagined
state enough to prevent harmful downstream VLA action changes, while retaining
any genuine benefit of imagination. The result may be positive, partial, or a
negative finding.

## Execution gates

1. Consolidate the existing 15-scene paired WAM/VLA evidence and literature
   collision map.
2. Implement the smallest geometry-witness pilot using simulator RGB-D/
   PointMap supervision; do not train a full WAM before the gate passes.
3. Compare raw WAM, direct reject/replan, anchored image blend, and
   geometry-conditioned repair on paired starts and at least three seeds where
   feasible.
4. Audit raw outputs and record supported/unsupported claims.

## Stop conditions

- The current WAM remains too inaccurate for a meaningful geometry test;
  report the limitation rather than claiming repair success.
- Geometry repair does not beat direct reject/replan on harmful-intervention
  rate and action regret.
- Any integrity, ownership, or GPU-safety check fails.

## Current status

The existing pilot has established downstream sensitivity and two harmful
baseline-success/raw-failure pairs, but has not established a learned physical
repair method. This file is a local milestone because an older system goal is
already blocked and cannot be replaced concurrently.

## Execution update (2026-09-02)

The paired experiment was extended to 18 scenes and three independent goal
seeds. Three baseline-success/raw-failure pairs were observed. A planned
5000-step WAM continuation was attempted with bounded startup fixes, but the
personal training launcher is currently blocked by its Hydra/DeepSpeed launch
contract after the existing 500-step checkpoint; no training process remains
running and no GPU is occupied. This is recorded as a blocker rather than
silently treating the 500-step checkpoint as a production WAM.

The final launcher attempt was stopped when it tried to download the missing
Wan2.2 VAE. No external download or real-robot run is permitted. The goal is
therefore complete for the current evidence gate with a **partial/blocked**
claim: downstream harm is established, repair efficacy is not.

## Resume after local asset provision (2026-09-03)

The user authorized the missing model download. `Wan2.2_VAE.safetensors` was
downloaded from the official ModelScope repository on the Windows client,
SHA-256 checked, and copied to the personal remote model directory. The
minimal WAM loading/inference sanity passed. A new offline 4×A100 training run
(`max_steps=5000`, W&B disabled) is now running from the personal FastWAM
workspace; the current log is
`<PERSONAL_RESEARCH_ROOT>/results/policy-relevant-imagined-state-repair/e1/fastwam_train5000_offline.log`.
