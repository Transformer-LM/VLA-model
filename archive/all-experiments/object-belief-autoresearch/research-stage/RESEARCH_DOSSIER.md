# Research Dossier — OA-WAM × EvoScene Interaction-Fingerprint Pilot

## Final outcome

**Exact idea killed.** The privileged mass/friction oracle supplies only +0.5828pp mean assignment gain and degrades one of three paired seeds. The preregistered M1a gate fails, so system-ID/full-history M1b was correctly not run.

Assurance: **same-family provisional**. Current integrity status: **WARN** after remediation.

## Research route

The direct combination “OA-WAM object slots + EvoScene action-updated memory” was rejected as insufficiently novel. The narrowed hypothesis was that object-specific physical response to controlled interactions could act as an identity fingerprint after object crossing/occlusion. This was tested only through a cheap privileged-ceiling gate before implementing the full method.

## Pilot method

- Environment: procedural MuJoCo plane, three identical boxes, spatial pusher.
- State: exact object XY and unordered post-interaction detections.
- Comparison: shared action-conditioned effect model versus true mass/friction oracle.
- Data: 12,000 episodes, one dataset seed; 8,400/1,800/1,800 train/validation/test.
- Runs: seeds 11/22/33 per variant, fixed 80 epochs, 2,000 steps.
- Gate: oracle gain ≥5pp, random-address assignment error reduction >0, and all paired seeds positive.
- Execution: six A100 jobs; 200.90 GPU seconds = 0.0558 GPU hours; no paid compute and no real robot.

## Main results

| Variant | hard_id assignment | random-address error | posterior NLL |
|---|---:|---:|---:|
| Shared | 95.5322% | 4.8951% | 0.32484 |
| GT-property oracle | 96.1150% | 4.0793% | 0.30910 |
| Difference | +0.5828pp | −0.8159pp | −0.01575 |

Paired assignment gains: seed 11 −0.8159pp, seed 22 +1.1655pp, seed 33 +1.3986pp.

The shared baseline is already 95.5322%, so a perfect oracle could improve at most 4.4678pp. The realized task cannot satisfy the preregistered 5pp threshold. This is a structural task/gate ceiling mismatch and prevents a universal “physical properties are useless” conclusion.

## Integrity and provenance

- v3/v4 are invalid because `mj_setConst` reset randomized qpos; they are excluded from v5.
- Deterministic evidence check found all 6/6 cited values.
- Full audit initially returned FAIL because the tracker and local provenance archive were stale/incomplete.
- After checkpoints, R000/R001/M1a/orchestrator logs and sanity/prelaunch data were restored from the user's personal server path, a fresh delta audit returned WARN.
- Remaining warnings: no per-example prediction archive, one dataset seed, incomplete manifest coverage for several existing logs, and no deep checkpoint replay.
- `hard_id` is not genuinely hard: pose-only assignment is 96.39%.
- `wrong_target_rate` is random-address assignment error, not downstream policy failure.

## Claim ledger

Supported:

- The current privileged-headroom gate fails.
- M1b must remain stopped on this dataset.
- The exact current operationalization is not worth further compute.

Unsupported:

- IFB/system-ID works.
- System-ID beats full-history memory.
- OA-WAM × EvoScene combinations generally fail.
- Any RGB/RGB-D, learned perception, VLA, long-horizon, recovery or real-robot claim.

## Reproducible artifacts

- Raw result: `results/20260829_ifb_v5/M1a_headroom_summary.json`
- Terminal marker: `results/20260829_ifb_v5/FINAL_STATUS.txt`
- Dataset: `results/20260829_ifb_v5/ifb_main_v5_12000.npz`
- Checkpoints/provenance: `results/20260829_ifb_v5/checkpoints/`, `provenance/`, and `PROVENANCE_MANIFEST.sha256`
- Experiment tracker/results: `refine-logs/EXPERIMENT_TRACKER.md`, `EXPERIMENT_RESULTS_20260830_001250.md`
- Integrity: `EXPERIMENT_AUDIT.md/json`
- Claim verdict: `CLAIMS_FROM_RESULTS.md/json`
- Full reviewer traces: `.aris/traces/experiment-audit/` and `.aris/traces/result-to-claim/`

## Cheapest next discriminating experiment

Do not lower the old gate or run M1b. A future, separately preregistered pivot must first construct an identity-ambiguity task where pose-only and shared dynamics are demonstrably unsaturated, interaction responses are identifiable, multiple dataset seeds are used, and the oracle ceiling is mathematically able to pass. Only a newly passing oracle gate would justify system-ID versus full-history experiments.
