# VLA / WAM / VLA × WAM 三域母方向总版图

**Run ID：** `20260806-vla-wam-tri-domain-field-map`  
**状态：** 方向版图完成，等待人工选择；未进入具体 Idea  
**版图规模：** 7 条 VLA + 7 条 WAM + 6 条强交叉 = **20 条母方向**

## 0. 怎样读这张图

- **VLA-only** 研究 policy 如何从视觉、语言和历史产生动作；可以完全没有 world model。
- **WAM-only** 研究动作怎样改变世界、怎样预测/记忆/利用这种变化；可以完全没有大型 VLA。
- **VLA × WAM** 研究二者在训练、推理、评价、数据或适配中怎样真正连接；“同时出现”不等于“形成强交叉”。

评分统一采用：科学影响 25%、创新空间 20%、证据缺口 20%、当前 `2 GPUh pilot / 8 GPUh total / 无真机` 配置可行性 20%、取得可信初证速度 15%。分数只帮助看版图，不是成功率、venue 概率或自动选择。

## 1. 20 条方向总览

| 域 | ID | 母方向 | 核心问题 | 证据密度 | 当前资源负担 | 分数 |
|---|---|---|---|---|---|---:|
| VLA | V1 | 数据规模、混合与通用策略预训练 | 哪些 robot/web/human 数据及配比真正产生可迁移 policy | 很高 | 极高 | 64.0 |
| VLA | V2 | VLM 知识到物理动作的 grounding | 语义与常识怎样稳定转成闭环物理成功 | 高 | 中 | 79.0 |
| VLA | V3 | 高频、连续、多峰动作生成接口 | token、chunk、diffusion、flow 怎样兼顾速度和控制 | 很高 | 低—中 | 86.0 |
| VLA | V4 | 跨具身动作语义与迁移 | 不同身体、坐标与频率怎样共享动作意图 | 高 | 中—高 | 80.0 |
| VLA | V5 | 少样本适配、小模型与实时部署 | 怎样以少数据和普通硬件可靠装到新平台 | 高 | 低—中 | 90.0 |
| VLA | V6 | 长程分层推理、记忆、主动感知与纠正 | 怎样拆任务、补信息并从中途错误恢复 | 中等 | 中 | 83.0 |
| VLA | V7 | RL / 交互式 post-training 与持续改进 | 怎样从自身成功失败学习而不 hacking/遗忘 | 中等、新兴 | 中—高 | 79.0 |
| WAM | W1 | Action-conditioned observable video WAM | 怎样生成真正听动作、守物理的可见未来 | 高 | 极高 | 74.0 |
| WAM | W2 | Task-centric latent 与 belief dynamics | 什么隐藏状态足够预测、控制、记忆和迁移 | 高 | 低—中 | 88.5 |
| WAM | W3 | Object/3D/contact 结构化动力学 | 怎样显式建模实体、几何、接触和触觉变化 | 中等 | 中—高 | 85.0 |
| WAM | W4 | Memory、system ID 与快速适应 | 怎样识别新负载/摩擦/延迟并快速修正模型 | 中低 | 低—中（仿真） | 88.5 |
| WAM | W5 | Counterfactual planning 与 MPC | 怎样用 learned future 做候选比较和闭环规划 | 高 | 中 | 87.0 |
| WAM | W6 | Imagined policy learning 与 data engine | 怎样把 learned world 变成可信训练场或数据源 | 高 | 高 | 80.5 |
| WAM | W7 | 功能评测、校准与安全 world model | 怎样判断 policy 成败以及模型何时不可相信 | 中等、快速增长 | 低—中 | 93.0 |
| 交叉 | H1 | 预测式 world objective 改善 VLA | 训练时预测未来是否因果改善 action quality | 中高 | 中 | 72.4 |
| 交叉 | H2 | Learned rollout 规划与 deployment steering | VLA 候选能否经 WM 想象后被更好选择 | 高 | 中—高 | 74.7 |
| 交叉 | H3 | VLA 裁判、critic 与安全闸门 | WM 能否可靠排名、预警、拒绝并覆盖 OOD | 中等 | 低—中 | **94.5** |
| 交叉 | H4 | Learned world 生成经验并后训练 VLA | imagined/synthetic 经验能否转成真实收益 | 中等、新兴 | 高 | 80.0 |
| 交叉 | H5 | 联合 World–Language–Action 基础模型 | 一个原生 joint model 是否胜过匹配预算的分离模块 | 很高、拥挤 | 极高 | 66.3 |
| 交叉 | H6 | 跨具身 action-effect 与 policy–world 共适应 | 怎样共享动作效果并避免 policy/WM 一起漂移 | 低—中 | 高 | 79.1 |

## 2. VLA 自身的七块版图

### V1 — 数据规模、混合与通用策略预训练

重点不是简单“更多数据”，而是 robot/web/human/synthetic 数据的质量、覆盖、配比与负迁移。RT-1、Open X/RT-X、DROID、Octo、OpenVLA、π₀ 等形成高密度证据，但数据、模型和训练预算常一起变化；完整 scaling 因果研究很昂贵。

### V2 — VLM 知识到物理动作的 grounding

这条线研究 VLM 的概念、语言组合和常识怎样跨过空间、接触与控制鸿沟。PaLM-E、RT-2、RoboFlamingo、OpenVLA、CogACT 等说明语义迁移存在，但“答对/选对物体”与“稳定完成动作”仍是两个 endpoint。

### V3 — 高频、连续、多峰动作生成接口

ACT/FAST 的时间压缩、Diffusion Policy/RDT 的多峰轨迹、π₀ 的 flow matching、OpenVLA-OFT 的连续并行解码都在回答同一个接口问题。它们预测动作而不是未来环境，因此仍是纯 VLA；关键权衡是量化、延迟、控制 Hz、chunk 反应性和表达力。

### V4 — 跨具身动作语义与迁移

同一物理意图在不同机器人上对应不同关节、坐标、频率和相机。Open X、Octo、SpatialVLA、GR00T、X-VLA 已显示异构正迁移，但真正有判别力的是完整留出新 embodiment，而不是训练集合内的多机器人平均分。

### V5 — 少样本适配、小模型与实时部署

研究 success-per-demo、训练/显存/能耗与闭环 latency，而不只是参数量。OpenVLA/OFT、TinyVLA、SmolVLA、Octo 与 Dita 提供开放路线；它是当前配置最容易研究的 VLA 大方向，但零真机只允许得出仿真和计算效率结论。

### V6 — 长程分层推理、记忆、主动感知与纠正

SayCan、RT-H、π₀.₅、Fast-ThinkAct、ActiveVLA 等分别用 skill、language motion、subtask、latent reasoning 或主动视角保持长程闭环。核心难点是固定低层 policy 和总观察/推理预算，避免把额外模块或更多视角本身误判为推理机制收益。

### V7 — RL / 交互式 post-training 与持续改进

这条线让 VLA 离开纯行为克隆，从自身访问到的失败状态、reward 和反馈继续学习。iRe-VLA、RIPT-VLA、VLA-RL、Z-1 与 continual VLA-RL 显示新簇正在形成；reset、reward hacking、on-policy 成本、安全和旧能力遗忘仍未解决。

更详细的边界、锚点和资源账本见 [VLA 独立版图](./VLA_DIRECTION_LANDSCAPE.md)。

## 3. WAM 自身的七块版图

### W1 — Action-conditioned observable video WAM

目标是生成真正服从动作、保持物体与接触一致的可见未来，而不仅是画面逼真。优势是可解释，代价是外观 nuisance、显存、存储、rollout latency 和长时漂移都很重。

### W2 — Task-centric latent 与 belief dynamics

不重建所有像素，而维护决策真正需要的隐状态。PlaNet/Dreamer 与 TD-MPC/DINO-WM 两类证据也暴露了核心争议：重建式 belief 与 task-only latent 没有统一赢家，必须在同数据和同 planner 下比较。

### W3 — Object/3D/contact 结构化动力学

用 object、particle、keypoint、3D、contact 或 tactile state 显式表达物理。它有组合性和可解释性，但 state extraction、privileged information 和多传感器硬件可能成为真正瓶颈。

### W4 — Memory、system ID 与快速适应

从短历史判断摩擦、负载、相机、延迟或 dynamics 是否改变，并快速恢复预测/控制。关键不是多塞帧，而是区分 hidden state、dynamics shift 和 behavior-policy shift，并计算安全 probing 成本。

### W5 — Counterfactual planning 与 MPC

PETS、PlaNet、TD-MPC、DINO-WM 等让 learned model 比较未来动作后果并重规划。该方向已经成熟；新的科学价值必须来自 WAM—planning 机制和同预算闭环收益，而不是换一个 optimizer。

### W6 — Imagined policy learning 与 data engine

Dreamer/DayDreamer、offline MBRL 与 DreamGen 类路线把 world model 变成训练场或数据源。最大问题是 policy exploitation、伪动作污染和总成本，而不是生成样本数量不够大。

### W7 — 功能评测、校准与安全 world model

它反过来审计 world model：是否能预测 policy 成败、尾部风险和自身不确定性。相对排名与 OOD 绝对安全之间存在明显断层，因此需要 model→policy→environment 三层 paired evidence。

更详细的边界、锚点和资源账本见 [WAM 独立版图](./WAM_DIRECTION_LANDSCAPE.md)。

## 4. 六座 VLA–WAM 桥

| 交叉方向 | 主要连接的 VLA 方向 | 主要连接的 WAM 方向 | 关键区别 |
|---|---|---|---|
| H1 预测辅助 | V1/V2/V3 | W1/W2 | world 只在训练时提供未来监督，可在推理时丢弃 |
| H2 rollout planning | V3/V6 | W1/W2/W3/W5 | world 在推理时真正消费 VLA 候选并改变动作选择 |
| H3 critic/safety | V5/V6/V7 | W7，兼用 W1/W2 | endpoint 是排序、校准、拒绝或风险，不是生成更漂亮的未来 |
| H4 imagined post-training | V1/V7 | W6/W7 | world 改变 VLA 的训练经验，最终必须回 ground truth 验收 |
| H5 joint WLA | V1/V2/V3 | W1/W2/W6 | world、language、action 原生共享；必须排除规模/容量收益 |
| H6 effect/co-adaptation | V4/V5/V7 | W4/W6/W7 | 处理新身体和时间变化，要求避免 policy 与 WM 共同漂移 |

### H1 — 预测式 world objective 改善 VLA

训练时让 VLA 同时预测 future image/feature/motion；最关键的问题是 matched action-only 对照和切断 world path 后动作收益是否仍在。

### H2 — Learned rollout 规划与 deployment steering

VLA 提议动作，WM 想象结果，再由 goal/value 选择并重规划。需要匹配 direct VLA 的 wall-clock、候选数和 FLOPs，否则远见可能只是额外计算。

### H3 — VLA 裁判、critic 与安全闸门

用 policy-conditioned future 做 checkpoint 排名、动作 veto、风险和 selective autonomy。当前证据断层最大、算力门槛又相对低，但相对排序绝不能被写成绝对安全保证。

### H4 — Learned world 生成经验并后训练 VLA

可生成伪示范、失败修正或 imagined RL 经验。必须把 imagined 高回报轨迹回放到真实/ground-truth 环境，检查 simulator/reward exploitation 与 effective sample yield。

### H5 — 联合 World–Language–Action 基础模型

同一模型共享 world、language 与 action。该路线最显眼也最拥挤；若没有 matched 参数、数据、token、训练步和切断实验，“joint”本身已不是充分贡献。

### H6 — 跨具身 action-effect 与 policy–world 共适应

用共享 effect/dynamics 翻译不同 native actions，并让 policy 与 WM 在线交替更新。固定 WM 会分布失配，共适应又可能共同学错，因此外部 ground-truth anchor 是核心。

更详细的强/弱交叉门槛见 [交叉独立版图](./INTERSECTION_DIRECTION_LANDSCAPE.md)。

## 5. 容易误分类的五个边界

1. **预测 action token ≠ WAM。** RT-2/OpenVLA/FAST/ACT/diffusion/flow 若不预测环境转移，仍是 VLA/action policy。
2. **无语言 ≠ 不是 WAM。** PETS、Dreamer、TD-MPC、DINO-WM 学到 action-conditioned dynamics，就是 WAM 本体证据。
3. **视频 + 动作 ≠ 强交叉。** 没有语言端或 VLA 没有消费 world path 时，只能算 WAM 或弱邻域。
4. **普通 simulator 中 RL ≠ VLA×WAM。** learned world 真正提供训练环境时才进入 H4；否则属于 V7。
5. **共享 backbone ≠ coupling 有效。** H5 必须证明 world objective/path 对动作 endpoint 有独立贡献。

## 6. 选择导航，但不替用户选择

按研究形状看，而不是按分数自动挑：

- 偏**低算力、因果审计和评价**：V3、V5、W2、W4、W7、H3。
- 偏**长程自主与部署时决策**：V6、W4、W5、H2、H3。
- 偏**数据与自我改进循环**：V1、V7、W6、H1、H4、H6。
- 偏**foundation-scale 统一模型**：V1、W1、H5；科学影响大，但明显不匹配当前 8 GPUh 从头训练预算。
- 偏**物理、结构与跨身体**：V4、W3、W4、H6。

这只是导航。当前配置仍为：

```text
research.selected_macro_direction = null
idea-discovery = blocked: awaiting human macro-direction selection
```

没有生成具体 hypothesis、算法、benchmark 组合、实验矩阵或论文 Idea。
