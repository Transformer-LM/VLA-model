# VLA × WAM 扩展文献地图

**Run ID：** `20260806-vla-wam-expanded-field-map`  
**检索截止：** 2026-08-06  
**用途：** 支撑 16 条交叉母方向的边界与证据密度判断；不用于生成具体 Idea。

## 1. 检索与去重审计

- 三路并行检索分别覆盖：表征/潜在动作/结构/记忆，规划/主动感知/critic/评测/安全，数据生成/想象训练/共演化/联合模型/跨具身/部署适应；合计 44 个定向 query family，另以 3 组 arXiv multi-query 和逐题名检索回查。
- 来源优先级为论文原页与正式 proceedings：arXiv、PMLR、RSS、CVF、NeurIPS、ICLR、ICML、IROS；项目页只用于补充方法接口，不承担强结论。
- `papers/` 与 `literature/` 未发现本地 PDF，因此本轮没有本地全文贡献。Semantic Scholar 多次 429；OpenAlex 出现 504/SSL EOF；DBLP 出现 500/SSL EOF；OpenReview 广搜召回为 0。所有纳入表的承重条目均另回到原始论文或正式会议页核验。
- 三批主线 arXiv 检索分别得到 32、40、48 条原始命中，对应 27、34、41 条批内去重记录；最终结合三路补查、旧版 29+7 条交叉地图与题名核验，形成下方 **69 条全局去重核心/关键邻域条目**。
- `World-Env` 与 CVPR 2026 的 `RehearseVLA` 是同一工作的版本/题名变化，只计一次。

证据记号：**E1**＝正式发表原文；**E2**＝可核验预印本。耦合记号：**强**＝同时有 VLA/语言策略端与 learned dynamics 的承重连接；**邻域**＝缺语言端、缺 forward rollout 或只覆盖相邻机制。`强/邻域` 表示对该母方向是核心锚点，但按最严格 VLA×可 rollout-WM 定义仍有一侧不足。

## 2. 世界表征、潜在动作、结构与记忆（P01–P19）

| ID | 论文（作者；年份/venue） | 主方向 | 耦合与作用 | 等级 | 主要边界 |
|---|---|---|---|---|---|
| P01 | [GR-1: Unleashing Large-Scale Video Generative Pre-training for Visual Robot Manipulation](https://arxiv.org/abs/2312.13139)（Hongtao Wu et al.; 2023, arXiv） | H1/H14 | 联合未来图像与动作预测，视频预训练进入语言策略 | 强/E2 | world objective、额外视频和规模未完全解耦 |
| P02 | [GR-2: A Generative Video-Language-Action Model with Web-Scale Knowledge](https://arxiv.org/abs/2410.06158)（Chi-Lam Cheang et al.; 2024, arXiv） | H1/H14 | 先学视频动态，再联合视频与动作生成 | 强/E2 | 私有 38M 视频与大算力造成 scale confound |
| P03 | [Robotic VLA Benefits from Joint Learning with Motion Image Diffusion](https://arxiv.org/abs/2512.18007)（Yu Fang et al.; 2025, arXiv） | H1 | optical-flow/motion future head 作训练辅助，推理可移除 | 强/E2 | 仍需 matched capacity 与静态辅助对照 |
| P04 | [DUST: Dual-Stream Diffusion for World-Model Augmented VLA](https://arxiv.org/abs/2510.27607)（John Won et al.; 2025, arXiv） | H1/H14 | 视觉状态流与动作流联合 diffusion/flow | 强/E2 | 架构、损失与无动作视频预训练同时改变 |
| P05 | [World-Language-Action Model for Unified World Modeling, Language Reasoning, and Action Synthesis](https://arxiv.org/abs/2606.05979)（Yi Yang et al.; 2026, arXiv） | H1/H14/H15 | World Expert 预测语义/物理 next state，并影响 Action Expert | 强/E2 | 极新；world path 可关闭，因果承重需更强切断消融 |
| P06 | [Latent Action Pretraining from Videos](https://arxiv.org/abs/2410.11758)（Seonghyeon Ye et al.; 2025, ICLR） | H2/H11/H15 | 从无标签视频学习离散 latent action，再落到 VLA 动作 | 强（H2）/E1 | 不是可独立 rollout 的 forward WM；仍需本体动作桥 |
| P07 | [UniVLA: Learning to Act Anywhere with Task-centric Latent Actions](https://arxiv.org/abs/2505.06111)（Qingwen Bu et al.; 2025, RSS） | H2/H15 | 语言约束 latent action，连接人类视频与多本体 VLA | 强（H2）/E1 | latent action 可辨识性与 native action 因果语义未保证 |
| P08 | [Joint-Aligned Latent Action: Towards Scalable VLA Pretraining in the Wild](https://arxiv.org/abs/2602.21736)（Hao Luo et al.; 2026, CVPR） | H2/H11/H15 | predictive action embedding 同时对齐 inverse dynamics 与真实动作 | 邻域/E1 | 刻意绕开完整未来世界重建 |
| P09 | [CLAM: Continuous Latent Action Models for Robot Learning from Unlabeled Demonstrations](https://arxiv.org/abs/2505.04999)（Anthony Liang et al.; 2026, IROS） | H2/H11/H15 | 自监督 dynamics prediction 推断连续 latent action，小量 play data 解码 | 强/邻域/E1 | 无语言端；每个 embodiment 仍需动作桥 |
| P10 | [DiLA: Disentangled Latent Action World Models](https://arxiv.org/abs/2605.15725)（Tianqiu Zhang et al.; 2026, arXiv） | H2/H15 | content/structure disentanglement 与 latent action 共演化 | 邻域/E2 | 未给直接 VLA 下游，主要证 action transfer/visual planning |
| P11 | [Unified World Models: Coupling Video and Action Diffusion](https://arxiv.org/abs/2504.02792)（Chuning Zhu et al.; 2025, RSS） | H2/H11/H14/H15 | 统一 forward/inverse/video/action diffusion，利用 action-free video | 邻域/E1 | 语言不是核心接口 |
| P12 | [3D-VLA: A 3D Vision-Language-Action Generative World Model](https://arxiv.org/abs/2403.09631)（Haoyu Zhen et al.; 2024, arXiv） | H3/H5/H14 | 3D 感知、语言、动作与目标图像/点云生成统一 | 强/邻域/E2 | 更接近 3D goal proposal；严格候选动作动态较弱 |
| P13 | [GEM-4D: Geometry-Enhanced Video World Models for Robot Manipulation](https://arxiv.org/abs/2605.22882)（Kaichen Zhou et al.; 2026, arXiv） | H3/H5 | 4D correspondence 约束视频 rollout，再由 IDM 执行动作 | 强/邻域/E2 | 语言端不是核心；几何教师与 world objective 混杂 |
| P14 | [Tactile-WAM: Touch-Aware World Action Model](https://arxiv.org/abs/2606.26663)（Siyu Wu et al.; 2026, arXiv） | H3/H14 | 联合预测视觉/触觉未来，action query 消费 predicted touch | 强/邻域/E2 | 语言接口不明；仅单一触觉体系且无独立复现 |
| P15 | [FeelWorld: Visuo-Tactile World Model for Hierarchical Contact Prediction and Planning](https://arxiv.org/abs/2607.24267)（Wenxuan Ma et al.; 2026, arXiv） | H3/H6 | 显式 contact、3D tactile latent、slip state，并作 CEM planning | 邻域/E2 | 无 VLA；任务与传感器范围窄 |
| P16 | [TACO: Tactile World Model as a Self-Corrector for Scalable VLA Post-Training](https://arxiv.org/abs/2607.02840)（Shengbang Liu et al.; 2026, arXiv） | H3/H10/H12/H13 | 触觉 WM 识别失败邻域、想象局部修正并后训练 VLA | 强/E2 | 特殊硬件与同步数据；任务局部且预印本很新 |
| P17 | [Recursive Belief Vision Language Action Models](https://arxiv.org/abs/2602.20659)（Vaidehi Bagaria et al.; 2026, arXiv） | H4 | world-model objective 学 action-conditioned latent belief，驱动 VLA | 强/E2 | 任务/基线范围有限，belief 校准未充分验证 |
| P18 | [ReMem-VLA: Empowering VLA with Memory via Dual-Level Recurrent Queries](https://arxiv.org/abs/2603.12942)（Hang Li et al.; 2026, arXiv） | H4 | recurrent memory + past-observation prediction 辅助 action policy | 邻域/E2 | 预测过去而非 future dynamics；可能只是更强记忆模块 |
| P19 | [Mem-World: Memory-Augmented Action-Conditioned World Models](https://arxiv.org/abs/2606.18960)（Zirui Zheng et al.; 2026, arXiv） | H4/H9/H11 | 4D surfel memory 支持持久 rollout、policy evaluation 与合成数据 | 强/邻域/E2 | VLA/语言端非核心；依赖几何重建与相机位姿 |

## 3. 计划、反事实、主动感知与 critic（P20–P39）

| ID | 论文（作者；年份/venue） | 主方向 | 耦合与作用 | 等级 | 主要边界 |
|---|---|---|---|---|---|
| P20 | [Learning Universal Policies via Text-Guided Video Generation (UniPi)](https://arxiv.org/abs/2302.00111)（Yilun Du et al.; 2023, NeurIPS） | H2/H5 | 文本条件视频计划经 inverse dynamics 转为动作 | 强/E1 | 非候选动作反事实；IDM 可执行性是瓶颈 |
| P21 | [Compositional Foundation Models for Hierarchical Planning](https://arxiv.org/abs/2309.08587)（Anurag Ajay et al.; 2023, arXiv） | H5 | 语言分解、视频物理 grounding、inverse action 组合规划 | 强/E2 | 多组件贡献难拆；接触与闭环误差仍弱 |
| P22 | [Video Language Planning](https://arxiv.org/abs/2310.10625)（Yilun Du et al.; 2023, arXiv） | H5 | text-to-video 生成/搜索视觉计划，再由 goal policy 执行 | 强/E2 | 物体出现/消失和错误物理会被 controller 放大 |
| P23 | [RoboDreamer: Learning Compositional World Models for Robot Imagination](https://proceedings.mlr.press/v235/zhou24f.html)（Siyuan Zhou et al.; 2024, ICML） | H5 | 语言技能因子组合为视频想象并连接执行 | 强/E1 | 技能可组合性假设与真实闭环范围有限 |
| P24 | [Incorporating Task Progress Knowledge for Subgoal Generation through Image Edits](https://arxiv.org/abs/2410.11013)（Xuhui Kang, Yen-Ling Kuo; 2024, arXiv） | H5/H8 | progress-aware latent image editing 生成自适应视觉子目标 | 邻域/E2 | 不是完整 action-conditioned WM |
| P25 | [LaWAM: Latent World Action Models for Efficient Dynamics-Aware Robot Policies](https://arxiv.org/abs/2606.15768)（Jialei Chen et al.; 2026, arXiv） | H2/H5 | latent-action-conditioned WM 预测 visual subgoal，直接条件化 VLA | 强/E2 | 极新；公开复现与跨域行动忠实度未知 |
| P26 | [Inference-Time Enhancement of Generative Robot Policies via Predictive World Modeling](https://arxiv.org/abs/2502.00622)（Han Qi et al.; 2025, RA-L） | H6 | policy 提候选，action-conditioned WM 预测并 rerank/refine | 强/邻域/E1 | 语言端非核心；短时任务与额外推理预算 |
| P27 | [DINO-WM: World Models on Pre-trained Visual Features Enable Zero-shot Planning](https://arxiv.org/abs/2411.04983)（Gaoyue Zhou et al.; 2025, ICML） | H6 | feature-space dynamics 直接优化 action sequence | 邻域/E1 | 无语言 VLA；受控 image-goal 任务为主 |
| P28 | [V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning](https://arxiv.org/abs/2506.09985)（Mido Assran et al.; 2025, arXiv） | H1/H6 | web-video latent WM 经 action conditioning 后做 image-goal planning | 邻域/E2 | foundation-scale 预训练；无语言任务接口 |
| P29 | [Cosmos Policy: Fine-Tuning Video Models for Visuomotor Control and Planning](https://arxiv.org/abs/2601.16163)（Moo Jin Kim et al.; 2026, arXiv） | H6/H8/H14 | 同一 video latent 生成动作、future state、value，并 best-of-N | 强/邻域/E2 | strict language 接口不清；推理成本与 scale confound 大 |
| P30 | [World Action Planner](https://arxiv.org/abs/2607.27599)（Xiangcheng Zhang, Yilun Du; 2026, arXiv） | H6 | VLM 提案，pose/image-conditioned WM 迭代 rollout/修正 | 强/E2 | 截止日前一周的新预印本，尚无独立复核 |
| P31 | [DREAMSTEER](https://arxiv.org/abs/2607.02865)（Hanchen Cui et al.; 2026, arXiv） | H6/H8 | 冻结 VLA 提 action chunks，latent WM 想象、语言 value 排序 | 强/E2 | 无 system identification；候选成本与 OOD 校准未解 |
| P32 | [World Pilot](https://arxiv.org/abs/2606.12403)（Zefu Lin et al.; 2026, arXiv） | H1/H6 | scene-evolution latent 与 anticipated trajectory 双路 steering VLA | 强/E2 | prior 容量、视频预训练与动态收益归因待解 |
| P33 | [World-Value-Action Model](https://arxiv.org/abs/2604.14732)（Runze Li et al.; 2026, arXiv） | H6/H8/H14 | future latent、trajectory value 与 action 联合做隐式规划 | 强/E2 | 理论/实证均新，需 matched direct/value-only 对照 |
| P34 | [Learning Active Tactile Perception Through Belief-Space Control](https://arxiv.org/abs/2312.00215)（Jean-François Tremblay et al.; 2025, ICRA） | H7 | generative WM + Bayesian filter + belief-space MPC 选触摸 | 强/邻域/E1 | 无语言；真实任务集中于低维物体参数估计 |
| P35 | [WoMAP: World Models for Embodied Open-Vocabulary Object Localization](https://arxiv.org/abs/2506.01600)（Tenny Yin et al.; 2025, CoRL） | H7 | VLM 提高层探索动作，latent dynamics/reward WM 做物理 grounding | 强/E1 | 主要是主动定位/导航，尚非通用操作 VLA |
| P36 | [Bridging Active Exploration and Uncertainty-Aware Deployment](https://www.roboticsproceedings.org/rss19/p086.html)（Taekyung Kim et al.; 2023, RSS） | H7/H10 | ensemble dynamics 的 epistemic uncertainty 切换探索与保守 MPC | 邻域/E1 | 低维车辆/轮式系统，无高维视觉语言策略 |
| P37 | [Video Prediction Models as Rewards for Reinforcement Learning](https://proceedings.neurips.cc/paper_files/paper/2023/hash/d9042abf40782fbce28901c1c9c0e8d8-Abstract.html)（Alejandro Escontrela et al.; 2023, NeurIPS） | H8/H12 | video predictor likelihood 直接成为视觉控制 reward | 强/邻域/E1 | 无 VLA；likelihood shortcut 与次优行为模仿 |
| P38 | [Multi-Stage Manipulation with Demonstration-Augmented Reward, Policy, and World Model Learning](https://proceedings.mlr.press/v267/escoriza25a.html)（Adrià López Escoriza et al.; 2025, ICML） | H8/H12 | dense reward、policy 与 latent WM 共同支持多阶段控制 | 强/邻域/E1 | demo/reward/policy/WM 同时变化，难归因 |
| P39 | [Steering Your Generalists: Improving Robotic Foundation Models via Value Guidance](https://proceedings.mlr.press/v270/nakamoto25a.html)（Mitsuhiko Nakamoto et al.; 2025, CoRL） | H8 边界 | value-only 对冻结 generalist policy action samples rerank | 邻域/E1 | 没有 forward dynamics；是检验“完整 WM 是否必要”的强对照 |

## 4. 评测、安全、训练数据与闭环学习（P40–P60）

| ID | 论文（作者；年份/venue） | 主方向 | 耦合与作用 | 等级 | 主要边界 |
|---|---|---|---|---|---|
| P40 | [WorldEval: World Model as Real-World Robot Policies Evaluator](https://arxiv.org/abs/2505.19017)（Yaxuan Li et al.; 2025, arXiv） | H9/H10 | action-following simulator 排名 policy/checkpoint 并检测危险动作 | 强/E2 | 相对排序不等于 OOD 绝对校准 |
| P41 | [WorldGym: World Model as an Environment for Policy Evaluation](https://arxiv.org/abs/2506.00613)（Julian Quevedo et al.; 2025, arXiv） | H9 | VLA 在 video WM 中 Monte Carlo rollout，由 VLM reward 评分 | 强/E2 | 真实物体交互与 OOD action fidelity 较弱 |
| P42 | [Ctrl-World: A Controllable Generative World Model for Robot Manipulation](https://arxiv.org/abs/2510.10125)（Yanjiang Guo et al.; 2025, arXiv） | H9/H11 | 多视角 action-conditioned rollout 同时作 policy ranking 与纠正数据 | 强/邻域/E2 | evaluator 与训练引擎共享偏差 |
| P43 | [dWorldEval: Scalable Robotic Policy Evaluation via Discrete Diffusion World Model](https://arxiv.org/abs/2604.22152)（Yaxuan Li et al.; 2026, arXiv） | H9 | V-L-A 统一 token，联合 future 与 progress token 做评测 | 强/E2 | 新预印本；progress calibration 与泄漏未知 |
| P44 | [WorldSimBench: Towards Video Generation Models as World Simulators](https://proceedings.mlr.press/v267/qin25f.html)（Yiran Qin et al.; 2025, ICML） | H9 边界 | 评测 action consistency 与 embodied utility | 邻域/E1 | 不是完整 policy/checkpoint 闭环 evaluator |
| P45 | [GigaWorld-1: A Roadmap to Build World Models for Robot Policy Evaluation](https://arxiv.org/abs/2607.02642)（GigaWorld Team; 2026, arXiv） | H4 边界/H9 | paired real/imagined rollouts 系统比较 memory、action encoding、horizon | 强（H9）/邻域（H4）/E2 | memory 服务 evaluator 设计，未建立校准 belief；且极新、尚无独立复核 |
| P46 | [World Action Verifier](https://arxiv.org/abs/2604.01985)（Yuejiang Liu et al.; 2026, arXiv） | H9/H13 | state plausibility + action reachability cycle 发现并修复 WM 盲区 | 强/邻域/E2 | 无明确 VLA 端；主要验证 WM 自改进 |
| P47 | [PiL-World: A Chunk-Wise World Model for VLA Policy-in-the-Loop Evaluation](https://arxiv.org/abs/2606.05773)（Chong Ma et al.; 2026, arXiv） | H9/H10 | VLA action chunk 与多视角 WM 交替预测作在线评估 | 强/E2 | 任务数少；长期漂移/风险校准未充分验证 |
| P48 | [Model-Based Runtime Monitoring with Interactive Imitation Learning](https://arxiv.org/abs/2310.17552)（Huihan Liu et al.; 2023, arXiv） | H10/H13 | cVAE latent dynamics 想象失败并请求人类干预 | 强/邻域/E2 | 无语言；依赖 human intervention 标签 |
| P49 | [Uncertainty-aware Latent Safety Filters for Avoiding OOD Failures](https://proceedings.mlr.press/v305/seo25a.html)（Junwon Seo et al.; 2025, CoRL） | H10 | latent generative WM + conformal calibration + reachability 替换危险动作 | 强/邻域/E1 | strict VLA 不完整；高维扩展与 coverage 假设受限 |
| P50 | [CheckVLA: Execution-Time Verification with Action-Conditioned World Model](https://arxiv.org/abs/2607.26789)（Yushan Liu et al.; 2026, arXiv） | H4 边界/H10 | 预测 committed chunk 的应有观测演化，event memory 与校准触发 suffix rewrite | 强（H10）/邻域（H4）/E2 | event memory 不等于对象持久 belief；目前只有仿真，风险保证依赖部署分布 |
| P51 | [DreamGen: Unlocking Generalization through Video World Models](https://arxiv.org/abs/2505.12705)（Joel Jang et al.; 2025, arXiv） | H11/H15 | WM 生成 neural trajectories，LAM/IDM 恢复伪动作训练 policy | 邻域/E2 | 下游语言 VLA 因果链不足；伪动作误差复合 |
| P52 | [Supervise What Survives: Geometry-Guided VLA Adaptation from Synthetic Robot Videos](https://arxiv.org/abs/2606.24448)（Danze Chen et al.; 2026, arXiv） | H11 | 生成视频只监督可保留的几何，不把伪动作当真实控制 | 强/邻域/E2 | 生成器不一定是交互式 WM；需验证更多接触任务 |
| P53 | [AVID: Adapting Video Diffusion Models to World Models](https://arxiv.org/abs/2410.12822)（Marc Rigter et al.; 2024, arXiv） | H11 边界 | 小量 action labels 把预训练视频模型变为 action-conditioned WM | 邻域/E2 | 未直接证明生成数据提升 VLA |
| P54 | [World-Env / RehearseVLA](https://arxiv.org/abs/2509.24948)（Junjin Xiao et al.; 2026, CVPR） | H12 | learned video environment + reward/termination 做 VLA RL post-training | 强/E1 | simulator、reward、termination 三类误差会复合 |
| P55 | [World-Gymnast](https://arxiv.org/abs/2602.02454)（Ansh Kumar Sharma et al.; 2026, arXiv） | H12/H13/H16 | VLA 在 WM 中 RL，含迭代改进与 test-time training | 强/E2 | exploitation、真实回放校准和更新稳定性未解 |
| P56 | [WMPO: World Model-based Policy Optimization for VLA Models](https://arxiv.org/abs/2511.09515)（Fangqi Zhu et al.; 2025, arXiv） | H12 | 像素想象中做 on-policy GRPO | 强/E2 | policy 可能利用 simulator artifact；多种子证据薄 |
| P57 | [WoVR: Reliable World Simulators for Post-Training VLA Policies with RL](https://arxiv.org/abs/2602.13977)（Zhennan Jiang et al.; 2026, arXiv） | H12/H13 | keyframe rollout 降误差深度，WM-policy co-evolution | 强/E2 | 共演化可能共同漂移；公开复现尚不足 |
| P58 | [SWORD: Style-Robust World Models as Simulators](https://arxiv.org/abs/2605.07288)（Jiaxuan Gao et al.; 2026, arXiv） | H12 | style augmentation + latent bootstrapping 提高 imagined simulator 稳健性 | 强/E2 | 主要证 simulator robustness，主动闭环较弱 |
| P59 | [World-VLA-Loop](https://arxiv.org/abs/2602.06508)（Xiaokang Liu et al.; 2026, arXiv） | H12/H13 | policy failure rollout 回灌 state-aware WM，再继续 VLA RL | 强/E2 | near-success 数据与二值奖励含任务先验；闭环漂移需审计 |
| P60 | [Hi-WM: Human-in-the-World-Model for Scalable Robot Post-Training](https://arxiv.org/abs/2604.21741)（Yaxuan Li et al.; 2026, arXiv） | H11/H13 | 人在 imagined failure 上 rollback/branch，纠正数据回灌 policy | 强/邻域/E2 | 仍依赖人类 oracle；语言端不是核心 |

## 5. 联合基础模型、跨具身与部署适应（P61–P69）

| ID | 论文（作者；年份/venue） | 主方向 | 耦合与作用 | 等级 | 主要边界 |
|---|---|---|---|---|---|
| P61 | [WorldVLA: Towards Autoregressive Action World Model](https://arxiv.org/abs/2506.21539)（Jun Cen et al.; 2025, arXiv） | H1/H14 | 单一 AR 框架统一 future image 与 action generation | 强/E2 | action 自回归误差传播；matched-scale 因果不足 |
| P62 | [RynnVLA-002](https://arxiv.org/abs/2511.17502)（Jun Cen et al.; 2025, arXiv） | H14 | world 与 VLA 双向互促，并在仿真/真机验证 | 强/E2 | 预印本；数据/规模与联合目标难拆 |
| P63 | [World Action Models are Zero-shot Policies (DreamZero)](https://arxiv.org/abs/2602.15922)（Seonghyeon Ye et al.; 2026, arXiv） | H14/H15/H16 | 14B video diffusion 联合 future/action，跨本体视频与 few-shot 新身体 | 强/E2 | foundation-scale 成本高；适配与系统辨识未显式解耦 |
| P64 | [DiT4DiT: Jointly Modeling Video Dynamics and Actions](https://arxiv.org/abs/2603.10448)（Teli Ma et al.; 2026, arXiv） | H1/H14 | video DiT 特征条件 action DiT，dual flow matching 联训 | 强/E2 | 级联而非完全共享；future path 是否承重待切断验证 |
| P65 | [VideoVLA: Video Generators Can Be Generalizable Robot Manipulators](https://arxiv.org/abs/2512.06963)（Yichao Shen et al.; 2025, NeurIPS） | H14/H15 | multimodal DiT 联合 video、language、action forecasting | 强/E1 | imagined future 与动作成功主要是相关性；跨本体范围有限 |
| P66 | [Scaling Cross-Embodiment World Models for Dexterous Manipulation](https://arxiv.org/abs/2511.01177)（Zihao He et al.; 2026, IROS） | H15 | 3D particle action-effect space 跨不同手，graph WM + MPC 控制新硬件 | 邻域/E1 | 无语言；手工几何接口且集中于灵巧手 |
| P67 | [AdaWorld: Learning Adaptable World Models with Latent Actions](https://arxiv.org/abs/2503.18938)（Shenyuan Gao et al.; 2025, ICML） | H15/H16 | latent action WM 用少量新交互适配异构动作并 visual planning | 邻域/E1 | 只证 WM adaptation，未形成 VLA 闭环 |
| P68 | [In-Context World Modeling for Robotic Control](https://arxiv.org/abs/2606.26025)（Siyin Wang et al.; 2026, arXiv） | H16 | task-agnostic 自交互历史隐式辨识系统，使 VLA 无参数更新适配 | 强/E2 | 目前最强实证落点是新相机视角；safe probing/形态证据窄 |
| P69 | [World Model Implanting for Test-time Adaptation of Embodied Agents](https://arxiv.org/abs/2509.03956)（Minjong Yoo et al.; 2025, arXiv） | H16 边界 | 检索/组合 domain-specific WMs 到语言 agent policy | 邻域/E2 | 主要是 VirtualHome/ALFWorld，非连续机器人 VLA |

## 6. 证据密度与冲突

| 方向组 | 证据形态 | 结论边界 |
|---|---|---|
| H1–H4 表征 | H1/H2 已有跨年锚点；H3/H4 大量集中在 2026 | 预测目标、额外数据和规模常混杂；记忆不等于 belief，3D/触觉输入不等于 dynamics |
| H5–H10 决策与 assurance | H5/H6/H9 密度较高；H7 最稀；H10 检测多、恢复少 | 视频合理不等于可执行；relative ranking 不等于绝对安全；value-only 是必要边界对照 |
| H11–H13 训练闭环 | H12 增长最快；H11 多为 latent/pseudo-action 邻域；H13 强锚点少 | synthetic、reward、termination 与 WM 误差会复合；co-evolution 可能共同学错 |
| H14–H16 架构与适应 | H14 很拥挤且 foundation-scale；H15 接口机制清楚但 strict VLA 证据薄；H16 已有 ICWM 直接锚点 | joint 不自动证明 world path 承重；跨具身需 effect↔native action 双向可恢复；适配需区分 planning 与 system ID |

共同冲突：

1. 更低 world loss、更好 FVD/LPIPS 或更漂亮视频不能替代闭环成功与 action fidelity。
2. world path 对 VLA 的收益经常与额外数据、参数、训练 token、候选数、推理延迟和环境交互混杂。
3. policy 进入 WM 后会制造训练分布外动作；planner、RL 和 evaluator 恰会主动放大模型盲点。
4. 2025–2026 的强交叉工作大多仍是预印本；失败轨迹、多随机种子、负结果与独立复现不足。
5. 直接 VLA×WM 主动感知、持久校准 belief、跨具身 action-effect 与 safe system identification 仍是证据宽度最窄的区域。

本地图只回答“有哪些真实路线、证据有多强、边界在哪里”，不构成具体 Idea、benchmark 或实验选择。
