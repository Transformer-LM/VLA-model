# WAM-only 文献地图

**Run ID：** `20260806-vla-wam-tri-domain-field-map`  
**检索截止：** 2026-08-06  
**范围：** 学习观测—动作—时间演化关系的 world/action model；不要求语言接口，也不把 VLA 论文当主证据。

## 1. 检索与筛选

两轮跨库查询分别围绕表示与用途展开：

```text
action-conditioned video prediction robotic manipulation world model
visual model-based reinforcement learning robot latent dynamics RSSM
structured object-centric 3D contact dynamics robot planning world model
robot world model belief state memory system identification adaptation

learned dynamics model predictive control visual robotics planning
world model imagination robot reinforcement learning physical robot
robot world model synthetic data generation policy training
robot world model policy evaluation calibration safety uncertainty
```

- 第一轮合并后 91 篇去重候选，第二轮 100 篇；再回到 arXiv、PMLR、OpenReview、NeurIPS、RSS、ICRA/DOI 原页核验。
- DBLP 多次 HTTP 500/读超时，Semantic Scholar 多组查询持续 429，OpenAlex 部分 504，OpenReview 两轮无命中；这些故障降低了 venue-only 长尾召回，不能声称穷尽。
- 纳入项必须学习动作条件未来、belief/state transition、reward/contact/termination，或明确把 learned model 用于 MPC、imagination、数据、评估或安全。
- 被动视频生成、纯 action policy、纯手工 simulator、纯静态表征与 survey 不进入核心表。

证据等级按本 run 契约统一：**E1**＝正式同行评审原始论文；**E2**＝细节可核验的原始预印本；**E3**＝摘要/项目页或只承担邻域说明的证据。

## 2. 表示与用途坐标

- **R1：** decoded pixels/video；**R2：** 可解码 video latent；**R3：** task-centric latent / belief；**R4：** 显式或结构化 state、object、3D、contact。
- **U1：** 表征预训练；**U2：** 目标/轨迹提议；**U3：** 候选、策略或风险评价；**U4：** MPC/显式规划；**U5：** imagined policy learning / 数据生成。

R 与 U 是正交轴；例如同一个 R3 模型可以用于 U3、U4 或 U5，不能把 latent、planning 和 MBRL 当互斥类别。

## 3. 去重核心工作（36 篇）

| # | 工作 | 年份/出处 | R/U | 支持什么，以及边界 | 证据 |
|---:|---|---|---|---|---|
| 1 | [PETS](https://papers.nips.cc/paper_files/paper/2018/hash/3de568f8597b94bda53149c7d7f5958c-Abstract.html) | NeurIPS 2018 | R4/U4 | 概率 ensemble 与 trajectory sampling 建立 uncertainty-aware learned MPC；低维、受控环境为主 | E1 |
| 2 | [PlaNet](https://proceedings.mlr.press/v97/hafner19a.html) | ICML 2019 | R3/U4 | RSSM belief 上从像素规划；单任务视觉控制，不含语言或开放机器人数据 | E1 |
| 3 | [SOLAR](https://proceedings.mlr.press/v97/zhang19a.html) | ICML 2019 | R3/U4 | 学结构化 latent 并在其中做局部线性控制；依赖受控任务 | E1 |
| 4 | [DPI-Net](https://openreview.net/forum?id=r1gRTCVFvB) | ICLR 2019 | R4/U4 | 粒子图动力学覆盖刚体、柔体和流体规划；视觉到粒子 state 是隐藏成本 | E1 |
| 5 | [Dreamer](https://openreview.net/forum?id=S1lOTC4tDS) | ICLR 2020 | R3/U5 | 在 latent imagination 中训练 actor–critic；不是显式 MPC | E1 |
| 6 | [SLAC](https://arxiv.org/abs/1907.00953) | ICML 2020 | R3/U5 | stochastic latent sequence model 与 actor–critic，强调部分可观测历史 | E1 |
| 7 | [Context-aware Dynamics](https://proceedings.mlr.press/v119/lee20g.html) | ICML 2020 | R3/R4-U4 | context latent 表示局部动力学并跨 dynamics 泛化 | E1 |
| 8 | [Keypoints into the Future](https://proceedings.mlr.press/v155/manuelli21a.html) | CoRL 2020 | R4/U4 | keypoint correspondence dynamics 服务视觉控制；结构偏置强、域窄 | E1 |
| 9 | [Action-conditioned Benchmarking](https://arxiv.org/abs/1910.02564) | ICRA 2020 | R1/评估 | 直接揭示感知画质与 action information 不一致 | E1 |
| 10 | [MOPO](https://proceedings.neurips.cc/paper/2020/hash/a322852ce0df73e204b7e67cbbef0d0a-Abstract.html) | NeurIPS 2020 | R4/U5 | 用模型不确定性惩罚 OOD imagined rollout | E1 |
| 11 | [MOReL](https://proceedings.neurips.cc/paper/2020/hash/f7efa4f864ae9b88d43527f4b14f750f-Abstract.html) | NeurIPS 2020 | R4/U5 | pessimistic MDP 抑制策略利用未知区域 | E1 |
| 12 | [Dreaming without Reconstruction](https://doi.org/10.1109/ICRA48506.2021.9560734) | ICRA 2021 | R3/U5 | 说明 visual MBRL 不一定需要像素重建目标 | E1 |
| 13 | [TD-MPC](https://proceedings.mlr.press/v162/hansen22a.html) | ICML 2022 | R3/U4 | task-oriented latent、短 rollout 与 terminal value 结合 | E1 |
| 14 | [DayDreamer](https://proceedings.mlr.press/v205/wu23c.html) | CoRL 2022 | R3/U5 | 四类真实机器人上直接在线学习；任务窄、reset 和安全成本高 | E1 |
| 15 | [Action-conditioned Tactile Prediction](https://roboticsproceedings.org/rss18/p070.html) | RSS 2022 | R4/U3 | 动作条件触觉预测用于 slip，补充视觉不可辨识的接触状态 | E1 |
| 16 | [Masked World Models](https://proceedings.mlr.press/v205/seo23a.html) | CoRL 2022 | R3/U5 | masked reconstruction 改善视觉 MBRL 表征与效率 | E1 |
| 17 | [COMBO](https://proceedings.neurips.cc/paper/2021/hash/f29a179746902e331572c483c45e5086-Abstract.html) | NeurIPS 2021 | R4/U5 | conservative model-based offline RL，不完全依赖显式 uncertainty | E1 |
| 18 | [RePo](https://arxiv.org/abs/2309.00082) | NeurIPS 2023 | R3/U5 | predictability regularization 抑制视觉 distraction | E1 |
| 19 | [UniPi](https://papers.nips.cc/paper_files/paper/2023/hash/1d5b9233ad716a43be5c0d3023cb82d0-Abstract-Conference.html) | NeurIPS 2023 | R1/U2 | 文本条件视频计划经 inverse dynamics 变为动作；IDM 是隐藏瓶颈 | E1 |
| 20 | [Online Dynamics Learning for Predictive Control](https://proceedings.mlr.press/v205/jiahao23a.html) | CoRL 2022 | R4/U4 | 部署中更新 dynamics 并用于 MPC；证据来自空中机器人 | E1 |
| 21 | [SafeDreamer](https://proceedings.iclr.cc/paper_files/paper/2024/hash/ece182f93af26c64187ba3f7dfd4309a-Abstract-Conference.html) | ICLR 2024 | R3/U5 | cost constraint 进入 imagination learning；主要仍是 Safety-Gymnasium | E1 |
| 22 | [TD-MPC2](https://arxiv.org/abs/2310.16828) | ICLR 2024 | R3/U4 | 单一可扩展 latent WM 覆盖大量连续控制任务；真实机器人有限 | E1 |
| 23 | [RoboDreamer](https://proceedings.mlr.press/v235/zhou24f.html) | ICML 2024 | R1/U2 | compositional video imagination 支持机器人子目标规划 | E1 |
| 24 | [DeformNet](https://doi.org/10.1109/ICRA57147.2024.10611243) | ICRA 2024 | R3/R4-U4 | deformable-object latent dynamics 与 manipulation planning | E1 |
| 25 | [MoDem-V2](https://doi.org/10.1109/ICRA57147.2024.10611121) | ICRA 2024 | R3/U5 | demonstration-bootstrapped visuomotor WM 用于真实操作学习 | E1 |
| 26 | [DORA](https://proceedings.mlr.press/v235/zhang24bc.html) | ICML 2024 | R3/U4 | 分离 dynamics context 与 behavior-policy shift，服务快速在线适应 | E1 |
| 27 | [RoboEXP](https://arxiv.org/abs/2402.15487) | CoRL 2024 | R4/U2 | 交互式 3D scene graph 作为结构记忆；更接近 belief 而非逐时 dynamics | E1 |
| 28 | [DINO-WM](https://arxiv.org/abs/2411.04983) | ICML 2025 | R3/U4 | 冻结 DINOv2 feature 上学 action dynamics，支持 image-goal planning | E1 |
| 29 | [DreamerV3](https://www.nature.com/articles/s41586-025-08744-2) | Nature 2025 | R3/U5 | 固定配置跨 150+ tasks；强通用证据但非机器人专属 | E1 |
| 30 | [GWM](https://arxiv.org/abs/2508.17600) | ICCV 2025 | R4/U1/U5 | Gaussian 3D world 表征兼顾 future reconstruction、预训练和 MBRL | E1 |
| 31 | [DreamGen](https://arxiv.org/abs/2505.12705) | 2025 预印本 | R2/数据 | 生成机器人视频并回译伪动作；视频与 IDM/LAM 错误可能共同污染 | E2 |
| 32 | [WorldEval](https://arxiv.org/abs/2505.19017) | 2025 预印本 | R2/U3 | 用 paired reality 评价 policy/checkpoint 与安全失败；OOD 校准未解决 | E2 |
| 33 | [WorldGym](https://arxiv.org/abs/2506.00613) | 2025 预印本 | R1/U3 | 视频 rollout + VLM reward；原文报告 OOD action 高估 | E2 |
| 34 | [V-JEPA 2](https://arxiv.org/abs/2506.09985) | 2025 预印本 | R3/U1/U4 | 大规模 predictive pretraining 后以少量机器人数据对齐规划 | E2 |
| 35 | [ReDRAW](https://proceedings.mlr.press/v331/lanier26a.html) | L4DC 2026 | R3/R4-U4 | latent-state residual 校准 sim→target dynamics | E1 |
| 36 | [WorldArena](https://arxiv.org/abs/2602.08971) | 2026 预印本 | 跨 R/评估 | 比较 14 个模型并揭示 perception–functionality gap | E2 |

## 4. 工作簇与冲突

| 工作簇 | 证据密度 | 尚未解决的冲突 |
|---|---|---|
| action-conditioned video | 中高、快速增长 | 画质与 action fidelity 脱钩；IDM 可能遮蔽失败 |
| task-centric latent / RSSM belief | 高、最成熟 | reconstruction 与 task-only latent 没有统一赢家 |
| object/3D/contact dynamics | 中等 | 物理结构清楚，但 state extraction 可能成为真正瓶颈 |
| memory/system ID/adaptation | 通用控制中高、视觉机器人中低 | dynamics shift 与 behavior-policy shift 容易混淆 |
| learned planning/MPC | 高 | representation、planner、候选预算经常同时改变 |
| imagined learning/data engine | 高 | 长 rollout、model exploitation 与额外算力/数据混淆 |
| evaluator/calibration/safety | 中等、2025–2026 增长快 | 相对排序不等于 OOD 绝对可信或尾部安全 |

跨簇共同盲区包括：paired real/WM rollout 稀少；缺 `R × U` 同数据同 planner 因子矩阵；接触、遮挡、触觉与不可逆失败覆盖不足；跨 embodiment action semantics 不统一；很少完整报告 rollout FLOPs、候选数、延迟和失败运行。

## 5. 对方向版图的约束

证据支持七条 WAM-only 母方向：observable video、task latent/belief、structured physics、memory/system ID、planning/MPC、imagined learning/data、functional evaluation/safety。联合 VLA/WLA 基座、普通动作策略和手工 simulator 不得挤占这张图；它们分别属于交叉域、VLA 域或对照域。
