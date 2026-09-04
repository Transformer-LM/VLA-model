# 领域探索契约补充：扩展方向版图

**日期：** 2026-08-06  
**触发：** 用户认为初版 6 个方向过少，并要求扩展及增加解释。  
**阶段：** 仍属于 `evidence-map` 的人工反馈修订；不进入 `idea-discovery`。

## 变更内容

初版把多个不同科学问题压在同一标签下：

- evaluator、单步 critic、整套 policy 排序与 safety 共用旧 D1；
- task latent、对象/3D/接触结构共用旧 D2；
- predictive pretraining、动作对齐、合成数据与主动 curriculum 共用旧 D3；
- visual subgoal、action-conditioned rollout 与 MPC 共用旧 D4；
- 静态 joint model 与长期 policy–world co-adaptation 共用旧 D6。

扩展版不再以 6 个粗标签作为直接选择项，而采用 **4 个上层问题区域 + 20 个中粒度母方向**。每条方向必须有不同的研究对象、主要 endpoint 和决定性证据；换 encoder、换 benchmark、加 uncertainty 模块或加速 rollout 不自动构成新方向。

用户关于“方向数量更多、解释更清楚”的指令优先于技能默认的 5–8 条建议，因此本轮显式把 `research.macro_direction_count` 从 6 改为 20。其余约束不变：

```text
research.exploration_level = field
research.selected_macro_direction = null
automation.require_direction_checkpoint = true
automation.auto_select_idea = false
```

## 新增探索轴

- 部分可观测性、长期记忆与对象持久性；
- 主动感知与主动数据获取（分别服务当前决策和未来学习）；
- 因果干预、可供性和跨具身 action/effect 语义；
- 视觉—触觉—本体感觉的接触动力学；
- 部署时 system identification、快速适应与长期持续学习；
- “评价 world model”与“用 world model 评价 policy”的反向区分。

## 仍然禁止的提前决定

扩展方向不等于提出具体 Idea。人工选择前仍不得固定算法、具体 benchmark、机器人形态、VLA/WAM checkpoint、主假设或实验矩阵。扩展完成后状态继续保持：

```text
idea-discovery = blocked: awaiting human macro-direction selection
```
