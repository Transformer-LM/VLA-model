# VLA / WAM / VLA × WAM 三域探索契约

**Run ID：** `20260806-vla-wam-tri-domain-field-map`  
**日期：** 2026-08-06  
**探索级别：** `field`  
**阶段目标：** 分别建立 VLA、WAM、VLA × WAM 三张证据地图，生成 7 + 7 + 6 条母方向并统一比较；不进入具体 Idea。

## 1. 三个检索域的操作性定义

### 1.1 VLA 域

研究对象是以视觉/多模态观测、语言目标或指令以及机器人动作为核心接口的策略、基础模型或决策系统。纳入工作可以完全不包含 learned world model。

纳入范围包括但不限于：

- VLA 架构、视觉语言骨干与动作 head；
- 连续、离散、token、chunk、diffusion/flow、技能或层级动作表示；
- 机器人、人类视频、多机器人、多任务和合成数据的预训练/后训练；
- 3D、触觉、本体感觉、历史记忆、长时推理与分层控制；
- 跨任务、跨场景、跨 embodiment、few-shot、online adaptation；
- VLA 的评测、鲁棒性、安全、校准、延迟和部署效率。

一个 VLA 只因能预测下一个 action token，不自动成为 WAM。若没有显式动态/未来状态目标或 learned rollout 用途，保留为纯 VLA 证据。

### 1.2 WAM / learned world-model 域

研究对象是学习观测、动作与时间演化之间可干预关系的模型，包括 decoded video、visual latent、task latent、显式状态、对象/3D/接触、reward/termination 或 belief dynamics。它可以服务任何机器人 policy，不要求大型 vision-language-action 基座。

纳入范围包括：

- action-conditioned video/pixel-latent simulator；
- task-centric latent、RSSM、state-space、object/3D/particle/contact dynamics；
- memory、partial observability、system identification 与 uncertainty；
- visual subgoal、candidate evaluation、MPC/planning、imagined RL、数据生成；
- world-model 功能评测、校准、物理一致性与安全边界。

静态视觉表示、普通 simulator、只做 next-token prediction 且没有动态语义的模型不自动纳入 learned WAM。

### 1.3 VLA × WAM 交叉域

研究对象必须同时有可识别的 VLA 接口和 learned world/dynamics 作用，并且能够回答“二者怎样耦合、相互帮助或相互伤害”。交叉不以论文标题是否出现 `world model` 判定，而以机制判定。

至少满足一项：

1. world prediction 用于 VLA 的表征预训练或辅助目标；
2. learned rollout 为 VLA 生成子目标、规划、rerank、critic、value、安全判断或策略评测；
3. world model 为 VLA 生成训练数据或提供 imagined post-training 环境；
4. video/state/world 与 language/action 在一个联合模型中共同预测；
5. world dynamics 连接不同 embodiment 的动作/effect 语义；
6. policy 与 world model 在部署或数据循环中交替/共同适应。

仅把 VLA 当作任意 black-box policy 在 WAM benchmark 中测试，或仅把 WAM 当背景叙述而无机制连接，降为邻域证据，不计作强交叉。

## 2. 三张地图必须保持对称

每个域独立完成以下问题，不能用另一域的答案代替：

| 轴 | VLA 要回答 | WAM 要回答 | 交叉域要回答 |
|---|---|---|---|
| 基本对象 | policy/action generator 如何构成 | 世界状态和转移如何构成 | policy 与 world 如何连接 |
| 数据 | 动作监督和异构数据如何获得 | 动态/动作条件数据如何获得 | 哪类数据同时训练或桥接二者 |
| 表征 | 语言、视觉、动作和历史怎样编码 | R1–R4 预测什么 | 共享、独立或可翻译什么 |
| 学习 | imitation、pre/post-training、RL、adaptation | predictive/self-supervised/MBRL | auxiliary、cascade、joint、alternating、co-evolution |
| 推理 | direct action、chunk、skill、reasoning | rollout、proposal、evaluation、MPC | VLA 是否真正消费 world prediction |
| 泛化 | task/object/scene/embodiment/instruction | dynamics/observation/policy distribution shift | world knowledge 是否转移为 VLA 收益 |
| 证据 | action 与环境成功 | model、planning 和环境一致性 | matched coupling 对照及三层证据 |
| 资源 | 数据、训练、延迟、部署 | rollout、模型训练、交互 | 额外 world path 的总成本与因果收益 |

## 3. 方向数量和粒度

总版图固定生成 20 条中粒度母方向：

- VLA：7 条；
- WAM：7 条；
- VLA × WAM：6 条。

方向必须由“核心科学问题 + 主要 endpoint + 决定性证据”定义。架构组件、单一 benchmark、单一机器人形态、长时/OOD 等压力测试不能独占一条方向。不同域可以共享技术，但必须指出研究问题为何不同。

每条方向包含：

1. 人话解释与核心问题；
2. 为什么现在值得研究；
3. 方法族与代表工作簇；
4. 最近工作密度、拥挤程度和冲突证据；
5. 未解缺口与相邻方向边界；
6. 决定性证据、候选任务性质和 baseline 家族；
7. 数据/算力/交互/真机负担、主要风险、廉价证伪；
8. 统一评分与保持未选择的推荐。

## 4. 搜索范围与证据等级

- 时间：2018-01-01 至检索日，重点覆盖 2023 年以后；必要时纳入更早的 foundational control/world-model work。
- 来源：优先论文原文、正式 proceedings、作者项目页和官方代码；二手综述只扩展检索词。
- VLA 种子：RT-1/RT-2、PaLM-E、SayCan、Open X-Embodiment/RT-X、Octo、OpenVLA、π 系列、RDT、ACT、Diffusion Policy，以及证据搜索得到的其他路线。
- WAM 种子：Visual Foresight、Dreamer/TD-MPC、video WAM、latent/structured dynamics、world-model evaluation 和 MBRL。
- 交叉种子：GR-1/GR-2、UWM/UVA、WorldVLA、DreamZero、Cosmos Policy、V-JEPA 2、WorldGym/WorldEval、DreamGen/RehearseVLA，以及查到的其他机制。

证据分级：

- **E1：** 正式发表原文，方法、对照和限制可核验；
- **E2：** 预印本或项目页，细节可核验但缺独立复现；
- **E3：** 摘要/仓库声明或邻域证据，只支持“存在路线”，不承担强结论。

## 5. 排除与降权规则

- 不因规模更大或 benchmark 分数更高就推断机制更优；
- VLA 比较检查数据、参数、训练 token、动作 horizon、control frequency 与 real-robot trials；
- WAM 比较把预测表征与控制用途分开，模型指标不能替代闭环结果；
- 交叉比较必须有 matched VLA-only、WAM-only/无耦合或 oracle 对照，避免把额外数据/算力归因于耦合；
- 2025–2026 大量工作为预印本，明确降级并保留复现盲区；
- benchmark contamination、私有数据、不可复现大规模预训练与 cherry-picked videos 明确记录。

## 6. 明确不作的预设

人工选择前不预设：

- manipulation 优于 navigation、mobile manipulation、humanoid 或其他 embodiment；
- LIBERO、RoboCasa、CALVIN、SIMPLER 或任何具体 benchmark；
- OpenPI、OpenVLA-OFT、Cosmos Policy 或任何实现框架；
- autoregressive、diffusion、flow、continuous action、token/action chunk 中任一必然更优；
- video WAM、latent dynamics、structured state 中任一必然更优；
- world model 必须进入 VLA，或 VLA 必须成为 WAM 的 policy；
- 更好的 action prediction、视频质量或模型 loss 自动等于环境成功。

## 7. 完成与暂停条件

只有以下条件同时满足，`evidence-map` 才能通过：

- 三张独立文献地图均记录查询、关键论文、来源、工作簇、冲突和盲区；
- 三张方向版图分别包含 7、7、6 条路线；
- 总版图能显示纯 VLA、纯 WAM 与交叉路线的归属、桥接和边界；
- VLA 论文不是只作为 WAM baseline 出现，WAM 论文也不是只作为 VLA 辅助模块出现；
- 推荐保持未选择，不提前生成 Idea、hypothesis、benchmark 或实现计划。

完成后必须执行：

```text
research.selected_macro_direction = null
idea-discovery = blocked: awaiting human macro-direction selection
```
