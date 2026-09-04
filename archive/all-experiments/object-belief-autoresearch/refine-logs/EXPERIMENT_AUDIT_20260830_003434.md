# Experiment audit — remediated snapshot

## Verdict: WARN

The first full audit remains historically **FAIL** because its snapshot had a stale tracker and incomplete provenance. After remediation, a fresh read-only delta audit verified:

- final tracker status is consistent;
- all six non-empty checkpoints exist and match the recorded manifest hashes;
- 2k sanity and 300 prelaunch datasets match their sidecars;
- R000/R001/M1a/orchestrator logs exist;
- all 31 entries currently listed in the manifest exist and match their SHA-256 values;
- core M1a KILL remains supported.

Remaining warnings: no per-example prediction archive, one dataset seed, simulation-only oracle state, pose-only accuracy 96.39% on `hard_id`, random-address rather than downstream wrong-target semantics, and incomplete manifest coverage of eight existing logs.

See `../EXPERIMENT_AUDIT.md` and `.aris/traces/experiment-audit/2026-08-30_run02/`.
