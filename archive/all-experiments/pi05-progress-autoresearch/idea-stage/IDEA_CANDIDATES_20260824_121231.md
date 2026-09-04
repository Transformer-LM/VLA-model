# Idea 候选池：长时 VLA 进度、验证与纠错

日期：2026-08-24

## 第一轮候选

| 候选 | 核心机制 | 初步结论 |
|---|---|---|
| Proof-Carrying Retraction Graph | 任务断言携带证据谱系，矛盾时局部撤销 | 与 TMS/ATMS、HELM、Goal2Skill、ReViP 高重叠；仅 VLA 内部错误传播评测仍可守 |
| Quarantined Conformal Commit | provisional/commit 两阶段写入与风险控制 | 有用但容易成为 conformal prediction 的应用 |
| History-Twin Quotient State | 双侧历史/外观配对学习任务状态 | IntentVLA/AliasBench 已覆盖关键一侧；适合作为诊断协议 |
| Belief-Value Active Reveal | 按决策遗憾主动补充观察 | active perception / belief-space planning 很成熟 |
| Reversible Partial-Order Progress | 非单调谓词配置和补偿边 | 与 PDDL/STRIPS/reversible planning 高重叠 |
| WAM Action-Effect Forensics | 对已执行 chunk 做多假设效果归因 | 必须击败几何、VLM 和判别 verifier |
| Effect-Residual Repair Interface | 类型化 effect residual 条件化独立 recovery | CheckVLA、Dream2Fix、FARL 组合攻击强 |
| Recovery Viability Envelope | 保护 K 步内可恢复性 | 与 viability kernel / safety shield 高重叠 |
| Bidirectional Action Contracts | chunk 的 pre/post/transient/compensation 契约 | 与 options、behavior tree、runtime monitor 高重叠 |
| Orthogonal Verify–Repair–Recover | 解耦检测、状态修正和恢复的析因协议 | 诊断价值高，但单独算法贡献弱 |
| Counterfactual Poison Vaccination | 对内部任务状态做因果污染增强 | 易被视为普通 adversarial augmentation |

## 查新反向驱动的第二轮候选

| 候选 | 不可交换的窄 claim | 一天级 kill-test |
|---|---|---|
| Policy-Conditional Commit Regret | 以 commit/suppress 同快照分叉造成的冻结策略多步控制损失训练写入 gate | oracle truth gate 对 oracle regret gate |
| Last-Correctable-Time Hazard | 预测仍来得及纠错的最后时刻，而非最终失败概率 | oracle t* 触发对完美但事后触发 |
| Minimal Policy Assumption Certificate | 只验证当前 chunk 真正依赖的最小进度假设 | oracle 状态格中枚举最小充分假设 |
| Intent-Orthogonal Outcome Supervision | 消除 verifier 复述 action intent 的确认偏差 | intent swap、观察不变的反事实测试 |
| Correlation-Adjusted Witness Objective | 按证据条件独立性而非数量提交状态 | top-confidence witness 对 least-correlated witness |

## 当前选择

选择 `Policy-Conditional Commit Regret` 进入方法细化，但状态为 **conditional go**，不是已证明可行。

原因：它不再声称新的 memory、world model 或 recovery stack，而是检验一个此前在机器人进度写入中尚未被完整回答的问题：状态真值准确率是否与其对固定 VLA 的闭环伤害错位。

硬退出条件：oracle regret gate 相对匹配提交率的 oracle truth gate 没有稳定闭环优势；或优势可被一步 action disagreement / 短视野 value critic 等价替代。
