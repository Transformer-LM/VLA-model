# H1 候选 Idea 联合集

**Run:** `20260806-vla-wam-expanded-field-map`  
**阶段:** idea-discovery / 生成完成、尚未排序  
**生成规则:** 合并独立机制生成、视频/数据路线、定向文献和远程可行性审计；仅做机械去重，不采用生成者自排结果  
**硬边界:** world objective 仅用于训练；推理期不 rollout、不规划、不 rerank；不使用真实机器人；总预算 8 GPUh，pilot 先限 2 GPUh

## 1. Robotics Problem Frame

- **Embodiment:** LIBERO 仿真中的单臂桌面操作；不外推到双臂、移动操作或真实硬件。
- **Task family:** pick/place、object/goal/spatial 与短多阶段 manipulation；pilot 只选少量动作后果清晰且 baseline 未完全饱和的任务。
- **Observation:** 第三视角/腕部 RGB、proprioception、language instruction，以现有 StarVLA/LIBERO 接口为准。
- **Action:** 连续 action chunk；所有 treatment/control 使用完全相同的动作空间、chunk 和执行协议。
- **Learning regime:** 固定离线演示数据；同一 action-only checkpoint 分支做短程 PEFT；world target 尽量离线缓存。
- **Available assets:** 个人 StarVLA bundle、LIBERO 数据与闭环评估、DINOv2、action-only checkpoint；全部位于 `<PERSONAL_RESEARCH_ROOT>`。
- **Compute:** 默认只用物理 GPU 2/3；每次作业前检查；仅在四卡均空闲时才可临时用 0/1；2 GPUh pilot、8 GPUh 总上限。
- **Safety/integrity:** 原 CF-DynAlign dirty tree 不可触碰，`lambda_cf` 不可开启；LIBERO-CF evaluation-only；已有 strict validation cache 不得宣称为全新 final test。
- **Contribution types allowed:** 可证伪方法、因果诊断或严格评估协议。负结果必须保留。

## 2. 统一比较合同

每个候选在进入训练前都必须明确匹配：初始化 checkpoint、训练样本、数据顺序、可训练 policy 参数、辅助 head 参数量、target 维度、optimizer、更新步数、action-loss token、辅助 target token 和近似训练 FLOPs。若某项无法匹配，必须把差异列为 treatment，而不能把增益归因于 predictive objective。

世界预测器还需先在 strict episode/temporal holdout 上超过 persistence 与 action-agnostic predictor；否则对应候选只能作为负例，不得以非零权重训练策略。

## 3. 未排序候选

### C01 — 时间箭头 × 动作身份的 2×2 因果矩阵

- **一句话:** 用 `future/past × correct/shuffled action` 四格等预算处理，检验只有“未来且动作身份正确”时是否出现额外策略收益。
- **机制:** 同一 frozen target encoder 和同形 predictor 分别预测等距离 future 或 past latent；动作在同任务、相近阶段/速度桶内保持分布地置换。主统计是 difference-in-differences：`(future_correct - future_shuffle) - (past_correct - past_shuffle)`。
- **最近邻/碰撞:** FLARE、VLAFlow、Motion Image Diffusion；SelfWAM 已做 action perturbation，但未见完整 time-arrow × identity 的 VLA matched matrix。贡献必须是识别协议，而不是 future head。
- **Matched controls:** action-only、dummy-head；四格 target 维度/方差/时间距离/head/FLOPs一致；报告每格世界预测难度，避免“past 更难”解释。
- **最低 pilot:** 2 个 LIBERO 任务，缓存 latent，四格各 1 seed 的短 PEFT；先看严格世界诊断与 paired action loss/小规模 rollout。
- **正信号:** DiD 在预注册表征诊断和闭环 success 上同号，且 future-correct 单独超过等预算 placebo。
- **反驳/负结果价值:** future-shuffle 同样提升说明只是正则化；past 同样提升说明不是预测特异性；world loss 降而控制不变说明表征旁路。
- **8 GPUh:** pilot 可行；四格全 benchmark×3 seeds 不可行。
- **真实硬件:** 不需要。

### C02 — 可控性匹配的预测目标阶梯

- **一句话:** 先量化 target 中有多少信息只能由动作解释，再检验该可控性是否预测 world objective 的策略迁移收益。
- **机制:** 从同一 transition 构造等维/归一化的 current/static latent、full future latent、future-current residual、motion latent；定义 `C(y)=L(y|o,l)-L(y|o,l,a)`。
- **最近邻/碰撞:** Motion Image Diffusion 已比较 future image/motion/language；DreamWAM 已比较 motion/geometry/semantics；新意只能来自事前可控性度量、等预算处理与收益单调关系。
- **Matched controls:** 同一投影维度、head、loss scale、target token、steps；重建难度/SNR 单独作为协变量；加入 random orthogonal target。
- **最低 pilot:** 离线估计所有 target 的 `C(y)`，只训练最高与最低两个极端加 action-only。
- **正信号:** 策略迁移收益更随 `C(y)` 而非 reconstruction loss 或 target variance 变化。
- **反驳/负结果价值:** 不相关说明“可控性”不是有效 target 选择原则，可解释现有 target 消融的不稳定性。
- **8 GPUh:** 两极+baseline 可行；完整阶梯多种子不可行。
- **真实硬件:** 不需要。

### C03 — 预测子空间的闭环因果中介

- **一句话:** 擦除共享表示中携带 action-specific future residual 的低秩子空间，检验 predictive objective 的任何闭环增益是否由该信息承载。
- **机制:** 在 treatment/placebo checkpoint 的 hidden states 上拟合 `S_dyn`；推理时只投影掉 `S_dyn`，比较 world-objective gain 是否消失。
- **最近邻/碰撞:** FLARE/GAM 有 layer 与 future-alignment 消融；低秩 probe/activation erasure 是通用工具。新意必须来自 paired VLA closed-loop mediation，而不能只是 probe accuracy。
- **Matched controls:** 同 rank/能量随机子空间、外观/语言子空间、投影前后 action-distribution drift、action-only checkpoint。
- **最低 pilot:** 复用 C01 或其他 treatment checkpoint；CPU/单卡拟合 probe，再做少量 paired rollout。
- **正信号:** 擦除 `S_dyn` 对 treatment 的损害显著超过随机子空间，并特异地消除 treatment 相对 placebo 的增益。
- **反驳/负结果价值:** 可解码但擦除无效说明 predictive feature 是旁观变量；随机擦除同样有害说明只是破坏 bottleneck。
- **8 GPUh:** 依赖已有 checkpoint 时高可行；不能独立支撑主张。
- **真实硬件:** 不需要。

### C04 — Predictive gradient 的层级路由

- **一句话:** 在匹配梯度范数和 LoRA 参数量时，只允许同一 world loss 更新视觉层、connector/VLM 中层或 action expert，定位负迁移来源。
- **机制:** stop-gradient 控制 world gradient 的入口层，保持 forward target 和 head 不变。
- **最近邻/碰撞:** FLARE 已观察层位敏感，GAM 已做多 split-layer 消融，碰撞很高。
- **Matched controls:** 相同 trainable 参数量、update norm、head、token 和 steps；action-only 与 dummy auxiliary。
- **最低 pilot:** 只比较早层与晚层两个极端。
- **正信号:** 路由产生稳定、可解释的 world/action trade-off，并跨任务保持。
- **反驳/负结果价值:** 所有路由相同说明层位不是关键；只由 update norm 解释则否定机制。
- **8 GPUh:** 双极可行；完整层网格不可行。
- **真实硬件:** 不需要。

### C05 — 预测时间带宽与 action-chunk 对齐

- **一句话:** 在固定 target-token 总量下比较短于、等于和长于 action chunk 的预测 horizon，检验有用监督是否集中于策略可控带宽。
- **机制:** horizon 改变但总 target 数、head 和训练 FLOPs不变；附加等距离 past control。
- **最近邻/碰撞:** 多步预测和 horizon ablation 普遍存在；Motion Image Diffusion 已将运动窗口与 chunk 对齐，独立 novelty 较弱。
- **Matched controls:** horizon-specific target normalization、同总 token、同 head；current/past placebo。
- **最低 pilot:** 三 horizon 单 seed 的 offline 世界诊断；只让最有区分力的两个进入策略短训。
- **正信号:** chunk-aligned horizon 在 controllability 与 policy transfer 上同时形成峰值。
- **反驳/负结果价值:** 最短 horizon 最好或无差异，则“action-chunk resonance”不成立。
- **8 GPUh:** 缩小策略分支后可行。
- **真实硬件:** 不需要。

### C06 — 只保留 action-compatible world gradient

- **一句话:** 只传播与 action-loss 梯度不冲突的 predictive gradient，并用 norm-matched 随机/反向梯度判断负迁移是否来自优化冲突。
- **机制:** 逐层或选定 adapter 上计算 gradient cosine，使用 aligned-only/orthogonal projection。
- **最近邻/碰撞:** PCGrad、CAGrad、ForkMerge 等通用多任务优化直接相邻；若没有 world-specific prediction，极易成为“套方法”。
- **Matched controls:** raw world gradient、projected、norm-matched random、action-only；匹配有效 update norm 与二次反传预算。
- **最低 pilot:** raw vs aligned-only 两组，记录 per-layer cosine 和 heldout action loss。
- **正信号:** 只在 predictive target 可靠且梯度相容时转为控制收益，并超过 generic random auxiliary。
- **反驳/负结果价值:** 任何 auxiliary 都同样受益，说明不是 H1 特异机制。
- **8 GPUh:** 二次反传昂贵，完整消融风险高。
- **真实硬件:** 不需要。

### C07 — Action-contrastive future JEPA

- **一句话:** 要求正确动作比同任务置换动作更接近真实 future latent，显式学习 action-outcome binding。
- **机制:** future JEPA loss 加 action margin/contrastive negatives。
- **最近邻/碰撞:** AquaJEPA 已有 action-conditioned JEPA/action margin；SelfWAM 已测 action sensitivity；本候选高度碰撞。
- **Matched controls:** ordinary future alignment、same-task shuffle、random negatives、inverse-dynamics auxiliary。
- **最低 pilot:** correct/shuffle 两组短训。
- **正信号:** action margin 提升 strict action sensitivity 且迁移到闭环控制。
- **反驳/负结果价值:** shuffle 不影响则 world objective 没有使用动作身份。
- **8 GPUh:** 可行，但 novelty 风险高。
- **真实硬件:** 不需要。

### C08 — 冻结视频先验的 action residual objective

- **一句话:** 先用 action-agnostic frozen predictor解释自然场景演化，仅让 policy 辅助分支预测真实未来相对该预测的 residual。
- **机制:** target=`future latent - frozen action-agnostic forecast`，试图隔离可控变化。
- **最近邻/碰撞:** AVID 的 frozen video prior + action adaptation 很接近；V-JEPA 2 与多种 residual dynamics 也相邻；容易滑向 H6/H11。
- **Matched controls:** full future latent、zero residual、random frozen predictor、等参 adapter。
- **最低 pilot:** 只有本地存在可用且通过 holdout 的 frozen video prior 才启动，否则立即 defer。
- **正信号:** residual 的 action controllability 明显高于 full future，且同预算策略迁移更强。
- **反驳/负结果价值:** residual 只放大噪声或无控制收益，说明通用先验未有效分离不可控变化。
- **8 GPUh:** 现有资产未发现对应视频权重，执行风险高。
- **真实硬件:** 不需要。

### C09 — Strict Validity–Transfer Gate

- **一句话:** 把“world predictor 是否在严格 holdout 上真正使用动作”作为预测监督进入策略前的硬准入门，并实验预测 validity 与 policy transfer 的关系。
- **机制:** 对一组受控质量的 predictor，先测相对 persistence/action-agnostic 的 strict advantage 与 action-shuffle sensitivity；只有 bootstrap 下界超过预注册阈值的 predictor 才允许非零 auxiliary weight。通过数据量、horizon corruption 或 checkpoint maturity构造 validity strata。
- **最近邻/碰撞:** WAM 文献通常报告 predictor 指标但少有硬准入；通用 model selection、safe auxiliary learning 和 validation gating 是强近邻。贡献必须是“world validity 预测 action transfer”的可证伪关系，而非工程 if-statement。
- **Matched controls:** 同 architecture、target、policy、steps；只改变预先构造的 predictor validity；invalid predictor 永不作为正方法训练，只作为安全负例/离线诊断。
- **最低 pilot:** 复用现有 strict-failed F 作为 invalid stratum，另训练/获得一个通过门的轻量 predictor；两者先做离线验证，只有 valid 分支进入 policy pilot。
- **正信号:** strict world advantage 对 action transfer 有预注册方向和阈值效应；standard split 指标不能替代 strict 指标。
- **反驳/负结果价值:** strict validity 不能预测 transfer，说明需要别的机制；如果没有 predictor 过门，则诚实终止而不消耗策略训练预算。
- **8 GPUh:** predictor 缓存/小模型可行；获得一个真实过门 predictor 是最大风险。
- **真实硬件:** 不需要。
- **本地重叠:** 不复用 CF-DynAlign 方法主张；其 strict-failed F 只能作为负诊断，`lambda_cf` 永远为 0。

### C10 — Held-out Action-Transfer Gate

- **一句话:** 每个 world-gradient 更新只有在一个冻结 mini-validation stream 上不恶化 action loss 时才被接纳，测试 predictive objective 的负迁移能否被在线阻断。
- **机制:** 类似 one-step lookahead/ForkMerge：比较 action-only update 与 action+world update 对 heldout action loss 的即时影响，再选择分支或权重。
- **最近邻/碰撞:** validation-based auxiliary weighting、ForkMerge、多任务优化高度相邻；H1 特异性最弱。
- **Matched controls:** action-only、固定 lambda、random auxiliary、gradient projection；严格限制 validation 重用并独立 final evaluation。
- **最低 pilot:** 小 adapter 上固定-lambda vs transfer-gated 两组；预先冻结 mini-validation stream。
- **正信号:** 对已知 harmful target 能拒绝，对 valid target 能保留，并在 final heldout/rollout 上超过固定 lambda。
- **反驳/负结果价值:** 仅优化 mini-validation 或退化为永远拒绝，说明 gate 无科学/实用价值。
- **8 GPUh:** 额外 forward/branching 增加成本，双组 pilot 勉强可行。
- **真实硬件:** 不需要。

## 4. 机械去重与碰撞记录

- “普通 future latent head”“推理时删除 future head”“clean action conditioning”“self-mask/geometry/semantic target”“action perturbation”没有单列，因为已被 VLA-JEPA、Fast-WAM、SelfWAM、DreamWAM 或 LiLa-WAM直接占据。
- “冻结 E/F/G、预测动作后果再对齐语言目标效果”没有单列，因为它与个人目录中的 CF-DynAlign 基本重复，且当前实现/strict F 均未过门。
- C03 是可附着于其他 treatment 的机制候选；评审需决定它能否作为主贡献，不能因增量算力低而自动升格。
- C04–C08 即使被后续淘汰也保留在永久候选历史中，避免只记录幸存者。

## 5. 下一门

将本文件与 `H1_DIRECTED_LITERATURE.md`、`H1_WAM_ROUTE_CARDS.md` 交给一个未参与候选生成的 reviewer。Reviewer 必须：

1. 独立评分 novelty、H1-specific mechanism、identifiability、8 GPUh feasibility、benchmark credibility、negative-result value；
2. 明确区分“新方法”“新诊断/发现”“普通 ablation”；
3. 最多推荐 3 个进入深查新；
4. 若没有候选值得训练，必须返回 `REVISE/NO-RUN`，不能为了推进流程强选。

