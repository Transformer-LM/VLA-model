# WAM-only 母方向版图（7 条）

**定位：** 这张图只回答“学习式世界模型自身有哪些大方向”。它不要求大型 VLA，也不把“给 VLA 加一个 world head”当作 WAM 本体问题。  
**评分：** 科学影响 25%、开放缺口 20%、WAM 专属性 20%、当前配置可行性 20%、取得可信初证速度 15%。分数是调查优先级，不是成功概率或自动选择。

## 总览

| ID | 母方向 | 一句话解释 | 密度/拥挤度 | 分数 |
|---|---|---|---|---:|
| W1 | Action-conditioned observable video WAM | 动作给定后，把可见未来预测对 | 高、拥挤 | 74.0 |
| W2 | Task-centric latent 与 belief dynamics | 只维护控制真正需要的隐藏状态 | 高、成熟但有根本争议 | 88.5 |
| W3 | Object/3D/contact 结构化动力学 | 显式追踪物体、几何与接触如何变化 | 中等、接口分散 | 85.0 |
| W4 | Memory、system ID 与快速适应 | 从历史判断当前世界的隐藏配置和变化 | 中低、开放空间大 | 88.5 |
| W5 | Counterfactual planning 与 MPC | 先想象多个动作后果，再闭环选择 | 高、成熟 | 87.0 |
| W6 | Imagined policy learning 与 data engine | 把 learned world 当训练场或数据源 | 高；机器人高保真证据不足 | 80.5 |
| W7 | 功能评测、校准与安全 world model | 判断策略会否成功，以及何时不该相信模型 | 中等、增长最快 | **93.0** |

## W1 — Action-conditioned observable video WAM

**人话解释。** 给定机器人将怎样动，模型要把未来画出来；重点不是视频好看，而是变化真的由动作引起，且足以支持控制。

**为什么是独立母方向。** 它研究的是可观察未来的生成表征，解释性强、可复查，但要同时承担外观、物理、接触和长时一致性。它与 W5 的区别是“预测什么”而非“怎样规划”。

**方法与锚点。** 像素 autoregression、video diffusion、token/video latent、关键帧预测；代表簇包括 action-conditioned video benchmark、UniPi、RoboDreamer、DreamGen、WorldEval。

**边界与冲突。** 被动视频生成、文本到视频、没有 action sensitivity 的模型不算。感知画质与动作信息脱钩，逆动力学也可能把 WAM 的缺陷藏起来。

**决定性证据。** 同初态不同动作应产生可辨识且与真实 effect 一致的未来；功能评价应尽量不依赖 IDM，并在匹配候选数、时延和 FLOPs 时连接到闭环端点。

**资源与风险。** 视频数据、显存、存储和 rollout 延迟最高；当前 2/8 GPUh 配置只适合复用公开 checkpoint 做功能审计，不适合从头训练基础视频模型。评分 **74.0**。

## W2 — Task-centric latent 与 belief-state dynamics

**人话解释。** 不必预测每个像素，只保留“为了决定动作真正需要知道的状态”，并用历史维护对不可见世界的信念。

**为什么是独立母方向。** 核心科学问题是何种压缩状态同时具备预测性、可控性、记忆与迁移能力；这与 W3 的显式 object/3D state 不同。

**方法与锚点。** RSSM、stochastic belief、value/reward-shaped latent、decoder-free task latent、JEPA/feature dynamics；PlaNet、Dreamer、SLAC、Dreaming、TD-MPC/2、MWM、RePo、DINO-WM、DreamerV3。

**边界与冲突。** 只有 encoder、没有 action-conditioned transition 的表征学习不算。DreamerV3 支持 reconstruction belief 的通用性，Dreaming/RePo/DINO-WM 则说明 nuisance reconstruction 可能浪费容量，目前没有统一赢家。

**决定性证据。** 在同数据、模型规模和 planner 下比较可解码视频、task latent 和结构 state；同时看闭环成功、belief calibration、多步 drift、history ablation 与单位计算控制价值。

**资源与风险。** 低到中等算力即可做可靠机制比较；风险是 latent loss 更好却不改善控制，或 reward shortcut 破坏迁移。评分 **88.5**。

## W3 — Object/3D/contact 结构化动力学

**人话解释。** 让模型明确追踪物体、几何、粒子、接触、力或触觉，而不是把所有物理关系藏进不可解释向量。

**为什么是独立母方向。** 结构偏置可能带来物体持久性、组合性和接触可解释性，但也把问题转移给 state extraction；这是与 W2 最关键的权衡。

**方法与锚点。** object slots/graphs、keypoints、particles、3D flow/Gaussian、contact graph 与 tactile dynamics；DPI-Net、Keypoints into the Future、action-conditioned tactile prediction、DeformNet、RoboEXP、GWM。

**边界与冲突。** 静态 object detector、静态 scene graph 或“看起来有 3D”的视频不够；必须有实体、几何或接触 transition。使用 privileged state 的优势不能直接外推到真实 RGB。

**决定性证据。** 从真实观测恢复结构后仍保持 event/contact accuracy、多步物理一致性和闭环收益；去掉 privileged state，并与同预算 latent/video WM 比较。

**资源与风险。** 多视角、RGB-D、触觉或 simulator state 提高数据成本，接口也难统一。评分 **85.0**。

## W4 — 在线 system ID、memory 与快速 world-model adaptation

**人话解释。** 遇到新负载、摩擦、相机、延迟或环境变化时，先从短历史判断“现在这个世界怎样运转”，再修正预测。

**为什么是独立母方向。** 它关注隐藏配置、变化点和适应速度，而不是静态多域泛化；部分可观测 memory 与 dynamics identification 在这里汇合。

**方法与锚点。** recurrent/context belief、episodic/spatial memory、context encoder、residual dynamics、online update/change-point；Context-aware Dynamics、Online Dynamics Learning、DORA、ReDRAW，PlaNet/SLAC 提供 belief 基础。

**边界与冲突。** 仅增加上下文长度或静态多域训练不算。context 可能编码 behavior policy 而不是 physics，DORA 表明 policy shift 与 dynamics shift 必须分开。

**决定性证据。** 在受控 dynamics、perception 与 action-latency shift 下报告 probe-to-recovery、adaptation regret、变化检测、校准和安全探测成本，而非只报预测误差。

**资源与风险。** sim-first pilot 成本低；真实部署结论仍需硬件，主动 probing 可能危险。评分 **88.5**。

## W5 — Learned-model counterfactual planning 与 MPC

**人话解释。** 让 WAM 先想象多种动作后果，选择更好的动作，并在新观测到来后继续重规划。

**为什么是独立母方向。** 这是 world model 的控制用途方向，可以消费 W1–W4 任一表征；核心不是换 planner 名字，而是预测如何形成更好的闭环决策。

**方法与锚点。** CEM/trajectory sampling、gradient/diffusion planning、visual goal search、short rollout + terminal value；PETS、PlaNet、SOLAR、TD-MPC/2、DINO-WM、UniPi、RoboDreamer。

**边界与冲突。** 只做 actor–critic imagination 属 W6；离线 policy audit 属 W7。representation 与 planner 经常一起变化，因此很多提升无法归因。

**决定性证据。** 同一个 WM 下比较无规划、learned-model planning 与 oracle dynamics，并匹配候选数、horizon、replanning 频率、FLOPs 和 wall-clock；还要统计 planner 利用模型漏洞的频率。

**资源与风险。** 模型训练可中等，但候选搜索和长 horizon 推理昂贵。评分 **87.0**。

## W6 — Imagined policy learning 与 world-model data engine

**人话解释。** 把学到的世界当作训练场，让策略在里面练习，或从里面生成新的训练轨迹，再回真实环境验收。

**为什么是独立母方向。** 它改变训练分布和策略本身，而 W5 只在推理时规划；价值来自降低真实交互或扩大数据覆盖。

**方法与锚点。** latent imagination actor–critic、short branched rollouts、pessimistic offline MBRL、video/LAM/IDM synthetic data；Dreamer、DayDreamer、MoDem-V2、MOPO、MOReL、COMBO、DreamerV3、GWM、DreamGen。

**边界与冲突。** 普通图像增强、程序化 simulator data 和联合 WLA next-token 训练不算。长 rollout 提供远见也放大 model bias；合成数量不等于有效样本量。

**决定性证据。** 在固定真实交互、训练步数、参数与总 FLOPs 下，检查 imagined/真实 return gap、policy exploitation 和 synthetic effective yield，并与非 WM 数据引擎比较。

**资源与风险。** policy retraining、多种子和 rollout 都昂贵；完整结论常超过 8 GPUh，当前更适合做 exploitation 的早期证伪。评分 **80.5**。

## W7 — 可校准的 policy evaluator、风险预测与安全 world model

**人话解释。** 在不真实执行或少执行的前提下，判断一个策略会不会成功、哪里会失败，以及什么时候 world model 自己也不该被相信。

**为什么是独立母方向。** 它把预测能力转成外部评估、校准和风险覆盖，不是为当前一步在线选动作；这是模型—策略—环境三层证据最薄弱的一环。

**方法与锚点。** policy-conditioned rollout、success/value/risk head、VLM judge、conformal/selective prediction、functional benchmark；action-conditioned benchmark、SafeDreamer、WorldEval、WorldGym、WorldArena。

**边界与冲突。** 普通 success classifier 或视频质量 metric 不算。保留相对 checkpoint 排序不等于能对新 policy、对抗动作或罕见失败作绝对安全判断。

**决定性证据。** paired real/WM rollout；policy ranking、ECE/Brier、coverage–risk、危险 false-negative、policy/action/task OOD 与单位评价成本必须共同报告。

**资源与风险。** 有公开日志与 rollout 时只需低到中等算力，最匹配当前零真机配置；共享 foundation bias 与尾部失败稀缺是主要风险。评分 **93.0**。

## 七方向的边界

- W1–W4 主要回答“世界应怎样表示、记忆和适应”；W5–W7 回答“预测怎样进入决策、学习和审计”。
- W2 的 latent 可以被 W5、W6 或 W7 使用，因此表示与用途不是互斥分桶。
- W5 改变当前动作选择，W6 改变未来 policy，W7 评价或拒绝 policy；三者的 endpoint 不同。
- 本图没有选中任何方向；具体任务、模型、benchmark 和实验路线仍为空。
