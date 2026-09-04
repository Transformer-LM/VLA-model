# Novelty Report

日期：2026-08-24

## 结论

`Policy-Conditional Commit Regret` 未发现完整重复，但属于强先例可组合出的窄增量。

- 广义 claim：3/10，不成立。
- 严格机制 conjunction：约 6/10，`PROCEED WITH CAUTION`。
- 推荐动作：只先做 oracle kill-test；通过后才训练 gate。

## 可守的精确 claim

在固定执行策略、恢复机制和未来预算下，从同一序列化 simulator state 仅分叉 `commit/suppress` 一个候选进度断言，以两条未来的配对控制损失差定义 `policy-conditional commit regret`，再把该干预成本蒸馏为运行时轻量 admission gate。

它不声称发明 causal memory selection、decision-focused learning、selective gate 或 completion-aware VLA。

## 最危险近邻

- Causal Memory Intervention：已有 with/without/perturbed memory 的任务效用差，但面向 LLM QA 和检索选择。
- Causal Self-Talk：已有 RL memory-state intervention 和未来回报目标。
- VAML、SPO、Value Equivalence：已确立按下游价值而非真值误差学习的原则。
- SelectiveNet：已有 accept/reject gate。
- SeqVLA：已有 completion head 和阶段切换。
- ConsistencyGate、MemTX：已覆盖写入 admission / belief commit / downstream harm 的相邻叙事。

因此创新只能落在机器人 VLA 进度断言的 **paired-snapshot、frozen-policy、multi-step control-regret supervision** 这一完整接口和对应发现上。

## 最大科学风险

若 gate 允许写入“事实为假但有助于当前 policy”的断言，它会退化为操纵策略的 control token，而不是可靠任务状态。正式方案采用硬约束：只在真值不确定或多个语义可接受的候选之间用 regret 排序；事实一致性仍是约束，不以 false-beneficial assertion 作为成功来源。

## 查杀条件

1. true-harmful 样本稳定占比过低，或配对置信区间覆盖零。
2. oracle regret gate 相对 oracle truth gate 的成功率优势不足 5 个百分点，且无效动作降幅不足 20%。
3. commit regret 在 rollout seeds 间符号一致率低于 70%。
4. 优势只存在于单任务或单 horizon。
5. 一步 action-disagreement、短程 value critic 或 calibrated truth gate 达到同等效果。
6. 优势主要来自 false-beneficial assertion。

## 对前三个旧候选的结论

- Evidence-Carrying Retraction：严格收窄约 6/10；TMS/ATMS、HELM、Goal2Skill、ReViP 是核心冲突。
- Effect-Residual Repair Interface：约 4/10；CheckVLA、Dream2Fix、FARL 组合攻击强。
- History-Twin State Method：约 4/10；IntentVLA/AliasBench、RB-VLA、RS-CL、HAMLET 高碰撞。双侧配对可保留为诊断，不作为主方法。

## 覆盖限制

2026 年论文更新极快；部分索引出现限流。当前结论是高强度 provisional novelty assessment，不等价于正式专利查新或穷尽性检索。
