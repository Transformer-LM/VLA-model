# VLA-only 母方向版图（7 条）

**定位：** 这张图回答“VLA 自身有哪些母方向”。动作 token、chunk、diffusion 或 flow 都仍可属于纯 VLA；只有显式学习并消费未来环境 dynamics 时才跨入 WAM。  
**评分：** 科学影响 25%、创新空间 20%、证据缺口 20%、当前 2/8 GPUh 配置可行性 20%、取得可信初证速度 15%。不自动选方向。

## 总览

| ID | 母方向 | 一句话解释 | 密度/拥挤度 | 分数 |
|---|---|---|---|---:|
| V1 | 机器人数据规模、混合与通用策略预训练 | 哪些数据和配比真正产生通用 policy | 很高、资本/数据密集 | 64 |
| V2 | Web/VLM 知识到物理动作的 grounding | 把“听懂”稳定转成“做对” | 高、语义强而物理仍弱 | 79 |
| V3 | 高频、连续、多峰动作的统一生成接口 | token、chunk、diffusion、flow 怎样取舍 | 很高、仍有清晰因果问题 | 86 |
| V4 | 跨具身动作语义与异构机器人迁移 | 不同身体怎样共享同一种动作意图 | 高、强声明多、严格留出少 | 80 |
| V5 | 少样本适配、小模型与实时部署 | 用少数据、普通硬件把 VLA 装到新平台 | 高、工程与科学交汇 | **90** |
| V6 | 长程分层推理、记忆、主动感知与纠正 | 会拆任务、会找信息、会从中途错误恢复 | 中等、快速增长 | 83 |
| V7 | RL / 交互式 post-training 与持续改进 | 从自身成功失败继续学习而不遗忘 | 中等偏低、2025–2026 新主线 | 79 |

## V1 — 机器人数据规模、混合与通用策略预训练

**人话解释。** 研究“给机器人看多少、哪些、怎样混合的数据，才能学出真正通用的 policy”，而不只是把某个模型做大。

**为什么是独立母方向。** 机器人数据不是同分布 token：不同任务、操作者、相机、频率、坐标系和身体可能互相促进，也可能负迁移。数据组成和 scaling law 本身就是科学问题。

**方法与锚点。** 多任务真机收集、跨机构 mixture、质量/覆盖重加权、robot/web/human/synthetic mix、generalist pretraining；RT-1、BridgeData V2、Open X/RT-X、DROID、Octo、OpenVLA、π₀、GR00T N1。

**边界与冲突。** 主变量是数据量、质量、任务和平台构成；具体 action decoder 属 V3，完整留出新身体属 V4。现有跨论文无法分清收益来自数据量、多样性、筛选、参数还是训练 FLOPs。

**决定性证据。** 固定模型和总训练预算，给出数据数量、来源多样性与质量的 scaling curve、完整留出分布上的负迁移，以及每小时/每美元/每次示范的有效收益。

**资源与风险。** foundation-scale 预训练明显超过 8 GPUh；当前只能做数据审计、子集重加权或冻结模型的有限检验。评分 **64**。

## V2 — 互联网 VLM 知识如何真正落到机器人动作

**人话解释。** 机器人不仅要听懂“杯子、抽屉和清理”，还要把这些语义和常识可靠地变成物理动作。

**为什么是独立母方向。** VLM 能识别概念、组合语言和做高层推理，但空间精度、接触和控制是另一套能力；VLA 的核心承诺正是桥接两者。

**方法与锚点。** VLM co-finetuning、multimodal prompt、frozen/adapter backbone、语义—几何双流、specialized action expert；CLIPort、VIMA、PaLM-E、RT-2、RoboFlamingo、OpenVLA、CogACT、Gemini Robotics。

**边界与冲突。** action token 仍是动作输出，不是未来 world state。若显式预测未来并用于决策才进入交叉域。更大的 VLM 不稳定地带来更高精细操作成功。

**决定性证据。** 匹配机器人数据与 policy head，消融 web/VLM pretraining；在未见概念、语言组合和视觉类别上同时测语义选择与闭环物理成功，避免把 VQA 进步当控制进步。

**资源与风险。** frontier VLM 难复现，但开放 checkpoint 的冻结 backbone/LoRA 可做窄验证。评分 **79**。

## V3 — 高频、连续和多峰动作的统一生成接口

**人话解释。** 研究动作应被当作单步 token、动作块、扩散轨迹还是 flow，才能同时做到快、准、平滑和可反应。

**为什么是独立母方向。** 动作表示决定量化误差、时间压缩、控制频率、多峰行为和推理延迟，是 VLA 从语言模型走向真实闭环的核心接口。

**方法与锚点。** discrete autoregression、regression、ACT chunk、FAST frequency tokenization、diffusion transformer、flow matching、parallel action head；ACT、Diffusion Policy、RDT-1B、π₀、FAST、OpenVLA-OFT、Dita。

**边界与冲突。** 只建模动作和时间结构，不预测环境转移，因此这些方法不是 WAM。离散 token 接口统一但慢且有量化误差；diffusion/flow 表达强但训练/采样昂贵；长 chunk 高效却降低闭环反应。

**决定性证据。** 同一 backbone、数据和总算力比较表示族与 chunk 长度，并共同报告闭环成功、Hz、端到端 latency、smoothness、扰动恢复和总控制成本。

**资源与风险。** 公开小模型和仿真足以做有判别力的对比；最大风险是实现、采样步数和超参数不公平。评分 **86**。

## V4 — 跨具身动作语义与异构机器人迁移

**人话解释。** 不同机械臂、人形机器人和控制频率的命令不同，但 policy 应能共享“同一种动作意图”。

**为什么是独立母方向。** 这不是泛泛的数据规模问题，而是观察、动作与身体接口的等变性、归一化和可迁移表示问题；完整未见 embodiment 是关键 endpoint。

**方法与锚点。** shared/latent action space、adaptive action grids、embodiment prompt/token、per-robot decoder、geometry/equivariance、multi-embodiment mixture；Open X/RT-X、Octo、SpatialVLA、GR00T N1、X-VLA。

**边界与冲突。** 多机器人平均分提高不等于留出新身体成功。camera convention、control rate、坐标系、normalization 和专用 head 常同时变化，难以归因。

**决定性证据。** 完整留出形态或控制 convention；匹配目标数据和 adapter 容量，比较 shared interface 与 per-robot head，报告零/少样本曲线、action recoverability 和 source→target transfer matrix。

**资源与风险。** 多机器人仿真可行，但异构数据清洗和大矩阵训练可能超预算；无真机限制机械误差外推。评分 **80**。

## V5 — 少样本适配、小模型与实时部署

**人话解释。** 一个预训练 VLA 能否用几十到几百条示范快速装到新平台，并在普通 GPU、边缘设备或 CPU 上稳定实时运行。

**为什么是独立母方向。** foundation model 的能力只有经过数据高效适配、动作接口对齐和低延迟 serving 才成为机器人能力；参数量只是系统账本的一小部分。

**方法与锚点。** LoRA/adapter、action-head-only tuning、distillation/quantization、小型 backbone、parallel decoding、asynchronous action chunk；Octo、OpenVLA/OFT、TinyVLA、SmolVLA、Dita。

**边界与冲突。** V1 研究预训练数据规律，V5 研究下游 success-per-demo 和 deployment。小模型不自动意味着更低端到端时延、能耗或更高 OOD 成功。

**决定性证据。** 同一目标数据和硬件报告 success–demonstration curve、训练 FLOPs、显存、wall-clock、Hz、能耗、输入输出规范和 OOD 结果，而不只报参数量。

**资源与风险。** 最匹配当前配置，可复用开放 checkpoint 与 LoRA；无真机时只能证明仿真适配和计算效率。评分 **90**。

## V6 — 长程分层推理、记忆、主动感知与人类在线纠正

**人话解释。** policy 要会把长任务拆开、记住历史，信息不够时主动看，并允许人用语言在中途纠正或帮助恢复。

**为什么是独立母方向。** 直接 action prediction 在多阶段任务中会累积语义、状态和控制误差；层级、memory、active perception 与 intervention 都在解决“如何保持长程闭环”。

**方法与锚点。** skill/subtask hierarchy、language motion、latent/verbal reasoning、scene/episodic memory、active camera control、human intervention/recovery；SayCan、RT-H、π₀.₅、Gemini Robotics 1.5、Fast-ThinkAct、ActiveVLA。

**边界与冲突。** 若通过 learned future rollout 比较动作则进入 H2。分层提升可能来自人工技能库、更强低层 policy、额外视角或更大推理预算，并非 hierarchy 本身。

**决定性证据。** 固定低层 policy 与总推理/观察预算，比较 direct、显式/latent hierarchy、memory、主动视角和语言 intervention；报告长程成功、误差传播、恢复率、额外动作与 latency。

**资源与风险。** 仿真可做，但复杂环境与 proprietary frontier 模型难复现；模块多时归因成本高。评分 **83**。

## V7 — VLA 的 RL / 交互式 post-training 与持续改进

**人话解释。** 不再只模仿成功示范，而是让 policy 从自己访问到的成功、失败和反馈中继续变强，同时保留旧能力。

**为什么是独立母方向。** behavior cloning 的训练分布与 policy 自己造成的状态分布不同；交互式 post-training 直接处理这一缺口，并把 reward、exploration、稳定—可塑性与安全带入 VLA。

**方法与锚点。** online/offline RL、GRPO/PPO-style post-training、process reward、RL–SFT alternating、parameter-efficient continual learning、failure/recovery data；iRe-VLA、RIPT-VLA、VLA-RL、Z-1、Continual VLA-RL。

**边界与冲突。** 在真实或标准 simulator 中更新 policy 属纯 VLA；主要在 learned world 中优化转入 H4/W6。短期新任务收益可能伴随 reward hacking、旧技能遗忘与鲁棒性下降。

**决定性证据。** 匹配 demonstrations、environment interactions 与计算量比较 SFT、offline fine-tuning 和 online RL；多种子报告真实/高保真成功、旧任务遗忘、reward exploit、失败、reset 与安全成本。

**资源与风险。** 当前只适合少任务、小规模 simulator 检验；大 VLA on-policy RL 很可能超过 8 GPUh。评分 **79**。

## 横向证据合同

评测、鲁棒性、安全、污染和系统成本不另凑成一个笼统方向，而是七条路线共同必须满足：

- task/object/scene/instruction/embodiment shift 与最坏子组；
- success 之外的 Hz、latency、chunk horizon、恢复、拒绝/求助和危险 false-negative；
- 数据、参数、训练 token、推理采样、environment interactions 和真机 trials 的匹配账本；
- 开放与私有系统不可直接按作者自报分数横排。

本图保持 `selected_macro_direction = null`，没有选择具体模型、任务、benchmark 或 Idea。
