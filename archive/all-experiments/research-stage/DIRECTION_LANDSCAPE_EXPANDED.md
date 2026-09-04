# VLA × WAM 扩展母方向版图

> **版本：** v2 expanded，2026-08-06  
> **范围：** 4 个上层问题区域，20 条中粒度母方向  
> **状态：** 未选择方向；未进入具体 Idea、方法假设、benchmark 或实验设计  
> **证据：** [初版文献地图](./LITERATURE_MAP.md)、[扩展检索补充](./LITERATURE_MAP_EXPANSION.md)、[初版 6 方向版图](./DIRECTION_LANDSCAPE.md)

## 0. 先解释“母方向”是什么

母方向不是“使用 Transformer”“加一个 uncertainty head”或“在 LIBERO 上测试”。它是一类可以容纳多种方法和任务、但拥有独立科学问题与证据合同的研究路线。

例如：

- “用视频 world model”只是表征选择，不足以成为母方向；同一个视频模型可以用于生成子目标、MPC、策略评测、合成数据或 imagined RL。
- “长期任务”只是压力测试轴；它可以用来检验记忆、规划、持续学习等不同方向。
- “安全”只有在终点是危险覆盖、风险—收益权衡或选择性自治时才独立；若 uncertainty 只是 MPC 的一个组件，仍归 MPC。

这版用最简单的四个问题组织版图：

```text
A. 世界和动作应该怎样表示？          7 条
B. 做当前决策时怎样使用世界模型？    6 条
C. 怎样用世界模型训练和适应策略？    6 条
D. 怎样证明 WAM 真的有功能价值？     1 条
                                      ────
                                      20 条
```

R1–R4（视频、视频 latent、task latent、显式/结构状态）和 U1–U6（预训练、提议、评价、规划、想象优化、联合模型）仍作为专家标签，但不再作为用户理解版图的第一入口。

## 1. 为什么原来的 6 条显得少

初版按“世界模型大致用来做什么”压缩，适合快速制图，却把验证对象不同的路线合在了一起：

| 初版方向 | 本版拆分 |
|---|---|
| 旧 D1：evaluator / critic / safety | B3 单步/轨迹 critic；B4 整套策略评测；B5 安全与选择性自治 |
| 旧 D2：latent / structured dynamics | A2 task latent；A3 结构化物理；A4 记忆 belief；A5 多模态接触；A6 因果可供性 |
| 旧 D3：data / representation engine | A1 预测预训练；A7 动作语义；C1 合成数据；C3 主动采数 |
| 旧 D4：video planning | B1 可视子目标；B2 action-conditioned 反事实规划 |
| 旧 D5：imagined MBRL | C2 imagined VLA 后训练 |
| 旧 D6：joint / co-evolution | C5 静态联合基座；C6 长期共适应；A7 跨具身接口 |
| 初版未充分显式化 | B6 主动感知；C4 部署时系统识别；D1 WAM 功能基准 |

拆分标准不是“多给几个名字”，而是下列三项至少有一项不同：研究对象、主要 endpoint、决定性反证。

## 2. 总览与评分

评分仍为启发式决策量表，不是成功概率。维度和权重为：科学影响 25%、创新空间 20%、证据缺口 20%、当前 2/8 GPUh 配置可行性 20%、获得首个可信结果的速度 15%。

| ID | 方向 | 人话版 | 文献密度 | 分数 /100 |
|---|---|---|---|---:|
| A1 | 预测式视频/世界表征预训练 | 先看大量视频学世界变化，再把特征交给 VLA | 高 | 72.4 |
| A2 | task-centric latent 动力学 | 只记住对做决定有用的世界状态 | 通用高、VLA 中 | 86.5 |
| A3 | 对象、3D、几何与接触的结构化物理世界 | 把世界表示成持续存在且遵守物理的实体 | 中高 | 80.4 |
| A4 | 长时记忆与部分可观测 belief world model | 记住当前看不见、但过去发生过的事 | 中等、新近增长 | 88.1 |
| A5 | 视觉—触觉—本体感觉接触世界模型 | 看不清接触时，让触觉和身体状态补上 | 新兴，中等 | 75.8 |
| A6 | 因果动力学与可供性世界模型 | 理解哪个动作真正导致哪个效果 | 交叉区中低 | 84.2 |
| A7 | 跨具身动作语义与 effect-space 接口 | 不同机器人用不同关节命令实现同一物理效果 | 中等、快速增长 | 82.2 |
| B1 | 可视子目标与视频计划 | 先想象“下一幕该长什么样”，再执行 | 高且拥挤 | 71.3 |
| B2 | 动作条件反事实规划与 MPC | 把几组候选动作先放进 learned world 试演 | 高且拥挤 | 74.7 |
| B3 | world-model reward、value 与 critic | 用预测未来给当前动作或轨迹打分 | 中高 | 87.1 |
| B4 | 虚拟策略评测与排序 | 不上真机，先判断哪个 VLA/checkpoint 更好 | 中等、快速增长 | **94.5** |
| B5 | 失败预警、保守控制与选择性自治 | 模型没把握时减速、换方案、拒绝或求助 | 中高 | **91.8** |
| B6 | 主动感知与信息获取 | 不确定时先决定去哪里看、摸或探测 | 传统高、直接交集低中 | 86.9 |
| C1 | WAM 合成轨迹与数据引擎 | 用 imagined experience 扩充离线训练集 | 中等、快速增长 | 79.0 |
| C2 | imagined VLA 后训练与 model-based RL | 让 VLA 在 learned world 里练习，再回环境验收 | 通用高、直接交集新 | 80.5 |
| C3 | 主动数据获取与 world-model curriculum | 让模型决定下一条昂贵数据该去哪里采 | 通用中高、直接交集低 | 85.9 |
| C4 | 部署时系统识别与快速适应 | 先判断新现场的相机、摩擦、负载和身体 | 通用高、VLA-WAM 新 | 89.1 |
| C5 | 联合 World–Language–Action 基座 | 同一模型共同学习未来、语言和动作 | 很高且拥挤 | 66.3 |
| C6 | 持续学习与 policy–world 长期共适应 | 模型与策略长期更新，同时不能一起学错或遗忘 | 通用中、直接交集低 | 76.0 |
| D1 | WAM 功能评测与物理可执行性基准 | 不问视频多漂亮，只问它是否听动作、守物理、能决策 | 中等、快速增长 | **90.9** |

当前资源下分数最高的是 B4、B5、D1、C4、A4。它们只是优先阅读建议，**没有任何一条被自动选中**。

## 3. A 区：世界和动作应该怎样表示？

### A1 — 预测式视频/世界表征预训练

- **人话解释：** 先让模型从大量无动作或弱动作视频学会“场景通常怎样变化”，再把学到的视觉特征用于 VLA，而不是在线生成未来。
- **核心问题与时机：** predictive objective 是否比静态图像/语言预训练学到更好的对象持续性、运动和交互特征；大规模视频预训练已经可用，但控制收益经常与数据规模混杂。
- **方法与证据簇：** future feature prediction、masked world modeling、JEPA、video token prediction；锚点包括 [V-JEPA 2](https://arxiv.org/abs/2506.09985)、[GR-1](https://arxiv.org/abs/2312.13139) 与 masked visual world models。
- **边界与缺口：** 只主张 encoder/初始化收益；一旦在执行时 rollout 或用 imagined return 更新策略，就转入 B2/C2。缺口是 matched-data、matched-compute 下 predictive pretraining 的独立边际价值。
- **决定性证据：** 冻结或等量微调 encoder，在相同 policy、数据和训练 token 下比较静态、预测式和随机初始化；看 held-out 控制与动态诊断，而不只看 representation probe。
- **资源与廉价证伪：** 可复用公开 encoder，低至中算力；若小规模冻结特征对照中收益在匹配训练量后消失，就不值得扩大预训练。
- **判断：** 72.4/100。重要但拥挤，最容易被规模混淆。

### A2 — task-centric latent 动力学

- **人话解释：** 不重建每个像素，只预测对当前任务和动作选择真正有用的紧凑内部状态。
- **核心问题与时机：** 什么信息足以支持价值判断和规划，同时避免视频生成的巨大代价与无关视觉细节；通用 MBRL 已强，但语言条件 VLA 的 matched 对照仍少。
- **方法与证据簇：** RSSM、JEPA latent、value-aware/control-aware representation、latent transformer 与 latent MPC；邻近 [DreamerV3](https://arxiv.org/abs/2301.04104)、[TD-MPC2](https://arxiv.org/abs/2310.16828)。
- **边界与缺口：** A2 主要是 R3 紧凑 latent；若核心是显式对象/3D/接触结构则属 A3。缺口是同 planner、同数据、同计算下的 representation × control-use 因果比较。
- **决定性证据：** 相同 planner 和 rollout 预算下比较 pixel/video、task latent、structured state 与 oracle state；同时报告闭环结果、校准、长期漂移和延迟。
- **资源与廉价证伪：** 小仿真、冻结 encoder 和共享 planner 适合 2 GPUh pilot；若收益只来自更强 planner 或 privileged state，方向假设被削弱。
- **判断：** 86.5/100。机制清楚、当前配置适配度高。

### A3 — 对象、3D、几何与接触的结构化物理世界

- **人话解释：** 把世界看成持续存在的对象、表面、粒子、几何关系和接触，而不是一团不可解释的 token。
- **核心问题与时机：** 结构归纳偏置能否提升对象持久性、组合泛化、接触预测和样本效率；3D/point/slot 方法增加，但“结构化”并未自动统一语义、物理与不确定性。
- **方法与证据簇：** object slots、scene graph、point/particle dynamics、3D occupancy、contact graph；锚点包括 [Structured World Models from Human Videos](https://roboticsproceedings.org/rss19/p012.html) 与 [Object-Centric World Model for Language-Guided Manipulation](https://arxiv.org/abs/2503.06170)。
- **边界与缺口：** 仅换成 point-cloud encoder 不算；主张必须依赖可追踪实体或显式物理结构。与 A6 的区别是 A3 问“世界由什么构成”，A6 问“干预为何产生效果”。
- **决定性证据：** 在遮挡、对象数量/布局变化和未见关系组合下，验证身份一致性、关系/接触预测与闭环迁移；匹配 planner、数据和前端容量。
- **资源与廉价证伪：** 仿真可生成结构标签，但 privileged state 是大风险；先在同数据上比较结构 token 与普通 latent 的组合/OOD 增益。
- **判断：** 80.4/100。科学价值高，工程和公平比较负担中等。

### A4 — 长时记忆与部分可观测 belief world model

- **人话解释：** 当前相机看不到的东西，不代表它不存在；机器人要从长历史记住对象、动作结果和隐藏接触状态。
- **核心问题与时机：** 长上下文是否真的形成可校准的 persistent belief，还是只多塞帧；遮挡、腕部相机快速运动和多阶段任务已成为视频 WAM 的稳定失败点。
- **方法与证据簇：** recurrent belief state、retrieval memory、spatial/episodic memory、object persistence；[Mem-World](https://arxiv.org/abs/2606.18960) 是直接新证据，RSSM/Dreamer 提供基础。
- **边界与缺口：** A4 隐藏的是“当前状态”；C4 隐藏或变化的是“转移规律/系统配置”。向未来 rollout 的 B2 也不能替代对不可见当前状态的恢复。
- **决定性证据：** 设计当前画面近似相同、但历史决定真实状态的 paired tasks；匹配上下文计算量，比较短窗口、长历史、显式 memory 与 oracle state 的 belief 校准和闭环成功。
- **资源与廉价证伪：** 可用公开长轨迹/仿真回放，适合当前预算；若历史只改善视频指标而不改善真正非马尔可夫控制，方向不成立。
- **判断：** 88.1/100。上一版的重要漏项，也是当前配置下较强路线。

### A5 — 视觉—触觉—本体感觉接触世界模型

- **人话解释：** 抓稳、滑移、插入和受力往往看不出来，要让触觉、力和机器人身体状态进入动态理解。
- **核心问题与时机：** 哪些物理状态在 RGB 下不可辨识；怎样处理多传感器异步、噪声、缺失和硬件差异。2026 年已形成直接 visuo-tactile WAM 簇，但预印本比例高。
- **方法与证据簇：** tactile/force field prediction、多流 fusion、contact-aware latent dynamics、高频 residual/reflex；锚点包括 [Visuo-Tactile World Models](https://arxiv.org/abs/2602.06001) 及后续 contact-world 工作。
- **边界与缺口：** A5 的核心是观测可辨识性与跨模态 dynamics；若只在结构状态里加 contact label，仍可能属于 A3。主要缺口是跨硬件泛化和在匹配时延/数据下的独立价值。
- **决定性证据：** 在视觉相同但接触状态不同的条件下做 vision/proprio/tactile 受控消融、sensor dropout、跨材料测试，并同时测接触预测、校准和闭环成功。
- **资源与廉价证伪：** 公开同步数据可做离线 pilot；完整结论通常依赖触觉硬件或高保真接触仿真，与零真机约束不完全匹配。
- **判断：** 75.8/100。前沿清楚，但数据与硬件门槛高。

### A6 — 因果动力学与可供性世界模型

- **人话解释：** 不只预测“下一帧像什么”，还要知道哪个动作导致哪个效果、什么交互真正可行。
- **核心问题与时机：** action-conditioned prediction 可能仍依赖外观相关性；跨对象和场景泛化需要干预效果或 affordance 的不变性。
- **方法与证据簇：** affordance-space dynamics、intervention representation、controllable factors、effect prediction；[Structured World Models from Human Videos](https://roboticsproceedings.org/rss19/p012.html) 和 [HRP](https://www.roboticsproceedings.org/rss20/p068.html) 提供相邻证据。
- **边界与缺口：** 标题里写 causal 或输入 action 不等于因果识别。A3 研究实体结构，A6 必须用 intervention 或 spurious-correlation shift 检验动作—效果关系。
- **决定性证据：** 训练中让外观与效果相关，测试时翻转非因果因素；比较 intervention effect、可行动作集合和闭环迁移，不能只报 ID next-state accuracy。
- **资源与廉价证伪：** 仿真可低成本控制干预变量；若模型在相关性翻转下失败，即使生成质量高也否证主张。
- **判断：** 84.2/100。创新空间大，但必须避免“因果”标签泛化过度。

### A7 — 跨具身动作语义与 effect-space 接口

- **人话解释：** 两台机器人关节命令不同，但它们可能都在实现“向右推物体 5 cm”这个共同物理效果。
- **核心问题与时机：** 是否存在跨 morphology、DoF、控制频率与 action chunk 的共享动作语义，使人类视频和多机器人数据能服务同一 world model。
- **方法与证据簇：** latent action、inverse dynamics、effect-space/flow/particle action、robot-specific adapter；锚点包括 [LAPA](https://arxiv.org/abs/2410.11758)、[Scaling Cross-Embodiment World Models](https://arxiv.org/abs/2511.01177) 与 [Latent Policy Steering](https://arxiv.org/abs/2507.13340)。
- **边界与缺口：** A7 即使 world/policy 完全模块化也成立；C5 研究是否放进同一个联合基座。缺口是 action→effect 与 effect→native action 的双向可恢复性和负迁移。
- **决定性证据：** 留出完整 embodiment，匹配源/目标数据、adapter 容量和计算；报告零/少样本曲线、完整 source→target 迁移矩阵及物理可执行性。
- **资源与廉价证伪：** 多机器人仿真/公开异构日志可做中等成本 pilot；动作规范和同步工程较重，视觉形态 shortcut 是主要风险。
- **判断：** 82.2/100。证据正在形成，问题独立且有长期价值。

## 4. B 区：做当前决策时怎样使用世界模型？

### B1 — 可视子目标与视频计划

- **人话解释：** 先生成“接下来应该看到什么”或几个关键画面，再让 IDM/goal policy 把画面变成动作。
- **核心问题与时机：** 可视计划能否表达长时语义，同时保持物理可达和可执行；视频基座更强，但 plan-to-action gap 仍稳定存在。
- **方法与证据簇：** text-to-video plan、keyframe/subgoal generation、inverse dynamics、hierarchical execution；[UniPi](https://arxiv.org/abs/2302.00111)、[Video Language Planning](https://arxiv.org/abs/2310.10625)、[RoboDreamer](https://proceedings.mlr.press/v235/zhou24f.html)。
- **边界与缺口：** B1 生成“想达到的未来”，不要求给定候选低层动作；若显式输入并比较候选动作后果则为 B2。
- **决定性证据：** 匹配 controller、延迟和数据，测 plan feasibility、plan-to-action error、重规划频率与闭环成功；oracle/shuffled/no-plan 对照分离规划贡献。
- **资源与廉价证伪：** 先对现有生成计划做 kinematic/contact 审计；若同一 controller 无法执行，没必要训练更大视频模型。
- **判断：** 71.3/100。直观但拥挤，物理执行是硬门槛。

### B2 — 动作条件反事实规划与 MPC

- **人话解释：** 把若干候选动作放进 learned world 里“先试一遍”，选择结果最好的一组，并在新观测到来后重规划。
- **核心问题与时机：** learned rollout 能否在实时预算内保持 action sensitivity、校准和长时稳定；大模型提升表观质量，但候选数和延迟快速膨胀。
- **方法与证据簇：** action-conditioned video/latent rollout、CEM/MPPI/beam search、trajectory optimization；[Visual Foresight](https://arxiv.org/abs/1812.00568)、[iVideoGPT](https://arxiv.org/abs/2405.15223)、[V-JEPA 2](https://arxiv.org/abs/2506.09985)。
- **边界与缺口：** 必须有 action-conditioned rollout；纯 value 网络属于 B3。主要缺口是 matched-latency 的闭环价值和 policy 对模型错误的利用。
- **决定性证据：** 同 wall-clock/FLOPs/candidate budget 比 direct VLA、model-free search、oracle simulator；报告成功、延迟、rollout drift、OOD calibration。
- **资源与廉价证伪：** 少候选短 horizon 即可测出 action ranking 是否稳定；若轻微动作变化未被模型区分，MPC 不值得扩展。
- **判断：** 74.7/100。成熟高竞争，当前预算只适合窄验证。

### B3 — world-model reward、value 与 critic

- **人话解释：** 不一定搜索完整动作序列，而是根据预测未来给某个状态、动作或轨迹打分。
- **核心问题与时机：** semantic progress、physical feasibility 与安全代价能否被同一/组合 critic 正确评价；VLM reward 很方便，却可能忽略接触和不可逆失败。
- **方法与证据簇：** video likelihood reward、VLM reward、success/value head、future-conditioned critic、model ensemble；[VIPER](https://arxiv.org/abs/2305.14343) 与 [Cosmos Policy](https://arxiv.org/abs/2601.16163) 是代表邻域。
- **边界与缺口：** B3 的评价单位是一次决策或轨迹；整套 policy 跨 episode 排名属于 B4；危险覆盖与拒答属于 B5。
- **决定性证据：** matched observation/compute 下与 VLM-only judge、model-free value、oracle reward 比较 action/trajectory ranking、闭环收益和校准。
- **资源与廉价证伪：** 现有日志即可做 paired ranking；若 critic 只复现语义成功、系统性漏掉物理失败，则路线需收缩。
- **判断：** 87.1/100。资源适配好，但需要强物理负对照。

### B4 — 虚拟策略评测与排序

- **人话解释：** 在不反复跑真机的情况下，用 world model 判断哪套 VLA、哪个 checkpoint 或哪种 policy 更好。
- **核心问题与时机：** world rollout 能否保持真实环境中的 policy ranking，并在新策略/OOD 动作上知道自己不可信；策略迭代速度已快于真实评测。
- **方法与证据簇：** paired rollout、Monte Carlo policy evaluation、VLM/metric judge、calibrated ranking；[WorldEval](https://arxiv.org/abs/2505.19017)、[WorldGym](https://arxiv.org/abs/2506.00613)、[WorldArena](https://arxiv.org/abs/2602.08971)。
- **边界与缺口：** B4 是“WM 评价 policy”；D1 是“外部协议评价 WM”，箭头相反。主要缺口是同初态、跨策略族与 OOD 的排序/绝对价值校准。
- **决定性证据：** paired initial states 上报告 Kendall/Spearman、Brier/ECE、coverage–risk、最坏子组与置信区间；感知指标不能替代 policy agreement。
- **资源与廉价证伪：** 可复用 checkpoint 和日志，低至中算力；若轻微 policy shift 就导致排序翻转，方向可快速被否证。
- **判断：** 94.5/100。当前资源下最稳健的优先审阅项，但仍未被选中。

### B5 — 失败预警、保守控制与选择性自治

- **人话解释：** world model 不只说“可能发生什么”，还要知道自己何时不可靠，并据此减速、换安全动作、拒绝或求助。
- **核心问题与时机：** epistemic/aleatoric uncertainty 如何沿 rollout 传播，并转化为真正降低危险而非“什么都不做”的决策。
- **方法与证据簇：** ensemble、conformal/OOD calibration、risk-sensitive planning、reachability safety filter、selective autonomy；[Uncertainty-aware Latent Safety Filters](https://proceedings.mlr.press/v305/seo25a.html) 提供直接证据，SafeDreamer 等提供邻域。
- **边界与缺口：** 若 uncertainty 只测量准确度而不改变动作，归 B4/D1；B5 的终点必须是 risk–success Pareto、危险覆盖或干预质量。
- **决定性证据：** 固定同一 WM，只替换决策规则；在 policy/task/action shift 和尾部失败上报告危险 recall/FNR、CVaR、coverage–risk、任务成功与拒绝率。
- **资源与廉价证伪：** 公开仿真/现有 rollout 可做低中成本 pilot；共同错误和过度保守是主要风险。
- **判断：** 91.8/100。高影响且适合离线验证。

### B6 — 主动感知与信息获取

- **人话解释：** 看不清或不确定时，机器人先决定该换哪个视角、靠近哪里、触摸什么，再决定任务动作。
- **核心问题与时机：** world model 能否估计一个 sensing action 会减少多少任务相关不确定性，而不是被动等待更多观测。
- **方法与证据簇：** belief-space planning、next-best-view、information gain、active localization/exploration；[WoMAP](https://proceedings.mlr.press/v305/yin25b.html) 是直接 world-model active perception 锚点。
- **边界与缺口：** B6 的信息动作服务当前 episode；C3 主动采数据服务未来 policy 学习。B2 优化任务结果，B6 的动作价值首先来自减少不确定性。
- **决定性证据：** 匹配额外观测数、移动距离、延迟和总动作预算，与固定/随机/被动多视角/oracle 视角比较 belief 校准和任务成功。
- **资源与廉价证伪：** 仿真相机和遮挡任务即可强证伪，算力较低；若收益仅来自“多看了几帧”，不构成主动感知贡献。
- **判断：** 86.9/100。初版遗漏、科学合同干净、仿真可行。

## 5. C 区：怎样用世界模型训练和适应策略？

### C1 — WAM 合成轨迹与数据引擎

- **人话解释：** 用 world model 生成新的成功、失败、恢复或反事实轨迹，形成离线数据后再训练 VLA。
- **核心问题与时机：** synthetic trajectory 的视觉合理性是否能转化为动作有效性和 held-out 控制收益；数据稀缺使路线重要，但非 WM 数据引擎已是强对手。
- **方法与证据簇：** video rollout + IDM/LAM、counterfactual generation、filter/reweight、synthetic recovery data；[DreamGen](https://arxiv.org/abs/2505.12705) 是代表，ROSIE/MimicGen/RoboGen 是必要非 WM 对照。
- **边界与缺口：** 输出是一个离线训练集；若 policy 直接在 learned world 中优化则为 C2。缺口是 effective sample yield、action validity、污染和等预算边际价值。
- **决定性证据：** 固定真实数据、policy training token、模型与算力，比较 WM data、非 WM 合成、普通增强和纯真实；报告每个有效样本成本。
- **资源与廉价证伪：** 只加入小批经过/未经审计的合成样本；若收益不超过增强/重采样，停止扩大生成。
- **判断：** 79.0/100。规模价值高，完整闭环较吃资源。

### C2 — imagined VLA 后训练与 model-based RL

- **人话解释：** 让 VLA 在 learned world 中练习和更新参数，再回真实或高保真环境验收。
- **核心问题与时机：** imagined experience 能否提高真实 policy，而不是让 policy 学会利用 world-model error；通用 MBRL 成熟，直接 VLA × video world 仍新。
- **方法与证据簇：** Dreamer/MBPO/Dyna、offline model-based RL、conservative imagination、VLM reward；[DayDreamer](https://arxiv.org/abs/2206.14176)、[DreamerV3](https://arxiv.org/abs/2301.04104) 与 RehearseVLA 类工作。
- **边界与缺口：** C2 更新 policy；B2 只在执行时规划，C1 只生成数据。核心缺口是 policy shift 后的 world calibration 和 exploitation audit。
- **决定性证据：** matched real interactions/FLOPs 下比较 offline/model-free update；把模型内高回报轨迹回放到 ground-truth simulator，报告虚假高回报率和多种子置信区间。
- **资源与廉价证伪：** 小任务、冻结 WM、少量 update 即可审计 exploitation；完整主结论多半超出 8 GPUh。
- **判断：** 80.5/100。高风险高回报，当前适合窄证伪。

### C3 — 主动数据获取与 world-model curriculum

- **人话解释：** 不只是加工已有数据，而是让 world model 决定下一条昂贵轨迹、扰动或示范最值得在哪里采。
- **核心问题与时机：** 在固定 real/sim/human budget 下，怎样最大化最终 VLA 学习增益，同时避免追逐随机噪声或危险盲区。
- **方法与证据簇：** disagreement exploration、information gain、coverage curriculum、failure/recovery acquisition；[Self-Supervised Exploration via Disagreement](https://proceedings.mlr.press/v97/pathak19a.html) 与 [Plan2Explore](https://proceedings.mlr.press/v119/sekar20a.html) 是基础邻域。
- **边界与缺口：** B6 为当前任务获取信息；C3 的 acquisition action 是为未来学习收集数据。C1 生成合成数据，C3 决定真实/仿真采集位置。
- **决定性证据：** 固定总交互和人类时间，比较随机、当前 policy、uncertainty-only、coverage/curriculum 与 oracle；报告 held-out learning curve 和单位真实交互增益。
- **资源与廉价证伪：** 仿真中可中等成本完成；若模型只选 aleatoric noise 或奇异状态，主动采数机制被否证。
- **判断：** 85.9/100。直接交集稀疏，问题价值与可验证性较好。

### C4 — 部署时系统识别与快速适应

- **人话解释：** 机器人到新现场后先用少量安全交互判断相机、摩擦、负载、延迟和身体配置，再执行任务。
- **核心问题与时机：** 能否从短历史辨识 hidden dynamics context，并区分视觉域偏移、系统变化和策略变化；新 VLA 往往默认固定执行配置。
- **方法与证据簇：** in-context system identification、context encoder、adaptive dynamics、belief over parameters；[In-Context World Modeling](https://arxiv.org/abs/2606.26025) 是直接新证据，adaptive control/model-based adaptation 提供成熟基础。
- **边界与缺口：** A4 隐藏的是当前 state，C4 隐藏的是 transition/configuration；C6 处理长期任务序列，C4 处理秒到分钟的局部适应。
- **决定性证据：** 在相机、质量、摩擦、延迟或 morphology 受控变化下，固定基座和 probe budget，报告 success-vs-probe、恢复速度、辨识校准与安全探测成本。
- **资源与廉价证伪：** 仿真变化可低中成本系统控制；若 context 改善预测却不改善闭环，或主动探测本身不安全，则收缩方向。
- **判断：** 89.1/100。新且独立，适合当前配置的仿真 pilot。

### C5 — 联合 World–Language–Action 基座

- **人话解释：** 用同一个大模型共同学习未来视觉、语言语义和机器人动作，希望三者互相帮助。
- **核心问题与时机：** 联合目标是否产生可归因协同，而非只是数据、参数和训练 token 更多；这是当前最热门也最昂贵的路线。
- **方法与证据簇：** shared backbone + heads、joint video/action token、interleaved/denoising sequences；[GR-2](https://arxiv.org/abs/2410.06158)、[Unified World Models](https://www.roboticsproceedings.org/rss21/p015.html)、[DreamZero](https://arxiv.org/abs/2602.15922)、[Cosmos Policy](https://arxiv.org/abs/2601.16163)。
- **边界与缺口：** C5 是一次性/静态联合训练；C6 要求随 policy 数据分布长期更新。A7 即使模块化也研究跨具身接口。
- **决定性证据：** 同数据、参数、训练 token、优化步和推理预算做无 world objective / joint objective、shared/separate backbone 对照，并检验闭环相关性。
- **资源与廉价证伪：** 只能在公开 checkpoint 上做冻结/低秩小实验；从头训练明显超预算，且小实验不能外推 foundation-scale。
- **判断：** 66.3/100。远期影响高，当前适配最低。

### C6 — 持续学习与 policy–world 长期共适应

- **人话解释：** 机器人连续遇到新任务和环境，world model 与 policy 长期更新，同时不能遗忘旧技能或一起学会错误。
- **核心问题与时机：** stability–plasticity、replay、模型/策略互相造成的分布漂移，以及何时冻结、交替或共同更新。
- **方法与证据簇：** continual world models、selective replay、online planning、alternating policy–WM updates；[Continual-Dreamer](https://proceedings.mlr.press/v232/kessler23a.html)、[Planning with Online World Models](https://proceedings.mlr.press/v267/liu25p.html)、[DRAGO](https://proceedings.mlr.press/v267/fu25f.html)。
- **边界与缺口：** C5 是联合结构/目标，C6 是按时间顺序持续变化；C4 是一次局部快速适应。直接 VLA-WAM 共适应证据仍低密度。
- **决定性证据：** 预定义任务/动力学流并周期回访旧任务；匹配 memory、交互和 FLOPs，报告 forward/backward transfer、forgetting、AUC 与 WM 校准漂移。
- **资源与廉价证伪：** 可信主结论需长序列、多 seed 和大量 checkpoint，通常超出 8 GPUh；小规模可先测共同漂移是否立即出现。
- **判断：** 76.0/100。高潜力、低成熟、资源负担重。

## 6. D 区：怎样证明 WAM 真的有功能价值？

### D1 — WAM 功能评测与物理可执行性基准

- **人话解释：** 把 world model 本身放上考场：它是否真的响应动作、保持对象、遵守接触和物理，并能支持后续决策，而不只是视频看起来漂亮。
- **核心问题与时机：** FVD/PSNR/人工观感与控制价值经常脱钩；大量 WAM 出现后，需要统一的功能协议决定模型是否可用。
- **方法与证据簇：** action sensitivity、inverse action recovery、paired rollout、physical consistency、policy-ranking agreement、functional task suite；[Action-conditioned Benchmarking](https://arxiv.org/abs/1910.02564)、[WorldArena](https://arxiv.org/abs/2602.08971) 与 RoboWM-Bench 类工作。
- **边界与缺口：** D1 是“外部基准评价 WM”；B4 是“用 WM 评价 policy”。不能只因为两者都出现 ranking 就合并。
- **决定性证据：** 同一模型同时测模型层、策略层和环境层；检验 action sensitivity、长期漂移、物理/接触约束、OOD calibration 以及功能指标对真实控制的预测效度。
- **资源与廉价证伪：** 以公开 checkpoint 和日志为主，最符合当前预算；风险是 benchmark 被快速过拟合、任务覆盖窄或使用特权 simulator state。
- **判断：** 90.9/100。基础设施型、高可行性方向，和 B4 同为优先审阅项。

## 7. 容易混淆的边界

| 容易混淆 | 判定问题 |
|---|---|
| A1 vs A2 | 只把 predictive feature 交给 policy 是 A1；用 action-conditioned latent rollout 做决策是 A2 |
| A2 vs A3 | 主状态是压缩任务 latent 属 A2；主张依赖可追踪对象/几何/接触结构属 A3 |
| A3 vs A6 | “世界由哪些实体组成”是 A3；“哪个干预导致哪个效果”是 A6 |
| A4 vs C4 | 隐藏当前状态是 A4；隐藏或变化的转移规律/系统配置是 C4 |
| A7 vs C5 | 动作接口能否跨身体共享是 A7；world/action 是否联合训练是 C5 |
| B1 vs B2 | 生成想达到的未来是 B1；给定候选动作预测会发生什么是 B2 |
| B3 vs B4 vs B5 | 分别评价单次决策、整套 policy、危险与可信度并改变控制 |
| B6 vs C3 | 当前 episode 为了看清楚而探索是 B6；为了未来训练收集数据是 C3 |
| C1 vs C2 | imagined 结果写入离线数据集是 C1；policy 在 learned world 中被优化是 C2 |
| C5 vs C6 | 静态联合结构/目标是 C5；随时间和 policy 分布持续更新是 C6 |
| B4 vs D1 | B4 用 WM 评 policy；D1 用外部协议评 WM |

以下内容仍是横向轴，不单独算母方向：长时序、OOD、sim-to-real、实时加速、能耗、manipulation/navigation/humanoid 等 embodiment，及某个 encoder/diffusion/transformer 组件。它们应在选定主方向后作为压力测试或实现选择。

## 8. 选择导航，但不替用户选择

如果你的兴趣是：

- **让模型“记得住、看得懂物理”**：先看 A3、A4、A5、A6。
- **让不同机器人共享世界知识**：先看 A7，必要时再看 C5。
- **让 world model 直接改善当前决策**：B1–B3；若关心不确定信息，B5/B6。
- **降低真实评测成本、提高可靠性**：B4、B5、D1。
- **让 VLA 从 imagined experience 学习**：C1、C2、C3。
- **让机器人到新环境后继续适应**：C4、C6。
- **做大一统 foundation model**：C5，但当前资源不匹配从头训练。

在当前 2 GPUh pilot、8 GPUh 总预算、无真机、无已配置 GPU backend 的约束下，优先让人审阅的五条是：

1. B4 虚拟策略评测与排序；
2. B5 失败预警、保守控制与选择性自治；
3. D1 WAM 功能评测与物理可执行性基准；
4. C4 部署时系统识别与快速适应；
5. A4 长时记忆与部分可观测 belief world model。

这个排序仍只是“值得先读”，不是系统选择。用户也可以先选一个上层区域（A/B/C/D），要求再做一轮区域内细化，而不必现在就从 20 条里定一条。

## 9. 人工检查点

```text
research.selected_macro_direction = null
idea-discovery = blocked: awaiting human macro-direction selection
```

下一步允许的动作只有：选择 A1–A7、B1–B6、C1–C6 或 D1；选择一个上层区域继续细分；要求修改/合并某些边界；或停止。收到明确选择前，不生成具体 Idea。
