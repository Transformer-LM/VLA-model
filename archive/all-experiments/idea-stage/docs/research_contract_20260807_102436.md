# Research Contract: PGR-Audit

> 当前唯一激活的 H1 研究契约。恢复运行时优先读取本文件、refine-logs/PGR_AUDIT_PROTOCOL.json、refine-logs/INPUT_MANIFEST.json 与 refine-logs/EXPERIMENT_TRACKER.md；不要重新引入已淘汰候选或 CF-DynAlign predictor。

## Selected Idea

- **名称：** Predictive Gradient Routing at a VLA Action Interface（PGR-Audit）
- **描述：** 在 frozen StarVLA 的 action-token interface 插入 rank-32 identity adapter，用 frozen valid future-latent decoder 的梯度形成 A treatment；与 action-only B 和一个固定 matched deranged-target C 对比。只有 predictive validity 与 controlled effect 先通过，才允许用 cross-fitted P/Q projector intervention 检验闭环策略是否局部依赖 treatment-associated predictive component。
- **来源：** idea-stage/H1_CYCLE3_SELECTION.md。
- **选择理由：** 三轮 idea discovery 后，其他候选因 prior overlap、identifiability、host mismatch 或预算失败被淘汰。PGR-Audit 的新意上限是窄的 diagnostic protocol，而非新 objective、adapter 或 WAM；method review 为 READY 9.0/10，执行计划正在修复后复审。

## Core Claims

1. **C0 predictive validity：** frozen action interface 与 demonstrated action 对 held-out future-latent residual 的预测超过最强 current-state/action/task controls，并对 action/representation derangement 敏感。
2. **C1 controlled algorithmic effect：** valid future correspondence 的 gradient algorithm 相对 action-only B 与一个固定 matched wrong-correspondence C，在 fixed tasks/checkpoint/states 上产生 seed-consistent closed-loop gain。
3. **C2 conditional placebo-relative reliance：** 只有 C0/C1 与全 seed P/Q eligibility 通过时，移除 predictive projector 比移除 empirical-support/action-output-matched Q projector 更伤害闭环成功率。
4. **Scope：** 最多支持 behavior-policy association、controlled algorithmic effect 与 task-local placebo-relative reliance；不支持 natural mediation、physical causality、SOTA 或跨架构泛化。

## Method Summary

Host 为 clean StarVLA commit 3422b9f…、frozen Qwen3-VL-4B 与 frozen deterministic MLPResNet action head。Adapter 只位于 [B,8,2560] action-token representation 与 frozen action head 之间。Future target 来自 main/wrist DINOv2 t+8−t CLS difference，经 D_head-train whitening、固定 32+32 projection 与 current-state/task/progress nuisance residualization。

A/B/C 共享 identity initialization、500 个 pre-hashed task-balanced batches 与 plain SGD。A 接收 action+valid-future gradient，B 只接收 action gradient，C 接收 action+fixed deranged-future gradient；aux dose 相对 common B action gradient 固定为 0.30。Checkpoint 必须先由 1k/5k/10k 的 sealed 30-rollout screen 自动选择，任何 cache/head/adapter/PQ 都只能依赖选中 checkpoint。

Mechanism 层从 D_post folds0–1 的 A−B delta 学习 nuisance-annihilated predictive basis P；fold2 选 ridge/rank，fold3 选 matched Q，fold4 在全部 artifact freeze 后只打开一次。Rollout intervention 只使用 h、m_A、m_B 与 frozen linear W/P/Q，不允许 online DINO、progress、action teacher 或 target。

## Experiment Design

- **Dataset：** 个人 LIBERO-10 数据中的 dataset task-index 1 与 8；对应 benchmark task ID 6 与 3。Cardinality-aware fixed split 为 D_head 45%、D_adapter 30%、D_post 25%，全部 episode ID 已冻结。
- **Host checkpoint：** 仅候选 steps 1000、5000、10000；screen states0..4；两 task SR 分别落在 [.2,.8]，pooled 最接近 .5，tie earlier step。
- **Baselines/controls：** action-only B、fixed deranged C、state-only、action-only head、current-DINO+action、additive、nuisance ridge、task-progress mean、zero。
- **Primary metrics：** task-equal joint64/main32 nMSE、episode-bootstrap LCB/UCB、seed-level paired SR difference、exact sign test、pooled pp gain、per-task reversal、P/Q R² 与 equivalence。
- **Training seeds：** [0,1,2,3,4,5,6,7,8,9]；budget fallback 只能取固定前缀 [0,1,2,3,4]。
- **Evaluation states：** screen 0..4；10-seed final 5..9；5-seed final 5..14。
- **Compute：** 4×A100-PCIE-40GB host；默认仅物理 GPU 2/3；0/1 只有同一 fresh snapshot 四卡全空时才可按 2,3,0,1 使用。Pilot≤2.0 GPUh，完整投影≤7.2，actual≤8.0。
- **Storage：** 所有 project/data/model/env/cache/tmp/log/metric/video/W&B/result 都在 <PERSONAL_RESEARCH_ROOT>，且真实路径在 <PERSONAL_RESEARCH_ROOT_ALIAS>。禁止团队/共享目录。

## Baselines

| Method | Dataset | Metric | Score | Source |
|---|---|---|---:|---|
| Frozen final StarVLA checkpoint | LIBERO-10 task ID3 | SR | 0.94 | 既有个人 baseline full-eval log，仅用于 task feasibility，不参与 checkpoint screen |
| Frozen final StarVLA checkpoint | LIBERO-10 task ID6 | SR | 0.90 | 同上 |
| Screen-selected early checkpoint | fixed two tasks/states | SR | pending | 必须由 sealed 1k/5k/10k screen 自动产生 |
| B action-only adapter | fixed two tasks/states | paired SR | pending | Stage1 |
| C fixed deranged-target adapter | fixed two tasks/states | paired SR | pending | Stage1 |

## Current Results

当前没有 H1 GPU 结果；GPU hours=0.0，jobs=0。首次 experiment-plan jury 为 NO-GO，五项执行阻断已修复并等待 renewed jury。不得把方法 READY、既有 final-checkpoint SR 或任何 CF-DynAlign 结果当作 H1 实验结果。

| System | Split / task | Metric | Result | Status |
|---|---|---|---|---|
| PGR-Audit | H1 | GPUh | 0.0 | no launch |
| Repaired experiment protocol | method-plan | renewed jury | pending | no execution authority |

## Key Decisions

- 贡献定位为 diagnostic sequential identification contract，而不是新 world objective。
- Checkpoint screen 必须是第一类 GPU launch，避免 host-dependent artifact 的 circular ordering。
- 原 50/30/20 在实际 episode 数下会使 fold4 每 task 仅一个 episode；修为 45/30/25，使 locked fold4 每 task 三个 episode。该改变必须重新审查。
- 动作归一化复现 clean StarVLA：前六维 min-max，第七维 gripper identity；不得凭印象改成 mean/std。
- Seed0 triplet/PQ 为正式保留 artifact，预算未来项只计 n−1，避免 double charge。
- Seed count 只由 sealed timing ledger 自动选择，seed0 scientific metrics 在选择 hash 前不可见。
- Stage2 始终是 conditional；P/Q 任一 seed 不合格只禁止 Stage2，不允许删 seed。
- CF-DynAlign predictor、cache、metric、result 与 lambda_cf 禁止复用；base checkpoints/raw personal data 可以用。
- Negative、NO-RUN、underpowered 与 budget stop 都是合法结果，不得删 control 或调阈值挽救。

## Status

- [x] Idea selected
- [x] Method refined and reviewed
- [x] Repaired machine-readable protocol and input manifest
- [ ] Renewed experiment-plan jury pass
- [ ] Isolated implementation and fresh-agent code review
- [ ] Screen-selected baseline checkpoint
- [ ] C0 predictive gate
- [ ] Main A/B/C Stage1 result
- [ ] Conditional P/Q Stage2 result
- [ ] Integrity audit and result-to-claim
- [ ] Paper draft（明确 out of scope）

