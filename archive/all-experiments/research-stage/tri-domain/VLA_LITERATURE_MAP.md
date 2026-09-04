# VLA-only 文献地图

**Run ID：** `20260806-vla-wam-tri-domain-field-map`  
**检索截止：** 2026-08-06  
**范围：** 当前/历史视觉、语言与可选本体状态直接产生机器人动作或 action chunk 的策略、训练、接口和评价；显式预测未来环境才进入 WAM。

## 1. 一个关键边界

离散 action token、ACT chunk、diffusion、flow matching 与 FAST tokenization 都是在建模**动作分布**，本身不是 world model。纯 VLA 可以完全没有 learned dynamics；这张地图因此不再把 VLA 论文只当作 WAM 的 policy baseline。

类型：**P**＝直接 VLA/generalist policy；**A**＝无语言但构成 VLA action head 的动作策略底座；**H**＝高层 embodied VLM/技能规划先驱；**I**＝数据、接口或 benchmark 基础设施；**P\***＝主体是 VLA，但带生成/预测辅助，不因此自动归为 WAM。

证据等级：**E1**＝正式同行评审原始论文；**E2**＝可核验预印本/技术报告；**E3**＝只承担邻域或项目存在性证据。

## 2. 可审计检索轨迹

六源并集查询：

```text
vision language action robot foundation policy
generalist language conditioned robot policy manipulation
cross embodiment robot policy Open X-Embodiment
diffusion transformer robot action policy
```

- 首轮 15 条/源因数据库内部串行和 API 延迟在 364 秒外层超时；输出缓冲导致无可用 partial table。
- 以连接超时 10 秒、读超时 45 秒、单次尝试、12 条/源重跑：arXiv 48、OpenAlex 12、Crossref 48，99 篇去重、合并 9 条跨源重复；DBLP/OpenReview/Semantic Scholar 为 0。
- OpenAlex 三个查询返回 504；Semantic Scholar 四个查询均为 429；Crossref 含语言政策、社会学 embodiment 与普通 action-recognition 噪声，均已剔除。
- 本地 `papers/`、`literature/` 和配置的 Paper Library 没有 PDF；定向补检只采用 arXiv、PMLR、OpenReview、RSS/CVF proceedings、作者官方页和正式技术报告。
- 一个第三方 SmolVLA 页面给出错误作者与 arXiv ID，已以正式 [arXiv:2506.01844](https://arxiv.org/abs/2506.01844) 纠正。

## 3. 去重核心与边界工作（40 篇）

| # | 工作 | 年份/出处 | 类别 | 支持什么，以及边界 | 证据 |
|---:|---|---|---|---|---|
| 1 | [CLIPort](https://arxiv.org/abs/2109.12098) | CoRL 2021 | P | CLIP 语义“what”与 Transporter 空间“where”结合；桌面 pick-place 为主 | E1 |
| 2 | [SayCan](https://arxiv.org/abs/2204.01691) | CoRL 2022 | H | LLM 技能先验与可执行性 value 组合，支持真机长程技能链；非端到端 VLA | E1 |
| 3 | [VIMA](https://arxiv.org/abs/2210.03094) | ICML 2023 | P | 文本、图像与示范组成 multimodal prompt；仿真对象化假设较强 | E1 |
| 4 | [RT-1](https://arxiv.org/abs/2212.06817) | 2022 技术报告 | P | 大规模多任务真机数据与 Transformer 的 scaling 锚点；数据私有、机器人家族有限 | E2 |
| 5 | [PaLM-E](https://arxiv.org/abs/2303.03378) | ICML 2023 | H | 连续视觉/状态编码注入 LLM，展示 embodied reasoning 与跨任务正迁移；主要输出高层文本 | E1 |
| 6 | [Diffusion Policy](https://arxiv.org/abs/2303.04137) | RSS 2023 | A | 条件扩散生成多峰 action sequence；无语言且不是环境动力学 | E1 |
| 7 | [ACT / ALOHA](https://arxiv.org/abs/2304.13705) | RSS 2023 | A | CVAE Transformer 生成 action chunks，强化精细双臂模仿；任务专用 | E1 |
| 8 | [RT-2](https://arxiv.org/abs/2307.15818) | 2023 技术报告 | P | 将动作表示为 token，与 web VLM 数据共同训练，展示语义迁移；action token 不是 world state | E2 |
| 9 | [BridgeData V2](https://arxiv.org/abs/2308.12952) | CoRL 2023 | I | 公开多环境、多任务机器人数据，并显示规模与多样性收益 | E1 |
| 10 | [Open X-Embodiment / RT-X](https://arxiv.org/abs/2310.08864) | ICRA 2024 | I/P | 超过百万条、22 类 embodiment 的异构数据与跨机器人正迁移；normalization 混淆显著 | E1 |
| 11 | [RoboFlamingo](https://arxiv.org/abs/2311.01378) | ICLR 2024 | P | 冻结/轻调 OpenFlamingo，加历史与 policy head；真机和跨 embodiment 证据有限 | E1 |
| 12 | [DROID](https://arxiv.org/abs/2403.12945) | RSS 2024 | I | 76K demonstrations、564 scenes、84 tasks 的 in-the-wild 数据与复现硬件协议 | E1 |
| 13 | [RT-H](https://arxiv.org/abs/2403.01823) | RSS 2024 | P | language motion 形成动作层级并支持在线语言纠正 | E1 |
| 14 | [Octo](https://arxiv.org/abs/2405.12213) | RSS 2024 | P | 约 800K OXE 轨迹训练开放 diffusion generalist policy，强调新平台适配 | E1 |
| 15 | [OpenVLA](https://arxiv.org/abs/2406.09246) | CoRL 2024 | P | 开放 7B VLA、约 970K demonstrations 与可复现 fine-tuning；原始离散解码慢 | E1 |
| 16 | [TinyVLA](https://arxiv.org/abs/2409.12514) | 2024 预印本 | P | 小 VLM + diffusion decoder，强调少样本与快速适配；评测规模有限 | E2 |
| 17 | [LAPA](https://arxiv.org/abs/2410.11758) | ICLR 2025 | I/P | 从无动作视频量化 latent action，再映射到真动作；latent action discovery 不是 WAM | E1 |
| 18 | [RDT-1B](https://arxiv.org/abs/2410.07864) | ICLR 2025 | P | 1B diffusion Transformer 建模双臂高维连续动作；偏专用、预训练成本高 | E1 |
| 19 | [π₀](https://arxiv.org/abs/2410.24164) | RSS 2025 | P | 在 VLM 上加入 flow-matching action expert，覆盖多机器人形态 | E1 |
| 20 | [CogACT](https://arxiv.org/abs/2411.19650) | 2024 预印本 | P | VLM cognition 与专用 diffusion action transformer 解耦；多项设计贡献交织 | E2 |
| 21 | [SpatialVLA](https://arxiv.org/abs/2501.15830) | RSS 2025 | P | Ego3D encoding 与 adaptive action grids 注入空间/跨机器人归纳 | E1 |
| 22 | [FAST](https://arxiv.org/abs/2501.09747) | 2025 预印本 | I/P | DCT 压缩 action chunks，支持高频灵巧动作；token reconstruction 不等于闭环成功 | E2 |
| 23 | [OpenVLA-OFT](https://arxiv.org/abs/2502.19645) | 2025 预印本 | P | continuous action、parallel decoding、chunking 与低秩适配，系统研究速度/成功权衡 | E2 |
| 24 | [GR00T N1](https://arxiv.org/abs/2503.14734) | 2025 预印本 | P\* | 双系统 VLM + flow action model，混合真机、仿真、人类视频与生成轨迹；来源贡献混杂 | E2 |
| 25 | [Gemini Robotics](https://arxiv.org/abs/2503.20020) | 2025 技术报告 | P | frontier multimodal backbone 扩展动作模态与多机器人控制；专有、难独立核验 | E2 |
| 26 | [π₀.₅](https://arxiv.org/abs/2504.16054) | 2025 预印本 | P | 混合 web、机器人和高低层数据，面向陌生环境长程操作；系统归因困难 | E2 |
| 27 | [RIPT-VLA](https://arxiv.org/abs/2505.17016) | 2025 预印本 | P/post | 用稀疏二值 reward 做交互式 RL 后训练；主要在可 reset 仿真 | E2 |
| 28 | [VLA-RL](https://arxiv.org/abs/2505.18719) | 2025 预印本 | P/post | trajectory-level 在线 RL、process reward 与规模化实现；计算和 reward 偏差需审计 | E2 |
| 29 | [SmolVLA](https://arxiv.org/abs/2506.01844) | 2025 预印本 | P | 小型、单 GPU 训练并支持 consumer GPU/CPU 异步执行；社区数据质量不均 | E2 |
| 30 | [Dita](https://openaccess.thecvf.com/content/ICCV2025/html/Hou_Dita_Scaling_Diffusion_Transformer_for_Generalist_Vision-Language-Action_Policy_ICCV_2025_paper.html) | ICCV 2025 | P | diffusion transformer 直接对连续动作去噪，覆盖跨数据训练与少样本真机适配 | E1 |
| 31 | [iRe-VLA](https://arxiv.org/abs/2501.16664) | 2025 预印本 | P/post | 交替 RL 与 supervised learning，缓解大 VLA 在线训练不稳 | E2 |
| 32 | [X-VLA](https://arxiv.org/abs/2510.10274) | ICLR 2026 | P | data-source/embodiment soft prompt 吸收异构数据；可能记忆 dataset identity | E1 |
| 33 | [Gemini Robotics 1.5](https://arxiv.org/abs/2510.03342) | 2025 技术报告 | P | multi-embodiment VLA 加 embodied reasoning，强调长程思考与 motion transfer；专有 | E2 |
| 34 | [Fast-ThinkAct](https://openaccess.thecvf.com/content/CVPR2026/html/Huang_Fast-ThinkAct_Efficient_Vision-Language-Action_Reasoning_via_Verbalizable_Latent_Planning_CVPR_2026_paper.html) | CVPR 2026 | P | verbalizable latent reasoning 压缩显式 CoT；teacher 与低层 policy 贡献需隔离 | E1 |
| 35 | [ActiveVLA](https://openaccess.thecvf.com/content/CVPR2026/papers/Liu_ActiveVLA_Injecting_Active_Perception_into_Vision-Language-Action_Models_for_Precise_3D_CVPR_2026_paper.pdf) | CVPR 2026 | P | 把 camera motion / active perception 纳入 VLA；额外视角与运动成本必须计账 | E1 |
| 36 | [Z-1](https://arxiv.org/abs/2606.31846) | 2026 预印本 | P/post | 在 flow VLA 上做 task-wise GRPO；仿真为主、rollout 成本高 | E2 |
| 37 | [Continual VLA-RL: Simple Recipe Works](https://arxiv.org/abs/2603.11653) | 2026 预印本 | P/post | 系统研究多模型、多 lifelong RL benchmark 的稳定—可塑权衡 | E2 |
| 38 | [LIBERO](https://arxiv.org/abs/2306.03310) | NeurIPS 2023 | I/评测 | 130-task lifelong manipulation，区分 declarative/procedural transfer；仍是仿真分布 | E1 |
| 39 | [SIMPLER](https://arxiv.org/abs/2405.05941) | 2024 原始论文 | I/评测 | 配对 sim-real 验证 policy behavior 与 shift sensitivity；不能替代所有真机端点 | E1 |
| 40 | [VLABench](https://arxiv.org/abs/2412.18194) | 2024 预印本 | I/评测 | 语言、常识与长程推理压力测试；当前 VLA 普遍仍困难 | E2 |

Helix、GR00T N1.5/N1.6 等产业更新保留在检索日志中，但没有重复计为承重 archival 论文。2025–2026 的新模型和 RL 工作预印本比例很高，不能按作者自报 success rate 直接排序。

## 4. VLA 自身的工作簇与冲突

| 工作簇 | 共识 | 尚未解决的冲突 |
|---|---|---|
| 机器人数据规模与通用策略 | 数据多样性通常重要 | 数据量、多样性、筛选质量、模型规模与训练 FLOPs 难解耦 |
| VLM 语义迁移 | web 知识能改善对象、语言和组合泛化 | 更强语义不稳定地转化为精细空间、接触和闭环控制 |
| 动作表示 | token、chunk、diffusion、flow 都可形成强策略 | 离散统一但慢；连续生成强但昂贵；长 chunk 高效却降低反应性 |
| 跨具身 | 异构数据可能正迁移 | normalization、相机、频率、坐标系与专用 head 经常同时变化 |
| 适配与部署 | LoRA、小模型、并行解码显著降低门槛 | 参数量小不等于低端到端 latency、能耗或高 OOD 成功 |
| 长程/层级/主动感知 | hierarchy 提高可解释和可纠正性 | 收益可能来自更强低层 policy、技能库、额外视角或更大推理预算 |
| RL/持续后训练 | policy 可从自己访问到的失败状态继续学习 | reset、reward hacking、on-policy 成本、安全和旧能力遗忘仍关键 |

## 5. 横向证据合同与盲区

- 每条 VLA 路线都应报告 task/object/scene/instruction/embodiment shift，而不只报一个平均 success rate。
- 动作质量要与 control Hz、端到端 latency、chunk horizon、扰动恢复和坐标/归一化协议一起报告。
- 私有 frontier 模型与开放小模型的数据、硬件和评测不同，不能横向读取自报分数。
- 真实失败、近失误、不可逆接触、拒绝/求助、校准与长期遗忘证据明显少于成功轨迹。
- 当前文献仍以 manipulation 为主；navigation、mobile manipulation、humanoid、双臂/灵巧手的接口不可简单互相外推。

这些证据支持七条纯 VLA 母方向：数据/预训练、语义 grounding、动作生成、跨具身、适配/部署、长程层级交互、RL/持续改进。评测、鲁棒性、安全、污染与系统成本作为七条方向的共同证据合同，而不是把所有困难塞进一个宽泛“评价”桶。
