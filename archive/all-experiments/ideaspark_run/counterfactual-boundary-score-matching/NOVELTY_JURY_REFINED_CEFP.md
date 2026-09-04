# CEFP 严格新颖性复审

## 结论

- **Verdict：FAIL**
- **Novelty：6.65 / 10**
- **门槛：严格大于 7.0；7.0 本身也不通过**
- **方法自然性：7.35 / 10**
- **实现可行性：6.9 / 10**，但可行不等于新颖
- **CPU compiler E0：不授权作为当前 CEFP 的正式实验启动**
- **GPU E0：不授权**

CEFP 比上一版 BLSM 更严谨：它修复了不同轨迹在 raw time index 上错误对齐的问题，也把训练支持严格限制到了 π0.5 实际会执行的 `h_exec=5` 前缀。然而，重新加入 2026 年最接近的 flow-preference 文献后，CEFP 已不能守住 `>7.0` 的严格 novelty gate。

最强的审稿人归纳是：

> CEFP 是把 FlowPRO/Flow-DPO 已有的 frozen-reference-adjusted flow preference，应用到由显式物理可行性工作启发的 simulator geometry-flip pairs，并用共同 suffix 将 preference 限制在实际执行前缀。K=2、共享噪声/flow time、共同 padding 和 replay preservation 使实验更干净，但尚不足以构成新的核心学习机制。

这不是说实验没有可能产生正结果；而是说，即使结果为正，目前最可信的论文贡献仍是一个**受控的训练支持构造与经验结论**，不是新 preference algorithm，也不是首次进行 VLA 物理可行性偏好学习。

## 复审对象的精确定义

本次只审查以下 CEFP 机制，不把外围工程组件计作创新：

1. 从同一个完整 simulator/controller/RNG/camera checkpoint 出发；
2. 构造一个无效 continuation 和 `K=2` 个 simulator-verified feasible alternatives；
3. 候选只在下一次实际执行的 `h_exec=5` 前缀中不同，其余 action chunk 使用共同 frozen-reference suffix；
4. positive、negative 和 frozen reference 共享 flow time `t`、完整噪声 `xi` 和 suffix；
5. 只在执行前缀上计算 OpenPI native-flow residual；
6. 使用 `e_ref-e_theta` 形成 positive-vs-invalid reference-adjusted preference；
7. 保留标准 imitation/replay/reference preservation；
8. 部署时只运行微调后的 π0.5，不使用 WAM、深度、几何 oracle 或 reranking。

## 最接近的精确机制

### 1. FlowPRO 是最强单篇近邻

[FlowPRO: Reward-Free Reinforced Fine-Tuning of Flow-Matching VLAs via Proximalized Preference Optimization](https://arxiv.org/abs/2606.05468) 已经覆盖 CEFP 学习目标的主体：

- 对 flow-matching VLA 使用 positive/negative action preference；
- 通过 intervention 和 rollback，从同一个较早状态形成错误动作与人类纠正动作；
- 以逐样本 flow-matching regression loss 作为 likelihood proxy；
- 使用 frozen reference 构造 `loss_ref-loss_theta` 型隐式奖励；
- 对 chosen/rejected action chunks 使用 pairwise log-sigmoid preference；
- 混合 SFT/replay 数据以保留基座能力；
- 通过插值把 trajectory preference 转成 per-state positive/negative action chunks。

因此，CEFP 的以下部分不能再主张新颖：

- native-flow preference 本身；
- frozen-reference adjustment；
- 同状态的 positive/negative action learning；
- flow regression loss 作为相对偏好代理；
- preference 与 imitation/replay preservation 的联合训练。

CEFP 相对 FlowPRO 的真实差异只剩：

- 数据来自 simulator-certified functional-geometry flip，而不是人类 intervention/rollback；
- 固定只优化实际执行前缀；
- 用共同 suffix 消除 bidirectional action tokens 中的候选身份泄漏；
- `K=2` feasible alternatives 对同一 invalid continuation；
- 用 compiler-roster coverage 检查可行修正方式是否被压缩。

这些差异形成了一个合理的研究协议，但尚不像一个独立的新 preference 方法。

### 2. 2604.17896 覆盖几何可行性轴

[Can Explicit Physical Feasibility Benefit VLA Learning? An Empirical Study](https://arxiv.org/abs/2604.17896) 已经研究：

- 在参考轨迹附近编辑障碍物/几何，使原动作受干扰；
- 保持相同起点和目标，并通过重规划确认编辑后的任务仍可解；
- 训练期使用显式几何和机器人运动学；
- 只在 action chunk 中发生 active clearance violation 的时间点施加局部几何损失；
- 部署期仍只依赖常规视觉与语言输入。

它没有 CEFP 的 flow preference、共同 suffix 或 K-positive roster，但已经使下列主张失效：

- 首次用 geometry flip 训练 VLA；
- 首次要求 edited scene 仍然可解；
- 首次对 action chunk 做局部物理可行性监督；
- 首次做到训练期使用几何、部署期不使用几何。

FlowPRO 与该工作结合后，已经分别覆盖 CEFP 的学习目标和数据问题。审稿人不需要找到一篇逐字符相同的论文，就可以合理地把 CEFP 解释为两条成熟机制的直接结合。

## 其他直接近邻

| Primary source | 与 CEFP 的实质重叠 | 仍未覆盖的 CEFP 差异 |
|---|---|---|
| [FlowPRO](https://arxiv.org/abs/2606.05468) | 同状态正负动作、flow loss proxy、reference adjustment、pairwise preference、SFT/replay preservation | simulator geometry flip、固定 executed-prefix、共同 suffix、K=2 roster |
| [Can Explicit Physical Feasibility Benefit VLA Learning?](https://arxiv.org/abs/2604.17896) | geometry edit、编辑后仍可解、action-time-local feasibility、训练期几何/部署期 RGB | preference 而非 SDF/clearance shaping；共同前缀比较 |
| [Logic-VLA](https://arxiv.org/abs/2608.20556) | π0.5、满足/违反约束的 rollout pairs、flow-matching preference surrogate、物理/时序约束及 nominal behavior | 约束通常在推理输入中；trajectory-level，不是共同 suffix 的执行前缀比较 |
| [DEFLECT](https://arxiv.org/abs/2605.19294) | 冻结参考策略产生 counterfactual action pairs；flow-matching likelihood-ratio surrogate；离线 post-training | 研究 delay/staleness，不研究 functional geometry 和 mode roster |
| [GRAPE](https://arxiv.org/abs/2411.19309) | VLA chosen/rejected trajectories、reference-adjusted preference、成功/失败与安全目标、能力保持 | 不是 OpenPI native-flow executed-prefix estimator |
| [Diffusion-DPO](https://arxiv.org/abs/2311.12908) | diffusion/continuous generative model 的 reference-adjusted direct preference 基础形式 | 非机器人；不处理 action chunk 的局部物理可行性 |

Logic-VLA 和 DEFLECT 很重要，因为它们说明 2026 年的 VLA post-training 文献已经不仅有一般 DPO，还在直接研究 flow-matching likelihood surrogate、counterfactual action pairs 和约束满足。CEFP 因而不能依靠“把 DPO 改写到 flow loss 上”获得 novelty。

## 四个核心组件的严格判定

### A. 同一完整状态下的 geometry-flip feasibility pairs

**判定：有价值的数据控制，但单独 novelty 弱。**

相较 2604.17896，完整 checkpoint、完全相同观测条件和候选分支确实提高了因果可解释性。然而“原动作失效、编辑场景仍可解、另有可行重规划”已经存在。CEFP 的贡献是把它整理成适合 preference learning 的 BranchRecord，不是发现了新的物理学习问题。

### B. `h_exec=5` executed-prefix 与共同 suffix

**判定：本方案最有辨识度的部分，但更像 estimator hygiene，而非新的 learning principle。**

优点：

- 与 receding-horizon 实际执行接口一致；
- 避免用 negative 的 violation index 截取处于不同技能相位的 positive；
- 对 bidirectional action-token attention，候选共享 suffix 能防止从未执行的后缀读取正负身份；
- 共享 `t` 和 `xi` 是合理的 paired variance reduction。

限制：

- 共同 reference suffix 与候选前缀拼接后可能是动力学不连续的 hybrid chunk；
- loss 虽只落在前缀，模型预测仍受共同 suffix 的双向上下文影响；
- 固定 `h_exec=5` 来自 executor 配置，而不是自动识别的任务因果边界；
- shared noise/time 是严谨比较所需的控制变量，通常不会被视为单独算法创新。

该组件足以成为技术贡献或强 ablation，但很难单独支撑 `>7.0` 的整篇论文 novelty。

### C. frozen-reference-adjusted native-flow preference

**判定：被 FlowPRO 实质覆盖。**

CEFP 的 `g_theta=stopgrad(e_ref)-e_theta` 以及 positive-vs-invalid softplus，与 FlowPRO 的 reference-adjusted per-sample flow loss preference 在机制上属于同一类。符号、softplus/log-sigmoid、是否使用固定 margin 的差别不是本质差异。

需要避免使用“exact likelihood”措辞：flow regression residual 仍是 likelihood/preference surrogate，不是经过归一化验证的真实 action likelihood。CEFP 与 FlowPRO 都依赖这一代理。

### D. K=2 alternatives 与 preservation

**判定：诊断价值中等，算法新颖性低。**

把两个 positive 都压过同一个 negative，并不自动保证两个 positive 模式均被保留。pairwise objective 没有 positive-positive diversity、set coverage 或 anti-collapse 项；`L_pres` 主要保护 replay/base distribution，也不能证明 edited-state 的两个 alternatives 都维持概率质量。

因此可以测量 `compiler-roster coverage` 和 `worst-mode success`，但不能将当前方法写成“显式保持多模态支持”的新算法。`K=2` 是从二元偏好到多 positive 的直接扩展。

## 组件组合是否形成非平凡新机制

**严格结论：形成了连贯的实验问题，但尚未形成足够非平凡的新机制。**

CEFP 的组合不是随意堆叠：共同状态、实际执行前缀、共同 suffix 和多可行分支都围绕一个清晰问题——物理可行性 post-training 是否会在修正 invalid action 时破坏邻近可行行为。其 naturalness 明显高于旧 BLSM。

但在 novelty 上，组合路径过于自然：

1. 用 2604.17896 类 compiler 获得 geometry-sensitive feasible/invalid pairs；
2. 用 FlowPRO 类 reference-adjusted flow preference 训练 π0.5；
3. 因 policy 只执行前 5 步，mask 到前缀；
4. 因 action tokens 可能双向 attention，把后缀设成共同值；
5. 用 replay 和两个 positives 检查遗忘/覆盖。

这条推导几乎是将已有偏好算法适配到新的 pair compiler 时的直接工程选择。没有单篇论文同时包含全部组件，不等于联合机制自动具有高 novelty。

## 最强致命反对意见

> “The method is FlowPRO/Flow-DPO trained on simulator-generated geometry-flip preferences. The data construction follows explicit-physical-feasibility VLA training, while the executed-prefix mask and common suffix are controls needed to make chunk-level comparison well posed. K=2 and replay are standard extensions. Where is the new learning mechanism beyond support construction?”

当前 proposal 没有足够强的回答。最好的回应只能是：CEFP 提出了更干净的、prefix-identifiable support construction，并通过实验发现它比 whole-chunk preference 和 active SDF shaping 更少破坏行为支持。这是可发表潜力的 empirical finding，但在实验前不足以按严格标准评分超过 7。

第二个风险是 mode-preservation 叙事可能被高估。若两个 positives 都只与 negative 比较，模型仍可能把概率质量集中到其中一个容易模式；只有 roster success 指标并不能反推训练目标显式保存了 mode support。

## Claim ceiling

即使后续实验成功，当前 CEFP 最稳妥的最高 claim 是：

> 在 simulator-compiled、RGB 可观测、从同一可恢复物理 checkpoint 分支的局部 functional-geometry flips 上，将 FlowPRO-style frozen-reference flow preference 限制到 receding-horizon 实际执行前缀，并对所有候选使用共同后缀，可能在相近 invalid-action reduction 下，相比 whole-chunk preference 和 active-violation geometry shaping 减少未编辑行为漂移，并改善已枚举 compiler roster 的 worst-mode success。

不能主张：

- 新的 flow-matching preference algorithm；
- 首次 VLA positive/negative preference learning；
- 首次 same-state counterfactual action preference；
- 首次 geometry-flip VLA training；
- 首次 action-time-local physical feasibility supervision；
- 显式或有保证地保存所有 feasible modes；
- 一般性的 functional geometry、安全或真实机器人可靠性；
- VLA × WAM 方法。

## 最小非 GPU falsifier 与实验授权

### 在不考虑 novelty gate 时，CPU falsifier 本身是否合理

合理。最小检查应只验证：

- 能否从同一完整 checkpoint 稳定得到 1 invalid + 2 个实质不同的 feasible prefixes；
- candidates 是否在前 5 步已经显著分叉；
- edited geometry 是否在 policy RGB 中可观测且 render/collision mesh 一致；
- common-suffix hybrid chunk 是否造成异常大的 reference residual；
- 两个 unseen padding seeds 下 margin 符号和排序是否稳定；
- 200 attempts 后 overall yield `>=15%`、每个保留 family `>=8%`。

CPU kill criteria：任一成立即停止当前形式：

1. 200 attempts 后 overall eligible yield `<15%`；
2. 任一保留 family yield `<8%`；
3. 超过 10% 的 accepted edits 在 RGB 中不可辨识或 render/collision 不一致；
4. 少于 120 个独立 BranchRecords，或任一 record 不能提供两个经轨迹/事件聚类仍可区分的 positives；
5. candidates 不能在 `h_exec=5` 内形成有效动作差异；
6. common suffix 使 prefix flow residual 对 padding seed 的符号/排序高度不稳定；
7. hybrid chunks 的 frozen-reference residual 显著偏离真实完整 chunks，使 preference 主要学习 padding artifact。

### 按用户当前严格 novelty gate 的正式授权

- **CPU compiler E0：不授权。** 它可以验证可行性，却不能把 6.65 的 novelty 提升为 `>7.0`。继续 200–800 attempts 的正式采集会绕过用户先过 novelty gate 的要求。
- **GPU E0：不授权。** 正结果最多先支持一个经验型 delta；在当前 claim 结构下，不足以证明一个 `>7.0` 的新方法。

仅有的例外是：如果主研究方向先被重新定义，并引入真正不被 FlowPRO + 2604.17896 覆盖的核心机制，可以复用少量 BranchRecord/compiler 单元测试作为新方法的基础设施；这不等于授权当前 CEFP 开始正式 E0。

## 若要再次进入 >7.0 评审，需要新增什么

仅增加更多 task、更多 GPU 或更强结果不够。至少需要一个不能自然还原为“FlowPRO + geometry pair compiler + prefix mask”的核心机制，例如：

1. 对 bidirectional action-chunk flow 建立真正的 executed-prefix conditional objective，而不是共同 padding heuristic，并给出可验证的 estimator 性质；或
2. 不是固定 `h_exec=5`，而是从物理分支中识别最小充分 causal action support，并证明该 support 对干预结果有独立作用；或
3. 提出真正的 set-valued feasible-support objective，使多个可行 modes 的质量/覆盖具有直接训练约束或校准保证，而不是 K 个 binary positive-vs-negative terms。

以上仍需再次查新；它们只是 novelty 缺口，不是自动通过的 Idea。

## 最终判决

CEFP 是一个比旧版更自然、更可证伪、也更接近可执行实验的方案。但最新 primary prior art 表明，它的核心 preference 数学被 FlowPRO 覆盖，geometry/local-feasibility 数据轴被 arXiv:2604.17896 覆盖，Logic-VLA 与 DEFLECT 又进一步压缩了 counterfactual flow-preference 的空白。剩余贡献主要是 executed-prefix/common-suffix 支持构造、K=2 roster 诊断以及受控实证比较。

**严格 novelty = 6.65 / 10，FAIL。当前不授权 CPU compiler E0 或 GPU E0。**
