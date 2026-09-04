# VLA × WAM 交叉母领域扩展探索契约

**Run ID：** `20260806-vla-wam-expanded-field-map`  
**日期：** 2026-08-06  
**探索级别：** `field`  
**阶段目标：** 将上一轮 6 条 VLA × WAM 上位路线扩展为 16 条中粒度母方向；只交付证据地图与方向版图，不进入具体 Idea。

## 1. 操作性定义

### 1.1 VLA 侧

必须存在由视觉/多模态观测与语言目标共同条件化、并产生机器人动作、技能或可执行计划的 embodied policy 接口。普通视觉语言理解、无语言的纯控制策略和仅预测动作 token 的序列模型可作邻域证据，但不能单独构成交叉核心。

### 1.2 WAM / learned world-model 侧

必须显式学习可干预的时间演化：未来视频/视觉 latent、task latent、显式状态、对象/3D/接触、reward/termination、belief 或 action-effect 中至少一类，并且动作、潜在动作或策略选择会改变预测。静态 encoder、不可学习 simulator 和只重构当前帧的模型不计作核心 WAM。

### 1.3 强交叉

VLA 必须真实消费世界模型信号，或二者共享一个可检验的联合学习/适应机制。允许的耦合位置包括：

- 预训练或辅助世界预测；
- 未来/子目标提案与层级执行；
- 候选动作反事实预测、rerank、MPC 或 steering；
- reward/value/critic、策略评测、失败预测、安全过滤与恢复；
- 世界生成数据、想象式 RL 或 VLA post-training；
- world-language-action 联合建模；
- 跨具身 action-effect 接口；
- 主动采数、policy–world 共演化、system identification 或 test-time adaptation。

仅在同一论文中并列出现 VLA 与 world model、仅用 VLA 产生 WAM 条件、或仅把 VLA 当作任意被测策略，均降为邻域证据。

## 2. 双轴分类与耦合标注

每篇核心工作同时标注：

1. **世界表征：** R1 decoded video、R2 pixel/video latent、R3 task-centric latent、R4 explicit state/dynamics；
2. **控制用途：** U1 representation、U2 goal/trajectory proposal、U3 candidate evaluation、U4 MPC/planning、U5 imagined policy optimization、U6 joint world-action model；
3. **VLA 消费点：** pretraining、inference、evaluation、safety、post-training、deployment adaptation；
4. **耦合拓扑：** auxiliary、cascade、tool-use、joint、alternating、co-evolution；
5. **更新制度：** frozen、alternating、joint、continual、test-time；
6. **证据层：** model、policy、environment，以及是否存在 matched no-world/no-coupling 对照。

## 3. 16 条方向的覆盖配额

下列是检索覆盖格，不是预定方法结论；最终名称由证据聚类决定：

| 组 | 配额 | 必须区分的问题 |
|---|---:|---|
| 世界表征与 grounding | 4 | 预测式表征；潜在动作/action-effect；3D/对象/接触/触觉；记忆与 belief dynamics |
| 推理、决策与 assurance | 6 | 子目标/视频计划；反事实 rollout/MPC/rerank；主动感知；reward/value/critic；策略评测；安全/失败/恢复 |
| 训练、数据与闭环学习 | 3 | 世界生成数据；想象式 RL/post-training；主动采数、课程与 policy–world 共演化 |
| 联合架构、迁移与适应 | 3 | joint world-language-action；跨具身 action-effect；system identification/test-time adaptation |

如果两个候选格共享同一核心科学问题、同一主要 endpoint 且无法通过决定性证据区分，应合并并公开说明；如果证据支持新的独立问题，可替换格，但总数仍为 16。

## 4. 文献搜索与证据等级

- 时间：2018-01-01 至 2026-08-06，重点 2023 年以后；必要时纳入更早的 world-model/MBRL 基础工作。
- 来源：优先论文原文、正式 proceedings、作者项目页与官方代码；综述只用于扩展别名和引用链。
- 查询至少覆盖 `world model + VLA`、`video prediction + robot policy`、`latent action + video + robot`、`visual planning/subgoal`、`counterfactual rollout/MPC/rerank`、`policy evaluator/critic/safety`、`imagined RL/post-training`、`synthetic data`、`joint world action model`、`cross embodiment dynamics`、`active data/co-evolution`、`system identification/test-time adaptation`。
- **E1：** 正式发表且方法/对照可核验；**E2：** 可核验预印本/项目；**E3：** 摘要、仓库声明或邻域证据。
- 每条方向目标是至少 2 篇独立 primary-source 锚点；达不到时不得补造，必须标为 `frontier/sparse`。

## 5. 方向粒度与输出字段

母方向必须由“核心科学问题 + 世界模型在 VLA 系统中的作用端点 + 决定性证据”定义。单一架构、benchmark、机器人形态、数据集、长时/OOD 压测或工程优化不能独占一条方向。

每条方向必须包含：

1. 一句话人话解释；
2. 核心科学问题；
3. VLA 侧、WAM 侧与耦合位置；
4. R/U 分类与方法族；
5. 代表论文簇和证据强度；
6. 为什么现在值得研究、拥挤度与真实缺口；
7. 与相邻方向的边界；
8. 方向层的决定性证据与廉价证伪；
9. 数据、算力、推理延迟、环境交互和真机负担；
10. 研究可行性、风险和未选择的优先级。

“决定性证据”只描述未来选择该方向时需要证明什么，不得展开成具体 hypothesis、benchmark、实现或实验计划。

## 6. 覆盖与诚实性审计

方向版图通过前必须检查：

- 16 条方向之间不存在同义重命名；
- 上一轮 6 条上位路线均有明确去向，且新增盲区可追溯到查询或论文；
- 强交叉、邻域支撑和纯边界论文明确分层；
- 视频生成、latent dynamics、显式状态及 R1–R4 不与 U1–U6 混为互斥分类；
- 模型画质/loss 不替代闭环 VLA 收益；VLA benchmark 分数不替代世界机制证据；
- 额外数据、参数、算力、交互和 oracle 信息不被误归因于耦合；
- 2025–2026 预印本、未开放模型/数据与仅视频 demo 明确降权；
- 检索盲区和负面/冲突证据被保留。

## 7. 暂停条件

`evidence-map` 仅在扩展文献地图、16 条方向版图和边界覆盖审计全部存在且可追溯时通过。随后必须保持：

```text
research.selected_macro_direction = null
idea-discovery = blocked: awaiting human macro-direction selection
```

严禁在本轮生成具体 Idea、hypothesis、benchmark 选择、实现框架、实验计划或启动任何作业。
