# Experiment Tracker — live v3 run

**Remote session**：`ifb_v3_20260829`  
**Personal root**：`<PERSONAL_RESEARCH_ROOT>/workspace/object-belief-fingerprints`  
**Result namespace**：`results/20260829_ifb_v3`

| Run ID | Milestone | System | Split | Status | Notes |
|---|---|---|---|---|---|
| R000 | M0 | CUDA/MuJoCo/contact/no-pusher smoke | tiny | COMPLETE | tier-2 and tier-3 witnesses passed |
| R001 | M0 | v3 2k generator + leakage audit | sanity | RUNNING | CPU generation started 23:17; no GPU occupied |
| R100 | M0 | v3 12k generator + leakage audit | main | BLOCKED | waits for R001 audit PASS |
| R101–R113 | M1a | shared vs privileged oracle, 3 seeds | hard_id | BLOCKED | waits for R100 audit PASS |
| R121–R143 | M1b | system_id vs full_history/full_history_aux | hard_id | BLOCKED | only launches if M1a PASS |

GPU preflight at launch: physical 0/1/2/3 all individually idle (0 MiB, 0% utilization, no compute apps). The orchestrator rechecks before every training job.

