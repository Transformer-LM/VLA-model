# Experiment Audit Report

**Date:** 2026-08-30  
**Auditor:** GPT-5.6-Sol ultra（fresh same-family agent，provisional）  
**Project:** OA-WAM × EvoScene interaction-fingerprint belief pilot

## Current Overall Verdict: WARN

## Current Integrity Status: warn

第一次完整审计的历史 verdict 是 **FAIL**：核心 v5 数值和 `KILL_NO_PRIVILEGED_HEADROOM` 判定相互一致，但审计时归档不完整且 tracker 与实际状态矛盾。补档后由新的只读差分审计复核，硬 FAIL 条件已解除，当前快照降为 **WARN**。历史 FAIL 原件保留在 `refine-logs/EXPERIMENT_AUDIT_20260830_001250.md` 和 `.aris/traces/experiment-audit/2026-08-30_run01/`，没有追溯改写。

### Remediation delta

- 最终 tracker 已正确标记 R000/R001/R100/M1a complete、M1a KILL、M1b not run。
- 六个 checkpoint 均存在且非零，哈希与 provenance manifest 一致。
- 2k sanity、300 prelaunch、R000/R001/M1a/orchestrator logs 已归档。
- manifest 中已有的 31/31 条记录全部存在且 SHA-256 匹配。
- 仍缺逐样本预测，manifest 未覆盖八个已存在的 R100/训练日志；这些保留为 WARN。

## Checks

### A. Ground Truth Provenance: PASS

- 身份与状态真值来自 MuJoCo persistent body identity/state，不来自模型输出。
- `address_to_body`、detection permutation 和 effect target 可从原始 NPZ 精确重建。
- 这是 `simulation_only`、oracle-addressed pilot，不是端到端视觉 tracking。

### B. Score Normalization: PASS

- normalizer 只在训练集拟合；scale calibration 只用验证集。
- 未发现使用模型自身最大值/均值美化分数，也未发现 test-label calibration leak。

### C. Result Existence and Consistency: WARN after remediation

- 六个 JSON、日志、seed、hash、80 epochs、2,000 optimizer steps及汇总数字全部匹配。
- `hard_id` 上 shared 为 95.5322%，oracle 为 96.1150%，增益仅 0.5828pp；seed 11 为负增益，故 KILL 正确。
- 审计时最新 tracker 仍写 R001 TODO、R100/M1a blocked，且关键 provenance 未归档，因此历史审计判 FAIL；这些硬缺口现已补齐。当前仍没有逐样本预测，且 manifest 对部分训练/R100日志覆盖不完整，所以为 WARN。

### D. Dead Code and Metric Semantics: WARN

- 主要指标函数均被调用。
- summarizer 未严格 whitelist run IDs；显示的 gate 文本遗漏“wrong-target reduction > 0”和“每个 paired seed > 0”。
- `wrong_target_rate` 实际是随机 address 的 assignment error，不是下游任务失败率。

### E. Scope: WARN

- 单一程序化 MuJoCo 平面场景、三个相同 box、一个 pusher、一个 dataset seed、三训练 seeds/variant。
- 没有 RGB/RGB-D、真实遮挡、语言、VLA、闭环恢复或真实机器人。
- `hard_id` 对 pose-only 仍有 96.39% assignment accuracy，因此“真正困难身份集”这一描述不成立。

### F. Evaluation Type: PASS

`simulation_only` with simulator-provided `real_gt`; oracle variant 是 privileged ceiling only。

## Claim Impact

- “v5 M1a 因缺乏 privileged headroom 而 KILL”：数值支持。
- “质量/摩擦 oracle 至少提升 5pp”：本 pilot 反驳。
- “所有 oracle seeds 都优于 shared”：反驳，seed 11 为负。
- “system-ID 优于 full-history”：未测试，不能声称。
- 任何 VLA、OA-WAM×EvoScene、长时任务、视觉或真实机器人结论：均不支持。

完整历史审计见 `.aris/traces/experiment-audit/2026-08-30_run01/001-integrity-audit.response.md`；补档差分审计见 `.aris/traces/experiment-audit/2026-08-30_run02/001-remediation-delta.response.md`。
