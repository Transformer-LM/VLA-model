# VLA × WAM 方向扩展：文献地图补充

> 日期：2026-08-06  
> 目的：为 6→20 条方向拆分补充证据；不进行具体 Idea 查新。  
> 主文献地图：[LITERATURE_MAP.md](./LITERATURE_MAP.md)

## 1. 为什么需要补检索

初版围绕 video-generative WAM、latent dynamics、MBRL、evaluator、数据引擎和 joint world-action model 建图，充分覆盖“world model 的主要用途”，但对以下正交轴深度不足：

- 当前观测不充分时的长期记忆与 belief；
- 对象持续性、因果干预与 affordance；
- 视觉之外的触觉、力和本体感觉动态；
- 主动感知与主动数据获取的区别；
- 跨机器人 action/effect 语义；
- 部署时 system identification 与长期 continual co-adaptation；
- “评价 world model”与“用 world model 评价 policy”的反向关系。

## 2. 实际检索轨迹与故障

### 多数据库补搜

通过项目 `paper-search` 同时查询 arXiv、DBLP、OpenAlex、OpenReview、Semantic Scholar 和 Crossref，窗口 2018–2026，每源上限 6：

```text
robot world model long horizon memory partial observability active perception
causal affordance object-centric 3D world model robot manipulation
cross embodiment latent action world model robot policy online adaptation
uncertainty calibrated world model safe robot control
```

本次全源命令在 184 秒达到执行上限，退出码 124，且未返回可审计的部分结果。因此不把它计作成功来源，也没有把可能存在于进程中的标题写成证据。

### 降级后的原始来源核验

随后使用 arXiv、PMLR、RSS proceedings 和官方会议页面做窄检索/直接打开，核验标题、年份、摘要与方向边界。主要查询：

```text
robot world model long-term memory partial observability persistent belief
world model active perception robot information gathering
cross-embodiment world model latent action robot policy
continual online world model reinforcement learning
visuo-tactile world model robot contact
structured world models human videos affordance robot
safe world model uncertainty visual control robot
```

这次补充用于证明“存在工作簇”和界定成熟度，不声称穷尽文献；2026 预印本统一降级为 E2/E3，而非视为已复现事实。

## 3. 新增工作簇

### 3.1 长时记忆与部分可观测 belief

- [Mem-World: Memory-Augmented Action-Conditioned World Models for Persistent Robot Manipulation](https://arxiv.org/abs/2606.18960)，arXiv:2606.18960，2026 预印本：直接把频繁遮挡和腕部相机运动造成的历史遗忘定义为 persistent world modeling 问题，并以几何索引记忆检索历史。
- Dreamer/RSSM 系列提供 recurrent belief 的基础，但其常用环境不能自动证明开放场景对象持久性。
- 初版已核验的 DreamZero 短记忆限制与 V-JEPA 2 长 horizon 搜索/漂移问题提供反向证据。

**密度判断：** 通用 recurrent belief 高；直接 VLA/WAM persistent memory 中等且 2026 增长。足以独立为方向，但必须用真正非马尔可夫任务证明历史控制价值。

### 3.2 对象中心、结构化物理与因果可供性

- [Structured World Models from Human Videos](https://roboticsproceedings.org/rss19/p012.html)，RSS 2023：用人类视频学习 affordance-space world model，并以少量机器人交互适配。
- [Object-Centric World Model for Language-Guided Manipulation](https://arxiv.org/abs/2503.06170)，arXiv:2503.06170，2025 预印本：在对象中心 latent 中做语言条件未来预测。
- [HRP: Human Affordances for Robotic Pre-training](https://www.roboticsproceedings.org/rss20/p068.html)，RSS 2024：属于 affordance 预训练邻域，说明对象/接触 affordance 与跨形态控制的连接。

**密度判断：** object/3D/particle dynamics 中高，显式因果干预 × VLA-WAM 的完整交集偏低。结构表征与因果效应必须拆开验证：对象 token 本身不是因果证据。

### 3.3 视觉—触觉—本体感觉接触世界

- [Visuo-Tactile World Models](https://arxiv.org/abs/2602.06001)，arXiv:2602.06001，2026 预印本：以触觉补充视觉下不可辨识的接触状态，并连接到 planning。
- [OmniVTA](https://arxiv.org/abs/2603.19201)、[ContactWorld](https://arxiv.org/abs/2606.13877)、[ViTacWorld](https://arxiv.org/abs/2607.22530) 表明 2026 年已形成新簇，但目前集中于特定触觉硬件、数据和接触任务。
- 初版已核验的 ICCV 2025 multimodal action-conditioned video simulation 提供更早的多传感器动态证据。

**密度判断：** 新兴中等，预印本占比高。足以列为前沿母方向，但当前零真机配置只支持公开数据或仿真 pilot。

### 3.4 跨具身动作语义与 effect-space

- [Latent Action Pretraining from Videos](https://arxiv.org/abs/2410.11758)，ICLR 2025 / arXiv:2410.11758：无真实动作标签的视频先学习 discrete latent action，再用少量机器人数据映射到 native action。
- [Scaling Cross-Embodiment World Models for Dexterous Manipulation](https://arxiv.org/abs/2511.01177)，arXiv:2511.01177，2025 预印本：用共享 particle displacement 表示不同手/机器人动作效果。
- [Latent Policy Steering with Embodiment-Agnostic Pretrained World Models](https://arxiv.org/abs/2507.13340)，arXiv:2507.13340，2025 预印本：用 optical flow 作为跨具身动作表示并做 world-model latent search。
- UWM、DreamGen 与 LAPA 同时暴露 inverse/latent action 到 native control 的 executability gap。

**密度判断：** latent action 与跨具身 VLA 中等且增长；直接用可迁移 world dynamics 统一动作接口仍中低。必须做完整 held-out embodiment，而非只在共同训练机器人上报平均值。

### 3.5 主动感知与信息获取

- [WoMAP: World Models for Embodied Open-Vocabulary Object Localization](https://proceedings.mlr.press/v305/yin25b.html)，CoRL 2025：用 latent world model grounding 高层探索动作，属于直接 world-model active perception 证据。
- 传统 POMDP、active vision 和 next-best-view 文献很密，但不能自动等同于 VLA × WAM。

**密度判断：** 通用领域高，直接交集低到中等。核心 endpoint 应是相同感知/移动预算下 belief 校准和任务成功，而非单纯“多看几帧”。

### 3.6 主动数据获取与 curriculum

- [Self-Supervised Exploration via Disagreement](https://proceedings.mlr.press/v97/pathak19a.html)，ICML 2019：用动态模型 disagreement 指导探索。
- [Plan2Explore](https://proceedings.mlr.press/v119/sekar20a.html)，ICML 2020：在 world model 中规划预期 novelty，以少任务监督适配下游任务。
- RoboCat、自主真实机器人 RL 和 synthetic-data engine 是邻域，但不都属于 learned WAM。

**密度判断：** 通用主动探索中高；用 VLA 弱点与 WAM uncertainty 驱动真实采数的交集低。与主动感知的关键差异是 acquisition 服务未来训练，而不是当前 episode。

### 3.7 部署时 system identification 与快速适应

- [In-Context World Modeling for Robotic Control](https://arxiv.org/abs/2606.26025)，arXiv:2606.26025，2026 预印本：从短时、自生成、任务无关交互推断当前系统配置，不更新参数即适应新设置。
- adaptive control、context-aware dynamics 和 Rapid Motor Adaptation 等提供成熟邻域，但多数不是 VLA-WAM。

**密度判断：** 通用系统识别高，直接 VLA-WAM 低到中等。需要把 hidden state memory 与 hidden transition/configuration 严格分开。

### 3.8 持续 world model 与 policy–world 共适应

- [The Effectiveness of World Models for Continual Reinforcement Learning](https://proceedings.mlr.press/v232/kessler23a.html)，CoLLAs 2023：研究 replay、遗忘和迁移并形成 Continual-Dreamer。
- [Continual Reinforcement Learning by Planning with Online World Models](https://proceedings.mlr.press/v267/liu25p.html)，ICML 2025：在线更新 world dynamics 并用 MPC 解决顺序任务。
- [Knowledge Retention in Continual Model-Based Reinforcement Learning](https://proceedings.mlr.press/v267/fu25f.html)，ICML 2025：以 synthetic rehearsal 和 exploration 保留 world-model 知识。

**密度判断：** 通用 continual MBRL 中等；直接大型 VLA-WAM 共适应稀疏。必须报告整个任务序列、遗忘与校准漂移，而非最后一个任务。

### 3.9 不确定性感知的安全与选择性自治

- [Uncertainty-aware Latent Safety Filters for Avoiding Out-of-Distribution Failures](https://proceedings.mlr.press/v305/seo25a.html)，CoRL 2025：用 world-model epistemic uncertainty 和 conformal calibration 扩展 latent safety filter。
- PETS、MOPO、MOReL、COMBO、SafeDreamer 构成通用概率/保守 MBRL 邻域。
- 初版 WorldGym 的 OOD action 高估为直接反例：相对 policy ranking 可用不等于新动作安全。

**密度判断：** 通用 MBRL 高，高维生成式 WAM/VLA 交集低到中等。只有 uncertainty 真正改变动作并改善 risk–success Pareto 时才独立成方向。

### 3.10 WAM 功能评测与物理可执行性

- [Action-conditioned Benchmarking of Robotic Video Prediction Models](https://arxiv.org/abs/1910.02564)，ICRA 2020：表明感知质量与动作可辨识信息可能脱钩。
- [WorldArena](https://arxiv.org/abs/2602.08971) 与 RoboWM-Bench 类工作把对象持久性、空间、接触和可执行性提升为独立评测对象。
- WorldEval/WorldGym 则属于反向用途：使用 WAM 评测 policy，而非评测 WAM 本身。

**密度判断：** 中等且快速增长。该簇足以独立为基础设施方向，主要风险是 benchmark 任务窄、privileged state 与后续过拟合。

## 4. 由证据支持的拆分结论

以下拆分有不同 endpoint，因此不是机械加标签：

- 单次动作/轨迹 critic、整套 policy 排名、安全干预分别对应 decision quality、policy agreement、risk–success；
- visual subgoal 与 action-conditioned MPC 分别回答“想达到什么未来”和“某动作会造成什么未来”；
- predictive pretraining、synthetic data、imagined policy update 的输出分别是 feature、dataset、更新后的 policy；
- memory belief、system identification、continual adaptation 的时间对象分别是隐藏当前状态、当前转移规律、长期任务流；
- active perception 与 active acquisition 分别服务当前决策和未来学习；
- joint foundation model 与 continual co-adaptation 分别是静态训练结构和动态更新制度；
- policy evaluation 与 WAM benchmark 的评价箭头相反。

## 5. 仍然不能升格为独立母方向的内容

- diffusion、transformer、JEPA、scene graph、particle、object slot：是方法/表征家族；
- ensemble、conformal、uncertainty：只有绑定安全决策 endpoint 才形成 B5；
- IDM/LAM：通常是 B1/C1 的组件，只有 action/effect 对齐为主张时归 A7；
- long horizon、OOD、sim-to-real、实时 serving、能耗：横向压力测试；
- manipulation、navigation、humanoid、legged：具身/任务分层，不与科学用途混排。

## 6. 证据盲区

- 新增 A4/A5/C4 等路线高度依赖 2026 预印本，尚缺跨团队长期复现。
- 多模态接触、跨具身和真实部署适应最终需要硬件证据，当前配置只能做条件性仿真/离线判断。
- 主动数据获取和长期共适应的可信结果需要多轮交互及多 checkpoint，完整主结论可能超过 8 GPUh。
- social/multi-agent world models、human-in-the-loop WAM、能耗/实时 serving 和 navigation/humanoid 垂直路线尚未达到与 manipulation 同等深度；它们保留为后续补图而非本轮第 21 条。
- 全源 paper-search 补搜超时；窄检索提升了可信度，但降低了数据库覆盖广度。
