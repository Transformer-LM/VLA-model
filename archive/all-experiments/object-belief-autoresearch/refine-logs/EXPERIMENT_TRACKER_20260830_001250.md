# Experiment Tracker — v5 final

| Version / run | Status | Interpretation |
|---|---|---|
| v3 | INVALID | pre-yaw fixes and narrow hard split; never admissible evidence |
| v4 R000/R001/R100/M1a | INVALID | `mj_setConst` reset randomized qpos; all v4 data/results excluded |
| v5 R000 | DONE | corrected initialization/contact/no-pusher smoke passed |
| v5 R001 | DONE / PASS | fresh 2k integrity audit passed; data/log/hash now archived under `results/20260829_ifb_v5/provenance/` |
| v5 R100 | DONE / PASS | fresh 12k dataset and leakage/layout/contact audit passed |
| v5 M1a shared | DONE | seeds 11/22/33, fixed 80 epochs and 2,000 steps each |
| v5 M1a oracle | DONE | seeds 11/22/33, fixed 80 epochs and 2,000 steps each |
| v5 M1a gate | **KILL** | oracle gain 0.5828pp < 5pp and seed 11 paired gain is negative |
| v5 M1b | NOT RUN | correctly cancelled by the registered M1a stop gate |
| GPU state | RELEASED | GPUs 0–3 all at 0 MiB / 0% after completion |

Final marker: `results/20260829_ifb_v5/FINAL_STATUS.txt = KILL_NO_PRIVILEGED_HEADROOM`.

This tracker records execution completion, not a positive scientific result. The audit-time stale tracker was preserved in `EXPERIMENT_TRACKER_20260829_234000.md` for provenance.
