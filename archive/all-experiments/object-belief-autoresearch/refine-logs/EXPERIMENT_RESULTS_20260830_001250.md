# v5 M1a pilot results

## Outcome

`KILL_NO_PRIVILEGED_HEADROOM`. The privileged mass/friction oracle did not create the preregistered 5pp headroom, so system-ID/full-history M1b was not launched.

| Variant | hard_id assignment accuracy (3-seed mean) | wrong-address assignment error | posterior NLL |
|---|---:|---:|---:|
| Shared dynamics | 95.5322% | 4.8951% | 0.32484 |
| GT mass/friction oracle | 96.1150% | 4.0793% | 0.30910 |
| Oracle − shared | **+0.5828pp** | **−0.8159pp** | −0.01575 |

Paired assignment gains: seed 11 `−0.8159pp`, seed 22 `+1.1655pp`, seed 33 `+1.3986pp`.

Registered pass required all of:

1. oracle assignment gain ≥ 5pp;
2. wrong-address error reduction > 0;
3. every paired seed gain > 0.

Conditions 1 and 3 failed. The result only says that true mass/friction adds little marginal association information in this particular oracle-state MuJoCo setup. It does not test RGB object binding, long-horizon memory, VLA action quality, recovery, or real robots.

## Compute

Six A100 runs consumed 200.90 GPU seconds in total, approximately 0.0558 GPU hours. All server jobs exited and GPUs were released.

## Integrity notes

- v3/v4 are invalid and excluded.
- The v5 dataset/code hashes match all six result files.
- The strict fresh-agent audit rated the audit-time bundle FAIL because the tracker was stale and provenance incomplete; see `../EXPERIMENT_AUDIT.md`.
- After that audit, v5 checkpoints and missing R000/R001/orchestrator/summary logs were copied from the user's personal remote directory into the local v5 evidence bundle. The historical audit verdict is intentionally not rewritten.
