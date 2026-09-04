# VLA × WAM 强交叉母方向版图（扩展版，16 条）

**Run ID：** `20260806-vla-wam-expanded-field-map`  
**状态：** `evidence-map complete / awaiting human macro-direction selection`  
**边界：** 本文只回答“有哪些可区分的母方向、为什么值得研究、证据与成本如何”；不提出具体 Idea、hypothesis、benchmark、模型组合或实验方案。

## 1. 怎么读这张图

这里不按 Transformer、diffusion 或 video latent 等实现名词切方向，而按 **world model 在 VLA 系统里承担什么因果角色** 来切：

```text
VLA × WAM
├─ A. 塑造 VLA 看见的世界（H1–H4）
│  ├─ 预测表征  ├─ 潜在动作  ├─ 结构化物理状态  └─ 持久 belief
├─ B. 帮 VLA 思考、判断与止损（H5–H10）
│  ├─ 视觉计划  ├─ 反事实 rollout  ├─ 主动感知
│  └─ critic  ├─ policy 评测  └─ 安全与恢复
├─ C. 改写 VLA 的学习经验（H11–H13）
│  ├─ 生成数据  ├─ 想象式后训练  └─ 主动采数与共演化
└─ D. 把 world 与 action 做成可迁移、可适应的整体（H14–H16）
   ├─ 联合基础模型  ├─ 跨具身 action-effect  └─ 部署时系统辨识
```

双轴标记：世界表示分为 R1 decoded video、R2 pixel/video latent、R3 task-centric latent、R4 explicit state/dynamics；用途分为 U1 representation、U2 proposal、U3 candidate evaluation、U4 planning、U5 imagined optimization、U6 joint model。R 与 U 是正交轴，不是 10 个互斥类别。

“当前配置适配度”按 `2 GPUh pilot / 8 GPUh total / 无真机 / 仿真优先 / 复用公开 checkpoint 与日志` 判断；“探索优先分”按科学影响 25%、开放空间 20%、证据缺口 20%、当前配置适配 20%、可信初证速度 15% 粗排。它只帮助人工看图，不构成自动选题。

## 2. 总览

| 组 | ID | 母方向 | 一句话解释 | 证据形态 | 当前配置适配 | 探索优先分 |
|---|---|---|---|---|---|---:|
| A | H1 | 预测式 world objective 塑造 VLA 表征 | 让 VLA 因为预测未来而更懂动作后果 | 中高、已有稳定簇 | 高 | 74 |
| A | H2 | 无动作视频中的潜在动作与 action-effect | 从“只看到变化”中恢复可迁移的干预语义 | 中高、机制仍未闭合 | 高 | 79 |
| A | H3 | 3D、对象、接触与触觉世界 grounding | 把 RGB 世界改写为对象、几何和接触动力学 | 中、2026 快速增长 | 中低 | 68 |
| A | H4 | 持久 belief、记忆与对象连续性 | 遮挡和跨阶段后仍知道世界处于什么状态 | 低、直接证据新 | 高 | 84 |
| B | H5 | 视觉子目标、视频计划与层级规划 | 先想象任务过程长什么样，再让 VLA 执行 | 高、路线稳定 | 中低 | 65 |
| B | H6 | 动作条件反事实 rollout 与 steering | 在模型里试演候选动作，再选或修正 | 中高、快速增长 | 中 | 72 |
| B | H7 | 主动感知与信息收集 | 先决定看哪里、摸哪里、试什么来减少不确定性 | 直接交叉稀疏 | 高（仿真） | 78 |
| B | H8 | WM-derived reward、value、progress 与 critic | 让想象未来回答“这条轨迹有多好” | 广义成熟、直接交叉中等 | 高 | 86 |
| B | H9 | world model 作为 policy/checkpoint evaluator | 部署前在 learned world 中比较整套策略 | 中高、2025–2026 激增 | 很高 | 92 |
| B | H10 | 预测式安全、恢复与 selective autonomy | 执行中预判失败并过滤、改写、停机或求助 | 监控较强、恢复较弱 | 中高 | 87 |
| C | H11 | WM 生成经验与动作标签桥 | 把生成视频或未来轨迹转成 VLA 可学习的数据 | 中低、邻域工作多 | 中 | 75 |
| C | H12 | 想象环境中的 VLA RL/post-training | 让 VLA 在 learned environment 中继续学习 | 高增长、竞争激烈 | 中低 | 71 |
| C | H13 | 弱点驱动采数、课程与 policy–world 共演化 | policy 和 WM 互找弱点、互相补数据 | 低、刚形成工作簇 | 低 | 76 |
| D | H14 | 联合 World–Language–Action 基础模型 | 同一系统共同理解语言、预测世界并产生动作 | 高、foundation-scale 拥挤 | 低 | 54 |
| D | H15 | 跨具身 action-effect 接口与迁移 | 共享“动作造成什么效果”，而非共享关节坐标 | 中低、严格 VLA 证据薄 | 中低 | 74 |
| D | H16 | 部署时 system identification 与 test-time adaptation | 从新身体、新视角和新动力学的交互历史中在线认环境 | 低但已有直接锚点 | 中高 | 82 |

## 3. A 组：世界表征与 grounding

### H1 — 预测式 world objective 塑造 VLA 表征

**人话。** 训练 VLA 时要求它同时预测未来图像、运动、几何或 latent，希望动作表征因理解“接下来会发生什么”而更物理。

**科学问题与耦合。** 核心不是能否生成漂亮未来，而是 world objective 是否在匹配数据、参数与算力后，因果改善闭环 action quality。常见位置是预训练或辅助监督；推理时 world head 可以移除。覆盖 R1–R3、U1/U6，代表锚点为 P01–P05、P28、P32、P61、P64。

**边界与缺口。** 推理期真正比较候选动作归 H6；把 rollout 变成新训练经验归 H11/H12；共同架构本身归 H14。现有增益常与额外视频、模型容量和训练 token 混杂，且 world loss 更低不保证动作更好。

**方向级决定性证据。** 需要 matched-data、matched-capacity、matched-compute 的 action-only、静态辅助与 future-prediction 对照，并用切断 world path 后的闭环退化证明它确实承重。公开 checkpoint 上的小型辅助头或切断审计适合当前配置，适配度 **高**。

### H2 — 无动作视频中的潜在动作与 action-effect 学习

**人话。** 大量人类/网络视频没有机器人控制标签；这条路线试图从“世界如何变化”中发现 latent intervention，再把它翻译为真实机器人动作。

**科学问题与耦合。** 要区分相关运动与可干预动作语义，并验证 latent action 能否在不同数据源和身体之间稳定落到 native action。主要覆盖 R2/R3、U1/U2/U6；锚点 P06–P11、P20、P25、P51。

**边界与缺口。** 只学视频 embedding 不算；普通 inverse dynamics 若未利用 actionless video 或 action-effect 结构也不算。latent action 在统计上不可唯一辨识，现有方法通常仍需要每个 embodiment 的少量动作桥，接触丰富场景的闭环证据有限。

**方向级决定性证据。** 关键是证明 latent intervention 对真实 action effect 可恢复、对 held-out embodiment 可迁移，并优于同量有标签视频表征和普通 inverse-dynamics 对照。离线日志和少量适配可做低成本初证，适配度 **高**。

### H3 — 3D、对象、接触与触觉结构化世界 grounding

**人话。** 不把世界只压成一团 RGB latent，而是显式表示哪些对象存在、几何怎样、哪里接触、是否滑动以及动作会如何改变这些变量。

**科学问题与耦合。** 研究结构先验能否让 VLA 对遮挡、组合变化和接触物理更稳，而不是只提升重建质量。覆盖 R3/R4 与 U1/U2/U4/U6；锚点 P12–P16、P19、P66。

**边界与缺口。** 静态点云 encoder、对象检测或把触觉直接拼进输入都不是 world model；语言条件目标点云若不对候选动作建模，只是 goal proposal。对象 slot 会漂移，3D 方法依赖标定/教师，触觉高度依赖传感器，跨硬件证据很薄。

**方向级决定性证据。** 应证明结构变量在动作下可预测、可被 policy 消费，并在 matched sensory information 下超过整体 latent；还要分离传感器增益与 dynamics 增益。无专用硬件时只能做仿真/公开数据机制验证，适配度 **中低**。

### H4 — 持久 belief、记忆与对象连续性

**人话。** 当对象被遮住、相机移动或任务跨多个阶段时，机器人仍能维持“世界现在到底怎样”的可修正信念，而不只是回看几帧历史。

**科学问题与耦合。** 历史观测和动作应更新 action-conditioned belief，并让 VLA 依据隐藏状态、不确定性和 imagined future 行动。主要覆盖 R3/R4 与 U1/U3/U6；直接锚点为 P17、P19，P18、P45、P50 是重要记忆边界。

**边界与缺口。** 更长 context、KV cache、检索记忆或循环状态不自动等于 belief dynamics。当前直接证据多为 2026 预印本；对象身份交换、错误记忆修正、超长遮挡和 belief calibration 尚缺系统验证。

**方向级决定性证据。** 必须排除当前帧捷径和阶段记忆，验证 belief 随新证据正确更新、错误时能撤回，并把 belief quality 与动作收益连接。合成遮挡和离线轨迹可低成本控制变量，适配度 **高**。

## 4. B 组：推理、决策与 assurance

### H5 — 视觉子目标、视频计划与层级规划

**人话。** 先想象任务中间应该变成什么样，再让 VLA 或低层控制器执行这些关键帧、视频片段或语言步骤。

**科学问题与耦合。** WM 的主要输出是计划表示，而不是直接选择当前动作。覆盖 R1–R3、U2；锚点 P12、P13、P20–P25。

**边界与缺口。** 显式 rollout 多个动作序列并搜索动作归 H6；纯视频预训练归 H1。视觉合理不等于机器人可执行，IDM 和低层控制器常是隐藏瓶颈，模块归因、接触物理与闭环重规划仍弱。

**方向级决定性证据。** 需要把计划可视质量与可执行性分开，并在匹配低层控制器和时延下证明视觉计划优于语言/状态子目标。冻结模型审计可行，但训练视频模型和长时生成超预算，适配度 **中低**。

### H6 — 动作条件反事实 rollout、MPC、reranking 与 steering

**人话。** VLA 先给几种动作方案，WM 分别预演“这样做会怎样”，系统再挑选、修正或滚动重规划。

**科学问题与耦合。** 必须有 `action candidate → predicted consequence → decision` 的反事实链。覆盖 R2–R4、U3/U4；锚点 P15、P26–P33。

**边界与缺口。** 静态 value rerank 归 H8；比较整套 policy 归 H9；没有 learned dynamics 的普通 simulator planning 不算。policy 提出的 OOD 动作往往正是 WM 最不可靠的区域，planner 又会主动利用模型误差；候选预算和推理延迟常未公平匹配。

**方向级决定性证据。** 需同时检验 action sensitivity、real/imagined consequence 一致性、planning regret 与 wall-clock matched 的闭环收益。短时、少候选的 latent rollout 可做，长时高分辨率规划不适合当前预算，适配度 **中**。

### H7 — 主动感知、信息收集与 belief-aware control

**人话。** 机器人有时不该立刻抓取，而应先换视角、触摸或试探，以消除真正影响任务的未知量。

**科学问题与耦合。** WM/belief 的不确定性驱动 information-gathering action，新观测再更新 belief 与后续 VLA 决策。覆盖 R3/R4、U4，并把 uncertainty 作为显式接口；锚点 P34–P36。

**边界与缺口。** 首要目标必须是 information gain、belief reduction 或 identification；直接追求任务回报归 H6/H8，因风险拒绝归 H10，为未来数据集采样归 H13。严格的 language-VLA × learned-WM 操作证据最稀，epistemic/aleatoric 混淆与真实交互成本未解。

**方向级决定性证据。** 信息收益必须转化为下游任务价值，并相对随机探测、启发式探测和同交互预算的直接行动成立。仿真中可精确控制隐藏状态，适配度 **高（仿真）**；不能据此外推真实触觉或硬件安全。

### H8 — WM-derived reward、value、progress 与 critic

**人话。** 不一定让 WM 负责完整规划，而是让它回答“这条未来好不好、进展多少、成功概率多大”。

**科学问题与耦合。** 预测视频或 latent trajectory 被压成 reward、value、progress 或 success probability，再用于 policy 训练或 action rerank。覆盖 R2–R4、U3/U5/U6；锚点 P24、P29、P31、P33、P37–P39。

**边界与缺口。** 用完整 dynamics 搜索动作主归 H6；评整套 policy 归 H9；输出成为硬风险干预归 H10。likelihood shortcut、reward hacking、共享 foundation bias 和对新 policy 分布的失准是核心问题；value-only 是判断完整 WM 是否必要的强边界。

**方向级决定性证据。** 应比较 world-derived critic、观察-only/VLM critic、value-only 与可得的真实结果标签，重点看 calibration、ranking 和 policy 改善能否同时成立。冻结 rollout 与轻量 critic 适合当前预算，适配度 **高**。

### H9 — world model 作为 policy/checkpoint evaluator

**人话。** 在真实部署前，让不同 VLA 或 checkpoint 在 learned world 中完整运行，先判断谁更可靠、哪里会失败。

**科学问题与耦合。** 决策单位是完整 policy，而非一步动作；WM 要在该 policy 的动作分布下持续模拟反馈，再产生 success/safety/progress 排名。覆盖 R1–R3、U3；锚点 P19、P40–P47。

**边界与缺口。** 只评视频质量不算；部署时逐步 veto 归 H10。现有强项多是相对排序，绝对成功率与尾部风险校准较弱；OOD actions、长时物体交互和 evaluator 与被评 policy 的共享偏差是主要风险。

**方向级决定性证据。** 必须用 paired ground-truth outcomes 检查 rank correlation、绝对 calibration、coverage–risk 和跨 policy family 泛化，而不是只展示想象视频。可复用 checkpoint、日志和冻结 WM，是当前配置下适配度 **很高** 的母方向。

### H10 — 预测式安全、恢复与 selective autonomy

**人话。** 机器人边执行边预判继续下去会不会失败，必要时过滤动作、改写后缀、重规划、停机或请求帮助。

**科学问题与耦合。** `committed action/chunk → imagined outcome or uncertainty → runtime intervention`；覆盖 R2–R4、U3/U4。锚点 P16、P36、P40、P47–P50。

**边界与缺口。** 必须实际改变运行时决策；只有 failure detector 指标不够。部署前整套 policy 审核归 H9，普通 nominal MPC 归 H6。检测证据显著多于成功恢复；false-negative 尾部、不可逆接触失败、policy 更新后的校准和 human burden 仍缺。

**方向级决定性证据。** 评价应同时考虑危险漏报、正常动作误杀、任务收益、干预成本与恢复后的最终结果。仿真适合故障注入和 monitor/filter 审计，完整 recovery 与真实安全结论较难，综合适配度 **中高**。

## 5. C 组：训练、数据与闭环学习

### H11 — WM 生成经验与动作标签桥

**人话。** 让 WM 生成未来视频、纠正轨迹或 neural trajectory，再用 latent action、IDM 或几何监督把它们转成 VLA 可学习的数据。

**科学问题与耦合。** 关键不是“生成更多视频”，而是每单位 synthetic experience 最终产生多少可验证的 policy 增益。覆盖 R1–R3、U1/U2；锚点 P06–P11、P19、P42、P51–P53、P60。

**边界与缺口。** 只把视频模型改成 action-conditioned WM、却不训练 policy，是数据引擎边界；在 learned environment 中在线优化 policy 归 H12。伪动作、几何和接触误差会复合，生成量大不代表有效样本多。

**方向级决定性证据。** 需要报告 synthetic-to-real action fidelity、effective sample yield，并与同量真实数据、普通增强和非世界模型视频生成匹配比较。离线数据审计可做，完整生成流水线可能偏重，适配度 **中**。

### H12 — 想象环境中的 VLA RL/post-training

**人话。** 把 world model 当成可交互训练环境，让 VLA 在里面试错、获得奖励并继续优化，然后回到 ground-truth 环境验收。

**科学问题与耦合。** world dynamics、reward 和 termination 共同定义 imagined MDP，VLA 的新动作分布又持续挑战 simulator。覆盖 R1–R4、U5；锚点 P16、P37、P38、P54–P59。

**边界与缺口。** 固定生成训练集归 H11；只在推理时选动作归 H6。该方向增长最快之一，但 simulator exploitation、复合误差、真实回放校准和多种子稳定性仍是硬问题。

**方向级决定性证据。** imagined 高回报轨迹必须回放到独立 ground truth，且在匹配真实交互与总训练算力后优于 real-only、普通增强和 model-free 后训练。当前预算可审计 frozen-WM exploitation，但可信完整 post-training 较吃力，适配度 **中低**。

### H13 — 弱点驱动采数、课程与 policy–world 共演化

**人话。** policy 暴露 WM 的盲区，WM 又找到 policy 的失败区域；二者据此主动补数据和更新，而不是一次训练后永远冻结。

**科学问题与耦合。** 核心是闭环采样是否比被动扩数据更快覆盖真正影响控制的分布，同时避免 policy 与 WM 一起学错。主要是 U5/U6 与 alternating/co-evolution；锚点 P16、P46、P48、P55、P57、P59、P60。

**边界与缺口。** 当前任务中的信息动作归 H7；固定 WM 的单轮后训练归 H12；普通 dataset balancing 不算。直接 VLA×WAM 强锚点仍少，选择偏差、共享 scorer 偏差、灾难性漂移和人类 oracle 成本未解决。

**方向级决定性证据。** 需要在同交互预算下比较随机/静态课程/弱点驱动采数，并独立验收每轮 WM calibration 与 policy performance，防止共同过拟合。持续闭环和多轮统计超出小 pilot 舒适区，适配度 **低**。

## 6. D 组：联合架构、迁移与适应

### H14 — 联合 World–Language–Action 基础模型

**人话。** 不把 VLA 和 WM 简单串联，而让同一系统共同理解语言、预测未来、估值并输出动作。

**科学问题与耦合。** 研究共享或交错的 world/action representations 是否产生不可由独立级联替代的协同。主要覆盖 U6 和 R1–R3；锚点 P01、P02、P04、P05、P11、P12、P14、P29、P33、P61–P65。

**边界与缺口。** 只有 next-action token、只共享视觉 backbone 或没有语言接口不算强交叉。“联合”已非常拥挤，额外数据、参数和训练 token 是普遍 confound，world path 是否真正承重常未证。

**方向级决定性证据。** 必须在 matched scale 下比较 action-only、world-only、separate cascade 与 joint model，并通过切断/冻结路径验证协同。公开 checkpoint 小消融尚可，从头训练 foundation model 远超预算，适配度 **低**。

### H15 — 跨具身 action-effect 接口与迁移

**人话。** 不同机器人关节坐标不同，但“让杯子向左移动”这样的物理效果可以共享；这条路线用 action-effect 作为身体之间的中间语言。

**科学问题与耦合。** 要验证 `native action → shared effect → target native action` 是否双向可恢复，并保持因果、接触和语言语义。覆盖 R3/R4 与 U1/U2/U4/U6；锚点 P05–P11、P51、P63、P65–P67。

**边界与缺口。** 没有 learned dynamics 的普通 action tokenizer/adapter 不算；只有跨机器人数据混训也不算。严格的 VLA×rollout-WM 证据较薄，latent action 不可辨识、手工几何接口和目标本体少量标签依赖仍明显。

**方向级决定性证据。** 应在 held-out embodiment 上匹配目标数据和 adapter 容量，验证 action-effect 可恢复性、闭环 transfer 与非世界模型对照。公开多机器人日志可做离线机制验证，但真正跨硬件结论受零真机限制，适配度 **中低**。

### H16 — 部署时 system identification 与 test-time adaptation

**人话。** 新相机、新负载、新身体或动力学变化出现时，系统先从近期交互判断“现在这个世界/机器人是什么系统”，再调整 VLA，而不是整套重训。

**科学问题与耦合。** 关键是历史交互是否识别了可影响预测和控制的隐藏系统变量，以及 adaptation 是否安全、快速并避免遗忘。覆盖 R3/R4 与 U3/U4/U6，更新制度为 in-context/test-time；直接锚点 P55、P63、P67、P68，P69 是 agent 边界。

**边界与缺口。** 仅根据当前状态重规划归 H6；普通 domain adapter 没有 dynamics identification 不算。ICWM 已使该方向不再是“没有直接证据”，但证据宽度仍窄：新视角强于新形态/接触，safe probing、校准与持续漂移未解决。

**方向级决定性证据。** 必须把 system identification 与普通上下文记忆、规划和参数微调分开，并考察少量安全交互后的预测校准、控制恢复与遗忘。离线/仿真 shift 可做，适配度 **中高**。

## 7. 版图结论（仍不是 Idea 选择）

- **证据最密、竞争最激烈：** H5、H6、H9、H12、H14。这里容易找到强 baseline，但“再做一个更大模型/更长 rollout”很难构成独立问题。
- **当前配置最容易形成可信方向级初证：** H1、H2、H4、H7（仿真）、H8、H9，以及 H10 的 monitor/filter 部分；这只是资源匹配，不代表已经选定。
- **证据最稀、研究空间较大：** H4、H7、H13、H15、H16；其中 H13 需要多轮闭环，H15 受硬件/多本体数据限制，H16 已有直接工作但外延尚窄。
- **最容易出现伪进展的区域：** H1/H14 的规模混杂，H5 的“视频合理但不可执行”，H6/H12 的 model exploitation，H9/H10 的相对排序冒充绝对安全，以及 H11/H15 的伪动作误差。
- 同一篇论文可以跨多个方向，但同一项研究主张必须按主要 endpoint 归到一个方向；否则会把组件堆叠误当成多个贡献。

本版图停在母方向层；`research.selected_macro_direction` 保持 `null`。
