已完成独立一手核验；全程只读，未修改文件。

总体结论：五篇均不构成 H1 的完整先例。最接近的组件分别是：

- CheckVLA：训练时 action–future 配对置乱，但作用于独立 verifier。
- dWorldEval：最明确的测试时 action derangement。
- Hallucination：测试时 action-shuffle 指标，并有 last-frame persistence baseline。
- CoCo：训练时结构化反事实动作约束，但不是 shuffle。
- VLAFlow：真正的 VLA predictive auxiliary shaping，但 shuffle 的是语言目标，future latent 分支还被禁止读取动作。

| 论文 | shuffle 定义 | 训练还是测试 | persistence / action-agnostic | 下游用途 |
|---|---|---|---|---|
| CheckVLA | 打乱 action–future 训练配对，保留 action-token marginal；具体置乱算法未给出 | 重训 world model | 有重训的 observation-only predictor；无 last-frame baseline | 固定 VLA 的执行时验证与 suffix repair |
| dWorldEval | 测试 batch 内排列动作，明确要求 \(\pi(i)\ne i\) | 仅测试/推理时 | 无 persistence 或 observation-only baseline | imagined rollout policy evaluation |
| Hallucination | one-step teacher-forced flow MSE 的正确动作/批内置乱动作比值 | 仅评估指标 | 有 last-frame repeat；无 learned action-agnostic predictor | CEM closed-loop MPC |
| CoCo | 无 shuffle；inverse、zero、mirror-action 是结构化反事实 | 训练时损失 | 无 persistence/observation-only baseline | CEM visual planning；另有 MBPO policy learning |
| VLAFlow | batch 内随机排列语言目标 \(y_{\pi(i)}\)，不是动作 | 训练时 pretraining ablation | 无 persistence；future-latent 分支结构上看不到 action tokens | VLA pretraining/fine-tuning |

### 1. CheckVLA — 最接近“训练时 future × shuffled action”，但不是 policy shaping

一手来源：[CheckVLA arXiv HTML](https://arxiv.org/html/2607.26789)

关键位置：

- §5 “Ablation Studies and Deployment Audits” → “Action conditioning”，Table 4
- Appendix H “Action-Conditioned Detector Ablations”，Table S3
- Appendix I “Inference-Time Action–Consequence Binding”，Table S5
- Method §4.2 “Action-Conditioned Rolling Prediction”

可安全复述：

- Appendix H 明确称其为“training-time negative control”：保持 verifier 架构和 action-token marginal，破坏 committed action 与 predicted consequence 的对应关系；该 world model 被重新训练，并独立重新拟合 discrepancy statistics 和 calibration threshold。
- Table S3 的行名明确为 “Action-shuffled world model, retrained”。其 timely recall 为 37.9%，对比 full verifier 的 77.9%；另有重训的 observation-only world predictor，timely recall 48.6%。
- Appendix I 是另一项测试时审计：冻结完整 world model，从同一 simulator snapshot 执行 factual action 与四类可行 counterfactual action，再做 action–future assignment；不能与训练时 shuffled control 混为一项实验。
- 下游不是 policy training、MPC 或纯 policy evaluation，而是固定 VLA 周围的 execution-time verification 和 suffix rewriting。Appendix H 明确固定 action backbone、downstream rewriter 和测试轨迹，只重训 detector variant。

不可过度声称：

- 论文没有说明 shuffle 是否 batch 内进行、是否强制无固定点、按 episode/phase/action family 如何配对。只能说保留 action-token marginal，不能提升为严格的 conditional-distribution-matched derangement。
- observation-only 是明确 action-agnostic baseline；文中的 temporal “persistence aggregation”不是 last-frame persistence predictor。
- 这不证明 shuffled-action auxiliary 对 policy representation 的影响：world model/monitor 与 policy path 分离，监控 encoder 冻结，预测损失不回传塑造 VLA 表征。
- Table S5 只证明联合的 action tokens + deterministic proprioceptive rollout 具有 binding，论文自己指出不能分离这两条信息路径。

与 H1 的明确差异：H1 把 predictive auxiliary 放入共享 policy/VLA 训练并考察 representation 与 closed-loop；CheckVLA 的 action shuffle 训练的是独立 verifier，闭环收益来自检测和重写。

### 2. dWorldEval — 定义最严格的 derangement，但完全是测试时诊断

一手来源：[dWorldEval arXiv HTML](https://arxiv.org/html/2604.22152)

关键位置：

- Appendix B “Verifying Causal Dependency via Action Shuffling”，Table 5、Figure 9
- §3.1 “Policy evaluation via imagination”
- §4.2.1 “Evaluating Action Controllability”
- §4.3 “World-Model as a Reliable Proxy for Policy Evaluation”

可安全复述：

- 对测试 batch \(\{o_t^i,h^i,l^i,a^i,o_{t+\Delta}^i\}\)，以 batch-wise permutation 替换动作：
  \[
  \tilde a^i=a^{\pi(i)},\qquad \pi(i)\ne i.
  \]
  当前观察、历史和语言保持原样。
- 这是明确的无固定点 batch derangement；另外以概率 \(p\) 交换来自其他样本/episode 的 action chunks。
- world model 不重训。Appendix B 明确称其为 inference-time corruption，并在同一测试集上比较 aligned 与 shuffled rollout。
- Table 5：LPIPS 从 0.215 恶化到 0.461，\(\Delta\)LPIPS 从 0.324 恶化到 0.697。
- 下游是 policy evaluation：policy 与 world model 闭环交互形成 imagined rollout，再用预测 progress/success 估计和排序真实 policy performance。论文还明确将其与 policy learning 区分。

不可过度声称：

- 动作来自其他样本/episode，未做 instruction、phase、state 可达性或难度匹配；因此它是强 action-sensitivity sanity check，不是保证物理可行的 same-state counterfactual。
- 没有重训的 shuffled model，也没有 representation 或 policy-learning 因果效应。
- WorldEval、WorldGym、Ctrl-World 都是 action-conditioned world-model baselines；论文未提供 last-frame persistence 或 observation-only learned predictor。
- “证明 causal dependency”是作者的章节措辞；更保守的表述是“证明预测和评估指标对输入动作对齐敏感”，不能据此证明真实因果模型被辨识。

与 H1 的明确差异：H1 把 derangement 作为训练条件；dWorldEval 只在冻结模型的输入端做测试时污染，并把结果用于 world-model fidelity 和 policy-ranking 诊断。

### 3. Hallucination in World Models — shuffle 指标 + persistence baseline + MPC

一手来源：[Hallucination in World Models arXiv HTML](https://arxiv.org/html/2606.27326)

关键位置：

- §5 “Experiments” → Evaluation metrics
- §5.1，Tables 1–2
- §4.3 “Mitigating Hallucination”
- Appendix D “Data Collection”

可安全复述：

- “Action shuffle ratio”以 one-step teacher-forced flow MSE 比较正确动作与 batch-shuffled actions；比值越高代表更强动作敏感性，论文以 ratio \(\le 1.1\) 标记 action-marginalized。
- shuffle 是对已训练 world model 的评估指标，不是 shuffled-action 模型训练条件。覆盖感知 mid-training 和 targeted finetuning 是另一套干预。
- 明确存在 persistence baseline：将最后一帧重复整个 rollout horizon；rollout PSNR 相对它的增益 \(\le0\) 被定义为 scene-divergent。
- 下游性能通过 CEM closed-loop MPC 测量，规划 horizon 32，每 16 步重规划。不是 policy evaluation，也不是把预测损失回传到 policy。
- Table 2 中 no-op/random/expert/human/curiosity 是数据采集来源，不是 action-agnostic dynamics baselines。

不可过度声称：

- 正文没有给 batch shuffle 的排列单位、是否无固定点，亦未声明状态/任务/phase 匹配；不能称为严格 derangement 或严格 distribution-preserving control。
- persistence 只是 rollout-quality 的静态基准，不是容量匹配、重新训练的 action-agnostic world model。
- shuffle ratio 是 teacher-forced one-step sensitivity；不能直接替代自由 rollout、闭环控制或 policy-representation 的因果证据。
- MPC 改善只能说明 world model 对规划有用，不说明 auxiliary shaping 改善了 policy representation。

与 H1 的明确差异：它研究 standalone world-model coverage 和 hallucination；shuffle 只生成评估标签，闭环由 MPC 驱动，不存在 future/past × correct/shuffled 的 policy-training factorial。

### 4. CoCo — 训练时 counterfactual constraints，但没有 shuffle

一手来源：[CoCo arXiv HTML](https://arxiv.org/html/2608.04653)

关键位置：

- Method “Multi-Step Counterfactual Consistency”，Eqs. 2–4
- “Action-Spatial Counterfactual Consistency”，Eq. 5
- Experiments “Visual Planning”，Table 2
- “Model-based Reinforcement Learning”，Figure 6

可安全复述：

- 全文没有 action shuffle/derangement。
- MSC2 是训练时三分支约束：
  - reference branch 用真实动作预测真实未来；
  - inverse-action branch 从 reference 的预测终点执行逆动作，要求回到起始状态；
  - zero-action branch 要求零动作下不漂移。
- ASC2 同时镜像场景并变换动作，约束 hidden representation 的空间等变性。
- 下游有两类：
  - VP² visual planning：CEM 优化 horizon-10 action sequence，属于 MPC；
  - MetaWorld：预训练 CoCo world model 被用于 MBPO，属于 model-based policy learning。
- “ARC random baseline = 1/3”是三选一指标的机会水平，不是 random-policy 或 action-agnostic world-model baseline。

不可过度声称：

- inverse、zero、mirrored actions 都是有语义结构的干预，不保留原动作分布，不能称为 shuffled-action control。
- 没有 observation-only 或 last-frame persistence predictor。
- zero-action branch 是训练约束，不是 action-agnostic baseline。
- 论文明确承认逆动作对不可逆接触/复杂语义动作可能不成立；零动作恒等假设对有惯性或自主动态的环境也不应泛化。
- 虽然 MBPO 会训练 policy，CoCo 损失训练的是 world model，而不是作为共享 VLA/policy representation auxiliary 直接回传。

与 H1 的明确差异：CoCo 比 H1 更接近“改善 action controllability 的训练方法”，但缺少 shuffled marginal control、past target、2×2 factorial 和共享 VLA 表征诊断。

### 5. VLAFlow — 与 H1 的训练范式最接近，但 shuffle 对象和因果路径不同

一手来源：[VLAFlow arXiv HTML](https://arxiv.org/html/2607.01586)

关键位置：

- §3.1 “Controlled Comparison Protocol”，Table 1
- §3.4 MindLPI
- §3.5 MindWPI，Eqs. 5–6
- §4.5 “Action–language correspondence”，Eq. 8、Table 7
- §4.5 MindWPI objective ablation，Table 9
- Appendix A.3 “Attention Mask”

可安全复述：

- Table 7 shuffle 的是由 action chunk 生成的语言描述 \(y_i\)，不是动作：
  \[
  \mathcal L_{\rm lang}(o_i,\ell_i,y_{\pi(i)}).
  \]
  \(\pi\) 每个 pretraining mini-batch 独立随机采样；observation、instruction、连续动作目标、loss weight 和训练 protocol 不变。
- 该干预近似保持语言目标的 vocabulary、template、length 和 batch marginal，破坏 example-wise action–language correspondence。它属于训练时 pretraining ablation。
- 没有声明 \(\pi(i)\ne i\)，所以不能称为严格 derangement。
- MindWPI 是真实的 VLA predictive auxiliary shaping：共享模型同时优化 action loss 和 future V-JEPA2 latent loss，并在下游 fine-tuning/closed-loop policy evaluation 中比较迁移。
- 但 Appendix A.3 明确规定 latent tokens 不能读取 noised action tokens；future latent prediction只依赖当前视觉、语言和当前 latent。动作 token 可以反向读取预测 latent。
- 论文控制了 backbone、action space、数据源、sampling、training steps、optimizer 和学习率；但没有证明 auxiliary variants 的 token 数、FLOPs 或有效优化难度完全匹配。

不可过度声称：

- Table 7 不能作为 shuffled-action 证据；它只说明 action-derived language target 的逐样本对应有价值。
- 论文自己指出置乱会产生 contradictory supervision，因此不能据此声称模型获得了可解释动作语义。
- MindWPI 的 latent predictor 被结构性禁止读取动作，不能将其叫作 action-conditioned future predictor，也无法用它直接回答“正确动作身份是否必要”。
- MindPI/action-only + current-V-JEPA 是 policy-training controls，不是 observation-only/persistence world-model baselines。
- 没有 past target，也没有 future/past × correct/shuffled 2×2 interaction。

与 H1 的明确差异：VLAFlow 已覆盖“future predictive auxiliary 塑造 VLA 并影响闭环迁移”这一主轴；H1 若要保持独立性，关键增量必须落在 action identity 的严格 matched derangement、past negative control、完整 factorial interaction，以及 representation/closed-loop 双层证据上。

最终可用于 novelty 表述的安全版本是：

> 现有工作分别研究了独立 verifier 的训练时 action–future shuffle、冻结 world model 的测试时 action derangement、world-model action-shuffle diagnostics、结构化反事实动力学约束，以及 VLA 的 future-latent auxiliary shaping；尚未在共享 VLA/policy 训练中，以 matched 的 future-vs-past × correct-vs-marginal-preserving shuffled-action 设计联合识别 predictive supervision 的时间方向与动作身份贡献。
