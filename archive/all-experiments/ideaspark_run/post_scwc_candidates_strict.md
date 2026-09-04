# Post-SCWC 严格机制缺口审查

**审查截止：** 2026-08-31  
**硬门槛：** strict novelty 下界必须 **> 7.0**；7.0 仍为 FAIL  
**范围：** 无触觉；VLA、WAM 或 VLA×WAM；不启动实验

## 结论先行

本轮只保留 **2 个**候选，没有为了凑满 3 个而保留临界项：

| 排名 | 候选 | strict novelty | naturalness | 判定 |
|---|---|---:|---:|---|
| 1 | Earliest Passive Observable Witness（ESW）+ Observability-Hazard Verification | **7.2–7.7** | **8.4/10** | 保留 |
| 2 | Contact-Phase Perturbation Controllability（CPPC） | **7.1–7.5** | **7.3/10** | 有条件保留 |

没有第三项通过。PCCS、Event-Time WAM 以及若干普通 memory/progress 变体均因 exact-mechanism 邻近工作或经典机制组合而被压至 `<=7.0`。

这里的“保留”只表示：在已核验的 primary literature 中，尚未找到覆盖其不可约机制的单篇论文，且其组合不是显然的模块拼装。它**不表示已经证明不存在先行工作**，也不构成 GPU 实验授权。

---

## 候选 1：Earliest Passive Observable Witness + Observability-Hazard Verification

### 要解决的精确问题

长时任务中的关系谓词（如 `grasped(o)`、`inside(o,c)`、`closed(drawer)`）经常在物理上已经成立或失效，但当前 RGB/proprio 仍无法区分两种情况。普通 verifier 在每一时刻都输出成功/失败，等价于强迫模型在“证据原则上还没出现”时猜答案，会导致：

- 过早宣布完成；
- 把正确进度错误回滚；
- 遮挡阶段反复改写任务记忆；
- 将“尚不可观察”误当作“执行失败”。

核心命题不是再做一个 failure classifier，而是显式学习：**某个谓词最早在什么时候、通过什么被动观测证据才具有可验证性。**

### Exact mechanism

1. 在模拟器中构造 matched hidden-state twins：两条状态拥有相同可见 RGB、proprio、语言和机器人位姿，但某个隐藏谓词分别为真/假。
2. 从两个 twin 执行完全相同、位于冻结 VLA 支持内的 suffix `a[t:t+H]`，不加入主动诊断动作。
3. 在真实相机噪声、遮挡和视角条件下，标注两个未来观测分布第一次可被区分的时间：

   `tau* = inf {tau : O_{t+tau}^+ and O_{t+tau}^- are distinguishable}`。

   若在 horizon 内始终不可区分，则使用 right-censoring，而不是伪造一个失败标签。
4. 训练 action-conditioned WAM/verifier 输出 competing-risk、interval-censored witness hazard：真谓词证据何时出现、假谓词证据何时出现、以及哪一对象区域/观测通道应承载证据。
5. 运行时，在 predicted witness opportunity 到来前把谓词保持为 `PENDING`；只有当机会出现且实际证据支持某一假设时才 commit/retract。WAM 输出的是**可观察性时机**，不是 reward/value，也不进行候选动作 reranking。

### 最强先行工作与组合威胁

- [How Visible Are Silent Manipulation Failures?](https://arxiv.org/abs/2606.03134) 已直接研究 false success 中视觉和 proprioception 能恢复多少信息，是最强单篇问题近邻；但它做 episode-level modality separability，不编译 matched predicate twins、同 suffix 的 first witness，也不把不可观察区间纳入在线进度提交语义。
- [IntentVLA](https://arxiv.org/abs/2605.14712) 已通过 AliasBench 研究相似观测下由历史/阶段造成的动作歧义，是 matched aliasing 的强近邻；但目标是 history-conditioned action generation，不是谓词的未来可观察性。
- [Runtime Monitoring via Embedding Temporal Logic](https://arxiv.org/abs/2605.12651) 已在 embedding trace 上做时序谓词监控和 conformal calibration；它假定 trace 中已有可评价证据，不估计“证据最早何时原则上可能出现”。
- [Foresight](https://arxiv.org/abs/2606.23085)、[CheckVLA](https://arxiv.org/abs/2607.26789) 和 [When to Trust Imagination](https://arxiv.org/abs/2605.06222) 已覆盖 WAM latent failure monitoring、未来—现实不一致和执行期干预，但都没有 observation opportunity / censoring 语义。
- 经典 POMDP distinguishability、partial-observation runtime verification 和 survival/competing-risk modeling 是明确的组合威胁。

### 不可约 delta

不可约贡献必须同时包括：

1. **matched hidden-state twins**，而不是普通成功/失败轨迹；
2. **同一个 policy-supported suffix**，从而将差异限定为隐藏谓词的未来可观察后果；
3. **first passive witness / right-censoring label**，而不是每帧二分类；
4. witness hazard 真正改变在线语义：witness 之前 `PENDING`，witness 之后才允许 commit/retract。

若删掉任一项，工作会退化成 AliasBench、failure detection、三值 temporal monitor 或普通 progress estimator。

### 最强致命反对

Reviewer 可以指出：这只是 POMDP observability 与三值 runtime monitoring 的机器人实例化；而且 `tau*` 并非谓词的固有属性，它依赖 suffix、相机、policy 和判别器。若论文把 `tau*` 写成普适真值，主张不成立。

此外，某些谓词在纯 RGB/proprio 下永远无被动 witness。方法必须诚实输出 censored/non-verifiable，不能把等待本身包装成验证成功。

### Claim ceiling

可主张：**policy-conditional、sensor-conditional 的 earliest passive witness supervision 减少了证据出现前的错误完成和错误回滚。**

不可主张：证明了物理谓词真值；提供通用形式化可观察性保证；或对未建模相机/真实世界域偏移仍然正确。

### E0 feasibility 与 kill test

**非 GPU compiler/oracle E0 可行，建议先做；本报告没有实际启动。**

- 在至少 3 类谓词（抓持、包含、抽屉闭合）上各构造 >=300 matched twins；固定 VLA/script suffix，加入相机噪声与遮挡。
- 检查是否存在真正的 delayed-witness 区域，而不是第 0 帧已可区分或整个 horizon 永远不可区分。
- 与 fixed-time binary verifier 和 ordinary three-state monitor 比较，匹配观测、特征和 classifier capacity。

预注册 kill：满足任一项即停止。

1. 至少两个 predicate family 中，`initially ambiguous -> later passively distinguishable` 的样本比例低于 **25%**；
2. witness gating 在 matched final AUC 下，未将 pre-evidence false commit/retract 至少降低 **30% relative**；
3. 超过 **40%** 的 episode 因长期 `PENDING` 导致任务停滞或超时；
4. 换 suffix 或相机后 `tau*` 排序相关性低于 **0.5**，且条件化模型无法恢复。

---

## 候选 2：Contact-Phase Perturbation Controllability（CPPC）

### 要解决的精确问题

RGB 外观相似不代表物理关系相同。夹爪贴近物体、真正抓住物体、物体在容器边缘卡住，可能只有微小视觉差异，但“动作怎样传递到对象运动”的局部结构已经改变。

CPPC 不再仅比较一条 WAM 预测与真实图像的 pixel/latent residual，而是询问：

> 在当前实际观测下，对动作做小的安全反事实扰动，WAM 预测的对象效果空间是否发生与 grasp/release/insertion 相符的 rank、subspace 或 nullspace 转换？

### Exact mechanism

1. 冻结 action-conditioned WAM，并使用 RGB-derived object effect representation；模拟器 object state/PointMap 只能作为训练或 E0 teacher，部署不得依赖 privileged geometry 或 tactile。
2. 在 VLA 当前 action chunk 附近生成成对、policy-supported 的安全微扰 `a+epsilon*d_j` 与 `a-epsilon*d_j`。对 stochastic WAM 使用 common noise/common seed，有限差分得到局部 action-to-object-effect Jacobian：

   `J_t[:,j] = (e(F(o_t,a+epsilon*d_j)) - e(F(o_t,a-epsilon*d_j))) / (2 epsilon)`。
3. 不使用 `||J||` 单标量，而追踪 singular values、effective rank、principal subspace angle 与 task-axis nullspace。典型事件签名例如：

   - pre-grasp：夹爪动作对目标对象效果近似低耦合；
   - grasp-established：末端平移方向进入对象效果 principal subspace；
   - release：该耦合消失；
   - constrained insertion：被环境约束的横向方向进入 nullspace/高残差区域。
4. 只有当观察后的 CPPC signature 跨过与目标关系一致的 phase-transition template 时，才把相应 progress predicate 作为已建立/已失效；否则保持不确定或触发普通恢复。
5. 无 candidate search、WAM reward/value、DPO 或 test-time reranking。微扰只在冻结 WAM 内反事实执行，不在真实机器人上探测。

### 最强先行工作与组合威胁

- [WorldSimProbe](https://arxiv.org/abs/2608.09298) 是最强单篇 WAM 近邻：它已经测试 local control sensitivity、action-to-motion correspondence、interaction grounding 和 dynamics；但输出是 simulator-faithfulness benchmark，不把局部 response Jacobian 的 rank/subspace transition 用作对象关系进度 verifier。
- [WorldEcho/WorldSync](https://arxiv.org/abs/2608.24885) 已覆盖 action interventions 与 intervention-effect alignment，并证明 WAM 会忽略 off-expert actions；但其目标是改善 WAM action following，不从局部 differential structure 识别 contact phase。
- [CheckVLA](https://arxiv.org/abs/2607.26789) 已用冻结 WAM 做执行期 verification；差异在于它监测 committed rollout 与真实观察的 mismatch，而 CPPC 检查当前状态下 action-effect map 的局部结构。
- 经典 local controllability、linearization、controllability rank/Gramian、contact-mode identification 是强组合近邻。因此“用了 Jacobian/rank”本身没有 novelty。

### 不可约 delta

可保留的新贡献只有：**将冻结视觉 WAM 的 policy-supported action→object-effect differential geometry，特别是 rank/principal-subspace/nullspace 的事件转换，作为无触觉 contact-relation progress verification signal。**

它不是新的 controllability theory，也不是新的 WAM architecture。若最终只用 Jacobian norm、动作敏感性分数或普通 contact classifier，novelty 立即跌至 6.x。

### 最强致命反对

接触动力学恰好在 grasp/release/impact 处非光滑，局部 Jacobian 可能不存在或对 `epsilon` 极度敏感。视觉 WAM 的 rank change 也可能来自遮挡、latent saturation、动作忽略或 object tracker 抖动，而非真实接触关系。因此不能称其为物理“certificate”。

这是本候选 naturalness 低于 ESW 的原因，也是其只被“有条件保留”的原因。

### Claim ceiling

可主张：**CPPC signature 是一种比单轨迹 residual 更具结构性的、无触觉 contact-phase progress evidence。**

不可主张：局部可控性等价于真实接触；rank transition 提供形式化认证；或冻结 WAM 在 OOD 微扰下保持可信。

### E0 feasibility 与 kill test

**只授权 oracle simulator E0 的纸面可行性；在 oracle 通过前不应启动大 WAM/GPU 训练。**

- 在 grasp/release/insertion 各自成功与 matched failure post-state 上，用 simulator rollback 做 symmetric micro-perturbation；扫描至少 4 个 `epsilon` 和 3 个 object/geometry family。
- 先在 privileged object-pose effect 上计算 oracle Jacobian，再测试 RGB-derived WAM effect latent 是否复现相同 subspace ordering。
- 强 baseline 必须包括：direct contact/progress classifier、object-motion magnitude、ordinary WAM prediction residual、WorldSimProbe-style local sensitivity scalar。

预注册 kill：满足任一项即停止。

1. oracle rank/subspace 特征对 matched phase transition 的 AUROC 低于 **0.85**；
2. signature 在合理 `epsilon` 区间内的 rank/principal-angle 排序相关性低于 **0.7**；
3. WAM signature 与 oracle principal subspace 的平均 canonical correlation 低于 **0.6**；
4. 相对最强 direct classifier，phase AUPRC 未提升至少 **5 个百分点**，或 false progress update 未降低至少 **25% relative**；
5. 增益仅存在于 privileged geometry，而 RGB-derived effect representation 中消失。

---

## 未通过项

### PCCS：Progress Correction Slack

**判定：6.8–7.0，FAIL。**

“在同一物理状态编辑 policy memory，并测量最晚仍可恢复成功的时间”有一定新意，但 [TFP](https://arxiv.org/abs/2607.08283) 已在固定 observation/state/instruction 下做 hidden-state intervention，并证明 task-progress belief 因果改变 action chunk；[MemoAct](https://arxiv.org/abs/2603.18494) 及其 memory-intervention 分析进一步占据机器人 memory patching。剩余的 latest-editable-time/slack 很容易被评价为 hidden-state intervention 加经典 point-of-no-return/recoverability metric，而非新的控制机制。π0.5 又没有天然可编辑的离散 progress predicate，latent patch 很可能 off-manifold。严格下界不能给到 >7。

### Event-Time WAM Verification

**判定：6.8–7.0，FAIL。**

将 predicted/observed rollout 做 monotone time warping，再把 along-phase residual 与 orthogonal effect residual 分开，问题自然，但 mechanism 是经典 DTW/phase–amplitude decomposition 与 WAM verifier 的直接组合。[World Action Models in Real Time](https://arxiv.org/abs/2608.01880) 已明确指出 observation/prediction/executed-command temporal alignment 是核心部署条件；CheckVLA 与 When to Trust Imagination 已覆盖执行 mismatch。除非出现比 time warp 更不可约的新统计对象，否则不能过 strict gate。

### 普通 history/belief/progress memory

**判定：最高 6.x，FAIL。**

[IntentVLA](https://arxiv.org/abs/2605.14712)、TFP、MemoAct、RB-VLA、CAMP、EvoScene-VLA、ProgressVLA、ProgVLA、RTCF、StreamVLA 与 HarnessWAM 已形成密集工作簇。仅增加 event graph、keyframe bank、task-progress token、action history compression 或 WAM discrepancy memory 均不再构成 >7 novelty。

## 最终建议

若只推进一个，选择 **ESW + Observability-Hazard Verification**。它与用户的实际痛点——长时任务错误完成、进度误回滚、遮挡阶段 verifier 乱猜——对齐最直接，E0 又能先用 simulator compiler 在非 GPU 条件下证伪。

CPPC 可以作为第二条高风险机制线，但必须先通过 oracle smoothness/identifiability gate；不要直接把 4×A100 投入 WAM 训练，更不要使用“物理认证”措辞。

本轮检索已停止扩展。结论建立在截至 2026-08-31 可访问的 primary arXiv/OpenReview 页面与现有本地证据库上；“未发现 exact prior”不等于证明其不存在。
