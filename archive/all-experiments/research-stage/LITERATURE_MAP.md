# VLA × WAM 母领域文献地图

> **扩展说明（2026-08-06）：** 用户要求把 6 条粗方向进一步展开后，新增长期记忆、主动感知、多模态接触、因果/可供性、跨具身动作语义、部署时适应、持续学习与主动采数等检索簇。补充检索、来源和证据边界见 [LITERATURE_MAP_EXPANSION.md](./LITERATURE_MAP_EXPANSION.md)。

**Run ID：** `20260806-061818-vla-wam-world-action-model-latent-dynamics-model`  
**检索截止：** 2026-08-06  
**时间窗：** 2018-01-01 至 2026-08-06，重点 2023 年以后  
**用途：** 领域制图与宏方向比较；不构成具体 Idea、novelty 结论或实验选择  
**保证级别：** 原始来源可追溯的 discovery map；2025–2026 年大量工作仍是预印本，未做独立复现

## 1. 检索与筛选协议

本地图按 `FIELD_DISCOVERY_CONTRACT.md` 的操作性边界检索：候选工作必须学习或使用观测—动作—时间演化关系，或把该关系用于 VLA/具身策略的表征、提议、评价、规划、训练、适应或安全。纯静态 VLM、无动作语义的视频生成和只有营销材料的系统不进入承重证据集。

### 1.1 数据源

- 结构化检索：arXiv、DBLP、OpenAlex、OpenReview、Semantic Scholar、Crossref；使用项目 `paper-search` 脚本。
- 深读核验：arXiv 原文/HTML、PMLR、OpenReview、NeurIPS/CVF/RSS proceedings、正式 DOI 页和作者官方项目页。
- 本地库：`papers/` 与 `literature/` 均未发现 PDF；项目未配置额外 Paper Library。
- Research Wiki：已初始化，并写入 12 篇跨方向锚点论文；没有写入 Idea、claim 或 experiment 节点。
- 首轮完整、未做相关性截断的 107 条去重记录保存在 [`allinone.md`](../allinone.md)。该文件保留低相关和词义碰撞结果，用于审计关键词偏差。

### 1.2 实际查询轨迹

| 分片 | 查询（`|` 表示 multi-query union） | 可用结果与异常 |
|---|---|---|
| 母领域宽搜 | `vision language action world model robotics | world action model robot policy | embodied world model robot learning` | 107 unique；arXiv、OpenAlex、Crossref 为主要贡献源；Semantic Scholar 两个查询持续 429；完整结果见 `allinone.md` |
| 视频/WAM | `action conditioned video prediction robot manipulation | world action model robotics | robotic world model video generation action`；`visual foresight robot manipulation planning | future image goal generation robot control inverse dynamics | video prediction trajectory proposal robotics`；`world model synthetic data robot policy training | video world model synthetic trajectories imitation learning robotics | generative simulator data engine robot learning` | 首轮并行命令到 364 s 上限；隔离重跑得到 arXiv 18 hits/17 unique、Crossref 18；DBLP TLS `DECRYPTION_FAILED_OR_BAD_RECORD_MAC`，OpenAlex 504，Semantic Scholar 429 |
| latent/MBRL | `robot task-centric latent dynamics world model visuomotor control`；`robot learned dynamics model predictive control candidate action evaluation manipulation navigation`；`robot imagination policy optimization model-based reinforcement learning world model manipulation navigation` | 每组 27–30 unique；Semantic Scholar 429；部分 OpenAlex 504；定向 PlaNet/DayDreamer/TD-MPC/DreamerV3 union 得 55 unique，定向 MOTO/MoDem/DINO-WM/offline MBRL union 得 60 unique；DBLP 多次 TLS 错误 |
| evaluator/safety | `robotics world model critic reward evaluator verifier | robot world model failure prediction uncertainty safety risk | action-conditioned dynamics uncertainty safe robot manipulation` | 31 unique；arXiv SSL EOF、Semantic Scholar 429、OpenAlex 一项 504 |
| structured/3D | `object-centric world model robot manipulation | 3D scene dynamics world model embodied robot planning | structured world model contact dynamics robotic manipulation | graph neural dynamics model object manipulation planning | neural scene representation action-conditioned robot world model` | 60 unique；OpenAlex 出现 SSL EOF、504 和 connection reset；误返回的 2026-08-06 以后论文已剔除 |
| joint/adaptation/pretraining | `joint world model policy training robotic manipulation | policy world model co-evolution robotics | online adaptation learned world model robot control | world model representation pretraining robot policy | video prediction pretraining robotic manipulation | action-conditioned predictive pretraining robot representation` | 54 unique；Semantic Scholar 五项 429；OpenAlex SSL EOF/504 |
| proceedings 补扫 | `world model robot policy evaluation verifier | robot failure prediction dynamics model safety | object-centric 3D world model robot manipulation | joint video action world model robot pretraining` | Crossref 32 hits，补出正式 DOI；DBLP/OpenReview 0。Crossref 大量词义噪声被排除 |

上述 hit/unique 数只反映具体查询的召回，不是领域论文总量，也不直接等于方向价值。重复项按 DOI、arXiv ID、规范化标题合并；关键方法结论以原文而非数据库摘要为准。

### 1.3 证据等级

| 等级 | 含义 |
|---|---|
| E3 | 正式同行评审原始论文，并含下游策略/环境证据、真实机器人或较强的跨任务控制证据 |
| E2 | 原始预印本/技术报告，方法与下游证据完整但尚缺同行评审、跨组复现或覆盖较窄 |
| E1 | Workshop/早期预印本、主要模型指标、有限演示，或结论需要重要补证 |

等级只描述当前证据形态，不是对论文质量的裁决。

## 2. 字段分类：两个轴不能混为一个

### 2.1 表征轴

- **R1 decoded video/pixels：** 直接生成可见未来；解释性强，易受外观 nuisance、长时漂移和高推理成本影响。
- **R2 decodable video latent：** 在 VAE/token latent 中生成并可解码为视频；仍属于视频生成式 WAM。
- **R3 task-centric latent：** 预测由 reward、value、controllability、JEPA 或任务目标塑形的紧凑状态；可以不重建像素。
- **R4 explicit/structured state：** 显式状态、奖励、接触、粒子、点云、3D flow、scene graph、Gaussian 或风险状态。

### 2.2 控制用途轴

- **U1** 表征预训练；**U2** 目标/视频轨迹提议；**U3** 候选动作、策略或风险评价；
- **U4** MPC/显式规划；**U5** imagined policy optimization / model-based RL；**U6** 联合 world-action policy。

同一论文可以同时属于多个格。例如 Cosmos Policy 是 R2/U6 的直接策略，也可用未来状态与 value 做 U3；DreamZero 是 R2/U6，而 V-JEPA 2-AC 是 R3/U4。不能把“视频生成式”“latent dynamics”“model-based RL”当成互斥类别。

## 3. 核心工作簇与证据

### 3.1 动作条件视频、视觉 foresight 与推理时规划（R1/R2；U2/U3/U4）

| 工作 | 分类 | 关键证据 | 主要边界 | 等级 |
|---|---|---|---|---|
| [Visual Foresight](https://arxiv.org/abs/1812.00568) (2018) | R1/U4 | 自监督机器人视频动力学 + visual MPC，在桌面刚体/柔性物体上闭环 | 无语言、多任务与现代长时视频；范围窄 | E2 |
| [UniPi](https://papers.nips.cc/paper_files/paper/2023/hash/1d5b9233ad716a43be5c0d3023cb82d0-Abstract-Conference.html) (NeurIPS 2023) | R1/U2 | 文本条件视频计划经 inverse dynamics 变为动作，覆盖组合目标与真实机器人 | 视频可见正确不保证 IDM 解出的动作可执行 | E3 |
| [Video Language Planning](https://arxiv.org/abs/2310.10625) (2023) | R1/U2/U3 | VLM policy/value、视频 dynamics 与 tree search；模拟和 3 个真实硬件平台 | 原文展示物体出现/消失、物理不守恒与错误知识迁移 | E2 |
| [RoboDreamer](https://proceedings.mlr.press/v235/zhou24f.html) (ICML 2024) | R1/U2 | 语言原语分解改善 RT-X 未见组合目标的视频计划与模拟执行 | 组合原语不等于开放世界物理泛化；真机控制证据不足 | E3 |
| [iVideoGPT](https://arxiv.org/abs/2405.15223) (NeurIPS 2024) | R2/U3/U4/U5 | 动作条件 token dynamics 覆盖预测、planning 与 MBRL | 广泛真实机器人、接触与长时闭环证据有限 | E3 |
| [AVID](https://arxiv.org/abs/2410.12822) (2024) | R2/predictor | 用少量动作标注把黑盒视频扩散模型适配为 world model | 主要是生成指标，未建立多任务控制收益 | E2 |
| [IRASim](https://openaccess.thecvf.com/content/ICCV2025/html/Zhu_IRASim_A_Fine-Grained_World_Model_for_Robot_Manipulation_ICCV_2025_paper.html) (ICCV 2025) | R2/U3/U4 | 多数据集视频模拟、策略相关性和 Push-T planning 改善 | 相关性/单任务指标不能外推到广泛真实接触 | E3 |
| [World Action Planner](https://arxiv.org/abs/2607.27599) (2026) | R1/R2/U4 | VLM 提案 + pose/image 条件 WM rollout 的迭代搜索，强调组合与布局泛化 | 极新预印本，需匹配推理预算与独立复现 | E1 |

**密度：** 高。最近竞争点已经从“能否生成未来”转向 action fidelity、闭环纠错、视频到动作接口、推理延迟及同预算控制收益。

### 3.2 task-centric latent、显式/结构化动力学与 MPC（R3/R4；U3/U4）

| 工作 | 分类 | 关键证据 | 主要边界 | 等级 |
|---|---|---|---|---|
| [PETS](https://arxiv.org/abs/1805.12114) (NeurIPS 2018) | R4/U4 | 概率 ensemble + CEM 显示模型不确定性与样本效率 | 低维 state、仿真、无视觉语言 | E3 |
| [PlaNet](https://proceedings.mlr.press/v97/hafner19a.html) (ICML 2019) | R3/U4 | RSSM + CEM 从像素做少样本规划 | 单任务仿真，未回答 VLA 语义/异构数据 | E3 |
| [TD-MPC](https://proceedings.mlr.press/v162/hansen22a.html) (ICML 2022) | R3/U4 | decoder-free task latent、短 rollout + terminal value，在视觉/状态连续控制中强 | 奖励已知、主要仿真 | E3 |
| [TD-MPC2](https://arxiv.org/abs/2310.16828) (ICLR 2024) | R3/U4 | 104 个在线 RL 任务，单一 317M agent 覆盖 80 tasks/多 action spaces | 交互与算力规模大，仍不是语言 VLA 或真实开放数据 | E3 |
| [DINO-WM](https://arxiv.org/abs/2411.04983) (ICML 2025) | R3/U4 | 冻结 DINOv2 patch 上学 action dynamics，零 reward/expert 的 image-goal planning | 环境受控，foundation pretraining 成本未匹配 | E3 |
| [V-JEPA 2](https://arxiv.org/abs/2506.09985) (2025) | R3/U1/U4 | 百万小时视频预训练，少于 62 h DROID 后训练，跨两实验室 Franka image-goal planning | 原文明示相机位姿敏感、长时误差和搜索空间爆炸；不是开放语言长程策略 | E2 |
| [Diffusion Dynamics for Cloth](https://proceedings.mlr.press/v305/tian25c.html) (CoRL 2025) | R4/U4 | 生成完整布状态并做 diffusion dynamics/MPC，含真机折布 | 使用显式/近 privileged state，任务域窄 | E3 |
| [DPI-Net](https://arxiv.org/abs/1810.01566) (ICLR 2019) | R4/U4 | 粒子图动力学跨刚体、柔体、流体并用于 planning | 视觉到粒子状态成本与长时漂移 | E3 |
| [RoboEXP](https://arxiv.org/abs/2402.15487) (CoRL 2024) | R4/U2 | 交互式 3D scene graph 支持结构记忆和长程任务规划 | 更接近 memory 而非逐时 dynamics；LMM 关系更新会累错 | E3 |
| [GWM](https://arxiv.org/abs/2508.17600) (ICCV 2025) | R4/U1/U5 | Gaussian 世界表征兼顾 3D future reconstruction、policy pretraining、MBRL | 多视角/重建重，接触物理非显式，归因受数据规模影响 | E3 |

**密度：** 通用视觉 MBRL 很高；真实机器人中等；显式语言/VLA 条件、开放数据、多 embodiment action semantics 下明显较低。结构化路线高度异质，不能把 object slots、particles、3D flow、Gaussian 和 scene graph 直接按 success rate 排序。

### 3.3 imagined policy optimization 与 VLA 后训练（R1–R4；U5）

| 工作 | 分类 | 关键证据 | 主要边界 | 等级 |
|---|---|---|---|---|
| [Dreamer](https://arxiv.org/abs/1912.01603) (ICLR 2020) | R3/U5 | RSSM imagination actor-critic 在视觉连续控制中建立经典路线 | 仿真；模型利用和真实迁移未证 | E3 |
| [MBPO](https://arxiv.org/abs/1906.08253) (NeurIPS 2019) | R4/U5 | 短 branched rollout 显示模型偏差可压过长想象的数据收益 | 低维 state；也是“长 rollout 越多越好”的反证 | E3 |
| [DayDreamer](https://proceedings.mlr.press/v205/wu23c.html) (CoRL 2022) | R3/U5 | 四类真机直接在线学习，小时级适应 | 窄任务、真实交互与安全 reset 成本高、无语言 | E3 |
| [DreamerV3](https://www.nature.com/articles/s41586-025-08744-2) (Nature 2025) | R3/U5 | 固定配置覆盖 150+ tasks/8 domains，提供跨域 scale 证据 | 不是 VLA，缺真实机器人与异构机器人视频 | E3 |
| [MOTO](https://arxiv.org/abs/2401.03306) (CoRL 2023) | R3/U5 | 视觉 offline pretrain → online fine-tune，处理 epistemic uncertainty | 仍需在线 fine-tune；off-dynamics 与 reward shift | E3 |
| [DiWA](https://proceedings.mlr.press/v305/chandra25a.html) (CoRL 2025) | R3/U5 | 用离线 play 与 WM 想象适配 diffusion skills | 节省物理交互依赖既有 play 数据，exploitation 审计不足 | E3 |
| [World4RL](https://arxiv.org/abs/2509.19080) (2025) | R1/R2/U5 | 冻结 diffusion WM 后在 imagined environment 中优化策略 | 预印本；reward/model exploitation 与真实校准待审 | E1 |
| [World-Gymnast](https://arxiv.org/abs/2602.02454) (2026 Workshop) | R1/R2/U5/U6 | VLA 在视频 WM 中 rollout，以 VLM reward 做 RL | workshop；WM 与 VLM 双重 shortcut、低基线倍数和共演化稳定性风险 | E1 |
| [RehearseVLA](https://openaccess.thecvf.com/content/CVPR2026/html/Xiao_RehearseVLA_Simulated_Post-Training_for_VLAs_with_Physically-Consistent_World_Model_CVPR_2026_paper.html) (CVPR 2026) | R2/U5 | learned video environment + reflector 做 VLA post-training | simulator 与 reward/termination 必须同时正确；跨域复现有限 | E2 |

**密度：** 通用 MBRL 高；VLA 在 learned video world 内做 RL 是 2025–2026 新兴簇，直接证据少、潜力高、完整性风险也最高。

### 3.4 世界模型作为数据与表征引擎（U1、synthetic trajectories）

| 工作 | 分类 | 关键证据 | 主要边界 | 等级 |
|---|---|---|---|---|
| [VIP](https://arxiv.org/abs/2210.00030) (ICLR 2023) | R3/U1/U3 | Ego4D 学 value-implicit embedding，可作冻结表征与视觉 reward | action-free embedding 不是 forward dynamics；goal distance 不等于可控性 | E3 |
| [GR-1](https://arxiv.org/abs/2312.13139) (2023) | R2/U1/U6 | 大规模视频生成预训练后联合未来图像/动作，CALVIN 与真机泛化改善 | 额外视频、规模与 world objective 的贡献未完全分离 | E2 |
| [LAPA](https://arxiv.org/abs/2410.11758) (2024) | latent action/U1 | 从无动作标签视频量化 latent action，少量机器人数据映射到真实动作 | latent code 可能捕捉视觉 shortcut；跨 embodiment 可执行性是瓶颈 | E2 |
| [V-JEPA 2](https://arxiv.org/abs/2506.09985) (2025) | R3/U1/U4 | web-scale predictive representation 可用少量机器人视频对齐到规划 | 百万小时预训练不可本地复现，只能复用 checkpoint | E2 |
| [DreamGen](https://arxiv.org/abs/2505.12705) (2025) | R2/U2→policy data | 视频 WM 生成 trajectory，LAM/IDM 回收伪动作并扩展 humanoid 行为 | 伪动作错误会在大规模训练中放大 | E2 |
| [RoboDream](https://arxiv.org/abs/2606.02577) (2026) | R2/data engine | 用渲染 robot motion 与显式场景/物体先验组合生成新场景、新物体、新视角示范 | 极新预印本；需逐轨迹物理审计与总成本对照 | E1 |
| [ROSIE](https://roboticsproceedings.org/rss19/p027.html) (RSS 2023) | 非 WM 图像增广 | 低成本语义 inpainting 改物体/背景并提高真实泛化 | 不产生新动作/接触，是 WAM data engine 的强负对照 | E3 |
| [MimicGen](https://proceedings.mlr.press/v229/mandlekar23a.html) (CoRL 2023) | 非 learned-WM data engine | 约 200 人类示范扩为 50K+、18 tasks | 依赖 simulator state/任务结构，也是必须匹配的强基线 | E3 |

**密度：** action-free 视频表征预训练高；用生成式 WM 直接创造可执行训练轨迹为中等且较新。方向价值必须在同等真实数据、总 FLOPs 和筛选成本下击败 ROSIE/MimicGen/RoboGen 等强替代方案。

### 3.5 world model 作为 evaluator、critic、reward 与安全预演（U3）

| 工作 | 分类 | 关键证据 | 主要边界 | 等级 |
|---|---|---|---|---|
| [Failure Prediction with Statistical Guarantees](https://arxiv.org/abs/2202.05894) (RSS 2022) | R4/U3 | PAC-Bayes class-conditional failure bounds | 窄 predictor；保证依赖训练分布，不是完整 WM | E3 |
| [Model-Based Runtime Monitoring](https://arxiv.org/abs/2310.17552) (2023) | R3+R4/U3 | latent counterfactual rollout + failure classifier，持续吸收人类 intervention | 人在环、任务少、operator bias | E2 |
| [WorldEval](https://arxiv.org/abs/2505.19017) (2025) | R2/U3 | paired real evaluations 显示可排名政策/checkpoint，并做 safety detector | 相关性不等于 OOD 绝对校准；物体交互/action following 是难点 | E2 |
| [WorldGym](https://arxiv.org/abs/2506.00613) (2025) | R1/U3 | Monte Carlo video rollout + VLM reward，保留相对 policy ranking | 原文明确：ID 动作价值低估、OOD 动作高估，复杂物体交互不真实 | E2 |
| [GPC](https://arxiv.org/abs/2502.00622) (RA-L 2026) | R3/R4/U3/U4 | 预测 WM 排序/细化冻结 generative policy，含真实 manipulation | 需额外专家+随机探索数据，增加时延，任务较短 | E3 |
| [World Action Verifier](https://arxiv.org/abs/2604.01985) (2026) | R3/R4/U3 | state plausibility + action reachability 的 forward–inverse 自验证 | 主要仿真，无真机；inverse model 是隐藏瓶颈 | E1 |
| [GigaWorld-1](https://arxiv.org/abs/2607.02642) (2026) | R1/R2/U3 | 多 WM、多动作编码与 paired reality evaluation，强调长时 action fidelity | 12,000+ h 视频、预印本、复现和同源 benchmark 风险 | E2 |
| [WorldArena](https://arxiv.org/abs/2602.08971) (2026) | benchmark | 14 个模型的感知与 data engine/evaluator/planner 功能评估，直接揭示 perception–functionality gap | 新 benchmark，仍需跨组与跨平台验证 | E2 |
| [KineBench](https://arxiv.org/abs/2607.19876) (2026) | executable benchmark | 用显式运动学减少 IDM 归因歧义，评估可执行性、平滑度、manipulability | 极新预印本，任务/模拟器覆盖有限 | E1 |

**密度：** 广义安全 monitor 已成熟；把完整动作条件 WM 当 VLA evaluator 在 2025–2026 爆发增长。领域的核心缺口从“是否相关”转为 OOD calibration、尾部 false negative、共享偏差和跨政策分布稳定性。

### 3.6 联合 world-action foundation model 与 policy–WM coupling（U6）

| 工作 | 分类 | 关键证据 | 主要边界 | 等级 |
|---|---|---|---|---|
| [GR-2](https://arxiv.org/abs/2410.06158) (2024) | R2/U6 | 38M clips / 50B tokens 预训练，联合视频与动作，100+ tasks | 极大规模；机制与数据/模型规模混淆 | E2 |
| [Unified World Models](https://www.roboticsproceedings.org/rss21/p015.html) (RSS 2025) | R2/U1/U2/U6 | 单一 diffusion transformer 做 policy、forward/inverse dynamics、video generation | 从零训练与强 policy 接近，主要收益来自预训练；非在线共演化 | E3 |
| [Unified Video Action Model](https://www.roboticsproceedings.org/rss21/p074.html) (RSS 2025) | R2/U6 | 联合 latent 与双 diffusion heads，覆盖多种 world/action 接口 | action inference 可绕过视频 decoder，不能证明 rollout 本身有用 | E3 |
| [WorldVLA](https://arxiv.org/abs/2506.21539) (2025) | R2/U6 | 自回归统一理解、生成和动作 | 动作自回归误差传播；仍需 matched-scale 对照 | E2 |
| [DreamZero](https://arxiv.org/abs/2602.15922) (2026) | R2/U6 | 14B 视频扩散骨干联合视频/动作，真实闭环 7 Hz，任务/环境/embodiment 泛化 | 2×GB200；作者明确短记忆、精细任务、20 Hz VLA 差距与高成本 | E2 |
| [Cosmos Policy](https://arxiv.org/abs/2601.16163) (2026) | R2/U3/U6 | 同一视频 latent 生成动作、未来状态、value；直接策略与 best-of-N planning | planning 用 8×H100 约 4.9 s/chunk；需 rollout data，动态任务受限 | E2 |
| [DiT4DiT](https://arxiv.org/abs/2603.10448) (2026) | R2/U6 | 视频 DiT 中间特征条件 action DiT，dual flow-matching | 新预印本；视频 backbone、额外算力与 joint objective 未解耦 | E2 |
| [WLA](https://arxiv.org/abs/2606.05979) (2026) | R2/U6 | 联合语言 subtask、subgoal image 与动作，可在推理时启用 world prediction | 极新；2B/RTX 5090 报告需独立复现和匹配对照 | E1 |

**密度：** 很高且极快拥挤。“把视频预测和动作头放在一起”已不是充分贡献。真正稀疏的是可归因的 coupling 机制、冻结/交替/joint/online 的因子比较，以及 policy–WM 共演化在 policy shift 下不自我强化错误的证据。

## 4. 跨工作簇的冲突证据

1. **视觉真实感不等于动作信息或控制价值。** ICRA 2020 的 [action-conditioned benchmarking](https://arxiv.org/abs/1910.02564) 显示高感知质量可对应低动作可辨识度；[WorldArena](https://arxiv.org/abs/2602.08971) 在 14 个模型上报告 perception–functionality gap；RoboWM/KineBench 类评测又暴露视频→动作归因歧义。
2. **重建式 latent 与任务式 latent 没有统一赢家。** DreamerV3 的重建 RSSM 跨域很强；DreamerPro、RePo、DINO-WM、V-JEPA 2 则表明 nuisance reconstruction 可能浪费容量。现有论文缺同数据/同 planner 的 encoder 交叉矩阵。
3. **长想象既提供远见，也放大模型误差。** PlaNet/Dreamer依赖多步 imagined rollout；MBPO 和 TD-MPC 系用短 rollout、terminal value 或 uncertainty 折中。长时预测 loss 不能替代环境回报。
4. **相对 policy ranking 不等于 OOD 绝对可信。** IRASim/WorldEval 报告相关性；WorldGym 明确观察 OOD action value 高估。新 policy 或 adversarial action 正是评估器最需要、也最薄弱的分布。
5. **联合模型的收益常与规模混淆。** GR-2、UWM、DreamZero、Cosmos Policy 同时改变预训练数据、backbone、参数与目标；UVA 甚至可在动作推理时不解码视频。需要 matched-data/compute/parameters 的 action-only 与 joint 对照。
6. **生成数据可能复制或放大错误。** VIPER 会从次优视频学到次优行为；DreamGen/RoboDream 的 IDM/LAM 或生成 hallucination 会污染伪动作。生成轨迹数量不是有效样本数。
7. **安全保证依赖分布假设。** PAC/Conformal monitor 在给定分布能给 false-negative 界；policy 更新、WM 共演化和开放词汇指令会破坏 exchangeability/coverage。

## 5. 最近工作碰撞与未解问题

| 研究问题 | 最近工作密度 | 尚未解决的碰撞 |
|---|---|---|
| 视频/关键帧计划 → 动作 | 高 | 语义规划 vs 物理可执行；IDM/goal policy 是隐藏瓶颈；闭环计算预算不匹配 |
| task latent/structured dynamics → MPC | 通用控制高，VLA-specific 低 | representation 与 planner 同时变化；语言/奖励 shortcut；多 embodiment action normalization |
| imagined RL / VLA post-training | 通用 MBRL 高，VLA-WM 低 | policy exploit、VLM reward shortcut、imagined return 与真实回报尾部差距 |
| WM data engine | 中等增长 | synthetic fidelity vs 可执行性；生成/筛选总成本；需击败 ROSIE/MimicGen 等便宜强基线 |
| WM evaluator/critic/safety | 中高且增长最快 | OOD calibration、绝对 success、false negative、共享 foundation bias、尾部失败数据稀缺 |
| joint WAM/VLA | 很高 | “联合”本身拥挤；真正缺冻结/交替/joint/coevolution 因果比较与长期稳定性 |

## 6. 领域级证据缺口

- 缺少统一的三层链条：**action sensitivity / calibration → policy endpoint → environment endpoint**。
- 缺少同数据、参数、优化、交互、候选数、预测 horizon 与推理时延下的 `representation × control-use` 因子比较。
- 缺少在最终 policy 分布上报告 rollout error、uncertainty recall、imagined-return/real-return gap 与模型漏洞利用。
- 接触、遮挡、力/触觉、多视角 3D、一致 object state 和不可逆失败仍是最稳定的困难区。
- 跨 embodiment 的动作语义仍碎片化：关节、7-DoF、action chunk、latent action、手势、3D flow、proprioception 无统一接口。
- 真实导航、移动操作和 humanoid 的证据少于桌面 manipulation/仿真连续控制。
- 尾部失败/危险数据决定 evaluator 与 safety 路线的上限，但安全采样成本最高，论文普遍低估此账本。
- 互联网视频 provenance、许可、污染、模型训练 FLOPs、生成 rollout 成本和失败 run accounting 不完整。

## 7. 覆盖范围与盲区

### 已覆盖

- 必查种子：视频生成式 WAM、task-centric latent dynamics、model-based RL。
- 种子外路线：evaluator/critic、安全监控、结构化/3D dynamics、数据/表征引擎、联合 world-action、在线适应/共演化。
- 控制角色 U1–U6；仿真、离线、在线真实与混合数据；操作、导航、连续控制、deformable、humanoid 的代表证据。

### 已知盲区

- 英文关键词与公开可索引来源为主；非英语、企业内部负结果、尚未公开数据/代码的工作低估。
- Semantic Scholar 的持续 429、OpenAlex 的 504/连接错误和 DBLP TLS 错误降低了 venue-only 召回；已用正式 proceedings/DOI 补扫，但不能声称穷尽。
- 未下载系统性本地 PDF 库；关键锚点读了原文/HTML 方法与 limitation，长尾候选只做标题—摘要—官方页筛选，不承担承重结论。
- 2026 年 8 月 6 日后的条目全部排除；极新工作多数尚无独立复现，评分会降低其证据成熟度。
- 自动驾驶世界模型仅在方法直接支持 robot/VLA 表征或控制问题时旁证，没有单独展开。
- citation count 未用于方向排序；新近、开放源码和负结果都可能被现有数据库低估。

## 8. 对宏方向生成的约束

证据支持把版图按“科学问题 + 世界模型角色 + 决定性证据”划分为六条宏方向，而不是按单一架构标签划分：

1. 可校准 evaluator/critic/safety；
2. task-centric latent / structured dynamics for control；
3. 可审计的数据与表征引擎；
4. 推理时视频反事实规划；
5. imagined VLA post-training / model-based RL；
6. 联合 world-language-action foundation model 与 policy–WM coupling。

它们在 `DIRECTION_LANDSCAPE.md` 中以统一分数、资源账本和证据门槛比较。排名只代表当前配置下的调查优先级；在用户选择前，`research.selected_macro_direction` 必须保持为空。
