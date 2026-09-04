# VLA × WAM 强交叉文献地图

**Run ID：** `20260806-vla-wam-tri-domain-field-map`  
**检索截止：** 2026-08-06  
**强交叉门槛：** 同时有可识别的 VLA/语言条件策略端点，以及真正进入训练、动作选择、规划、评价、安全或适配闭环的 learned dynamics。

## 1. 检索轨迹与分类

- 六库宽检以 `vision language action predictive world model robotics`、`VLA world model planning critic evaluation safety`、`VLA world model synthetic data imagination post-training`、`joint world language action cross embodiment adaptation` 为主：arXiv 40、Crossref 40、OpenAlex 10、Semantic Scholar 20，104 篇去重、合并 6 条跨源重复。
- arXiv 聚焦补检 `world model VLA robot`、`vision-language-action world model`、`world model policy evaluation VLA`、`world model post-training VLA`：100 条原始命中、70 篇去重。
- OpenAlex 出现 429、读超时与 504，Semantic Scholar 两个查询为 429；最后逐篇回到 arXiv、RSS、PMLR、CVF 原页核验。CVF 的 RehearseVLA 页面抓取遇到 403，但正式 CVPR 页面和既有原页核验可用。
- 仅共享视频 backbone、只报生成指标、静态 VLM、通用 Dreamer/MBRL 而无 VLA 接口者不计强交叉。

耦合代码：**P**＝预测预训练/辅助目标；**R**＝rollout planning；**E**＝critic/evaluation/safety；**T**＝synthetic data 或 imagined post-training；**J**＝联合 WLA；**A**＝跨 embodiment/在线共适应。

证据等级：**E1**＝正式发表原文；**E2**＝方法细节可核验的原始预印本；**E3**＝摘要/项目页或弱邻域。

## 2. 强交叉工作（29 篇）

| # | 工作 | 年份 | 耦合 | 核验结论与主要边界 | 证据 |
|---:|---|---:|---|---|---|
| 1 | [GR-1](https://arxiv.org/abs/2312.13139) | 2023 | P/J | 语言、历史图像与机器人状态共同预测动作和未来图像；收益与视频规模混杂 | E2 |
| 2 | [UniPi](https://arxiv.org/abs/2302.00111) | 2023 | R | 语言条件视频计划经 inverse dynamics 变为动作；不是候选动作反事实 rollout | E1 |
| 3 | [Video Language Planning](https://arxiv.org/abs/2310.10625) | 2023 | R | 语言生成视觉计划，再由 goal-conditioned policy 执行；plan/controller 归因困难 | E2 |
| 4 | [RoboDreamer](https://proceedings.mlr.press/v235/zhou24f.html) | 2024 | R | 语言引导视频世界预测服务执行；视频合理不保证动作可执行 | E1 |
| 5 | [3D-VLA](https://arxiv.org/abs/2403.09631) | 2024 | R/J | 统一 3D 感知、语言、动作并生成目标图像/点云；真实闭环有限 | E2 |
| 6 | [GR-2](https://arxiv.org/abs/2410.06158) | 2024 | P/J | 大规模视频预训练后联合视频和动作；规模、数据与 world objective 未解耦 | E2 |
| 7 | [WorldVLA](https://arxiv.org/abs/2506.21539) | 2025 | J | 单框架统一动作与未来图像；自回归动作误差传播仍存在 | E2 |
| 8 | [WorldEval](https://arxiv.org/abs/2505.19017) | 2025 | E | learned simulator 排名 policy/checkpoint 并检测危险动作；相关性不等于 OOD 校准 | E2 |
| 9 | [WorldGym](https://arxiv.org/abs/2506.00613) | 2025 | E | VLA 在视频世界 Monte Carlo rollout，VLM 给 reward；复杂交互真实性弱 | E2 |
| 10 | [World-Env](https://arxiv.org/abs/2509.24948) | 2025 | T | learned simulator + VLM reward/termination 做 VLA RL；多类错误会复合 | E2 |
| 11 | [WMPO](https://arxiv.org/abs/2511.09515) | 2025 | T | 像素想象中做 on-policy GRPO；需排除 simulator artifact exploitation | E2 |
| 12 | [RynnVLA-002](https://arxiv.org/abs/2511.17502) | 2025 | J | 未来图像与动作互促，含仿真和真机；缺独立 matched-scale 复现 | E2 |
| 13 | [DUST](https://arxiv.org/abs/2510.27607) | 2025 | P/J | 双流 diffusion 联合 state/action 并支持无动作视频预训练；多项架构变化并发 | E2 |
| 14 | [Joint Learning with Motion Image Diffusion](https://arxiv.org/abs/2512.18007) | 2025 | P | optical-flow motion head 作辅助目标、推理路径不变；较干净的 P 类锚点 | E2 |
| 15 | [IRL-VLA](https://arxiv.org/abs/2508.06571) | 2025 | E/T | reward world model 为驾驶 VLA 提供闭环 RL 信号；域窄且 reward model 不等于完整 dynamics | E2 |
| 16 | [Gemini Robotics in a Veo World Simulator](https://arxiv.org/abs/2512.10675) | 2025 | E | 商用 VLA 与视频世界模拟器的直接评价交叉；闭源、难因果复现 | E2 |
| 17 | [Cosmos Policy](https://arxiv.org/abs/2601.16163) | 2026 | R/E/J/A | 同一 video latent 生成动作、未来 state 和 value，并支持 best-of-N；算力/延迟高 | E2 |
| 18 | [DreamZero](https://arxiv.org/abs/2602.15922) | 2026 | J/A | 大型视频扩散 WAM 直接闭环控制并跨机器人适配；foundation-scale 成本极高 | E2 |
| 19 | [World-Gymnast](https://arxiv.org/abs/2602.02454) | 2026 | T/A | VLA 在 action-conditioned video WM 中 RL，并含测试时训练；exploitation 风险高 | E2 |
| 20 | [World-VLA-Loop](https://arxiv.org/abs/2602.06508) | 2026 | E/T/A | 帧/reward 模型改善 policy，policy rollout 再反哺 WM；直接 co-evolution 锚点 | E2 |
| 21 | [WoVR](https://arxiv.org/abs/2602.13977) | 2026 | T/A | keyframe initialization 与 policy–simulator co-evolution 控制长时误差；共同漂移仍可能 | E2 |
| 22 | [RehearseVLA](https://openaccess.thecvf.com/content/CVPR2026/html/Xiao_RehearseVLA_Simulated_Post-Training_for_VLAs_with_Physically-Consistent_World_Model_CVPR_2026_paper.html) | CVPR 2026 | T | physically consistent learned environment 做 VLA post-training；同时依赖 dynamics/reward/termination | E1 |
| 23 | [SWORD](https://arxiv.org/abs/2605.07288) | 2026 | T | style augmentation 与 latent bootstrapping 提高 WM simulator 稳健性；覆盖仍窄 | E2 |
| 24 | [TACO](https://arxiv.org/abs/2607.02840) | 2026 | E/T | 触觉世界模型识别失败邻域、想象局部修正；需要特殊硬件与同步数据 | E2 |
| 25 | [World Pilot](https://arxiv.org/abs/2606.12403) | 2026 | P/R | world-action prior steering VLA 感知与动作链；额外容量归因待解 | E2 |
| 26 | [DREAMSTEER](https://arxiv.org/abs/2607.02865) | 2026 | R/E | 采样 VLA chunks，以 latent WM 想象和语言 value 排序；候选成本/OOD 校准是瓶颈 | E2 |
| 27 | [World-Value-Action Model](https://arxiv.org/abs/2604.14732) | 2026 | R/E/J | future latent、trajectory value 与 action 统一为隐式规划；主张仍待独立 matched 对照 | E2 |
| 28 | [PiL-World](https://arxiv.org/abs/2606.05773) | 2026 | E | VLA action chunk 与多视角 WM 预测交替，policy-in-the-loop 评价；目前任务少 | E2 |
| 29 | [GigaWorld-1](https://arxiv.org/abs/2607.02642) | 2026 | E | 多 WM、多动作编码、imagined/真机配对；强调长时 action fidelity | E2 |

## 3. 降级弱邻域（7 篇）

| 工作 | 年份 | 为什么不承担“强交叉已经成立”的结论 |
|---|---:|---|
| [Unified World Models](https://www.roboticsproceedings.org/rss21/p015.html) | RSS 2025 | 视频/动作、正逆动力学和 policy 耦合强，但语言/VLA 接口不是核心 |
| [Unified Video Action Model](https://www.roboticsproceedings.org/rss21/p074.html) | RSS 2025 | joint video-action latent 强但无明确语言端；动作可绕过视频解码 |
| [V-JEPA 2](https://arxiv.org/abs/2506.09985) | 2025 | learned latent world 与 image-goal planning 成立，但没有语言条件 VLA 接口 |
| [DreamGen](https://arxiv.org/abs/2505.12705) | 2025 | WM→LAM/IDM→policy data 成立，但下游 VLA 因果链不足 |
| [Hi-WM](https://arxiv.org/abs/2604.21741) | 2026 | 人类纠错和 WM 后训练强，但语言接口并非关键机制 |
| [LAPA](https://arxiv.org/abs/2410.11758) | 2024 | latent action discovery 支持无标签视频预训练，但没有 learned forward world 被消费 |
| [Scaling Cross-Embodiment World Models](https://arxiv.org/abs/2511.01177) | 2025 | 跨 embodiment dynamics 很相关，但 downstream VLA 收益链尚不充分 |

## 4. 交叉簇的冲突与盲区

- 视觉真实度与控制真实度脱钩；短时好看不保证长时 action-following、接触和可执行性。
- relative policy ranking 不等于绝对安全；新 policy、对抗动作和罕见失败恰是模型最可能过度自信的区域。
- GR-2、DreamZero、Cosmos Policy 等同时改变数据、参数、目标与训练预算，“joint”收益缺 matched attribution。
- 共享 backbone 不证明 world objective 有效；世界路径可被绕过时，动作收益可能来自额外特征或容量。
- frozen WM 会随 policy 提升而 distribution shift；co-evolution 又可能让二者共同学错，缺独立 ground-truth anchor。
- imagined RL 的核心风险是 simulator/reward exploitation，不只是视频不漂亮。
- synthetic trajectory 还叠加 video、IDM/LAM、筛选和 retraining 错误；数量不能代替 effective sample yield。
- pixel、video latent、task latent 和 structured state 缺同 planner、同数据、同延迟的交叉矩阵。
- 接触、形变、遮挡、长记忆和部分可观测仍不足；触觉目前只是早期单点。
- 2025–2026 强交叉绝大多数仍是预印本；真实任务数、随机种子、失败视频和负结果有限。

## 5. 对方向版图的约束

六条强交叉母方向应按耦合发生的位置拆分：训练时预测辅助、推理时规划、评价/安全、生成经验/后训练、原生联合模型、跨具身/在线共适应。弱邻域只帮助定义边界，不能把“视频+动作”或“共享 backbone”自动升级为 VLA×WAM。
