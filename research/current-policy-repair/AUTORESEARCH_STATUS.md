# Autoresearch status 鈥?imagined-state repair

**Status:** blocked at method-evidence gate  
**Score:** 5.5/10 (routing heuristic; provisional)  
**Integrity:** pass for the 18-scene paired pilot  
**Claim:** partial  
**Deadline milestone:** 2026-09-03 12:00 Asia/Shanghai

## Working claim

An action-conditioned WAM imagined frame can change a frozen VLA's next action
and can cause harmful downstream execution on repeated simulation seeds.

## Evidence

- 18 paired scenes across LIBERO goal/spatial suites.
- Baseline success: 15/18; raw WAM: 12/18; anchored image repair: 13/18.
- Three baseline-success/raw-failure pairs; anchored repair rescues one.
- Mean next-action L2 to the oracle future: raw 3.1044, anchored 1.1827.
- Repeated identical-image policy queries are deterministic.

## Why the full idea is not validated

The available 500-step WAM checkpoint has final-frame PSNR around 9.5--10.0
and is not a reliable physical state source. Anchored blending is only a
diagnostic baseline. No learned independent geometry witness or state-level
repair has been evaluated, and direct reject/replan already avoids the observed
harmful cases.

## Required next evidence

Provide a complete local Wan VAE (or use an explicitly synthetic physical-
corruption benchmark) and train/evaluate a stronger WAM. Then compare raw WAM,
reject/replan, anchored blend, and PointMap/relative-geometry state repair with
paired starts, at least three seeds, harmful-intervention rate, action regret,
and calibration. If repair cannot beat direct reject/replan, preserve the
negative result and pivot.

## Current execution

The missing VAE has now been downloaded locally and copied to the personal
remote model directory with matching SHA-256. The minimal WAM load/inference
sanity passed. A four-GPU, W&B-disabled 5000-step continuation is running from
the personal FastWAM workspace; no real-robot process is active. The new
checkpoint and downstream evaluator remain pending until this run finishes.
