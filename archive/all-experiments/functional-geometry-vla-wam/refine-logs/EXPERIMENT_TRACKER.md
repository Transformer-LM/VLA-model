# Experiment Tracker

| Run ID | Milestone | Purpose | System / Variant | Split | Metrics | Priority | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| R001 | M0 | 候选覆盖 sanity | frozen π0.5, K candidates | pilot ID + intra-category OOD | diversity, duplicate rate, top-k coverage, legality | MUST | TODO | 若覆盖为零，转 action generation |
| R002 | M1 | Oracle gap | top-1 vs terminal-pose oracle vs full-rollout oracle | paired OOD states | success, regret, failure type | MUST | TODO | ≥10pp 才继续 |
| R003 | M1 | 排除终点位姿解释 | terminal-matched geometry pairs | controlled OOD | path/grasp/phase difference, success | MUST | TODO | 建立 HOW necessity |
| R004 | M2 | 最小 WAM overfit | object-relative PointMap WAM | tiny pilot | geometry/event loss, ranking | MUST | TODO | Gate 1 capacity |
| R005 | M2 | 动作因果控制 | valid/shuffled/zero action | held-out pilot | prediction delta, pairwise rank | MUST | TODO | Gate 2 causality |
| R006 | M2 | 表征比较 | RGB vs global PointMap vs object-relative PointMap | OOD pilot | rank accuracy, regret, calibration | MUST | TODO | 同预算 |
| R007 | M3 | 强基线 | π0.5 + PointMap adapter | OOD pilot | closed-loop success | MUST | TODO | model-free geometry baseline |
| R008 | M3 | 强基线 | training-only future geometry | OOD pilot | closed-loop success | MUST | TODO | auxiliary objective baseline |
| R009 | M3 | 强基线 | direct action scorer | OOD pilot | ranking, success, latency | MUST | TODO | WAM necessity baseline |
| R010 | M3 | 主方法 | geometry WAM reranking, seed 1–3 | OOD pilot | success, Oracle-gap recovery | MUST | TODO | ≥5pp and ≥30% gap |
| R011 | M3 | 机制消融 | no relative frame/no reference/no action | OOD pilot | model + policy metrics | MUST | TODO | causal isolation |
| R012 | M4 | 跨任务 | fixed method on 3 task families | held-out instances/pairs | per-task success, failures | MUST | TODO | 不调 final split |
| R013 | M4 | 真实机器人 | frozen configs | real intra-category OOD | success, safety, latency | MUST | TODO | 先完成安全接口审查 |
| R014 | M5 | exploitation audit | high-imagined/low-real actions | stress | imagined-real gap, tail risk | MUST | TODO | uncertainty rejection |
| R015 | M5 | qualitative | representative successes/failures | final | videos/trajectories | NICE | TODO | 不替代定量证据 |

