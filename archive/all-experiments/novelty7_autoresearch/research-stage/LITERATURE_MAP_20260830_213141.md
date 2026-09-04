# 扩展文献证据图：VLA / WAM / VLA×WAM

**Run**: `20260830-novelty7-vla-wam`  
**检索截止**: 2026-08-30  
**边界**: 旧 16 条只作种子；排除依赖触觉或力传感器的路线；允许 RGB、RGB-D、PointMap/3D、proprio、执行轨迹与语言。

## 1. 检索与证据完整性

- 在线主检索覆盖 arXiv、OpenAlex、Crossref、DBLP，并交叉读取当日更新的 `awesome-vla-wam`。
- 本地库参与证据综合，重点复核 `CheckVLA`、`When to Trust Imagination`、`WAV`、`Imperfect World Models are Exploitable`、`WorldEval`、`PROWL`、`OA-WAM`、`MRO-GWM`、`PointAction`、`EvoScene-VLA`、`MemoryVLA`、`π0.5` 等全文转写。
- arXiv API 在三组自动检索中多次出现 SSL EOF；OpenAlex 对两组 WAM 查询返回 504；全源默认检索一次超时。缺口用 arXiv 页面、标题精确检索和本地全文补齐，但这仍然不是“证明绝对无人做过”。
- 2026-08-05 之后出现的论文会明显改变边界，尤其是 DreamWAM、Robust-WAM、ForeTime-VLA、LAWA 与 WALL-SS，因此旧版方向判断不能直接沿用。

## 2. VLA 证据簇

| 证据簇 | 代表工作 | 已经覆盖的命题 | 仍未闭合的边界 |
|---|---|---|---|
| 动作表示与生成 | FAST；OpenVLA-OFT；AsyncVLA (2511.14148)；ABot-M0 (2602.11236) | tokenization、diffusion/flow、低维 action manifold、token 级自修正 | 动作输出是否有校准语义；执行中分布变化如何反馈到 action head |
| intent / action 解耦 | DIAL (2603.29844)；CoT/Reasoner 类 VLA | latent intent、future latent 与低层 inverse dynamics | intent 正确但执行失败时，系统如何定位责任与采取不同干预 |
| 长时记忆 | MemoryVLA (2508.19236)；MemoryVLA++ (2606.09827)；EvoScene-VLA | 历史检索、场景更新、memory+imagination | 记忆写入依据若来自错误预测，如何避免错误撤销或错误保持 |
| 3D / 4D / 对象 grounding | SpatialVLA；4D-VLA；Lift3D-VLA (2607.06564)；POT-VLA；OA-WAM | 当前 3D 输入、未来几何辅助、对象地址与对象状态 | “有 3D”不等于能识别谁出了错；功能几何策略变化仍缺统一诊断 |
| 校准与验证 | CoVer-VLA (2602.12281)；CheckVLA (2607.26789) | 指令—动作对齐验证、执行期 action-conditioned verification | 现有接口大多把异常压成一个分数，没有区分 robot / model / observation 来源 |
| 经验学习与 TTT | EVOLVE-VLA (2512.14666)；π*0.6；TT-VLA；RIPT-VLA | progress reward、on-policy corrections、test-time update | 错误反馈由谁造成；错误 world feedback 可能把 policy 更新坏 |
| 动态与执行时序 | DynamicVLA；AsyncVLA；ForeTime-VLA (2608.20735) | moving objects、phase/time-to-transition、非均匀生成 | 预测误差与真实执行误差的在线归因仍未成为标准问题 |

## 3. WAM 证据簇

| 证据簇 | 代表工作 | 已经覆盖的命题 | 仍未闭合的边界 |
|---|---|---|---|
| RGB 视频未来 | DreamZero；LingBot-VA；τ0-WM (2606.01027) | video-action joint modeling、candidate rollout、progress scoring | 视觉逼真不代表 action-following，也不代表可安全作为执行真值 |
| 控制充分 latent | Fast-WAM (2603.16666)；LaWAM (2606.15768)；ImageWAM (2606.19531)；Being-H0.7；LAWA (2608.24882) | 训练期 world objective、latent endpoint、image editing、latent intention | 哪类状态变量足以支持具体干预决策，而非只提高平均成功率 |
| 超越 RGB 的结构化未来 | PointWorld (2601.03782)；MRO-GWM (2606.01950)；DreamWAM (2608.04996)；Lift3D-VLA | point flow、object Gaussian、motion/geometry/semantics future supervision | “加 depth/geometry”本身已不新；关键要证明其改变了决策或错误归因 |
| 长时与 memory | Mem-World (2606.18960)；MemoryWAM；Next Forcing (2606.11187)；WALL-SS (2608.26239) | 4D memory、多 chunk、分钟级压缩历史 | 模型在长历史中何时错、错在哪个因果源，仍缺明确接口 |
| 模型自验证 | WAV (2604.01985)；WorldEval；Foundational WM failure monitor | state plausibility、action reachability、policy ranking、conformal anomaly | WAM 自己不可靠与机器人真的失败会产生相似 residual |
| 可利用性与保守使用 | Imperfect World Models are Exploitable (2605.15960)；PROWL；WoVR (2602.13977) | exploit 不可避免性、安全 horizon、KL 约束、policy-WM co-evolution | 在实际 VLA verifier 中如何识别“不要修 policy，而应怀疑 WAM” |
| 运行时信任 | When to Trust Imagination (2605.06222)；CheckVLA | prediction-observation consistency 决定 chunk 长度或 repair | 一维 discrepancy 将不同原因混在一起，错误干预尚未被系统评估 |
| 测试时适应 | WAM-TTT (2607.06988)；AdaJEPA；system-ID/rapid adaptation 系列 | 人类视频 steering、adaptive memory、deployment adaptation | 适应触发信号若来自错误归因，可能造成自强化漂移 |
| 效率与部署 | Faster/Fast/Flash-WAM；QuantWAMs (2607.28405) | 跳过视频、蒸馏、量化、低延迟 | 速度不是空白；需要和实际干预收益、false intervention 一起评估 |

## 4. VLA×WAM 强交叉证据簇

| 强交叉角色 | 最近邻 | 已占据范围 | 可防守的剩余问题 |
|---|---|---|---|
| world objective 塑造 policy | Fast-WAM、DreamWAM、Robust-WAM、DIAL、ForeTime-VLA | RGB/semantic/geometry/future latent 辅助已高度拥挤 | 不应再以“加入 Depth/PointMap loss”为核心创新 |
| WAM rollout 选动作 | τ0-WM、DreamSteer、VLA-Reasoner、CoVer | sample/rerank/MCTS/progress | 普通 reranking 已拥挤；必须处理模型漏洞或归因 |
| 执行期验证与恢复 | When to Trust、CheckVLA、HELM、ReViP | mismatch detection、chunk adaptation、rollback/replan、false completion | **异常来源归因**：执行失败、WAM 失配、观测含混不能用同一干预 |
| imagined RL / 共同进化 | World-VLA-Loop (2602.06508)、VLAW、WoVR、WAM-RL | synthetic rollouts、co-evolution、hallucination regulation | independent ground-truth anchor 与反馈污染仍开放，但工程较重 |
| 对象/3D/action effect | OA-WAM、PointWorld、MRO-GWM、Lift3D、DreamWAM | object address、3D dynamics、geometry auxiliary | 纯组合重叠高；需要新的决策问题，如 functional strategy shift 或 cause attribution |
| 长时 memory+world | EvoScene、MemoryVLA++、Mem-World、Event/Chain 类工作 | past belief、future imagination、revisable state | 普通 memory/retraction 已拥挤；错误证据的来源与干预代价仍少 |

## 5. 本轮改变判断的最新论文

1. **DreamWAM (2608.04996)** 已把 RGB、motion、geometry、semantics 作为互补未来监督；因此“给 WAM 加 Depth/PointMap”不能再作为核心 claim。
2. **Robust-WAM (2608.05903)** 已用 semantic foresight 对抗 appearance shift；因此“语义 latent 提高 OOD”也不够。
3. **ForeTime-VLA (2608.20735)** 已做 future-token distillation、phase、time-to-transition、relational geometry 与 action-equivalence；因此简单的未来 token/阶段蒸馏已经撞车。
4. **LAWA (2608.24882)** 已将 latent action 作为 future intention，平衡 future-aware generalization 与 latency。
5. **WALL-SS (2608.26239)** 已覆盖 scale-wise long-horizon action-conditioned world generation 与压缩 memory。

## 6. 证据支持的优先 gap

- **G1：WAM discrepancy 的因果来源没有被可靠区分。** 当前执行 verifier 多输出单个 trust/risk 分数；WAV 检查模型本身，CheckVLA/When-to-Trust 检查执行一致性，但两类证据没有统一成 source-aware decision。
- **G2：VLA/WAM 对功能几何的“策略结构泛化”缺乏专门评测。** 3D/对象表示很多，但同一语义任务在新对象对几何下是否需要改变接近/接触/阶段结构，尚缺标准 benchmark；非 VLA 的 GIFT/FMB/RPDiff 是强祖先。
- **G3：WAM 的 action support 与 planner exploitation 缺少 VLA 级统一压力测试。** 但 WoVR、WAV、PROWL 与理论 exploitation 已使方法空间拥挤。
- **G4：world feedback 污染 policy memory/TTT 的问题自然且重要。** 但需要长期闭环数据，首篇执行风险较高。
- **G5：控制充分状态应按决策而不是重建误差定义。** DreamWAM/Temporal Ratio/Fast-WAM 已占大量表示贡献，剩余空间更适合诊断或因果评测。

## 7. 初步结论

当前最干净、最自然、最可用现有 π0.5 与非触觉传感器验证的缺口是 **G1：source-aware world-model verification**。它不是再加一个几何 head，而是改变系统在 disagreement 后的动作：修复 policy、重新观察，还是暂时不信/更新 WAM。是否达到 novelty > 7.0 仍须进入最近邻查重和独立 reviewer gate。
