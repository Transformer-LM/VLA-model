# Experiment Tracker — v5 integrity restart

| Version / run | Status | Interpretation |
|---|---|---|
| v3 | INVALID | pre-yaw fixes and narrow hard split; no GPU main |
| v4 R000/R001/R100 | INVALID DATA | `mj_setConst` reset randomized qpos |
| v4 M1a | INVALID RUN | validation instability exposed data bug; not evidence |
| v5 R000 | TODO | corrected initialization smoke + no-pusher |
| v5 R001 | TODO | fresh 2k + layout/settling/leak audit |
| v5 R100 | BLOCKED | fresh 12k after v5 R001 PASS |
| v5 M1a/M1b | BLOCKED | fresh code/data hashes only |

