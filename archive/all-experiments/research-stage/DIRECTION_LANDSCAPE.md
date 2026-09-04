# VLA × WAM 母领域方向版图

> **版本说明（2026-08-06）：** 这是首次制图留下的 6 方向粗粒度版本。用户指出颗粒度过粗后，流程保留本文件用于审计，并生成了当前阅读与选择入口：[DIRECTION_LANDSCAPE_EXPANDED.md](./DIRECTION_LANDSCAPE_EXPANDED.md)。扩展版包含 4 个上层问题区域、20 条中粒度母方向和更通俗的解释；尚未选择任何方向。

> 阶段：field discovery / macro-direction checkpoint  
> 状态：**仅完成方向制图，尚未选择方向，尚未进入具体 Idea**  
> 当前配置：`research.exploration_level = field`，`research.selected_macro_direction = null`，6 个候选母方向  
> 证据底图：[LITERATURE_MAP.md](./LITERATURE_MAP.md)；检索原始汇总：[allinone.md](../allinone.md)

## 0. 如何阅读这张版图

这里的“方向”是可以容纳多种方法、任务和实现的母问题，不是论文 Idea、方法命名或预先写好的结论。每个方向都回答同一组问题：核心科学问题、时机、方法族、邻近工作密度、尚未解决的缺口、什么证据才算决定性、可能使用的任务与基线族、资源需求、主要风险、低成本证伪方式，以及在当前配置下的推荐度。

版图沿两个正交轴组织，不能把二者混为一谈：

- **表征轴 R**：R1 像素/视频；R2 压缩视觉 token；R3 task-centric latent；R4 显式结构状态（对象、3D、点、粒子、接触或场景图等）。
- **控制用途轴 U**：U1 表征/数据预训练；U2 未来或子目标生成；U3 评估、reward、critic 与安全预演；U4 规划/MPC；U5 imagined policy optimization；U6 world–action 联合建模或共同适应。

因此，一条母方向可以横跨多个 R，但必须在 U 上有清楚的控制用途和可检验的决策价值。

## 1. 版图总览

| ID | 母方向 | 主要 R/U 位置 | 邻近工作密度 | 当前配置适配度 | 综合分 /100 | 排名 |
|---|---|---|---|---:|---:|---:|
| D1 | 可校准的世界模型策略评估、critic 与安全预演 | R1–R4；U3 | 中等，2025–2026 快速增长 | 高 | **94.5** | 1 |
| D2 | task-centric latent / 结构化动力学用于可控预测与高效规划 | R3/R4；U3/U4 | 通用 WM 高，VLA 专属较稀疏 | 高 | **86.5** | 2 |
| D5 | learned world 中的 VLA 后训练与 imagined model-based RL | R1–R4；U5 | 通用 MBRL 高，VLA-WM 较稀疏且新 | 中低 | **80.5** | 3 |
| D3 | 可审计的世界模型数据与表征引擎 | R1–R3；U1 + data | 中高，非 WM 数据增强已成熟 | 中 | **79.0** | 4 |
| D4 | 推理时视频反事实规划与可执行子目标 | R1/R2；U2/U3/U4 | 高且拥挤 | 中低 | **75.5** | 5 |
| D6 | 统一 World–Language–Action 基座与 policy–WM 共演化 | R1–R3；U6 | 联合建模很高，共演化因果证据稀疏 | 低 | **67.5** | 6 |

### 1.1 评分规则

各项为 1–5 分；综合分为加权百分制。高分表示在当前研究约束下更值得优先让人审阅，不表示自动选择。

| 维度 | 权重 | 5 分含义 |
|---|---:|---|
| 科学影响力 | 25% | 若解决，会改变 VLA × WAM 的核心能力或评估范式 |
| 创新空间 | 20% | 邻近工作未把关键机制做透，仍有清晰的新知识空间 |
| 证据缺口 | 20% | 当前结论依赖代理指标、缺对照或存在相互冲突的证据 |
| 当前配置可行性 | 20% | 可复用公开模型/日志，接近 2 GPUh pilot、8 GPUh 总预算，无真机 |
| 获得可信结果的速度 | 15% | 5 分代表可较快完成有判别力的证伪或验证 |

| ID | 影响力 | 创新空间 | 证据缺口 | 可行性 | 速度 | 加权分 |
|---|---:|---:|---:|---:|---:|---:|
| D1 | 5.0 | 4.5 | 5.0 | 4.5 | 4.5 | 94.5 |
| D2 | 4.5 | 4.0 | 4.5 | 4.5 | 4.0 | 86.5 |
| D5 | 5.0 | 4.5 | 5.0 | 2.5 | 2.5 | 80.5 |
| D3 | 4.5 | 4.0 | 4.0 | 3.5 | 3.5 | 79.0 |
| D4 | 4.5 | 3.5 | 4.5 | 3.0 | 3.0 | 75.5 |
| D6 | 5.0 | 3.5 | 4.5 | 1.5 | 1.5 | 67.5 |

## 2. D1 — 可校准的世界模型策略评估、critic 与安全预演

**版图位置：** R1–R4 均可；核心用途是 U3。重点不在“生成得像不像”，而在模型能否对真实控制结果作可靠判断。

### 核心问题

世界模型能否在不真实执行、少真实执行或受限仿真中，可靠地比较 VLA 策略、发现失败、估计风险并提供可校准的不确定性？目前最危险的断层是：感知质量、视频质量或自动语义评分看起来很好，但不能保持真实环境中的策略排序，更不保证发现接触、动力学和尾部安全失败。

### 为什么是现在

- WorldEval、WorldGym、WorldArena、GigaWorld、GPC、WAV 等工作把 world model 从“演示生成器”推向 evaluator / critic / policy testing，说明用途正在形成独立研究簇。
- 多个评测同时报告“感知保真度不等于功能保真度”，世界模型也可能在 OOD 策略上高估能力；这是清楚但尚未被统一解决的证据冲突。
- VLA 策略迭代速度已快于真机评测能力，而当前配置禁止真机、预算紧，正适合优先研究离线且可审计的判断机制。

### 主要方法族

- 同初始状态的真实/仿真轨迹与 world rollout 配对，学习或校准策略排序。
- 基于 VLM、reward model、success classifier 或 task metric 的轨迹 critic。
- dynamics-aware failure detector、风险边界与 reachability / constraint checking。
- ensemble、conformal prediction、distribution shift detector 与选择性拒答。
- evaluator–policy 去耦：跨架构、跨预训练源或外部传感器的独立审计。

### 最近工作密度与边界

**密度：中等、快速上升。** 通用 failure/safety monitor 较成熟，但“world model 生成 + VLA 策略排序 + OOD 校准 + 尾部失败覆盖”这一完整交集仍不密。若只做一个 VLM 成功分类器，容易落入成熟区；真正的开放空间在功能一致性、排序稳定性、拒答和偏差审计。

### 尚未解决的缺口

1. 同一初态下 world rollout 与真实/高保真仿真结果之间，缺少跨策略族、跨任务和跨分布的配对协议。
2. 多数工作重均值准确率，较少报告策略排序、校准误差、风险覆盖率、假阴性以及置信区间。
3. evaluator、policy 与 world model 可能共享 foundation bias，形成“模型为模型作证”的自洽假象。
4. 对罕见接触、不可逆失败和安全边界，数据稀疏导致总体指标掩盖尾部错误。

### 什么证据具有决定性

- 在相同初始状态集合上，world evaluator 对真实/高保真环境的 policy ranking 保持较高且有置信区间的 Kendall/Spearman 一致性。
- 校准后的 success/risk probability 在 ID 与 OOD policy、task、visual shift 上均报告 ECE/Brier、coverage–risk 曲线与选择性拒答表现。
- 危险事件的 recall、false-negative rate、最坏子组结果不能被平均成功率替代。
- 与直接 VLM critic、行为克隆 value、仿真器 oracle、随机/恒定预测器等基线在相同观测和计算预算下比较。
- 明确披露每次策略评估的 rollout 成本、吞吐、延迟和失败类别；不能只用视频感知指标作为控制结论。

### 候选任务与基线族（未选择）

- **任务族：** 多阶段操作、精密接触、可变形物体、导航-操作组合、扰动恢复、带安全约束的操作。
- **策略族：** diffusion VLA、autoregressive VLA、分层 policy、经典 imitation/RL policy，至少包含能力差异和失败模式差异。
- **基线族：** VLM-only judge、learned value/success classifier、ground-truth simulator metric、model-free OOD detector、world-model ensemble。

### 数据与计算需求

若有公开策略 checkpoint、轨迹日志或可重放仿真，主要是推理与统计，预期低到中等算力；可以先做无训练或轻量校准。完整跨策略/跨任务结论仍需要大量配对 rollout，但比训练新视频基座更符合 2/8 GPUh 和零真机约束。

### 主要风险

- 可用公开轨迹未必包含相同初态与充分多样的策略，排序结论可能不稳。
- world model 与 critic 共享视觉语义偏差，校准看似正常但共同漏掉物理失败。
- 高保真仿真不是现实；若声称真机安全，仍需未来追加现实证据。
- rare-event 样本太少时，安全结论容易过度外推。

### 最便宜的证伪

不训练新 world model：选择现有 world rollout、对应 simulator replay 和若干能力不同的公开策略，先检验排序一致性、OOD 校准与危险假阴性。如果在轻微策略分布偏移下排序即翻转，或拒答机制不能隔离错误，则该 evaluator 路线在扩展前即被否证。

### 方向建议

**推荐度：第一梯队，94.5/100。** 它最贴合当前资源，而且直击“生成指标不能支持控制结论”的领域共性缺口。这里的推荐是让人优先审阅，**不是已经选定 D1，也不是一个具体 Idea**。

## 3. D2 — task-centric latent / 结构化动力学用于 VLA 的可控预测与高效规划

**版图位置：** 主要是 R3/R4，服务 U3/U4。问题不是“latent 是否比 video 好”，而是什么状态对动作选择足够、可预测、可校准且计算高效。

### 核心问题

VLA 控制需要预测哪些未来信息？像素重建可能浪费容量、放大不可控细节，过度压缩的 task latent 又可能丢掉接触、几何与可恢复性。核心是找到在给定任务和控制接口下，既保留 action-relevant 信息又支持长时滚动、风险判断与规划的表征。

### 为什么是现在

- Dreamer、TD-MPC、DINO-WM、V-JEPA 2 等表明 latent dynamics 可服务控制，但多数成功不等于已解决 VLA 条件、语言任务和跨 embodiment 接口。
- 3D、点、粒子、对象 slot 与接触结构工作快速增加，为 R4 提供更强归纳偏置，同时也暴露了“结构化不等于语义、接触和不确定性全都解决”的边界。
- 大视频模型的 rollout 代价和延迟突出，使紧凑状态是否能以较低成本提供相同决策价值成为实际瓶颈。

### 主要方法族

- task-centric predictive latent：JEPA、contrastive/predictive coding、value-aware 或 control-aware representation。
- stochastic latent state-space model、RSSM、latent transformer 与 uncertainty ensemble。
- 对象/关键点/3D point/particle/contact graph 等显式结构状态。
- latent MPC、CEM/MPPI、trajectory optimization、hierarchical planning 与 terminal-value planning。
- hybrid representation：语义 latent + 几何/接触结构 + 不确定性，而非强迫单一表征获胜。

### 最近工作密度与边界

**密度：通用 world-model control 很高，VLA 专属机制证据较稀疏。** 如果只做一个新 latent encoder 或在单任务上超过旧 MBRL，竞争拥挤；开放空间在 matched representation × control-use 对照、语言/动作接口条件化、跨分布校准和每单位计算的控制价值。

### 尚未解决的缺口

1. 缺少在同一数据、planner、参数量和推理预算下，对 R1–R4 表征进行公平比较的控制实验。
2. pixel/video、latent 与 structured state 的优劣常被不同架构、预训练规模和任务难度混淆。
3. 长 rollout 能减少规划频次，但累计模型偏差可能令策略利用错误；这一权衡少有统一报告。
4. action token、continuous control、跨 embodiment normalization 等 VLA 接口会改变什么信息必须进入状态，但常被忽略。

### 什么证据具有决定性

- 固定数据、控制用途、planner 搜索预算和模型规模，对不同 R 表征作成组对照，而非跨论文比较。
- 以闭环 success、return、恢复能力和安全约束为主结果，同时报告一步/多步误差、校准、不确定性和 inference FLOPs/latency。
- 分离 representation quality 与 planner quality：包含 oracle dynamics、oracle state、无规划 policy 和相同 planner 的负对照。
- 在视觉、物体组合、动力学或 action-interface shift 下检验是否仍保留排序与控制收益。

### 候选任务与基线族（未选择）

- **任务族：** 视觉目标控制、长时多阶段操作、接触丰富操作、可变形/粒子对象、导航或移动操作。
- **表征基线族：** pixel/video predictor、visual token model、JEPA/RSSM latent、object/3D/particle state、ground-truth state。
- **控制基线族：** TD-MPC/Dreamer 类 latent control、CEM/MPPI、model-free VLA、行为克隆、oracle simulator planner。

### 数据与计算需求

小型开放仿真和冻结 encoder 可在低至中等算力下完成首轮机制比较，较契合 pilot。要宣称跨 embodiment 或长时优势，需要更多任务、种子和表征×规划组合，完整矩阵可能超出 8 GPUh，需先裁剪到最有判别力的轴。

### 主要风险

- “公平比较”本身很难：不同表征的最佳模型容量和 planner 超参并不相同。
- ground-truth structured state 可能形成不现实的特权信息基线。
- 单一仿真任务会把感知问题消掉，无法支持 VLA 一般性结论。
- 过强压缩可能在训练内有效，却在任务变化和接触异常上脆弱。

### 最便宜的证伪

在一个公开仿真任务族中冻结现有 encoder，使用相同小型 dynamics 和相同 planner，对视觉 latent、task latent 和可用结构状态作短 horizon 对照。若任何收益在 matched compute 或轻微 OOD 下消失，说明“表征机制”不是值得扩展的主因。

### 方向建议

**推荐度：第一梯队，86.5/100。** 它是机制清晰度与资源可行性的最佳平衡，适合希望回答“world model 为什么帮助控制”的路线。仍然只是候选方向，未锁定表征、任务或方法。

## 4. D3 — 可审计的世界模型数据与表征引擎

**版图位置：** 以 U1 和 data engine 为主，覆盖 R1–R3；world model 用于生成、标注、筛选、补全或预训练，而非在线闭环规划。

### 核心问题

世界模型能否把少量真实机器人数据、无动作视频或已有策略日志转化为真正有效的 VLA 训练信号？需要区分“产生更多看似合理的视频”和“产生经过物理、动作与任务审计后，能提升 held-out 控制的有效样本”。

### 为什么是现在

- 大规模人类视频预训练、latent action、robot video generation 和 synthetic trajectory 工作已显示数据路线的规模潜力。
- 机器人数据稀缺仍是 VLA 的根本约束；数据引擎通常比在线规划更容易部署到现有 VLA pipeline。
- ROSIE、MimicGen、RoboGen 等非 world-model 数据增强已经形成强基线，迫使 WM 路线回答它独有的价值，而不是只证明“更多数据有帮助”。

### 主要方法族

- 无动作视频的 latent action / inverse dynamics 标注与 robot action 对齐。
- action-conditioned video 生成后由 IDM、controller 或 trajectory optimizer 回译动作。
- world rollout 生成 counterfactual、恢复、失败或长尾轨迹。
- synthetic trajectory 的过滤、重加权、uncertainty gating 与 curriculum。
- world-model predictive pretraining、future representation learning 和跨 embodiment transfer。

### 最近工作密度与边界

**密度：中高。** 视频/latent-action 预训练与合成数据快速增长，普通视觉增强和程序化数据生成已较成熟。空白不在“再生成一批数据”，而在有效样本率、动作可执行性、分布覆盖、污染审计、与非 WM 引擎的等预算比较。

### 尚未解决的缺口

1. 生成视频到 action label 的回译误差常是隐性瓶颈，视觉合理不代表动作可执行。
2. synthetic data 收益常与更多总训练步、更多真实 seed data 或更大模型混杂。
3. 对重复样本、benchmark contamination、物理无效轨迹和失败模式覆盖缺少统一审计。
4. world-generated data 可能放大基策略偏差，形成闭环自我模仿。

### 什么证据具有决定性

- 固定真实数据量、总训练 token/step、模型容量和计算预算，比较 WM 数据、非 WM 合成数据、常规增强与纯真实数据。
- 报告生成总数之外的 **effective sample yield**：通过物理/动作/任务审计且对 held-out 控制产生边际收益的比例。
- 收益必须出现在 held-out task、object、scene 或 embodiment，而不只是在生成模型熟悉的分布。
- 展示 action validity、轨迹多样性、失败覆盖、污染/近重复检查及每个有效样本的生成成本。

### 候选任务与基线族（未选择）

- **数据制度：** 少量机器人轨迹 + 大量人类视频；已有 VLA 日志 + counterfactual；成功数据 + 稀缺恢复/失败数据。
- **任务族：** 多对象操作、长时序指令、恢复行为、跨场景/跨 embodiment transfer。
- **基线族：** 纯真实数据、视觉增强、ROSIE 类语义增强、MimicGen/RoboGen 类程序化生成、latent-action 预训练、随机或难例重采样。

### 数据与计算需求

若复用预训练生成器和公开 VLA checkpoint，小规模有效样本审计可用中等算力；完整生成—过滤—重训 pipeline 通常是中高到高算力，并对存储和数据许可有要求。当前配置禁止未经批准的数据许可变更和外部付费算力，因此必须从小规模边际价值测试开始。

### 主要风险

- 训练 VLA 的成本可能远大于生成数据，超出总预算。
- synthetic trajectory 与 benchmark 共享数据源，导致看似泛化实际是污染。
- IDM 或 action alignment 错误会让数据在像素层面漂亮、在控制层面有毒。
- 与强非 WM 数据引擎对照后，WM 的独特收益可能消失。

### 最便宜的证伪

复用一个公开生成器，在固定小型真实集上只加入少量经过/未经审计的合成样本，保持 policy 训练步完全一致。若有效样本率低、动作误差高，或收益不超过普通增强/重采样，则无需扩大生成规模。

### 方向建议

**推荐度：第二梯队，79.0/100。** 产业与规模价值高，但完整闭环较吃资源；只有把“可审计的有效样本”置于核心，才有足够清晰的研究边界。

## 5. D4 — 推理时视频反事实规划与可执行子目标

**版图位置：** R1/R2；横跨 U2、U3、U4。world model 在执行时生成一个或多个可视未来，用于选动作、选子目标或重规划。

### 核心问题

视频式未来能否成为 VLA 的可用思考空间：既表达任务语义与可视结果，又能被稳定地转换为当前 embodiment 的可执行动作，并在延迟受限的闭环中胜过直接 policy？关键不是生成一条成功视频，而是搜索、评价、动作回译和闭环纠错的联合有效性。

### 为什么是现在

- UniPi、VLP、RoboDreamer、World Action Planner 等展示了 video plan / keyframe / visual foresight 的可行性。
- 新一代视频基座提升时空一致性，使多候选 counterfactual 与 visual subgoal 更现实。
- 同时，现有系统暴露数秒级规划延迟、短记忆、无效物理未来和隐式 IDM 瓶颈，形成明确工程与科学断点。

### 主要方法族

- language-conditioned video plan / keyframe plan，再由 inverse dynamics 或 goal-conditioned policy 执行。
- action-conditioned video rollout + CEM/beam search/best-of-N candidate selection。
- hierarchical planner：高层 visual subgoal、低层 VLA/controller、事件触发重规划。
- future-conditioned critic、feasibility filter、uncertainty-aware candidate pruning。
- 并行/缓存/蒸馏 rollout 以降低在线延迟。

### 最近工作密度与边界

**密度：高且拥挤。** “生成视频作为计划”的概念已有多条路线；简单提升视频指标或加一个 IDM 难形成稳固空间。仍开放的是 matched-latency 的闭环价值、可执行性、长 horizon 误差、candidate diversity 与 action-interface 解耦。

### 尚未解决的缺口

1. 视频计划物理上或几何上不可执行时，低层 policy 往往被迫补救，但论文把成功归因于 planner。
2. 更多候选通常意味着更多算力；success gain 未与 inference budget 公平匹配。
3. IDM、goal-conditioned controller 或 VLA 本身可能贡献主要收益，world model 的因果作用不清。
4. 开环视频质量与闭环纠错、扰动恢复、接触稳定性之间缺一致关系。

### 什么证据具有决定性

- 在相同 wall-clock、FLOPs、candidate 数和 controller 条件下，与直接 VLA、无生成层级 policy、model-free search 比较闭环成功。
- 分别测量 video plan feasibility、plan-to-action error、低层纠错负担、重规划频率和 end-to-end latency。
- 用 oracle plan、shuffled plan、single-candidate、no-IDM/no-critic 等对照分离各模块贡献。
- 在扰动、视觉 OOD、动力学变化和长 horizon 条件下展示收益不由 benchmark shortcut 驱动。

### 候选任务与基线族（未选择）

- **任务族：** 多阶段桌面操作、导航-操作、需要视觉子目标的长时任务、环境扰动后的恢复。
- **规划基线族：** UniPi/VLP 类 visual planning、action-conditioned rollout search、经典 CEM/MPPI、symbolic/subgoal planner。
- **执行基线族：** direct VLA、goal-conditioned policy、IDM、oracle low-level controller。

### 数据与计算需求

复用视频模型可避免训练成本，但多候选推理与闭环仿真依然较重；高分辨率或长 horizon 很可能超出 2 GPUh pilot。需先用少量候选、缓存 rollout 或轻量模型测量是否存在 matched-latency 收益。

### 主要风险

- 生成延迟无法满足真实控制频率。
- 视频语义合理但接触和动力学错误，且 evaluator 无法识别。
- IDM / low-level controller 成为隐藏的性能来源或跨 embodiment 瓶颈。
- 高质量闭环结果依赖私有大模型和私有数据，难复现。

### 最便宜的证伪

不训练 policy：对现有生成计划进行 simulator kinematic/contact 审计，并让同一 goal-conditioned controller 执行真实/生成/扰动计划。若可执行率、动作回译或 matched-time 闭环收益不成立，则不值得扩大视频模型。

### 方向建议

**推荐度：第二梯队，75.5/100。** 方向直观且可展示，但概念拥挤、推理昂贵；必须以闭环、matched-latency 和模块归因为门槛，不能以视频质量作为主张。

## 6. D5 — learned world 中的 VLA 后训练与 imagined model-based RL

**版图位置：** R1–R4 都可能，核心是 U5。world model 不只评价动作，而是提供 imagined experience 更新 VLA policy。

### 核心问题

能否在 learned world 中对已有 VLA 进行可靠后训练，从少量真实日志扩展出恢复、长尾和长时行为，同时避免 policy 学会利用 world-model error？这要求区分“在模型里回报变高”和“真实/高保真环境中的策略真的改善”。

### 为什么是现在

- Dreamer、MBPO、TD-MPC 等通用 MBRL 已建立 imagined learning 的方法基础，但与大型 VLA、语言条件和机器人视频 world 的结合仍早期。
- World4RL、World-Gymnast、RehearseVLA 等近作开始把 learned video world 用于 policy training/evaluation，说明交集刚进入可验证阶段。
- VLA 基座越来越强，使“从零训练”不再必要；冻结或低秩后训练降低门槛，也让 world model 的边际价值更容易隔离。

### 主要方法族

- frozen world model + policy/value optimization；短 imagined rollout 与 real-data anchoring。
- uncertainty-aware / conservative imagination，拒绝高模型误差区域。
- Dyna-style real–imagined mixture、offline model-based RL、latent actor-critic。
- VLM/reward model 提供语义 reward，dynamics model 提供可达性和后果。
- adversarial exploitation audit、policy constraint、behavior regularization 与 periodic grounding。

### 最近工作密度与边界

**密度：通用 MBRL 高，直接 VLA × learned video world 较稀疏且极新。** 创新空间大，但完整系统需要同时解决 world quality、reward validity、policy optimization 和 transfer。只报告 imagined return 或单个种子不构成证据。

### 尚未解决的缺口

1. policy 更新后分布发生变化，world model 在新动作区域最不可靠，容易被系统性利用。
2. imagined rollout 的真实样本效率收益常未按总环境交互、训练 FLOPs 和预训练成本公平核算。
3. VLM reward 能判断语义进展，却可能忽略接触、损坏和不可逆失败。
4. 大部分结果缺少 matched simulator/real rollout 来验证 policy-shift 后的模型偏差。

### 什么证据具有决定性

- 在相同真实环境交互数、总优化步和计算预算下，imagined update 相对 offline/model-free 后训练提高真实或高保真仿真 return/success。
- 每轮 policy shift 后测量 world prediction、reward calibration 和真实 return 的偏差，而非只测初始 policy 分布。
- 包含 exploitation audit：用 ground-truth simulator 回放模型内高回报轨迹，报告虚假高回报率、OOD action 和不确定性。
- 至少多种子、置信区间、matched-budget baseline，并包含短/长 imagination、无 uncertainty、无 real anchoring 等必要消融。

### 候选任务与基线族（未选择）

- **任务族：** 稀疏奖励长时操作、恢复与纠错、低数据多任务、带分布转移的操作/导航。
- **world-model 基线族：** video world、latent RSSM、structured dynamics、ground-truth simulator。
- **学习基线族：** offline RL、behavior cloning fine-tune、Dyna/MBPO/Dreamer 类、纯真实 rollout 后训练、无 policy update 的 reranking。

### 数据与计算需求

完整结论通常需要重复 world rollout、policy optimization 和 ground-truth 验证，计算与实验矩阵都高；在当前 8 GPUh 内很难支撑母方向级主结论。但复用小型冻结 world model 与轻量 policy，可做一个严格的 exploitation / transfer 证伪 pilot。

### 主要风险

- policy 明显利用 world-model artifacts，模型内进步与真实退化并存。
- reward model 与 world model 共享语义偏差，形成双重自我确认。
- 多模块失败使负结果难归因，实验矩阵快速膨胀。
- 预训练成本若不计入，会产生虚假的 sample-efficiency 叙事。

### 最便宜的证伪

在一个小型公开仿真任务中冻结 world model，只允许少量 policy update；把模型内最高回报轨迹立即送入 ground-truth simulator，并和同预算 offline update 比较。若出现明显 exploitation 或真实收益不超过基线，就暂停扩大训练。

### 方向建议

**推荐度：高风险高回报，80.5/100。** 科学缺口和潜在影响很大，故总排名第三；但当前算力只适合做窄而严格的可行性/证伪，若选中需重新核验资源边界。

## 7. D6 — 统一 World–Language–Action 基座与 policy–WM 共演化

**版图位置：** 多为 R1–R3，核心 U6。研究对象是统一 token/latent/transformer 中世界预测与动作生成的关系，或二者随数据与 policy 分布共同适应。

### 核心问题

将未来视觉、语言理解和动作生成放入同一模型，是否产生可归因的控制协同，而非仅仅来自更大数据、更多参数和更多训练 token？进一步地，policy 与 world model 共同更新能否改善 distribution alignment，又不陷入自我确认和灾难性漂移？

### 为什么是现在

- GR-2、UWM、UVA、WorldVLA、DreamZero、Cosmos Policy、WLA、DiT4DiT 等使 joint world–action modeling 成为高能见度路线。
- 统一 diffusion/transformer 架构让视频与动作共享表征、互相条件化变得工程可行。
- 现有大模型结果同时暴露短记忆、控制频率、精密动作和高自由度接口问题，说明规模化并未自动解决耦合机制。

### 主要方法族

- joint video/action token prediction、共享 backbone + 多头、交替 denoising 或 interleaved sequence。
- world-prediction auxiliary objective 用于 direct VLA policy。
- policy-conditioned world adaptation、world-conditioned policy adaptation。
- alternating / joint update 的闭环数据收集与 self-improvement。
- cross-embodiment action tokenizer、shared latent interface 与 modular world/policy composition。

### 最近工作密度与边界

**密度：联合建模很高且快速拥挤；真正的 policy–WM 共演化因果证据较稀疏。** “加世界预测辅助损失”“共享一个大 backbone”本身很难构成新方向。开放空间在共享什么、何时共享、何时冻结、如何防止耦合偏差，以及是否有 matched-scale 的因果收益。

### 尚未解决的缺口

1. joint model 常比基线更大、数据更多，world objective 的真实贡献无法分离。
2. 世界预测与动作生成的最优表征粒度、更新频率和梯度关系可能冲突。
3. 共同更新会让 evaluator 与 policy 一起漂移，缺少外部锚点判断真实改善。
4. 跨 embodiment action semantics 与控制频率不统一，使“统一 token”很可能只在单一平台成立。

### 什么证据具有决定性

- 在同数据、参数量、训练 token、优化步和推理预算下，进行至少 2×2 对照：无 world objective / 有 world objective，以及 frozen / alternating / joint coupling。
- 分离 world prediction、action accuracy 和闭环 success，报告三者相关性及失败案例；不能用单一 loss 降低推断控制收益。
- 检验跨任务、跨 embodiment、长 horizon 和 policy-shift 的稳定性、校准与遗忘。
- 使用独立 simulator/real evaluator 或不共享预训练源的外部审计，避免系统自我评分。

### 候选任务与基线族（未选择）

- **任务族：** 多任务 manipulation、跨 embodiment transfer、长时指令、交互式数据收集。
- **模型基线族：** direct VLA、独立 world+policy cascade、共享 backbone 多头、joint token model、frozen/alternating/joint variants。
- **接口基线族：** embodiment-specific action head、shared tokenizer、latent action、inverse-dynamics bridge。

### 数据与计算需求

从头训练可信的统一基座需要大规模视频/机器人数据与高算力，明显超出当前 8 GPUh。只有复用公开 checkpoint、冻结大部分网络、研究小型头或局部更新，才可能开展低成本机制 pilot；这类 pilot 又不能外推到 foundation-scale 结论。

### 主要风险

- 参数量、预训练数据和训练 token 的规模混淆几乎不可避免。
- 多目标梯度冲突造成动作能力退化，或视频 loss 主导优化。
- 自生成数据和共同更新形成 self-confirmation loop。
- 推理延迟、控制频率和跨 embodiment action 归一化削弱统一模型的实际价值。

### 最便宜的证伪

在一个公开小型 VLA checkpoint 上增加冻结或低秩的世界预测辅助头，严格匹配总训练步和参数预算；若 action/闭环收益不随可测的 predictive improvement 出现，或 matched-scale 后消失，就没有理由扩大到统一基座训练。

### 方向建议

**推荐度：远期高影响，当前低适配，67.5/100。** 它适合作为长期研究主题，但当前配置难产出可信 foundation-scale 因果证据。除非可复用合适 checkpoint 并把问题缩成机制审计，否则不宜作为本轮首选。

## 8. 六方向之间的边界与组合关系

方向不是六个互斥模型架构，而是六种主要科学问题。为避免后续把多个大课题拼成一个过载 Idea，建议按“一个主用途 + 一个必要支撑”理解组合关系：

| 主方向 | 可作为支撑的相邻方向 | 不应偷偷替代的核心证据 |
|---|---|---|
| D1 evaluator/critic | D2 的 compact state；D4 的 rollout；D6 的 joint model | 必须验证真实/高保真结果的排序与校准，不能以生成质量替代 |
| D2 latent/structured | D1 的风险评估；D4 的 planner | 必须用 matched planner/compute 隔离表征贡献 |
| D3 data engine | D1 的样本审计；D6 的预训练接口 | 必须证明 held-out 控制的边际价值与有效样本率 |
| D4 video planning | D1 的候选评价；D2 的低层状态 | 必须证明 matched-latency 的闭环收益与可执行性 |
| D5 imagined MBRL | D1 的 exploitation audit；D2 的 compact world | 必须在 policy shift 后回到真实/高保真环境验证 |
| D6 joint/co-evolution | D1 的独立审计；D3 的数据循环 | 必须做 matched-scale 因果对照，不能把规模收益归因于耦合 |

三条典型分叉可帮助人工选择：

- 若更关心 **“world model 的判断是否可信”**：优先审阅 D1。
- 若更关心 **“什么内部状态真正有助于控制”**：优先审阅 D2。
- 若愿意承担更高系统与算力风险，追求 **“world model 能否直接改进 policy”**：优先审阅 D5；D3/D4/D6 分别对应数据、推理和统一基座三种落点。

这只是问题定位，不是对任何具体方案的承诺。

## 9. 覆盖范围、已知盲区与选择前置条件

### 已覆盖的证据面

- 2018–2026 的通用 latent MBRL、视觉 foresight、机器人视频生成、VLA 后训练、evaluator/critic、结构化动力学与 joint world-action modeling。
- 公开论文与项目页的主张、公开限制、邻近工作密度和相互冲突的结果。
- representation × role 二维分类、闭环功能证据、计算/数据约束、failure/safety 与 matched-budget 要求。

### 当前盲区

- 本地 `papers/` / `literature/` 没有可优先解析的全文 PDF；深读主要依赖公开 HTML/摘要/项目材料，部分 2026 工作尚未经历长期复现检验。
- Semantic Scholar 检索出现限流，OpenAlex 有重试；广搜覆盖足以制图，但不能证明穷尽所有同期工作。
- 私有数据、未公开训练配方、真实机器人失败分布和硬件成本不可见。
- humanoid、legged locomotion、drone、autonomous driving 与 mobile manipulation 没有分别做同等深度的垂直盘点；版图当前更偏通用 embodied control 与 manipulation 证据。
- 当前没有 GPU backend、数据集或 benchmark 被授权/选定，因此可行性分数是基于公开 checkpoint 和仿真的条件性判断。

### 选中方向后才应确定的事项

1. 具体任务/embodiment 与 benchmark；
2. 可用 checkpoint、数据许可和 GPU backend；
3. 主张类型及最小决定性证据；
4. matched-budget 基线、种子、置信区间和 integrity gate；
5. 是否需要进一步对选中母方向做近期查新。

在人工选择前提前锁定这些项目，会把领域探索误写成具体 Idea，因此本阶段有意保留为空。

## 10. 人工方向检查点

### 排名解读

- **D1（94.5）**：当前配置下最稳健，优先解决可信评估和安全预演的基础缺口。
- **D2（86.5）**：机制与可行性最平衡，适合研究“什么世界表征真正支持 VLA 控制”。
- **D5（80.5）**：高风险高回报，科学问题强，但需严格限制 pilot 并准备资源复核。
- D3、D4、D6 分别是数据规模、在线规划、统一基座三种有价值但当前约束更重的路线。

### 明确的非决策声明

**本文件没有替用户选择母方向。** 当前应保持：

```text
research.selected_macro_direction = null
idea-discovery = blocked: awaiting human macro-direction selection
```

下一步只能由人工选择 D1–D6、要求修改/合并版图，或终止本轮探索。系统在收到选择前不得生成具体 Idea、方法假设、实验方案或 benchmark 绑定。
